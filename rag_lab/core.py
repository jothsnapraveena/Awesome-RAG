"""Shared corpus handling and retrieval; deliberately simple and readable."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re

ARCHIVE_SHA256 = "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165"


def load_dataset(root):
    folder = Path(root) / "data/scifact"
    if not (folder / "manifest.json").is_file():
        raise FileNotFoundError("Run python scripts/prepare_data.py from the repository root first.")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest["archive_sha256"] != ARCHIVE_SHA256:
        raise ValueError("Unexpected dataset snapshot")
    for relative, expected in manifest["files"].items():
        if hashlib.sha256((folder / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Dataset file changed: {relative}; rerun prepare_data.py")

    def read_records(name):
        records = {}
        with (folder / name).open(encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                key = record.pop("_id")
                if key in records or not record["text"].strip():
                    raise ValueError(f"Duplicate ID or empty text in {name}: {key}")
                records[key] = {"id": key, **record}
        return records

    corpus, queries = read_records("corpus.jsonl"), read_records("queries.jsonl")
    qrels = {}
    for split in ("train", "test"):
        judgments = defaultdict(dict)
        with (folder / f"qrels/{split}.tsv").open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                qid, did, score = row["query-id"], row["corpus-id"], int(row["score"])
                if qid not in queries or did not in corpus or score <= 0:
                    raise ValueError("Invalid relevance judgment")
                if did in judgments[qid]:
                    raise ValueError("Duplicate relevance judgment")
                judgments[qid][did] = score
        qrels[split] = dict(judgments)
    if set(qrels["train"]) & set(qrels["test"]):
        raise ValueError("Query IDs overlap across splits")
    if (len(corpus), len(queries), len(qrels["train"]), len(qrels["test"])) != (5183, 1109, 809, 300):
        raise ValueError("Unexpected dataset counts")
    return corpus, queries, qrels, manifest


def chunk_document(document, size=120, overlap=30):
    """Word windows with exact character offsets into the original abstract."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    spans = list(re.finditer(r"\S+", document["text"]))
    chunks = []
    for start in range(0, len(spans), size - overlap):
        end = min(start + size, len(spans))
        begin_char, end_char = spans[start].start(), spans[end - 1].end()
        chunks.append({"id": f"{document['id']}:{begin_char}-{end_char}",
                       "document_id": document["id"], "title": document["title"],
                       "start_char": begin_char, "end_char": end_char,
                       "text": document["text"][begin_char:end_char]})
        if end == len(spans):
            break
    return chunks


def tokenize(text):
    # Keep negation and digits. No stemming or stopword removal in either baseline.
    return re.findall(r"[a-z0-9]+", text.lower())


class LexicalIndex:
    """Inverted postings for TF-IDF cosine or BM25, with deterministic ID tie breaks.

    TF-IDF uses raw term counts, smoothed IDF, and L2 normalization.
    BM25 uses log(1 + (N-df+0.5)/(df+0.5)), k1=1.2 and b=0.75.
    Titles and text are indexed once each. Query terms are unique in BM25.
    """

    def __init__(self, records, method="bm25", k1=1.2, b=0.75):
        if method not in {"tfidf", "bm25"} or k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("Invalid index configuration")
        self.records = {record["id"]: record for record in records}
        if len(self.records) != len(records) or not records:
            raise ValueError("Records must be nonempty with unique IDs")
        self.method, self.k1, self.b = method, k1, b
        counts = {key: Counter(tokenize(record.get("title", "") + " " + record["text"]))
                  for key, record in self.records.items()}
        lengths = {key: sum(count.values()) for key, count in counts.items()}
        average_length = sum(lengths.values()) / len(lengths)
        if average_length == 0:
            raise ValueError("Corpus has no searchable terms")
        df = Counter(term for count in counts.values() for term in count)
        n = len(counts)
        self.idf = {term: (math.log((1 + n) / (1 + frequency)) + 1 if method == "tfidf"
                          else math.log(1 + (n - frequency + 0.5) / (frequency + 0.5)))
                    for term, frequency in df.items()}
        self.postings = defaultdict(list)
        for key, count in counts.items():
            if method == "tfidf":
                weights = {term: tf * self.idf[term] for term, tf in count.items()}
                norm = math.sqrt(sum(value ** 2 for value in weights.values()))
                weights = {term: value / norm for term, value in weights.items()} if norm else {}
            else:
                weights = {term: self.idf[term] * tf * (k1 + 1) /
                           (tf + k1 * (1 - b + b * lengths[key] / average_length))
                           for term, tf in count.items()}
            for term, weight in weights.items():
                self.postings[term].append((key, weight))

    def search(self, query, k=10, collapse_documents=False):
        if k < 1:
            raise ValueError("k must be positive")
        counts = Counter(term for term in tokenize(query) if term in self.idf)
        if self.method == "tfidf":
            weights = {term: count * self.idf[term] for term, count in counts.items()}
            norm = math.sqrt(sum(value ** 2 for value in weights.values()))
            weights = {term: value / norm for term, value in weights.items()} if norm else {}
        else:
            weights = dict.fromkeys(counts, 1.0)
        scores = defaultdict(float)
        for term, weight in weights.items():
            for key, value in self.postings[term]:
                scores[key] += weight * value
        ranking = sorted(scores, key=lambda key: (-scores[key], key))
        hits, seen = [], set()
        for key in ranking:
            record = self.records[key]
            document_id = record.get("document_id", key)
            if collapse_documents and document_id in seen:
                continue
            seen.add(document_id)
            hits.append({**record, "score": scores[key], "document_id": document_id})
            if len(hits) == k:
                break
        return hits


def retrieval_metrics(ranked_ids, judgments, k):
    if k < 1 or not judgments or any(value < 0 for value in judgments.values()):
        raise ValueError("Require k > 0 and nonnegative judgments with a positive grade")
    if len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError("Collapse chunks to distinct document IDs before evaluation")
    relevant = {key for key, grade in judgments.items() if grade > 0}
    if not relevant:
        raise ValueError("No positive relevance judgments")
    ranked = ranked_ids[:k]
    recall = len(set(ranked) & relevant) / len(relevant)
    rr = next((1 / rank for rank, key in enumerate(ranked, 1) if key in relevant), 0.0)
    dcg = sum((2 ** judgments.get(key, 0) - 1) / math.log2(rank + 1)
              for rank, key in enumerate(ranked, 1))
    ideal = sum((2 ** grade - 1) / math.log2(rank + 1)
                for rank, grade in enumerate(sorted(judgments.values(), reverse=True)[:k], 1))
    return {f"recall@{k}": recall, f"mrr@{k}": rr, f"ndcg@{k}": dcg / ideal}


def assemble_context(hits, max_chars=6500):
    """Keep complete source passages; report those excluded by the character budget."""
    if max_chars < 0:
        raise ValueError("max_chars must be nonnegative")
    blocks, sources, skipped = [], [], []
    for hit in hits:
        block = f"[{hit['id']}] {hit['title']}\n{hit['text']}"
        if len("\n\n".join([*blocks, block])) <= max_chars:
            blocks.append(block)
            sources.append(hit["id"])
        else:
            skipped.append(hit["id"])
    return "\n\n".join(blocks), sources, skipped
