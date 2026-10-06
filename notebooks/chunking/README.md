# Chunking for RAG

Chunking is the step where long source documents are split into smaller passages before indexing and retrieval.

In RAG, the retriever usually cannot search, rank, and send entire documents to the model. Chunking decides what a "retrievable unit" should be: a paragraph, a fixed-size word window, a section, a table, a sentence group, or another meaningful span.

Good chunking helps the system retrieve evidence that is complete enough to answer a question, small enough to fit a context budget, and traceable enough to cite. Poor chunking can split an answer across boundaries, bury important terms in oversized passages, or remove headings that explain what a passage means.

## Purpose

Chunking is used to:

- Fit long documents into embedding, retrieval, and prompt context limits.
- Preserve useful local context around facts, definitions, procedures, tables, and examples.
- Improve retrieval quality by making each indexed passage focused.
- Support citations by keeping source IDs, section names, and character offsets.
- Compare retrieval strategies under repeatable conditions.

## Usage in a RAG pipeline

A typical indexing flow looks like this:

```text
Documents -> parse and clean -> chunk -> embed or index -> store
```

A typical answering flow then retrieves chunks:

```text
Question -> retrieve chunks -> rerank optional -> assemble context -> generate cited answer
```

The best chunking strategy depends on the document type, retrieval method, and question style. A legal contract, API guide, scientific abstract, support article, and financial report may need different chunk boundaries.

## Shared use case

All notebooks in this folder use the same source document:

```text
data/sample_documents/AUG242026_05B2203_AAO.pdf
```

The PDF is treated as source data only. Any instructions or procedural language inside the document are part of the document content, not instructions for running this repository.

Use the same document when comparing chunking methods. This makes differences easier to see because the document, extraction quality, questions, and expected evidence stay fixed.

Recommended pattern for this repo:

- Use the shared PDF across all notebooks.
- Keep each notebook self-contained so learners can study one method without jumping into helper modules.
- Preserve metadata such as page number, chunk ID, character offsets, and headings when available.
- Ask the same comparison questions in every notebook.
- Compare chunk count, average size, overlap, readability, and whether a chunk can support a cited answer.

## Chunking types covered

| Notebook | Chunking type | Best for | Watch out for |
| --- | --- | --- | --- |
| [01 - Fixed-size chunking](01_fixed_size_chunking.ipynb) | Split every N words from the PDF text | Simple baselines and fast experiments | Can split sentences, tables, and definitions |
| [02 - Sliding-window chunking](02_sliding_window_chunking.ipynb) | Fixed-size PDF chunks with overlap | Reducing boundary misses | Adds duplicate content and index cost |
| [03 - Sentence chunking](03_sentence_chunking.ipynb) | Group complete PDF sentences | Readability and clean evidence spans | Sentence boundaries may ignore document structure |
| [04 - Paragraph chunking](04_paragraph_chunking.ipynb) | Keep extracted PDF paragraphs together | Articles, reports, support docs | PDF extraction may merge or split paragraphs imperfectly |
| [05 - Heading-aware chunking](05_heading_aware_chunking.ipynb) | Attach detected headings to chunks | Docs, policies, manuals | Requires reliable heading detection |
| [06 - Semantic chunking](06_semantic_chunking.ipynb) | Split when topic changes in the PDF | Mixed-topic documents | Needs embeddings or similarity heuristics in production |

## How to evaluate chunking

For each strategy, inspect:

- Does the chunk contain enough evidence to answer the question?
- Did the chunk preserve headings, definitions, and source references?
- Are chunks too small, too large, or too repetitive?
- Would a retriever find the right chunk from the user query?
- How many chunks are created and how much duplicate text is added?

Each notebook defines the PDF loading, inspection helpers, and the chunking function it teaches. This is intentional: learners should be able to open one notebook and understand the method end to end.

The foundational notebooks in `notebooks/foundations/` show related RAG ideas on the SciFact corpus.
