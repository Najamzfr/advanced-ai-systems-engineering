"""Deterministic teaching fixtures, Python 3.10+, standard library only.
These checks exercise engineering invariants, not live model quality.
"""
import argparse, json, math, sqlite3
from pathlib import Path


def retrieval_metrics(ranked, relevant, k):
    unique = list(dict.fromkeys(ranked))
    rel = set(relevant)
    hits = sum(x in rel for x in unique[:k])
    rr = next((1 / (i + 1) for i, x in enumerate(unique) if x in rel), 0.0)
    dcg = sum((1 if x in rel else 0) / math.log2(i + 2) for i, x in enumerate(unique[:k]))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(rel), k)))
    return {"recall": hits / len(rel) if rel else None, "reciprocal_rank": rr if rel else None,
            "ndcg": dcg / ideal if ideal else None, "k": k}


def dispatch_fixture():
    db = sqlite3.connect(":memory:")
    db.executescript("CREATE TABLE outbox (effect_key TEXT PRIMARY KEY, status TEXT); CREATE TABLE sink (effect_key TEXT PRIMARY KEY);")
    db.execute("INSERT INTO outbox VALUES (?,?)", ("event-7:draft-2", "pending"))
    db.commit()
    # First delivery: sink effect commits, then worker acknowledgement is lost.
    db.execute("INSERT INTO sink VALUES (?)", ("event-7:draft-2",))
    db.commit()
    # Restart: status lookup reconciles the same logical effect.
    exists = db.execute("SELECT 1 FROM sink WHERE effect_key=?", ("event-7:draft-2",)).fetchone()
    if exists:
        db.execute("UPDATE outbox SET status='delivered' WHERE effect_key=?", ("event-7:draft-2",))
        db.commit()
    result = {"logical_dispatches": db.execute("SELECT count(*) FROM sink").fetchone()[0],
              "outbox_status": db.execute("SELECT status FROM outbox").fetchone()[0], "mode": "deterministic_fixture"}
    db.close()
    return result


def contract_fixture():
    allowed = {"P1", "P2"}
    def validate(args):
        if set(args) != {"source_id", "section_id"}: return "SCHEMA_ERROR"
        if not all(isinstance(v, str) for v in args.values()): return "SCHEMA_ERROR"
        if args["source_id"] not in allowed: return "DENIED_SCOPE"
        if args["section_id"] not in {"abstract", "methods"}: return "NOT_FOUND"
        return "OK"
    return [validate(x) for x in [{"source_id":"P1","section_id":"methods"},
             {"source_id":"P9","section_id":"methods"},{"source_id":"P1","section_id":5}]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("activity", choices=["retrieval", "contracts", "kv", "durable", "all"])
    p.add_argument("--out", default="results")
    a = p.parse_args()
    results = {
        "retrieval": retrieval_metrics(["B", "A", "D", "C"], ["A", "C"], 2),
        "contracts": contract_fixture(),
        "kv": {"bytes_per_sequence": 2*32*8*128*2*4096, "MiB_per_sequence": 512},
        "durable": dispatch_fixture()
    }
    assert results["retrieval"]["recall"] == 0.5
    assert results["retrieval"]["reciprocal_rank"] == 0.5
    assert results["contracts"] == ["OK", "DENIED_SCOPE", "SCHEMA_ERROR"]
    assert results["durable"]["logical_dispatches"] == 1
    selected = results if a.activity == "all" else {a.activity: results[a.activity]}
    output = {"run_mode":"deterministic_fixture", "results": selected}
    target = Path(a.out); target.mkdir(parents=True, exist_ok=True)
    (target / (a.activity + ".json")).write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))

if __name__ == "__main__": main()
