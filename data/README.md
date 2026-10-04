# SciFact dataset

The foundation notebooks use the complete BEIR distribution of SciFact:

| Component | Records | Purpose |
| --- | ---: | --- |
| Corpus | 5,183 | Scientific titles and abstracts; all are retrieval candidates |
| Training queries | 809 | Development experiments and notebook examples |
| Test queries | 300 | Separate reporting after fixing configurations |
| Total queries | 1,109 | Scientific claims, not generated questions |

Relevance judgments identify evidence documents. They do not say whether a claim is supported or refuted, and this export does not provide reference answers or sentence-level evidence. Unjudged documents must not be assumed to be unanswerable examples. This dataset evaluates scientific evidence retrieval; it does not cover full-document parsing, OCR, or generated-answer quality.

## Source and attribution

- **Original dataset:** David Wadden and collaborators, SciFact, introduced in *Fact or Fiction: Verifying Scientific Claims* (2020). See the [authors' dataset documentation](https://github.com/allenai/scifact).
- **Retrieval distribution:** [BEIR SciFact dataset card](https://huggingface.co/datasets/BeIR/scifact) and the [BEIR dataset catalog](https://github.com/beir-cellar/beir#beers-available-datasets).
- **Download:** [BEIR SciFact archive](https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip).
- **License:** The dataset card lists [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The upstream data retains its own terms; this repository does not relicense it. Preserve attribution and applicable share-alike terms when redistributing adaptations.

The original archive contents are kept unmodified. Chunking and tokenization happen in memory. Downloaded data is ignored by Git; source documentation and the download procedure are versioned.

## Reproduce the snapshot

From the repository root:

```bash
python scripts/prepare_data.py
```

The script downloads once, validates both checksums, and writes only four explicitly allowed files. Running it again validates the cached archive and restores the same source files. It never disables certificate validation.

```text
Published BEIR MD5: 5f7d1de60b170fc8027bb7898e2efca1
Pinned SHA-256:     536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165
```

If Python on Windows cannot use your system certificate chain, download through PowerShell's system trust store, then run the same verification script:

```powershell
Invoke-WebRequest -Uri 'https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip' -OutFile 'data/scifact.zip'
python scripts/prepare_data.py
```

The prepared directory is approximately 8 MB:

```text
data/scifact/
  corpus.jsonl       # _id, title, text, metadata
  queries.jsonl      # _id, text, metadata
  qrels/train.tsv   # query-id, corpus-id, score
  qrels/test.tsv
  manifest.json     # source URL, archive digest, per-file SHA-256 hashes
```

The loader checks file integrity, unique IDs, nonempty text, judgment references, split separation, and record counts. It does not silently download data or substitute a smaller corpus.

## Evaluation discipline

Use the training queries for exploration and parameter decisions. Keep all corpus documents as candidates for both splits; indexing the complete document collection is part of this benchmark, not test-query training. Query IDs do not overlap, but related scientific claims may still be correlated across the dataset.

The test report compares fixed lexical baselines, not a production system. Labels may be incomplete. Report the exact tokenizer, fields, scoring formula, document aggregation, and cutoff. Generation and citation support need separate evaluation data or human review.
