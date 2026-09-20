import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Week4Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls): subprocess.run([sys.executable,'scripts/fetch_data.py','--cases','24'],cwd=ROOT,check=True); subprocess.run([sys.executable,'project.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 def test_unique_cases_and_real_manifest(self):
  m=json.loads((ROOT/'data/manifest.json').read_text()); self.assertEqual(m['status'],'real_data'); rs=(ROOT/'reports/results.jsonl').read_text().splitlines(); self.assertEqual(len(rs),24); self.assertEqual(len({json.loads(x)['case_id'] for x in rs}),24)
 def test_plans_have_dependencies_and_verification(self):
  for line in (ROOT/'reports/results.jsonl').read_text().splitlines():
   r=json.loads(line)['architectures']['planner_executor']; self.assertIn('verified',r['verification']); self.assertTrue(all('depends_on' in n for n in r['plan']['nodes']))
 def test_equal_budget_comparison_present(self):
  r=json.loads((ROOT/'reports/results.jsonl').read_text().splitlines()[0]); self.assertEqual(set(r['architectures']),{'single_agent','planner_executor','specialist_decomposition'})
 def test_callable_live_runtime(self):
  sys.path.insert(0,str(ROOT)); import agent_runtime
  result=agent_runtime.execute_request('How do Python virtual environments work?','live-runtime-test',failure_mode='tool_timeout')
  self.assertTrue(result['runtime']['live_execution']); self.assertEqual(result['request_id'],'live-runtime-test'); self.assertTrue(result['execution']['recovered'])
