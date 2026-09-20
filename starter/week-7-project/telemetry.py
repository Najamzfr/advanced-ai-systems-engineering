"""Small dependency-free OTLP/HTTP exporter used by the Week 7 runner."""
from __future__ import annotations
import json, os, time, urllib.request, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def _id(n=16): return uuid.uuid4().hex[:n]

def _attrs(values):
    out=[]
    for k,v in values.items():
        if isinstance(v,bool): value={"boolValue":v}
        elif isinstance(v,int): value={"intValue":str(v)}
        elif isinstance(v,float): value={"doubleValue":v}
        else: value={"stringValue":str(v)}
        out.append({"key":str(k),"value":value})
    return out

class Telemetry:
    def __init__(self, report_dir=None, endpoint=None):
        self.report_dir=Path(report_dir or ROOT/'reports'); self.report_dir.mkdir(parents=True,exist_ok=True)
        self.endpoint=(endpoint or os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT','http://localhost:4318')).rstrip('/')
        self.service=os.getenv('OTEL_SERVICE_NAME','week7-durable-agent'); self.local=self.report_dir/'telemetry.ndjson'
    def _record(self, kind, payload):
        with self.local.open('a',encoding='utf-8') as f: f.write(json.dumps({'kind':kind,**payload},sort_keys=True)+'\n')
    def _send(self, path, payload):
        try:
            req=urllib.request.Request(self.endpoint+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=0.35) as response: response.read()
            return True
        except Exception: return False
    def span(self, name, trace_id, parent_id=None, start_ns=None, end_ns=None, attrs=None, status='OK'):
        start_ns=start_ns or time.time_ns(); end_ns=end_ns or time.time_ns()
        span={'traceId':trace_id,'spanId':_id(),'parentSpanId':parent_id or '', 'name':name,'kind':1,'startTimeUnixNano':str(start_ns),'endTimeUnixNano':str(end_ns),'attributes':_attrs(attrs or {}),'status':{'code':1 if status=='OK' else 2,'message':status}}
        payload={'resourceSpans':[{'resource':{'attributes':_attrs({'service.name':self.service,'week':7})},'scopeSpans':[{'scope':{'name':'ase.week7'},'spans':[span]}]}]}
        self._record('span',{'trace_id':trace_id,'span_id':span['spanId'],'parent_span_id':parent_id,'name':name,'status':status,'attributes':attrs or {}}); self._send('/v1/traces',payload); return span['spanId']
    def log(self, trace_id, message, severity='INFO', attrs=None):
        now=str(time.time_ns()); values={'trace_id':trace_id,'severity':severity,'message':message,**(attrs or {})}; self._record('log',values)
        payload={'resourceLogs':[{'resource':{'attributes':_attrs({'service.name':self.service})},'scopeLogs':[{'scope':{'name':'ase.week7'},'logRecords':[{'timeUnixNano':now,'severityText':severity,'body':{'stringValue':message},'attributes':_attrs({'trace_id':trace_id,**(attrs or {})})}]}]}]}; self._send('/v1/logs',payload)
    def metric(self, name, value, attrs=None):
        values=attrs or {}; self._record('metric',{'name':name,'value':value,'attributes':values})
        metric={'name':name,'gauge':{'dataPoints':[{'asDouble':float(value),'timeUnixNano':str(time.time_ns()),'attributes':_attrs(values)}]}}
        payload={'resourceMetrics':[{'resource':{'attributes':_attrs({'service.name':self.service})},'scopeMetrics':[{'scope':{'name':'ase.week7'},'metrics':[metric]}]}]}; self._send('/v1/metrics',payload)

