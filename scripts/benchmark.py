"""Run fixed lexical baselines on full SciFact; defaults to train for development."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag_lab.core import LexicalIndex, load_dataset
from rag_lab.evaluation import evaluate, paired_bootstrap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=["train", "test"], default="train")
    args = parser.parse_args()
    corpus, queries, qrels, manifest = load_dataset(ROOT)
    report = {"dataset": manifest, "split": args.split, "corpus_documents": len(corpus),
              "created_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
              "platform": platform.platform(), "configuration": {
                  "fields": ["title", "text"], "tokenizer": "lowercase ASCII alphanumeric",
                  "stopwords": False, "stemming": False, "bm25_k1": 1.2, "bm25_b": .75,
                  "cutoffs": [1, 5, 10], "candidate_corpus": "all 5183 documents",
                  "tfidf": "raw TF, smoothed IDF, L2 cosine", "tie_break": "lexicographic document ID"},
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [ROOT / "rag_lab/core.py", ROOT / "rag_lab/evaluation.py", Path(__file__)]},
              "systems": {}}
    for method in ("tfidf", "bm25"):
        start = perf_counter()
        index = LexicalIndex(list(corpus.values()), method=method)
        build_seconds = perf_counter() - start
        result = evaluate(index, queries, qrels[args.split])
        result["build_seconds"] = build_seconds
        result["vocabulary_size"] = len(index.idf)
        report["systems"][method] = result
        print(method, json.dumps(result["summary"], indent=2))
    report["bm25_minus_tfidf"] = paired_bootstrap(report["systems"]["tfidf"], report["systems"]["bm25"])
    output = ROOT / "reports" / f"scifact-{args.split}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
