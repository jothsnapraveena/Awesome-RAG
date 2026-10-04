# SciFact reference run

`scifact-test.json` records a run over all 300 BEIR test claims with all 5,183 abstracts as candidates. Configuration was fixed before this run: title plus abstract, lowercase alphanumeric tokenization, no stemming or stopword removal, TF-IDF cosine versus BM25 with k1=1.2 and b=0.75. These transparent implementations are educational baselines, not official BEIR leaderboard runs.

| Baseline | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| TF-IDF | 0.7120 | 0.5464 | 0.5796 |
| BM25 | 0.7876 | 0.6270 | 0.6605 |

For BM25 minus TF-IDF, the mean nDCG@10 difference is 0.0809. A paired query bootstrap with 1,000 resamples and seed 42 gives a percentile interval of approximately [0.0486, 0.1139]. This estimates variation over the observed claims and does not establish superiority on other datasets.

The JSON includes per-query top-10 rankings, metrics at 1/5/10, in-process latency, index-build time, platform information, dataset hashes, and source-code hashes. Timing depends on the machine and is not a serving benchmark. Raw abstracts and claim texts are not copied into the report; IDs resolve against the prepared dataset.

Reproduce from the repository root:

```bash
python scripts/prepare_data.py
python scripts/benchmark.py --split test
```

For development, use `--split train`; it writes `scifact-train.json`. Repeatedly tuning against the published test scores compromises their value as held-out evaluation. The notebook's chunking comparison uses training queries only.
