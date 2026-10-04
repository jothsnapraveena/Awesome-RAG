import math
import unittest

from rag_lab.core import LexicalIndex, assemble_context, chunk_document, retrieval_metrics
from rag_lab.evaluation import paired_bootstrap


class RetrievalTests(unittest.TestCase):
    def test_chunk_source_coverage_and_offsets(self):
        doc = {"id": "source", "title": "Title", "text": "alpha\n\nbeta  gamma\tdelta epsilon"}
        chunks = chunk_document(doc, size=3, overlap=1)
        self.assertEqual([c["text"] for c in chunks], ["alpha\n\nbeta  gamma", "gamma\tdelta epsilon"])
        for chunk in chunks:
            self.assertEqual(chunk["text"], doc["text"][chunk["start_char"]:chunk["end_char"]])
        self.assertEqual(chunk_document({**doc, "text": ""}), [])
        with self.assertRaises(ValueError):
            chunk_document(doc, size=3, overlap=3)

    def test_bm25_against_hand_calculation(self):
        records = [{"id": "a", "text": "alpha alpha beta"}, {"id": "b", "text": "beta"}]
        index = LexicalIndex(records, method="bm25")
        expected = math.log(2) * (2 * 2.2) / (2 + 1.2 * (.25 + .75 * 3 / 2))
        self.assertAlmostEqual(index.search("alpha")[0]["score"], expected)
        self.assertEqual(index.search("alpha alpha"), index.search("alpha"))

    def test_tfidf_cosine_and_unknown_terms(self):
        index = LexicalIndex([{"id": "a", "text": "alpha beta"}, {"id": "b", "text": "gamma"}], "tfidf")
        self.assertAlmostEqual(index.search("alpha")[0]["score"], 1 / math.sqrt(2))
        self.assertAlmostEqual(index.search("alpha beta")[0]["score"], 1.0)
        self.assertEqual(index.search("unknown"), [])
        self.assertEqual(index.search(""), [])

    def test_collapse_happens_before_top_k(self):
        records = [{"id": "a1", "document_id": "a", "text": "alpha"},
                   {"id": "a2", "document_id": "a", "text": "alpha"},
                   {"id": "b1", "document_id": "b", "text": "alpha beta"}]
        hits = LexicalIndex(records).search("alpha", k=2, collapse_documents=True)
        self.assertEqual([hit["document_id"] for hit in hits], ["a", "b"])

    def test_metrics_multiple_relevant_and_graded_ndcg(self):
        result = retrieval_metrics(["x", "a"], {"a": 2, "b": 1}, 2)
        self.assertEqual(result["recall@2"], .5)
        self.assertEqual(result["mrr@2"], .5)
        self.assertAlmostEqual(result["ndcg@2"], (3 / math.log2(3)) / (3 + 1 / math.log2(3)))
        self.assertEqual(retrieval_metrics([], {"a": 1}, 10)["ndcg@10"], 0)
        with self.assertRaises(ValueError):
            retrieval_metrics(["a", "a"], {"a": 1}, 2)

    def test_context_budget_keeps_sources_aligned(self):
        hits = [{"id": "a", "title": "A", "text": "long " * 30},
                {"id": "b", "title": "B", "text": "brief"}]
        context, sources, skipped = assemble_context(hits, 20)
        self.assertLessEqual(len(context), 20)
        self.assertEqual(sources, ["b"])
        self.assertEqual(skipped, ["a"])
        self.assertIn("[b]", context)

    def test_paired_bootstrap_identical_results(self):
        result = {"per_query": [{"query_id": "a", "metrics": {"ndcg@10": .5}}]}
        interval = paired_bootstrap(result, result, samples=20)
        self.assertEqual(interval["percentile_95_interval"], [0, 0])


if __name__ == "__main__":
    unittest.main()
