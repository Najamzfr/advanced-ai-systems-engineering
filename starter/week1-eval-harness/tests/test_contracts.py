import json
import unittest
from pathlib import Path

from evals.metrics import macro_f1
from evals.providers import available_models, predict
from course.check import REQUIRED_CONFUSION_INTENTS as CHECKER_INTENTS
from scripts.fetch_banking77 import REQUIRED_CONFUSION_INTENTS as FETCH_INTENTS


class ContractTests(unittest.TestCase):
    def test_two_models_are_available(self):
        self.assertEqual(available_models(), ["baseline-v1", "robust-v2"])

    def test_provider_returns_structured_result(self):
        result = predict("baseline-v1", "I am still waiting for my card")
        self.assertEqual(result["label"], "card_arrival")
        self.assertTrue(result["schema_valid"])

    def test_macro_f1_is_reproducible(self):
        rows = [{"label": "a", "prediction": "a"}, {"label": "b", "prediction": "a"}]
        self.assertEqual(macro_f1(rows), 0.333333)

    def test_confusion_slice_is_fixed_and_shared(self):
        self.assertEqual(FETCH_INTENTS, CHECKER_INTENTS)
        self.assertEqual(len(FETCH_INTENTS), 15)
        self.assertEqual(len(set(FETCH_INTENTS)), 15)
        self.assertIn("card_arrival", FETCH_INTENTS)
        self.assertIn("cash_withdrawal_not_recognised", FETCH_INTENTS)
        self.assertIn("top_up_reverted", FETCH_INTENTS)
        self.assertIn("reverted_card_payment", FETCH_INTENTS)
        self.assertNotIn("reverted_card_payment?", FETCH_INTENTS)


if __name__ == "__main__":
    unittest.main()
