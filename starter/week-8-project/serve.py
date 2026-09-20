"""Minimal production-shaped HTTP adapter with health/readiness probes."""
import json, os, pathlib, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from project import load_rows, run

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, body):
        data=json.dumps(body).encode(); self.send_response(code); self.send_header('content-type','application/json'); self.send_header('content-length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path=='/healthz': return self.send_json(200,{'status':'ok','version':os.getenv('RELEASE_VERSION','week8-local')})
        if self.path=='/readyz':
            try: load_rows(); return self.send_json(200,{'status':'ready','checks':{'dataset':True,'runtime':True}})
            except Exception as e: return self.send_json(503,{'status':'not_ready','error':str(e)})
        self.send_json(404,{'error':'not_found'})
    def do_POST(self):
        if self.path!='/v1/ask': return self.send_json(404,{'error':'not_found'})
        try:
            length=int(self.headers.get('content-length','0')); payload=json.loads(self.rfile.read(length) or '{}'); question=str(payload.get('question','')).strip()
            if not question: return self.send_json(400,{'error':'question_required'})
            row={'case_id':'api-request','question':question,'expected':'ready','risk':'low'}
            course_root=os.getenv('COURSE_WORK_ROOT')
            # A mounted course-work directory turns the API into the same live
            # composition used by `make evaluate`; otherwise it advertises a
            # non-promotable smoke response rather than pretending to deploy.
            raw,metrics=run([row], pathlib.Path(course_root) if course_root else None, smoke=not bool(course_root)); x=raw[0]
            event={'ts':time.time(),'trace_id':x['trace_id'],'question':question,'answer':x['observed'],'policy':x['policy'],'failure':x['failure'],'latency_ms':x['latency_ms'],'cost_usd':x['cost_usd']}
            report_dir=pathlib.Path(__file__).resolve().parent/'reports'; report_dir.mkdir(exist_ok=True)
            with (report_dir/'api-telemetry.ndjson').open('a') as stream: stream.write(json.dumps(event)+'\n')
            return self.send_json(200,{'answer':x['observed'],'policy':x['policy'],'trace_id':x['trace_id'],'latency_ms':x['latency_ms'],'cost_usd':x['cost_usd'],'execution_mode':metrics['execution']['mode']})
        except Exception as e: return self.send_json(500,{'error':'request_failed','detail':str(e)})
    def log_message(self,*args): pass

if __name__=='__main__': HTTPServer(('0.0.0.0',int(os.getenv('PORT','8080'))),Handler).serve_forever()
