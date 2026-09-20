import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
class Week3Contract(unittest.TestCase):
 def test_mcp_lists_typed_tools(self):
  p=subprocess.Popen([sys.executable,'mcp_server.py'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True); p.stdin.write(json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/list'})+'\n'); p.stdin.flush(); out=json.loads(p.stdout.readline()); p.terminate(); p.wait(timeout=2); p.stdin.close(); p.stdout.close(); names={x['name'] for x in out['result']['tools']}; self.assertEqual(names,{'search_documents','fetch_document','store_result'})
 def test_smoke_run_is_server_backed(self):
  subprocess.run([sys.executable,'project.py','--allow-sample'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL); rows=[json.loads(x) for x in (ROOT/'reports/results.jsonl').read_text().splitlines()]; self.assertEqual(len(rows),3); self.assertTrue(all(len(x['trajectory'])==4 and x['server_round_trip'] for x in rows)); self.assertTrue(all(set(x['discovered_tools'])=={'search_documents','fetch_document','store_result'} for x in rows))
 def test_explicit_failure_is_retried_without_duplicate_effect(self):
  subprocess.run([sys.executable,'project.py','--allow-sample','--inject-one-failure'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  metrics=json.loads((ROOT/'reports/metrics.json').read_text())
  self.assertEqual(metrics['failure_injection']['injected_cases'],1)
  self.assertGreater(metrics['required_metrics']['retry rate'],0)
  self.assertEqual(metrics['required_metrics']['duplicate-effect rate'],0)
 def test_manifest_provenance(self):
  m=json.loads((ROOT/'data/manifest.json').read_text()); self.assertIn(m['status'],('smoke_fixture_only','real_data')); self.assertIn('minimum_cases_for_grade',m)
