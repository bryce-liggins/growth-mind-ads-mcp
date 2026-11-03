import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from growth_mind_ads_mcp import server, doctor


class HeaderTests(unittest.TestCase):
    def request(self, env):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with patch.dict(os.environ, env, clear=True), \
             patch.object(server, "_access_token", return_value="test-only-token"), \
             patch.object(server, "urlopen", return_value=response) as call:
            server._mutate("1234567890", [], True)
            return {k.lower(): v for k, v in call.call_args.args[0].headers.items()}

    def test_direct_access_does_not_require_legacy_token_or_manager(self):
        headers = self.request({})
        self.assertNotIn("developer-token", headers)
        self.assertNotIn("login-customer-id", headers)
        self.assertEqual(headers["authorization"], "Bearer test-only-token")

    def test_manager_and_legacy_header_are_optional_and_normalized(self):
        headers = self.request({"GOOGLE_ADS_LOGIN_CUSTOMER_ID": "111-111-1111",
                                "GOOGLE_ADS_DEVELOPER_TOKEN": "fictional-test-only"})
        self.assertEqual(headers["login-customer-id"], "1111111111")
        self.assertEqual(headers["developer-token"], "fictional-test-only")


class AuditTests(unittest.TestCase):
    def test_audit_omits_ticket_and_creates_private_file(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "audit"
            target = folder / "audit.jsonl"
            with patch.object(server, "AUDIT_DIR", folder), patch.object(server, "AUDIT_FILE", target):
                server._audit("validate", "1234567890", [],
                              {"approval_phrase": "never-persist-this", "applied": False})
            data = json.loads(target.read_text())
            self.assertNotIn("approval_phrase", data["result"])
            self.assertNotIn("never-persist-this", target.read_text())
            self.assertFalse(data["result"]["applied"])
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)


class DoctorTests(unittest.TestCase):
    def test_missing_config_is_failure_without_values(self):
        with patch.dict(os.environ, {}, clear=True):
            result = doctor.check()
        self.assertFalse(result["configuration_ok"])
        self.assertFalse(result["google_access_tested"])

    def test_existing_file_is_not_read_or_google_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            credential = Path(directory) / "private.json"
            credential.write_text("secret sentinel: contents must not be read")
            credential.chmod(0o600)
            with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": str(credential)}, clear=True), \
                 patch.object(Path, "read_text", side_effect=AssertionError("must not read")):
                result = doctor.check()
            self.assertTrue(result["configuration_ok"])
            self.assertFalse(result["google_access_tested"])
            self.assertNotIn("sentinel", json.dumps(result))


class AdditionalApprovalTests(unittest.TestCase):
    def test_ticket_cannot_cross_customer(self):
        operations = [{"campaignOperation": {"create": {"name": "Fictional"}}}]
        ticket = server._issue_approval_phrase("1234567890", operations)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            server._consume_approval_phrase(ticket, "1111111111", operations)

