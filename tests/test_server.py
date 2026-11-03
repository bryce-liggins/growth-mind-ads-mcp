import importlib.util
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


from growth_mind_ads_mcp import server


CUSTOMER = "1234567890"  # Fictional fixture; never call Google with it.


def setUpModule():
    global audit_tmp, audit_patches
    audit_tmp = tempfile.TemporaryDirectory()
    audit_patches = [patch.object(server, "AUDIT_DIR", Path(audit_tmp.name)),
                     patch.object(server, "AUDIT_FILE", Path(audit_tmp.name) / "audit.jsonl")]
    for item in audit_patches:
        item.start()


def tearDownModule():
    for item in audit_patches:
        item.stop()
    audit_tmp.cleanup()


class PreparationTests(unittest.TestCase):
    def test_positive_keyword_create_is_forced_paused(self):
        operations = [{
            "adGroupCriterionOperation": {
                "create": {
                    "adGroup": f"customers/{CUSTOMER}/adGroups/123",
                    "status": "ENABLED",
                    "keyword": {"text": "emergency plumber", "matchType": "PHRASE"},
                }
            }
        }]
        prepared, forced = server._prepare_for_customer(CUSTOMER, operations)
        payload = prepared[0]["adGroupCriterionOperation"]["create"]
        self.assertEqual(payload["status"], "PAUSED")
        self.assertEqual(forced, 1)

    def test_campaign_negative_keyword_can_be_created_live(self):
        operations = [{
            "campaignCriterionOperation": {
                "create": {
                    "campaign": f"customers/{CUSTOMER}/campaigns/123",
                    "negative": True,
                    "keyword": {"text": "example competitor", "matchType": "EXACT"},
                }
            }
        }]
        prepared, forced = server._prepare_for_customer(CUSTOMER, operations)
        payload = prepared[0]["campaignCriterionOperation"]["create"]
        self.assertNotIn("status", payload)
        self.assertEqual(forced, 0)
        summary = server._operation_summary(prepared, forced)
        self.assertEqual(summary["negative_keyword_creates"], 1)

    def test_pause_update_and_update_mask_are_preserved(self):
        operations = [{
            "adGroupCriterionOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/adGroupCriteria/123~456",
                    "status": "PAUSED",
                },
                "updateMask": "status",
            }
        }]
        prepared, _ = server._prepare_for_customer(CUSTOMER, operations)
        body = prepared[0]["adGroupCriterionOperation"]
        self.assertEqual(body["update"]["status"], "PAUSED")
        self.assertEqual(body["updateMask"], "status")

    def test_enable_update_is_allowed_but_summarized(self):
        operations = [{
            "campaignOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/campaigns/123",
                    "status": "ENABLED",
                },
                "updateMask": "status",
            }
        }]
        prepared, forced = server._prepare_for_customer(CUSTOMER, operations)
        summary = server._operation_summary(prepared, forced)
        self.assertEqual(summary["status_updates"], {"ENABLED": 1})

    @patch.dict(os.environ, {"GROWTH_MIND_ADS_ALLOWED_REMOVE_TYPES": "campaignCriterionOperation"})
    def test_remove_is_allowed_and_summarized(self):
        operations = [{
            "campaignCriterionOperation": {
                "remove": f"customers/{CUSTOMER}/campaignCriteria/123~456"
            }
        }]
        prepared, forced = server._prepare_for_customer(CUSTOMER, operations)
        self.assertEqual(server._operation_summary(prepared, forced)["remove_operations"], 1)

    def test_cross_account_resource_name_is_rejected(self):
        operations = [{
            "campaignOperation": {
                "update": {
                    "resourceName": "customers/1111111111/campaigns/123",
                    "status": "PAUSED",
                },
                "updateMask": "status",
            }
        }]
        with self.assertRaisesRegex(ValueError, "different customer"):
            server._prepare_for_customer(CUSTOMER, operations)

    def test_update_requires_update_mask(self):
        operations = [{
            "campaignOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/campaigns/123",
                    "status": "PAUSED",
                }
            }
        }]
        with self.assertRaisesRegex(ValueError, "updateMask"):
            server._prepare_for_customer(CUSTOMER, operations)


