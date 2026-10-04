# Contributing to Awesome RAG

Help readers understand a RAG decision, reproduce an experiment, or build a complete application. Contributions can include resource descriptions, corrections, notebooks, retrieval implementations, evaluation tools, datasets, and cloud projects.

Read the [contributor agreement](CONTRIBUTOR_AGREEMENT.md) and [code of conduct](CODE_OF_CONDUCT.md). The agreement explains the current licensing status and sign-off process.

## Choose a contribution

| Contribution | What to include |
| --- | --- |
| Resource | Original URL, what readers will learn, category, prerequisites, and access restrictions |
| Correction | The incorrect statement or broken behavior, evidence, and the proposed fix |
| Notebook | Learning objective, real data, executable experiment, observations, and limitations |
| Retrieval or evaluation code | Motivation, meaningful correctness checks, configuration, and comparable results |
| Dataset | Source, license, version, reproducible preparation, schema, and evaluation purpose |
| End-to-end project | Architecture, setup, ingestion, retrieval, generation, evaluation, deployment, and cleanup |

Small corrections can go directly to a pull request. For a new dependency, dataset, framework track, architecture, or cloud project, open a proposal first to align the scope and avoid duplicate work. Use the issue templates and search existing issues before starting.

## Set up the repository

Fork the repository on GitHub, clone your fork, and create a focused branch:

```bash
git switch -c add/retrieval-experiment
```

Use Python 3.11 or newer. From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe -m notebook
```

On macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/prepare_data.py
.venv/bin/python -m notebook
```

Data preparation downloads the pinned SciFact archive once. See [data instructions](data/README.md) for provenance, integrity checks, and the Windows certificate alternative. Use the virtual environment as your IDE's notebook kernel. Default lessons then run offline; optional models require separate setup.

## Where changes belong

| Location | Purpose |
| --- | --- |
| `README.md` | Resource directory, learning path, and links to available lessons |
| `notebooks/foundations/` | Independently runnable foundational experiments |
| `rag_lab/` | Shared, inspectable loading, retrieval, and evaluation code |
| `data/README.md` | Dataset provenance, licenses, schemas, and preparation instructions |
| `scripts/` | Reproducible preparation, validation, and benchmark commands |
| `tests/` | Focused correctness and regression checks |
| `reports/` | Reproducible benchmark results and their interpretation |

Propose new project directories when needed. Do not add empty tracks, placeholder notebooks, or README links to files that do not exist.

## Resource standards

- Prefer original research, official documentation, and implementations that explain their approach.
- Write an original, specific description of what a reader learns. Check the destination and place it in the most useful category.
- Explain the resource's relevance to a RAG component or engineering decision. Avoid promotional copy, referral links, and unexplained link dumps.
- State paid access, account requirements, important prerequisites, and your affiliation when recommending your own material.
- Preserve attribution. Link to papers and articles instead of copying their full text.

A resource-only change needs link and content review; it does not need a benchmark run.

## Notebook standards

Every notebook should provide:

1. **Purpose:** the decision being explored, intended audience, prerequisites, expected runtime, and required hardware or services.
2. **Data:** a real corpus with provenance and a reproducible preparation step. Explain any subset and keep full-corpus evaluation available when claiming benchmark results.
3. **Mechanism:** show or explain the relevant algorithm and intermediate results. Shared helpers are welcome, but essential behavior should be inspectable.
4. **Experiment:** a baseline, a controlled change, and a comparison using the same data and questions.
5. **Interpretation:** discuss failures and tradeoffs. Distinguish observations from claims that would need more evidence.
6. **Practice:** an exercise and links to the relevant lesson or primary references.

Run top-to-bottom in a fresh kernel. Resolve paths from the checkout rather than your home directory. Avoid hidden state, embedded credentials, automatic paid requests, or automatic model downloads. Keep optional service calls disabled by default and explain how to enable them.

Use seeds where randomness is involved, identify model versions, and record meaningful parameters. Describe token approximations honestly. Small synthetic fixtures are useful for unit tests, but should not support benchmark-quality claims.

Clear cell outputs and execution counts before committing notebooks. Put reproducible numerical results in `reports/`; attach a short execution summary to the pull request. Remove widget state, local paths, credentials, and private data from metadata as well as visible outputs.

The current checker discovers all notebooks in `notebooks/foundations/`. A new notebook directory must also be added to the checker or come with a documented execution command. Do not claim that an optional model or cloud cell was validated when only its disabled path ran.

