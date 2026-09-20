import json, pathlib, subprocess, sys, unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lora_adapter
class AdaptationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,"scripts/fetch_data.py"],cwd=ROOT,check=True)
        subprocess.run([sys.executable,"project.py","--limit","20","--adapter-mode","fallback"],cwd=ROOT,check=True)
    def test_run_and_split(self):
        m=json.loads((ROOT/"reports/metrics.json").read_text()); self.assertEqual(len(m["conditions"]),6)
        self.assertEqual(m["leakage"]["train_test_id_overlap"],0); self.assertEqual(m["leakage"]["train_test_text_overlap"],0)
        self.assertGreaterEqual(m["test_cases"],20)
    def test_checker(self):
        checker=(ROOT/"course/check.py").read_text(); self.assertIn("at least 300 cases",checker)
        from course.check import checks
        m=json.loads((ROOT/"reports/metrics.json").read_text())
        self.assertFalse(checks(m)[7][1],"offline fallback must not pass real-LoRA check")
        m["adapter"].update({"executed":"transformers_peft_lora","is_transformer_lora":True})
        m["real_lora_complete"]=True
        self.assertTrue(checks(m)[7][1],"the checker must accept the real path it asks learners to run")

    def test_mocked_real_lora_is_accepted(self):
        class FakePEFT:
            def __init__(self, labels, quantized=False):
                self.labels=list(labels); self.quantized=quantized; self.model_name="local/tiny"; self.train_seconds=.25
            def fit(self, rows): return self
            def predict(self, text): return self.labels[0]
        rows=[{"label":"a","text":"one"},{"label":"b","text":"two"}]
        with patch.object(lora_adapter,"peft_available",return_value=True), patch.object(lora_adapter,"PEFTAdapter",FakePEFT):
            _,meta=lora_adapter.train_adapter(rows,["a","b"],mode="peft")
        self.assertEqual(meta["executed"],"transformers_peft_lora")
        self.assertTrue(meta["is_transformer_lora"])
