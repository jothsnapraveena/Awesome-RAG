# Awesome RAG

**Study the resources. Inspect the pipeline. Build the application.**

Awesome RAG is a learning workspace for understanding how retrieval-augmented generation works, one engineering decision at a time. It brings together curated reading, runnable Jupyter experiments on real documents, and planned project tracks for different frameworks and clouds.

The central idea is to follow a document from ingestion to a cited answer. Along the way, inspect what each component produces, change one decision, and measure the effect. The resources below support that journey: use them to understand a component, explore its implementation, and decide what to try yourself.

**Project status:** Four foundational notebooks are available alongside the resource directory. Advanced notebooks and complete cloud projects are planned. External resources are labeled separately from this repository's lessons.

## Contents

- [Architecture overview](#architecture-overview)
- [Start here](#start-here)
- [Run the foundational notebooks](#run-the-foundational-notebooks)
- [Follow a document through RAG](#follow-a-document-through-rag)
- [Papers and surveys](#papers-and-surveys)
- [Courses and tutorials](#courses-and-tutorials)
- [Document ingestion and parsing](#document-ingestion-and-parsing)
- [Chunking and context preparation](#chunking-and-context-preparation)
- [Embeddings](#embeddings)
- [Vector indexes and databases](#vector-indexes-and-databases)
- [Retrieval and reranking](#retrieval-and-reranking)
- [Generation and grounded answers](#generation-and-grounded-answers)
- [Frameworks](#frameworks)
- [Advanced RAG](#advanced-rag)
- [Evaluation and datasets](#evaluation-and-datasets)
- [Observability and production](#observability-and-production)
- [Cloud guides and example projects](#cloud-guides-and-example-projects)
- [Notebook collections and implementations](#notebook-collections-and-implementations)
- [Our notebook and project roadmap](#our-notebook-and-project-roadmap)
- [Contributing resources](#contributing-resources)

## Architecture overview

![Multi-cloud RAG architecture showing ingestion, document processing, embeddings, indexing, retrieval, fusion, reranking, generation, evaluation, observability, security, and deployment](images/Production-Grade%20Multi-Cloud%20RAG%20Architecture.png)

This diagram maps the broader architecture the labs and projects explore. It includes planned capabilities; the lab catalog and roadmap identify what is currently implemented.

[Open the full-size architecture diagram](images/Production-Grade%20Multi-Cloud%20RAG%20Architecture.png).

## Start here

RAG retrieves information from an external collection and supplies that information as context for a model's response. A useful starting architecture has two flows:

```text
Indexing: Documents -> Parse and clean -> Chunk -> Embed -> Store
Answering: Question -> Retrieve -> Rerank (optional) -> Build context -> Generate answer
Evaluation: Check retrieved evidence and generated answers throughout development
```

For a first pass, follow this reading and building sequence:

1. **Understand the architecture:** Read [AWS's RAG introduction](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html) for an overview of the components.
2. **Build a first pipeline:** Follow a [Haystack tutorial](https://haystack.deepset.ai/tutorials) to connect retrieval and generation.
3. **Study each stage:** Work through the ingestion, chunking, embeddings, and retrieval resources below.
4. **Measure quality:** Use [Ragas](https://docs.ragas.io/en/stable/) to explore retrieval and answer evaluation.
5. **Experiment with improvements:** Explore [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) and compare changes against a baseline.
6. **Study a deployed application:** Explore the [Azure RAG sample](https://github.com/Azure-Samples/azure-search-openai-demo), then the other cloud examples.

## Run the foundational notebooks

These lessons use **5,183 real scientific abstracts, 809 development claims, and 300 separate test claims** from SciFact. They search the complete corpus, use published relevance judgments, and expose the intermediate results. Each notebook runs independently from a fresh kernel after a one-time data download; no API keys or model downloads are required for the default exercises. See [data provenance, licensing, and preparation](data/README.md).

| Notebook | What you will build |
| --- | --- |
| [01 - Documents and chunking](notebooks/foundations/01_documents_and_chunking.ipynb) | Corpus profiling, exact source spans, and chunking/storage comparisons |
| [02 - TF-IDF and BM25](notebooks/foundations/02_tfidf_retrieval.ipynb) | Full-corpus inverted indexes, scoring formulas, and ranking disagreements |
| [03 - Context and generation](notebooks/foundations/03_context_and_generation.ipynb) | Evidence budgets, source references, evidence-removal experiments, and optional Ollama generation |
| [04 - Retrieval evaluation](notebooks/foundations/04_retrieval_evaluation.ipynb) | Recall, MRR, nDCG, a chunking ablation, bootstrap intervals, and actual retrieval misses |

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

Open a notebook under `notebooks/foundations/` and run its cells in order. In VS Code, select the `.venv` Python interpreter as the notebook kernel. Installation and initial data preparation require internet access; subsequent default runs use Python's standard library and the local corpus. The dataset download is checksum-pinned and cached, with no silent sample mode. For Windows certificate issues, see the [documented download alternative](data/README.md#reproduce-the-snapshot).

TF-IDF and BM25 demonstrate lexical retrieval, not neural embeddings. SciFact evaluates evidence retrieval for scientific claims; it does not provide reference answers in this export. Lesson 03 defaults to evidence assembly. To enable generation, install Ollama and a model separately, then configure the optional cell. This model-dependent step is not part of the offline checks.

To validate notebook structure and execute all default cells in fresh kernels:

```powershell
.\.venv\Scripts\python.exe scripts/check_notebooks.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On macOS or Linux, use `.venv/bin/python scripts/check_notebooks.py`.

The [reference test report](reports/README.md) records both fixed baselines over all 300 test claims, including per-query rankings, configurations, dataset hashes, and source-code hashes. Use `python scripts/benchmark.py --split train` for development and `--split test` for final reporting after fixing your configuration.

## Follow a document through RAG

Use this map to choose what to study next. The foundational notebooks above cover the first experiments; the broader experiments below guide future lessons.

| Stage | Question to investigate | Experiment to build | Evidence to inspect |
| --- | --- | --- | --- |
| [Ingestion](#document-ingestion-and-parsing) | Did we preserve the information in the source? | Parse a document containing headings and a table | Extracted text, table structure, page references |
| [Chunking](#chunking-and-context-preparation) | Does each passage contain enough context? | Split the same document three ways | Broken sentences, missing headings, passage lengths |
| [Embedding](#embeddings) | Can similar meanings be found with different words? | Compare literal and paraphrased queries | Nearest passages and relevance judgments |
| [Indexing](#vector-indexes-and-databases) | What happens when a document changes? | Add, replace, and delete a source | Search results before and after each change |
| [Retrieval](#retrieval-and-reranking) | Why did the right passage miss the results? | Compare keyword, dense, and hybrid retrieval | Relevant passages found within a fixed result limit |
| [Reranking](#retrieval-and-reranking) | Can we move better evidence closer to the top? | Rerank the same candidate passages | Rank changes and added latency |
| [Generation](#generation-and-grounded-answers) | Does the answer follow from the evidence? | Ask answerable and unanswerable questions | Supported claims, citations, unsupported answers |
| [Evaluation](#evaluation-and-datasets) | Did the change actually help? | Run the same question set against two configurations | Quality differences, failure examples, cost |
| [Deployment](#cloud-guides-and-example-projects) | Can someone else reproduce the application? | Deploy a reference project and load the same corpus | Setup steps, request traces, cleanup results |

The foundational notebooks share the full SciFact corpus and its development judgments to make these changes comparable. Each notebook shows its inputs, intermediate outputs, and an exercise to extend the experiment.

## Papers and surveys

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — **Paper, 2020.** Foundational work combining a retriever with a generative model.
- [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) — **Paper, 2020.** Learn how dense representations support passage retrieval.
- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) — **Survey, 2023.** An overview of naive, advanced, and modular RAG approaches.
- [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496) — **Paper, 2022.** Introduces HyDE: using hypothetical documents to help retrieve real evidence.
- [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) — **Paper, 2023.** Studies learned retrieval and reflection behavior.
- [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884) — **Paper, 2024.** Explores evaluating retrieved evidence and correcting retrieval failures.

Years refer to the initial paper submissions. Read the linked versions for revisions and publication details.

## Courses and tutorials

- [LangChain: Chat with Your Data](https://www.deeplearning.ai/courses/langchain-chat-with-your-data) — **Course.** Study document loading, splitting, retrieval, and conversational question answering. Check the provider for current access terms.
- [Haystack Tutorials](https://haystack.deepset.ai/tutorials) — **Tutorials.** Guided examples for building search, question-answering, and RAG pipelines.
- [LlamaIndex Documentation](https://developers.llamaindex.ai/python/framework/) — **Documentation and examples.** Learn document ingestion, indexing, querying, and evaluation.
- [Sentence Transformers: Retrieve and Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) — **Tutorial.** Understand a two-stage retrieval pipeline using embeddings and a cross-encoder.

## Document ingestion and parsing

- [Docling](https://github.com/docling-project/docling) — **Library.** Convert documents into structured representations for downstream retrieval workflows.
- [Unstructured](https://github.com/Unstructured-IO/unstructured) — **Library.** Partition document formats into elements that can be cleaned, enriched, and indexed.
- [LlamaIndex](https://developers.llamaindex.ai/python/framework/) — **Framework documentation.** Explore document connectors and ingestion pipelines.

**Try investigating:** Select a paragraph and table in the original document. Can you find both in the parsed output and trace them back to the correct page?

## Chunking and context preparation

- [Unstructured Chunking](https://docs.unstructured.io/open-source/core-functionality/chunking) — **Guide.** Learn how document elements, size limits, and overlap affect chunks.
- [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) — **Engineering article.** Study an approach that adds explanatory context to chunks before indexing.
- [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) — **Examples.** Explore chunking and context-handling experiments alongside other retrieval techniques.

**Try investigating:** Find a question whose answer crosses a chunk boundary. Compare whether overlap or splitting by document structure makes the evidence easier to retrieve.

## Embeddings

- [Sentence Transformers](https://www.sbert.net/) — **Documentation.** Learn text embeddings, semantic similarity, and cross-encoder models.
- [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) — **Models and code.** Explore the BGE embedding and reranking ecosystem.
- [Massive Text Embedding Benchmark (MTEB)](https://github.com/embeddings-benchmark/mteb) — **Benchmark toolkit.** Study embedding evaluation across tasks, languages, and modalities.

**Try investigating:** Write a literal query, a paraphrase, and a query containing an exact identifier. Compare what each embedding model retrieves and record its latency.

## Vector indexes and databases

- [FAISS](https://github.com/facebookresearch/faiss) — **Library.** Learn similarity search and indexing for dense vectors; useful for understanding the index itself.
- [Chroma](https://docs.trychroma.com/docs/overview/introduction) — **Documentation.** Explore storing embeddings and querying collections.
- [Qdrant](https://qdrant.tech/documentation/) — **Documentation.** Study vector search, payload filtering, and retrieval workflows.
- [Milvus](https://milvus.io/docs) — **Documentation.** Explore vector indexing, search, and database deployment.
- [Weaviate](https://docs.weaviate.io/weaviate) — **Documentation.** Study vector and hybrid retrieval with structured object data.
- [pgvector](https://github.com/pgvector/pgvector) — **PostgreSQL extension.** Add vector similarity search alongside relational data.
- [Pinecone](https://docs.pinecone.io/guides/get-started/overview) — **Documentation.** Explore managed vector search and retrieval services.

## Retrieval and reranking

- [Sentence Transformers: Retrieve and Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) — **Tutorial.** Retrieve candidates efficiently, then score them with a cross-encoder.
- [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) — **Implementation.** Experiment with embedding models and rerankers.
- [HyDE Paper](https://arxiv.org/abs/2212.10496) — **Research.** Explore query expansion through hypothetical documents.
- [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) — **Engineering article.** Examine contextual embeddings, keyword retrieval, and reranking together.
- [BEIR](https://github.com/beir-cellar/beir) — **Evaluation toolkit.** Compare retrieval approaches across diverse datasets.

**Try investigating:** Collect one failed query for each retrieval method. Inspect whether the cause is vocabulary, missing context, filtering, or ranking before adding another component.

## Generation and grounded answers

- [Haystack Tutorials](https://haystack.deepset.ai/tutorials) — **Examples.** Connect retrievers, prompt construction, and generators into a pipeline.
- [LlamaIndex Documentation](https://developers.llamaindex.ai/python/framework/) — **Guides.** Explore query engines and response synthesis over retrieved content.
- [Ollama](https://github.com/ollama/ollama) — **Local model runtime.** Explore running the generation component locally; model and hardware requirements vary.
- [Azure RAG Sample](https://github.com/Azure-Samples/azure-search-openai-demo) — **Application.** Study how a document question-answering interface connects search results to generated responses.

**Try investigating:** Remove the passage containing the answer, then ask the same question again. Inspect whether the response acknowledges the missing evidence and whether its citations support its claims.

## Frameworks

- [LangChain Retrieval Documentation](https://docs.langchain.com/oss/python/deepagents/retrieval) — **Documentation.** Explore retrieval components and how they fit into model-driven applications.
- [LlamaIndex](https://developers.llamaindex.ai/python/framework/) — **Documentation.** Study data ingestion, indexes, query engines, and document workflows.
- [Haystack](https://haystack.deepset.ai/tutorials) — **Tutorials.** Build component-based retrieval and generation pipelines.

Choose one framework for a first project. Use a shared dataset and evaluation set when comparing implementations across frameworks.

## Advanced RAG

- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) — **Implementation.** Explore graph-based indexing and retrieval over document collections.
- [Self-RAG](https://arxiv.org/abs/2310.11511) — **Paper.** Study retrieval and generation with learned self-reflection.
- [Corrective RAG](https://arxiv.org/abs/2401.15884) — **Paper.** Study how retrieval-quality assessment can guide corrective steps.
- [ColPali](https://github.com/illuin-tech/colpali) — **Models and code.** Explore visual document retrieval over page images.
- [RAG with Deep Agents](https://docs.langchain.com/oss/python/deepagents/rag) — **Guide.** Explore agent-driven retrieval workflows.
- [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) — **Examples.** Explore additional approaches to query processing, retrieval, and context preparation.

## Evaluation and datasets

- [Ragas](https://docs.ragas.io/en/stable/) — **Documentation.** Explore context precision, context recall, faithfulness, and test-set generation.
- [DeepEval](https://github.com/confident-ai/deepeval) — **Evaluation framework.** Build automated checks for LLM and RAG application behavior.
- [BEIR](https://github.com/beir-cellar/beir) — **Datasets and toolkit.** Evaluate retrieval across different domains and tasks.
- [MTEB](https://github.com/embeddings-benchmark/mteb) — **Benchmark toolkit.** Compare embedding models using task-specific evaluations.

**Try investigating:** Keep the questions fixed while changing one component. Compare retrieval quality separately from answer quality, and save examples where one improves while the other does not.

## Observability and production

- [Langfuse](https://github.com/langfuse/langfuse) — **Observability platform.** Explore tracing, prompt management, and evaluation for LLM applications.
- [Phoenix](https://github.com/Arize-ai/phoenix) — **Observability and evaluation.** Inspect application traces and investigate retrieval or generation failures.
- [AWS RAG Architecture Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html) — **Architecture guide.** Review the data processing and retrieval components of a cloud RAG system.
- [Azure AI Search RAG Overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — **Architecture guide.** Study search-backed RAG patterns and their supporting components.

**Study focus:** Document updates and deletion, access-aware retrieval, caching, tracing, failure handling, deployment, and resource cleanup.

## Cloud guides and example projects

### AWS

- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — **Official guide.** Learn managed ingestion, retrieval, and generation with knowledge bases.
- [Amazon Bedrock Samples](https://github.com/aws-samples/amazon-bedrock-samples) — **Official examples.** Explore code for Bedrock capabilities, including RAG workflows.
- [RAG Architecture Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html) — **Official guidance.** Understand the components involved in choosing an AWS architecture.

### Microsoft Azure

- [RAG with Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — **Official guide.** Learn how search integrates with generation.
- [Azure Search and OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo) — **Official sample application.** Explore a deployable document chat application with search-backed retrieval.

### Google Cloud

- [Google Cloud RAG Engine](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview) — **Official guide.** Explore managed RAG capabilities and data-to-retrieval workflows.
- [Google Cloud Generative AI Examples](https://github.com/GoogleCloudPlatform/generative-ai) — **Official examples.** Find notebooks and sample applications, including retrieval and grounding workflows.

Check each provider's prerequisites, supported regions, pricing, and teardown instructions before running cloud examples.

## Notebook collections and implementations

- [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) — Detailed technique examples and notebook tutorials for hands-on experimentation.
- [Haystack Tutorials](https://haystack.deepset.ai/tutorials) — Guided pipeline implementations for search and RAG.
- [Google Cloud Generative AI](https://github.com/GoogleCloudPlatform/generative-ai) — Cloud notebooks and application examples.
- [Amazon Bedrock Samples](https://github.com/aws-samples/amazon-bedrock-samples) — Bedrock examples to study and adapt.
- [Azure RAG Demo](https://github.com/Azure-Samples/azure-search-openai-demo) — An application reference for a complete cloud project.
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) — A graph-based implementation to explore after building a baseline pipeline.

## Our notebook and project roadmap

The table distinguishes the available introductory lessons from the broader planned coverage.

| Track | Planned coverage | Status |
| --- | --- | --- |
| Foundations | Lexical retrieval, context assembly, and optional local generation | Available: lessons 01-03 |
| Ingestion | Verified benchmark loading, corpus profiling, and source metadata; document parsing to follow | Available: 01 |
| Chunking | Fixed-size word windows and overlap; document-aware strategies to follow | Basic lesson available: 01 |
| Embeddings and indexing | Similarity, index construction, updates, and deletion | Planned |
| Retrieval | TF-IDF and BM25 over the full corpus; dense, hybrid, and reranked retrieval to follow | Available: 02 |
| Generation | Context and source references with optional local LLM; robust answer validation to follow | Basic lesson available: 03 |
| Evaluation | Published judgments, ranking metrics, ablations, and failure analysis; answer evaluation to follow | Available: 04 |
| Advanced patterns | Query rewriting, graph, multimodal, and agentic RAG | Planned |
| Framework projects | Implement the same document assistant with LangChain, LlamaIndex, and Haystack | Planned |
| Cloud projects | Take a document assistant from local development to AWS, Azure, and Google Cloud | Planned |

The notebooks explain one component at a time and expose intermediate results. Planned end-to-end projects will connect ingestion, retrieval, generation, evaluation, and deployment, with setup and cleanup instructions. Comparable implementations will use shared data and evaluation questions where practical.

The first project will be a document assistant that answers with source references and handles missing evidence. Framework variants will explore how the same pipeline is expressed in different libraries. Cloud variants will explore deployment, storage, configuration, and operations. Each project will document its choices and the results of running the shared evaluation questions.

## Contributing resources

Contributions are welcome for resources, explanations, notebooks, datasets, evaluation tools, and complete projects. Start with the [contribution guide](CONTRIBUTING.md) for setup, quality standards, validation commands, and the pull-request workflow.

- Read the [contributor agreement](CONTRIBUTOR_AGREEMENT.md) for authorship, licensing, attribution, and DCO sign-offs. The project-wide license is currently undecided; the agreement explains how this affects external contributions.
- Follow the [code of conduct](CODE_OF_CONDUCT.md) in discussions and reviews.
- Use the issue templates for bugs, resource suggestions, notebook/project proposals, and datasets. Pull requests include a review checklist.

For a resource suggestion, provide the original link, what readers will learn, the relevant RAG stage, and any access requirements or affiliation. Listings are learning references, not rankings or endorsements.
