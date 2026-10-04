"""Evaluation utilities shared by notebooks and the benchmark command."""
import math
import random
from statistics import mean, median
from time import perf_counter

from rag_lab.core import retrieval_metrics


def evaluate(index, queries, judgments, ks=(1, 5, 10)):
    if not judgments or not ks or min(ks) < 1:
        raise ValueError("Require judgments and positive cutoffs")
    rows = []
    for qid in sorted(judgments):
        start = perf_counter()
        hits = index.search(queries[qid]["text"], max(ks), collapse_documents=True)
        elapsed = (perf_counter() - start) * 1000
        ranked = [hit["document_id"] for hit in hits]
        metrics = {}
        for k in ks:
            metrics.update(retrieval_metrics(ranked, judgments[qid], k))
        rows.append({"query_id": qid, "metrics": metrics, "latency_ms": elapsed,
                     "hits": [{"document_id": hit["document_id"], "passage_id": hit["id"],
                               "score": hit["score"]} for hit in hits]})
    summary = {key: mean(row["metrics"][key] for row in rows) for key in rows[0]["metrics"]}
    latencies = sorted(row["latency_ms"] for row in rows)
    summary.update({"queries": len(rows), "median_latency_ms": median(latencies),
                    "p95_latency_ms": latencies[max(0, math.ceil(.95 * len(rows)) - 1)]})
    return {"summary": summary, "per_query": rows}


def paired_bootstrap(first, second, metric="ndcg@10", samples=1000, seed=42):
    """Percentile interval for mean(second - first) over resampled query IDs."""
    if samples < 1:
        raise ValueError("samples must be positive")
    a = {row["query_id"]: row["metrics"][metric] for row in first["per_query"]}
    b = {row["query_id"]: row["metrics"][metric] for row in second["per_query"]}
    if not a or a.keys() != b.keys():
        raise ValueError("Paired evaluation requires matching nonempty query sets")
    differences = [b[qid] - a[qid] for qid in sorted(a)]
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(differences, k=len(differences))) for _ in range(samples))
    return {"metric": metric, "mean_difference": mean(differences),
            "percentile_95_interval": [means[int(.025 * (samples - 1))], means[int(.975 * (samples - 1))]],
            "samples": samples, "seed": seed}
