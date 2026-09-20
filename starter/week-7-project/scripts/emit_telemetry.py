"""Emit one independent OTLP smoke request for a running local stack."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from telemetry import Telemetry, _id

t=Telemetry(); trace=_id(32); parent=t.span('smoke.request',trace,attrs={'run_id':'smoke','operation':'demo'})
t.span('smoke.retrieval',trace,parent,attrs={'documents':3})
t.span('smoke.model',trace,parent,attrs={'tokens':42,'cost_usd':0.0003})
t.log(trace,'Week 7 telemetry smoke request emitted',attrs={'run_id':'smoke'})
t.metric('genai_requests_total',1,{'operation':'demo'}); t.metric('genai_tokens_total',42,{'operation':'demo'}); t.metric('genai_cost_usd_total',0.0003,{'operation':'demo'})
print('emitted trace_id='+trace+'; local copy: reports/telemetry.ndjson')
