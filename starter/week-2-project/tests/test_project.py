import json, unittest
from pathlib import Path
class StarterContract(unittest.TestCase):
    def test_smoke_fixture_has_three_cases(self):
        rows=[json.loads(x) for x in (Path(__file__).parents[1]/'data/sample.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows),3)
    def test_manifest_is_explicitly_smoke(self):
        m=json.loads((Path(__file__).parents[1]/'data/manifest.json').read_text())
        self.assertEqual(m['status'],'smoke_fixture_only')
if __name__=='__main__': unittest.main()