## Datasets and licensing

Document the dataset owner, original URL, license, version or checksum, schema, expected counts, and any transformations. Provide a download/preparation script with normal TLS validation, cache behavior, integrity checks, and clear errors. Do not silently replace missing data with a small sample.

Keep downloaded corpora, model weights, indexes, and large generated artifacts out of Git. Update `.gitignore` for new caches. Do not upload data without redistribution rights or assume the repository's future license covers upstream content. If a dataset requires authentication or usage approval, document it and provide an alternative execution path where practical.

## Evaluation standards

- Use development queries for exploration and parameter selection. Fix configurations before reporting test results.
- Compare methods against the same candidate corpus, query set, relevance judgments, and cutoffs. Document any exceptions.
- For chunk retrieval evaluated with document labels, collapse hits to unique parent document IDs before applying top-k.
- Report exact fields, tokenizer, model, parameters, seeds, source versions, and commands. Include per-query results so failures can be inspected.
- Distinguish retrieval relevance, claim support, answer quality, citation validity, and answerability. A high retrieval score does not establish all of them.
- Explain incomplete labels, correlated examples, domain limits, and uncertainty. Do not select only successful queries or describe local timing as a production load test.
- Preserve dataset and code hashes in benchmark reports. Explain why an existing report changed and summarize the differences.

The current [reference report](reports/README.md) documents the fixed SciFact baselines. Its test scores should not become a target for repeated parameter tuning.

## Cloud and framework projects

Include a complete architecture and reproducible setup, dependency versions, sample configuration without credentials, evaluation instructions, and known limitations. Specify provider, region, required permissions, paid services, cost assumptions, and how to delete all created resources. Keep deployments and billable calls explicit. Explain how secrets are supplied at runtime.

For framework comparisons, preserve the task and evaluation set. Separate framework differences from changes in model, retrieval configuration, or infrastructure. Do not label a demonstration production-ready without evidence for that claim.

## Validate your change

Choose checks based on the affected behavior:

| Change | Validation |
| --- | --- |
| Links or prose | Review facts, check links and Markdown rendering |
| Notebook | Restart and run every default cell; validate with the notebook checker |
| Shared Python code | Run focused tests plus every affected notebook |
| Retrieval or scoring | Run tests and a development benchmark; inspect per-query changes |
| Data preparation | Verify checksum handling, schema, counts, and repeat runs from the cache |
| Optional model or cloud integration | Report exactly what was exercised, environment, cost, and untested paths |

Windows commands:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/check_notebooks.py
.\.venv\Scripts\python.exe scripts/benchmark.py --split train
git diff --check
```

On macOS or Linux, substitute `.venv/bin/python` for the Python executable. The notebook checker leaves source notebooks unchanged. Run `--split test` only when the evaluation plan calls for a final comparison; it overwrites the reference test report.

Add a test for a corrected algorithmic bug or important edge case. Avoid tests that only repeat implementation details. Include exact commands and results in the pull request, and identify anything that could not be tested.

## Submit a pull request

1. Keep the change focused and update affected documentation and learning-path links.
2. Review the diff for unintended files, outputs, credentials, dataset copies, and unrelated report changes.
3. Follow the [contributor agreement](CONTRIBUTOR_AGREEMENT.md), including its licensing prerequisite and commit sign-offs.
4. Push your branch and open a pull request using the provided template. Link its proposal or bug report if applicable.
5. Describe the learning or behavior improvement, validation evidence, sources, and limitations. Mark unfinished work as a draft.
6. Respond to review with code or evidence. Preserve other contributors' attribution and coordinate before rewriting shared history.

Maintainers review educational value, reproducibility, correctness, scope, attribution, licensing, and sign-offs. They may ask for revisions or decline duplicate, unmaintainable, promotional, or unsupported material. Do not assume an automated check or review-time guarantee exists unless it is actually configured in the repository.

## AI-assisted contributions

AI assistance is allowed. You remain responsible for reading, understanding, testing, and having the right to submit the result. Disclose substantial AI assistance in the pull request, particularly generated explanations, code, data, or evaluations. Verify references and numbers against original sources; never present generated relevance judgments as human-labeled ground truth.

## Getting help

Use an issue for reproducible bugs, resource suggestions, or scoped proposals. Include file paths, commands, environment details, and sanitized errors. Do not put secrets, personal information, or confidential reports into public issues. Community conduct and reporting guidance are in the [code of conduct](CODE_OF_CONDUCT.md).
