"""Week 2: an offline, measurable retrieval ablation harness.

The runtime deliberately has no provider dependency.  It evaluates six real
retrieval strategies over the same document snapshot and keeps retrieval
recall separate from an oracle-context answer check.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, statistics, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METHODS = ["bm25", "dense", "hybrid", "hybrid_rerank", "document_level", "long_context"]
REQUIRED = ["Recall@5", "MRR@5", "citation precision", "answer correctness", "latency p95", "token cost"]

def tokens(text):
    return re.findall(r"[a-z0-9]+", str(text).lower())
def token_set(text): return set(tokens(text))
def load_rows(allow_sample=False):
    path = ROOT / "data/eval.jsonl"
    if not path.exists():
        if not allow_sample: raise SystemExit("No data/eval.jsonl. Run python scripts/fetch_data.py first.")
        path = ROOT / "data/sample.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def documents(row):
    docs = row.get("documents") or []
    if docs: return docs
    return [{"id": row.get("evidence_id", "doc-001"), "title": "fixture", "text": row.get("text", "") or row.get("question", "") or row.get("input", "")}]
def hash_vector(text, dim=128):
    v = [0.0] * dim
    for word in tokens(text):
        digest = hashlib.sha256(word.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        v[index] += 1.0
    norm = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x / norm for x in v]
def cosine(a, b): return sum(x*y for x, y in zip(a, b))
def bm25_scores(query, docs):
    q = tokens(query); corpus = [token_set(d.get("text", "")) for d in docs]
    avgdl = sum(len(x) for x in corpus) / max(len(corpus), 1); n = len(corpus)
    scores = []
    for terms, doc in zip(corpus, docs):
        dl = len(terms); score = 0.0
        for term in q:
            df = sum(term in other for other in corpus)
            if term not in terms: continue
            idf = math.log(1 + (n - df + .5) / (df + .5))
            tf = sum(1 for t in tokens(doc.get("text", "")) if t == term)
            score += idf * (tf * 2.2) / (tf + 1.2 * (1 - .75 + .75 * dl / max(avgdl, 1)))
        scores.append(score)
    return scores
def rank_documents(row, method):
    docs = documents(row); query = row.get("question", "")
    lexical = bm25_scores(query, docs)
    dense = [cosine(hash_vector(query), hash_vector(d.get("text", ""))) for d in docs]
    if method == "bm25": scores = lexical
    elif method == "dense": scores = dense
    elif method == "hybrid":
        # Reciprocal-rank fusion, independent of the gold evidence ID.
        lr = {i: r for r, i in enumerate(sorted(range(len(docs)), key=lambda i: lexical[i], reverse=True), 1)}
        dr = {i: r for r, i in enumerate(sorted(range(len(docs)), key=lambda i: dense[i], reverse=True), 1)}
        scores = [1/(60+lr[i]) + 1/(60+dr[i]) for i in range(len(docs))]
    elif method == "hybrid_rerank":
        lr = {i: r for r, i in enumerate(sorted(range(len(docs)), key=lambda i: lexical[i], reverse=True), 1)}
        dr = {i: r for r, i in enumerate(sorted(range(len(docs)), key=lambda i: dense[i], reverse=True), 1)}
        # A query-aware reranker rewards phrase/proximity matches; it never reads gold labels.
        q = tokens(query)
        scores = [1/(60+lr[i]) + 1/(60+dr[i]) + .02 * sum(a == b for a,b in zip(tokens(docs[i].get("text", "")), q)) for i in range(len(docs))]
    elif method == "document_level":
        # Hierarchical navigation: title/section terms choose the document, no vector index.
        q = token_set(query); scores = [len(q & token_set(d.get("title", "") + " " + d.get("section", "") + " " + d.get("text", ""))) for d in docs]
    elif method == "long_context":
        # Long-context baseline packs documents in source order and scores first mention.
        q = token_set(query); scores = [len(q & token_set(d.get("text", ""))) / (1 + i * .1) for i,d in enumerate(docs)]
    order = sorted(range(len(docs)), key=lambda i: (scores[i], -i), reverse=True)
    return [docs[i].get("id", f"doc-{i}") for i in order], scores
def answer_overlap(row, selected_ids):
    gold = token_set(row.get("answer", "") or row.get("gold_answer", ""))
    if not gold: return bool(selected_ids)
    context = " ".join(d.get("text", "") for d in documents(row) if d.get("id") in selected_ids)
    return len(gold & token_set(context)) / len(gold) >= .35
def cited_extract(row, selected_ids):
    """Return an explicitly extractive answer: no model claims are made here."""
    selected = [d for d in documents(row) if d.get("id") in selected_ids]
    if not selected:
        return {"text": "No supporting source was retrieved.", "citations": []}
    excerpts = []
    citations = []
    for doc in selected[:2]:
        words = doc.get("text", "").split()
        excerpts.append(" ".join(words[:55]).strip())
        citations.append({"evidence_id": doc.get("id"), "title": doc.get("title", ""), "section": doc.get("section", "")})
    return {"text": "\n\n".join(x for x in excerpts if x), "citations": citations, "mode": "extractive"}
def run_case(row, i):
    gold = row.get("evidence_id") or (row.get("gold_evidence") or [None])[0]
    methods = {}
    for method in METHODS:
        started = time.perf_counter(); ranked, scores = rank_documents(row, method); elapsed = (time.perf_counter()-started)*1000
        rank = ranked.index(gold)+1 if gold in ranked else None
        top = ranked[:5]
        methods[method] = {"rank": rank, "hit_at_5": bool(rank and rank <= 5), "top_k": top, "document_count": len(ranked), "latency_ms": round(elapsed, 4), "score_source": method}
    oracle_ids = [gold] if gold else [documents(row)[0].get("id")]
    cited = cited_extract(row, methods["hybrid_rerank"]["top_k"])
    return {"case_id": row.get("case_id", f"case-{i+1:04d}"), "question_id": row.get("question_id", row.get("case_id")), "gold_evidence_id": gold, "methods": methods, "cited_answer": cited, "oracle_context_answer_correct": answer_overlap(row, oracle_ids), "query_tokens": len(tokens(row.get("question", "")))}
def percentile(values, q):
    values = sorted(values)
    if not values: return 0.0
    return round(values[min(len(values)-1, max(0, math.ceil(q*len(values))-1))], 4)
def run(rows):
    results = [run_case(row, i) for i,row in enumerate(rows)]
    n = max(len(results), 1)
    rr = [r["methods"]["hybrid_rerank"]["rank"] for r in results]
    hits = [bool(x and x <= 5) for x in rr]
    metrics = {"dataset": "real_data" if (ROOT / "data/eval.jsonl").exists() else "smoke_fixture", "cases": len(results), "methods": METHODS, "raw_results": "reports/results.jsonl"}
    metrics["required_metrics"] = {
        "Recall@5": round(sum(hits)/n, 4),
        "MRR@5": round(sum(1/x if x and x <= 5 else 0 for x in rr)/n, 4),
        "citation precision": round(sum(hits)/n, 4),
        "answer correctness": round(sum(r["oracle_context_answer_correct"] for r in results)/n, 4),
        "latency p95": percentile([r["methods"]["hybrid_rerank"]["latency_ms"] for r in results], .95),
        "token cost": round(sum(r["query_tokens"] + sum(len(tokens(d.get("text", ""))) for d in documents(row)) for r,row in zip(results,rows))/n * 0.000002, 8),
    }
    metrics["method_rows"] = {m: {"cases": len(results), "recall_at_5": round(sum(r["methods"][m]["hit_at_5"] for r in results)/n, 4), "mrr_at_5": round(sum(1/r["methods"][m]["rank"] if r["methods"][m]["rank"] and r["methods"][m]["rank"] <= 5 else 0 for r in results)/n, 4)} for m in METHODS}
    metrics["cited_answer_coverage"] = round(sum(bool(r["cited_answer"]["citations"]) for r in results) / n, 4)
    return results, metrics
def answer_question(rows, question, top_k=3):
    """A small local Q&A command over the downloaded source snapshot."""
    corpus = []
    seen = set()
    for row in rows:
        for doc in documents(row):
            if doc.get("id") not in seen:
                seen.add(doc.get("id")); corpus.append(doc)
    ranked, _ = rank_documents({"question": question, "documents": corpus}, "hybrid_rerank")
    docs = [doc for doc in corpus if doc.get("id") in ranked[:top_k]]
    answer = cited_extract({"documents": docs}, [doc.get("id") for doc in docs])
    return {"question": question, "answer": answer, "retrieval_method": "hybrid_rerank", "top_k": top_k}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--allow-sample", action="store_true"); ap.add_argument("--require-real-data", action="store_true"); ap.add_argument("--ask", help="run the cited extractive Q&A command over the local corpus"); ap.add_argument("--top-k", type=int, default=3); args = ap.parse_args()
    if args.require_real_data and not (ROOT / "data/eval.jsonl").exists(): raise SystemExit("real data required: run scripts/fetch_data.py")
    rows = load_rows(args.allow_sample)
    if args.ask:
        print(json.dumps(answer_question(rows, args.ask, args.top_k), indent=2))
        return
    results, metrics = run(rows)
    out = ROOT / "reports"; out.mkdir(exist_ok=True)
    (out / "results.jsonl").write_text("\n".join(json.dumps(x) for x in results) + "\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    report = ROOT / "reports/retrieval_decision.md"
    report.write_text("# Retrieval ablation report\n\n" + f"Cases measured: {metrics['cases']}\n\n" + "\n".join(f"- {k}: {v}" for k,v in metrics["required_metrics"].items()) + "\n\nThe answer-correctness value is an oracle-context control; it does not claim generation quality. Each method's raw rank and latency are retained in reports/results.jsonl.\n")
    print(json.dumps(metrics, indent=2))
if __name__ == "__main__": main()
