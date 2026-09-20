import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_data


class QasperNormalizationContract(unittest.TestCase):
    def test_only_resolvable_source_evidence_becomes_a_case(self):
        paper = {
            "id": "paper-1",
            "title": "A paper",
            "full_text": [
                {"section_name": "Results", "paragraphs": ["The hybrid system improves evidence recall."]}
            ],
            "qas": [
                {"question_id": "q-1", "question": "What improves recall?", "answers": [{"answer": "The hybrid system", "evidence": ["The hybrid system improves evidence recall."]}]},
                {"question_id": "q-2", "question": "No citation?", "answers": [{"answer": "Unknown", "evidence": []}]},
            ],
        }
        rows = fetch_data.normalize({"rows": [{"row": paper}]}, 10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question_id"], "q-1")
        self.assertEqual(rows[0]["evidence_id"], "paper-1:0:0")


if __name__ == "__main__":
    unittest.main()
