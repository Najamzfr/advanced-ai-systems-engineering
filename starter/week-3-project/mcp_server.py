"""Small MCP-compatible JSON-RPC tool server used by the learner runtime.

The protocol is line-delimited JSON-RPC 2.0. It deliberately keeps the tool
surface narrow: search, fetch, and an idempotent store operation.
"""
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = [
    {"name":"search_documents","description":"Find weather records by location or question","inputSchema":{"type":"object","required":["query"],"properties":{"query":{"type":"string","minLength":2}}}},
    {"name":"fetch_document","description":"Fetch one weather record by evidence id","inputSchema":{"type":"object","required":["id"],"properties":{"id":{"type":"string","minLength":3}}}},
    {"name":"store_result","description":"Persist one result exactly once","inputSchema":{"type":"object","required":["action_id","case_id","value"],"properties":{"action_id":{"type":"string"},"case_id":{"type":"string"},"value":{"type":"object"},"simulate_transient_failure":{"type":"boolean"}}}},
]

def rows():
    p = ROOT / "data/eval.jsonl"
    if not p.exists(): p = ROOT / "data/sample.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

class Server:
    def __init__(self): self.records = {r["evidence_id"]: r for r in rows()}; self.writes = {}; self.failed_once = set()
    def call(self, name, args):
        if name == "search_documents":
            q = args.get("query")
            if not isinstance(q, str) or len(q.strip()) < 2: raise ValueError("query must be a non-empty string")
            terms = set(q.lower().split()); found=[]
            for r in self.records.values():
                text=(r.get("question","")+" "+r.get("location","")).lower()
                score=sum(t in text for t in terms)
                if score: found.append((score, r))
            return {"records":[r for _,r in sorted(found,key=lambda x:(x[0],x[1]["evidence_id"]),reverse=True)[:5]]}
        if name == "fetch_document":
            ident=args.get("id")
            if not isinstance(ident,str) or ident not in self.records: raise KeyError("unknown evidence id")
            return {"record":self.records[ident]}
        if name == "store_result":
            action=args.get("action_id"); cid=args.get("case_id"); value=args.get("value")
            if not all(isinstance(x,str) and x for x in (action,cid)) or not isinstance(value,dict): raise ValueError("invalid store arguments")
            # This is an explicit teaching switch, never a hidden random fault.
            # The client must retry the exact same idempotency key.
            if args.get("simulate_transient_failure") and action not in self.failed_once:
                self.failed_once.add(action); raise RuntimeError("simulated transient store failure")
            if action in self.writes: return {"stored":False,"duplicate":True,"action_id":action,"value":self.writes[action]}
            self.writes[action]=value; return {"stored":True,"duplicate":False,"action_id":action,"value":value}
        raise LookupError("unknown tool")

def reply(req, result=None, error=None):
    out={"jsonrpc":"2.0","id":req.get("id")}; out["result"]=result if error is None else None
    if error is not None: out["error"]=error
    print(json.dumps(out),flush=True)

def main():
    s=Server()
    for line in sys.stdin:
        try:
            req=json.loads(line); method=req.get("method")
            if method == "initialize": reply(req,{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"week3-bounded-agent","version":"1.0"}})
            elif method == "tools/list": reply(req,{"tools":TOOLS})
            elif method == "tools/call":
                p=req.get("params",{}); reply(req,{"content":[{"type":"text","text":json.dumps(s.call(p.get("name"),p.get("arguments",{})))}]})
            else: reply(req,error={"code":-32601,"message":"method not found"})
        except Exception as exc: reply(req if "req" in locals() else {"id":None},error={"code":-32000,"message":str(exc)})
if __name__ == "__main__": main()