class ConversionActionTests(unittest.TestCase):
    def operation(self, primary, **extra):
        return [{
            "conversionActionOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/conversionActions/123",
                    "primaryForGoal": primary,
                    **extra,
                },
                "updateMask": "primary_for_goal",
            }
        }]

    def test_primary_and_secondary_updates_are_prepared_and_summarized(self):
        for primary, label in [(True, "PRIMARY"), (False, "SECONDARY")]:
            with self.subTest(primary=primary):
                prepared, forced = server._prepare_for_customer(
                    CUSTOMER, self.operation(primary)
                )
                self.assertEqual(forced, 0)
                self.assertEqual(
                    server._operation_summary(prepared, forced)["conversion_goal_updates"],
                    {label: 1},
                )

    def test_incomplete_create_and_remove_are_rejected(self):
        for action, payload in [
            ("create", {"name": "test"}),
            ("remove", f"customers/{CUSTOMER}/conversionActions/123"),
        ]:
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    server._prepare_for_customer(
                        CUSTOMER, [{"conversionActionOperation": {action: payload}}]
                    )

    def booking(self, **changes):
        payload = {
            "name": "Example - Completed Booking", "type": "WEBPAGE",
            "category": "BOOK_APPOINTMENT", "countingType": "ONE_PER_CLICK",
            "primaryForGoal": False, "status": "ENABLED",
            "clickThroughLookbackWindowDays": 30,
        }
        payload.update(changes)
        return [{"conversionActionOperation": {"create": payload}}]

    def test_secondary_website_booking_creation_allowed_without_mutation(self):
        operations = self.booking()
        prepared, forced = server._prepare_for_customer(CUSTOMER, operations)
        self.assertEqual(prepared, operations)
        self.assertIsNot(prepared, operations)
        self.assertEqual(forced, 0)
        summary = server._operation_summary(prepared, forced)
        self.assertEqual(summary["secondary_website_booking_creates"], 1)
        self.assertEqual(summary["conversion_goal_updates"], {})

    def test_booking_create_allowed_in_legacy_create_only_preparation(self):
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.booking(), create_only=True)
        self.assertIs(prepared[0]["conversionActionOperation"]["create"]["primaryForGoal"], False)

    def test_booking_create_rejects_other_types_categories_counts_statuses(self):
        for changes in [
            {"type": "UPLOAD_CLICKS"}, {"category": "PAGE_VIEW"},
            {"countingType": "MANY_PER_CLICK"}, {"status": "REMOVED"},
            {"primaryForGoal": True}, {"primaryForGoal": 0},
            {"primaryForGoal": "false"}, {"primaryForGoal": None},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, self.booking(**changes))

    def test_booking_create_rejects_extra_fields_and_resource_ids(self):
        for changes in [
            {"valueSettings": {"defaultValue": 200}},
            {"resourceName": f"customers/{CUSTOMER}/conversionActions/-1"},
            {"enhancedConversionsForLeadsEnabled": True},
            {"phoneCallDurationSeconds": 60}, {"unknown": True},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, self.booking(**changes))

    def test_booking_name_validation(self):
        for value in ["", " ", None, 123, "x" * 101, "booking\ncompletion"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, self.booking(name=value))

    def test_booking_click_window_bounds_and_boolean_rejection(self):
        for value in [1, 30, 90]:
            server._prepare_for_customer(CUSTOMER, self.booking(clickThroughLookbackWindowDays=value))
        for value in [0, 91, True, False, "30", 30.0]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, self.booking(clickThroughLookbackWindowDays=value))

    def test_booking_optional_window_can_be_omitted(self):
        operation = self.booking()
        del operation[0]["conversionActionOperation"]["create"]["clickThroughLookbackWindowDays"]
        server._prepare_for_customer(CUSTOMER, operation)

    def test_every_required_booking_field_must_be_present(self):
        for field in server.CONVERSION_CREATE_REQUIRED_FIELDS:
            operation = self.booking()
            del operation[0]["conversionActionOperation"]["create"][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                server._prepare_for_customer(CUSTOMER, operation)

    @patch.object(server, "_mutate")
    def test_booking_payload_change_rejected_before_api_call(self, mutate):
        server.PENDING_APPROVALS.clear()
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.booking())
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        with self.assertRaisesRegex(ValueError, "payload changed"):
            server._apply_batch(CUSTOMER, self.booking(name="Different booking"), phrase)
        mutate.assert_not_called()

    @patch.object(server, "_audit")
    @patch.object(server, "_mutate")
    def test_booking_validate_is_nonmutating_and_apply_revalidates(self, mutate, audit):
        mutate.return_value = {}
        result = server._validate_batch(CUSTOMER, self.booking())
        self.assertFalse(result["applied"])
        self.assertEqual(mutate.call_args.kwargs["validate_only"], True)
        mutate.reset_mock()
        server._apply_batch(CUSTOMER, self.booking(), result["approval_phrase"])
        self.assertEqual([c.kwargs["validate_only"] for c in mutate.call_args_list], [True, False])

    def test_other_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "permits only"):
            server._prepare_for_customer(
                CUSTOMER, self.operation(False, status="REMOVED")
            )

    def test_mask_must_be_exact(self):
        for mask in ["primaryForGoal", "primary_for_goal,status"]:
            with self.subTest(mask=mask):
                operation = self.operation(False)
                operation[0]["conversionActionOperation"]["updateMask"] = mask
                with self.assertRaisesRegex(ValueError, "exactly primary_for_goal"):
                    server._prepare_for_customer(CUSTOMER, operation)

    def test_primary_flag_must_be_boolean(self):
        for value in [0, 1, "false", None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "must be a boolean"):
                    server._prepare_for_customer(CUSTOMER, self.operation(value))

    def test_resource_name_must_be_exact_and_customer_owned(self):
        for name in [
            "customers/1111111111/conversionActions/123",
            f"customers/{CUSTOMER}/conversionActions/not-an-id",
            f"customers/{CUSTOMER}/campaigns/123",
        ]:
            with self.subTest(name=name):
                operation = self.operation(False)
                operation[0]["conversionActionOperation"]["update"]["resourceName"] = name
                with self.assertRaisesRegex(ValueError, "resourceName in this customer"):
                    server._prepare_for_customer(CUSTOMER, operation)

    def test_approval_phrase_is_bound_to_primary_flag(self):
        server.PENDING_APPROVALS.clear()
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operation(False))
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        changed, _ = server._prepare_for_customer(CUSTOMER, self.operation(True))
        with self.assertRaisesRegex(ValueError, "payload changed"):
            server._consume_approval_phrase(phrase, CUSTOMER, changed)


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        server.PENDING_APPROVALS.clear()
        self.operations = [{
            "campaignOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/campaigns/123",
                    "status": "PAUSED",
                },
                "updateMask": "status",
            }
        }]

    @patch.object(server, "_mutate", return_value={"validated": True})
    @patch.object(server, "_audit")
    def test_approval_phrase_is_bound_to_payload(self, audit, mutate):
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operations)
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        changed = [{
            "campaignOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/campaigns/123",
                    "status": "ENABLED",
                },
                "updateMask": "status",
            }
        }]
        changed_prepared, _ = server._prepare_for_customer(CUSTOMER, changed)
        with self.assertRaisesRegex(ValueError, "payload changed"):
            server._consume_approval_phrase(phrase, CUSTOMER, changed_prepared)

    @patch.object(server, "_audit")
    @patch.object(server, "_mutate")
    def test_apply_reruns_validation_then_mutates(self, mutate, audit):
        mutate.side_effect = [{"validated": True}, {"results": []}]
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operations)
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        result = server._apply_batch(CUSTOMER, self.operations, phrase)
        self.assertTrue(result["applied"])
        self.assertEqual(
            [call.kwargs["validate_only"] for call in mutate.call_args_list],
            [True, False],
        )
        self.assertEqual(audit.call_count, 2)

    @patch.object(server, "_mutate")
    def test_changed_payload_rejects_prior_phrase_before_api_call(self, mutate):
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operations)
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        changed = [{
            "campaignOperation": {
                "update": {
                    "resourceName": f"customers/{CUSTOMER}/campaigns/123",
                    "status": "ENABLED",
                },
                "updateMask": "status",
            }
        }]
        with self.assertRaisesRegex(ValueError, "payload changed"):
            server._apply_batch(CUSTOMER, changed, phrase)
        mutate.assert_not_called()

    def test_approval_phrase_is_single_use(self):
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operations)
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        server._consume_approval_phrase(phrase, CUSTOMER, prepared)
        with self.assertRaisesRegex(ValueError, "unknown or already used"):
            server._consume_approval_phrase(phrase, CUSTOMER, prepared)

    @patch.object(server.time, "time", return_value=10_000)
    def test_approval_phrase_expires(self, now):
        prepared, _ = server._prepare_for_customer(CUSTOMER, self.operations)
        phrase = server._issue_approval_phrase(CUSTOMER, prepared)
        now.return_value = 10_000 + server.APPROVAL_TTL_SECONDS + 1
        with self.assertRaisesRegex(ValueError, "expired"):
            server._consume_approval_phrase(phrase, CUSTOMER, prepared)


if __name__ == "__main__":
    unittest.main()
