import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from google.auth.exceptions import RefreshError, TransportError
from growth_mind_ads_mcp import server, auth_health

CUSTOMER = '1234567890'
OPS = [{'campaignOperation': {'update': {'resourceName': f'customers/{CUSTOMER}/campaigns/123', 'status': 'PAUSED'}, 'updateMask': 'status'}}]

class FailureAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        for key, value in [('AUDIT_DIR', self.folder), ('AUDIT_FILE', self.folder / 'audit.jsonl')]:
            patcher = patch.object(server, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        server.PENDING_APPROVALS.clear()

    def entries(self):
        return [json.loads(line) for line in (self.folder / 'audit.jsonl').read_text().splitlines()]

    def test_local_validation_failure_is_logged_without_input_values(self):
        with self.assertRaises(ValueError):
            server._validate_batch('private-sentinel', [])
        entries = self.entries()
        self.assertEqual(entries[-1]['event'], 'validate_mutation_failed')
        self.assertNotIn('private-sentinel', json.dumps(entries))

    def test_google_validation_failure_does_not_log_error_secrets(self):
        with patch.object(server, '_mutate', side_effect=RuntimeError('secret-sentinel')):
            with self.assertRaises(RuntimeError):
                server._validate_batch(CUSTOMER, OPS)
        self.assertEqual(self.entries()[-1]['event'], 'validate_mutation_failed')
        self.assertNotIn('secret-sentinel', json.dumps(self.entries()))

    def test_invalid_ticket_apply_is_logged_without_phrase(self):
        with patch.object(server, '_mutate') as mutate:
            with self.assertRaises(ValueError):
                server._apply_batch(CUSTOMER, OPS, 'secret-ticket-sentinel')
            mutate.assert_not_called()
        self.assertEqual(self.entries()[-1]['event'], 'apply_mutation_failed')
        self.assertNotIn('secret-ticket-sentinel', json.dumps(self.entries()))

    def test_failed_revalidation_prevents_live_apply(self):
        ticket = server._issue_approval_phrase(CUSTOMER, OPS)
        with patch.object(server, '_mutate', side_effect=RuntimeError('no')) as mutate:
            with self.assertRaises(RuntimeError):
                server._apply_batch(CUSTOMER, OPS, ticket)
            self.assertEqual(mutate.call_count, 1)
            self.assertTrue(mutate.call_args.kwargs['validate_only'])
        self.assertEqual(self.entries()[-1]['event'], 'apply_mutation_failed')

    def test_remote_apply_timeout_is_logged_as_unconfirmed(self):
        ticket = server._issue_approval_phrase(CUSTOMER, OPS)
        with patch.object(server, '_mutate', side_effect=[{}, TimeoutError('private')]):
            with self.assertRaises(TimeoutError):
                server._apply_batch(CUSTOMER, OPS, ticket)
        result = self.entries()[-1]['result']
        self.assertEqual(result['outcome'], 'unconfirmed')
        self.assertTrue(result['readback_required'])

    def test_unwritable_audit_prevents_api_call(self):
        with patch.object(server, '_audit', side_effect=OSError('disk')), patch.object(server, '_mutate') as mutate:
            with self.assertRaises(OSError):
                server._validate_batch(CUSTOMER, OPS)
            mutate.assert_not_called()

    def test_failure_audit_write_failure_is_explicit(self):
        with patch.object(server, '_audit', side_effect=[None, OSError('disk')]):
            with self.assertRaisesRegex(RuntimeError, 'failure audit could not be saved'):
                server._validate_batch(CUSTOMER, [])

class PolicyTests(unittest.TestCase):
    def budget(self, amount, action='update', **extra):
        payload = {'amountMicros': amount, **extra}
        body = {action: payload}
        if action == 'update':
            payload['resourceName'] = f'customers/{CUSTOMER}/campaignBudgets/123'
            body['updateMask'] = 'amount_micros'
        return [{'campaignBudgetOperation': body}]

    def test_budget_disabled_without_owner_cap(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, 'require'):
            server._prepare_for_customer(CUSTOMER, self.budget(100))

    def test_create_and_update_enforce_cap(self):
        with patch.dict(os.environ, {'GROWTH_MIND_ADS_MAX_BUDGET_MICROS': '100'}, clear=True):
            for action in ['create', 'update']:
                server._prepare_for_customer(CUSTOMER, self.budget('100', action))
                for amount in [101, -1, 0, True, 1.5]:
                    with self.subTest(action=action, amount=amount), self.assertRaises(ValueError):
                        server._prepare_for_customer(CUSTOMER, self.budget(amount, action))

    def test_total_budget_and_wildcard_mask_rejected(self):
        with patch.dict(os.environ, {'GROWTH_MIND_ADS_MAX_BUDGET_MICROS': '100'}, clear=True):
            for extra in [{'totalAmountMicros': '100'}, {'period': 'CUSTOM_PERIOD'}]:
                with self.assertRaises(ValueError):
                    server._prepare_for_customer(CUSTOMER, self.budget(50, **extra))
            ops = self.budget(50)
            ops[0]['campaignBudgetOperation']['updateMask'] = '*'
            with self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, ops)

    def test_removals_require_type_specific_opt_in(self):
        ops = [{'campaignOperation': {'remove': f'customers/{CUSTOMER}/campaigns/123'}}]
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, 'disabled'):
            server._prepare_for_customer(CUSTOMER, ops)
        with patch.dict(os.environ, {'GROWTH_MIND_ADS_ALLOWED_REMOVE_TYPES': 'campaignCriterionOperation'}, clear=True), self.assertRaises(ValueError):
            server._prepare_for_customer(CUSTOMER, ops)
        with patch.dict(os.environ, {'GROWTH_MIND_ADS_ALLOWED_REMOVE_TYPES': 'campaignOperation'}, clear=True):
            server._prepare_for_customer(CUSTOMER, ops)

    def test_removed_status_cannot_bypass_removal_policy(self):
        ops = [{'campaignOperation': {'update': {'resourceName': f'customers/{CUSTOMER}/campaigns/123', 'status': 'REMOVED'}, 'updateMask': 'status'}}]
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, 'disabled'):
            server._prepare_for_customer(CUSTOMER, ops)

