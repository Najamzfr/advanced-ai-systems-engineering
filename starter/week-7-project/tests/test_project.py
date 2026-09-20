import json, tempfile, unittest
from pathlib import Path
import project
from telemetry import Telemetry

class WorkflowTests(unittest.TestCase):
 def test_retry_and_idempotency_are_journaled(self):
  with tempfile.TemporaryDirectory() as d:
   t=Telemetry(d,endpoint='http://127.0.0.1:1'); result=project.DurableWorkflow(t,approve=True).execute({'case_id':'test-1','question':'x','failure_mode':'tool_timeout','approval_required':False},0)
   self.assertEqual(result['status'],'COMPLETED'); self.assertEqual(result['retry_count'],1); self.assertTrue(any(e['event']=='retry_scheduled' for e in result['journal'])); self.assertEqual(len(result['completed_actions']),5)
 def test_approval_pauses(self):
  with tempfile.TemporaryDirectory() as d:
   t=Telemetry(d,endpoint='http://127.0.0.1:1'); result=project.DurableWorkflow(t,approve=False).execute({'case_id':'test-2','question':'x','failure_mode':'approval_required','approval_required':True},0)
   self.assertEqual(result['status'],'WAITING_APPROVAL'); self.assertEqual(result['approval_state'],'pending')
 def test_trace_contains_pipeline_spans(self):
  with tempfile.TemporaryDirectory() as d:
   t=Telemetry(d,endpoint='http://127.0.0.1:1'); result=project.DurableWorkflow(t,approve=True).execute({'case_id':'test-3','question':'x','failure_mode':'success','approval_required':False},0)
   self.assertGreaterEqual(result['span_count'],6); self.assertTrue(Path(d,'telemetry.ndjson').exists())
 def test_imported_week4_runs_live_runtime(self):
  week4=Path(__file__).resolve().parents[2]/'week4-production'
  with tempfile.TemporaryDirectory() as d:
   t=Telemetry(d,endpoint='http://127.0.0.1:1')
   row={'case_id':'imported-live','request_id':'imported-live','question':'How do I create a Python virtual environment?','failure_mode':'tool_timeout','approval_required':False,'source_runtime_mode':'imported_week4_planner_executor','source_id':'w4-001','source_artifact':'reports/results.jsonl','week4_runtime_root':str(week4),'week4_runtime_entrypoint':'agent_runtime.py:execute_request'}
   result=project.DurableWorkflow(t,approve=True,week4_root=week4).execute(row,0)
   self.assertTrue(result['source']['live_execution'])
   self.assertTrue(result['source']['live_runtime']['runtime']['live_execution'])
   self.assertTrue({'planner.execute','executor.execute','verifier.check'}.issubset({s['name'] for s in result['spans']}))
