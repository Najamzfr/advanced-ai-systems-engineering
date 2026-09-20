import json, pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ReleaseTests(unittest.TestCase):
    def setUp(self):
        subprocess.run([sys.executable,'project.py','--allow-sample'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    def test_smoke_has_raw_evidence(self):
        m=json.loads((ROOT/'reports/metrics.json').read_text()); rows=(ROOT/'reports/results.jsonl').read_text().splitlines()
        self.assertEqual(m['cases'],len(rows)); self.assertEqual(m['observability']['trace_count'],m['cases'])
        self.assertEqual(m['execution']['mode'],'smoke_fixture')
        self.assertTrue(all(json.loads(x)['execution_mode']=='smoke_fixture' for x in rows))
    def test_all_failure_boundaries_are_measured(self):
        m=json.loads((ROOT/'reports/metrics.json').read_text()); self.assertEqual(set(m['failure_matrix']),{'model_unavailable','retrieval_down','tool_timeout','database_timeout','approval_timeout'})
    def test_http_contract(self):
        import serve
        self.assertTrue(hasattr(serve.Handler,'do_GET')); self.assertTrue(hasattr(serve.Handler,'do_POST'))
    def test_live_release_requires_a_course_work_root(self):
        import project
        with self.assertRaises(project.LiveRuntimeError):
            project.run([{'case_id':'x','question':'x'}],smoke=False)
if __name__=='__main__': unittest.main()