class AuthHealthTests(unittest.TestCase):
    def check_with(self, error=None, **kwargs):
        cred = MagicMock()
        cred.token = 'private-token-sentinel'
        cred.refresh.side_effect = error
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/fictional/private'}, clear=True), patch.object(auth_health.google.auth, 'load_credentials_from_file', return_value=(cred, None)):
            result = auth_health.check(**kwargs)
        self.assertNotIn('sentinel', json.dumps(result))
        self.assertFalse(result['ads_access_tested'])
        return result

    def test_unknown_expiry_is_not_invented(self):
        result = self.check_with()
        self.assertEqual(result['status'], 'healthy')
        self.assertFalse(result['refresh_expiry_known'])

    def test_known_expiry_warning(self):
        result = self.check_with(known_refresh_expiry='2026-11-05T00:00:00Z', now=datetime(2026,11,3,tzinfo=timezone.utc))
        self.assertEqual(result['status'], 'expiry_warning')
        self.assertTrue(result['notification_required'])

    def test_invalid_grant_notifies_without_raw_error(self):
        self.assertEqual(self.check_with(RefreshError('invalid_grant private-sentinel'))['status'], 'reauthorization_required')

    def test_connection_failure_is_distinct(self):
        self.assertEqual(self.check_with(TransportError('private-sentinel'))['status'], 'connection_failed')

    def test_invalid_expiry_fails_without_refresh(self):
        with patch.object(auth_health.google.auth, 'load_credentials_from_file') as load:
            self.assertEqual(auth_health.check('2026-11-05')['status'], 'invalid_expiry_configuration')
            load.assert_not_called()

class ExampleTests(unittest.TestCase):
    def test_negative_examples_prepare_and_summarize(self):
        examples = Path(__file__).resolve().parents[1] / 'examples'
        for name in ['campaign-phrase-negative.json', 'shared-negative-list.json']:
            value = json.loads((examples / name).read_text())
            ops, forced = server._prepare_for_customer(value['customer_id'], value['operations'])
            self.assertEqual(forced, 0)
            self.assertEqual(server._operation_summary(ops, forced)['negative_keyword_creates'], 1)
