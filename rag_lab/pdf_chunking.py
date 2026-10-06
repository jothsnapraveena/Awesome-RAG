"""PDF-backed chunking helpers for the chunking notebooks."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


def load_pdf_pages(path):
    """Extract text from a PDF and return page records with source metadata."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("Install notebook dependencies first: python -m pip install -r requirements.txt") from exc

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, 1):
        text = normalize_text(page.extract_text() or "")
        if text:
            pages.append({"page": index, "text": text})
    if not pages:
        raise ValueError(f"No extractable text found in {path}")
    return pages


def normalize_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sample_document_path(root="."):
    return Path(root) / "data" / "sample_documents" / "AUG242026_05B2203_AAO.pdf"


def page_summary(pages):
    words = sum(len(page["text"].split()) for page in pages)
    chars = sum(len(page["text"]) for page in pages)
    return {"pages": len(pages), "words": words, "characters": chars}


def print_chunks(chunks, limit=5, preview_chars=650):
    for chunk in chunks[:limit]:
        label = f"{chunk['id']} | page {chunk['page_start']}"
        if chunk["page_end"] != chunk["page_start"]:
            label += f"-{chunk['page_end']}"
        if "heading" in chunk and chunk["heading"]:
            label += f" | {chunk['heading']}"
        print(label)
        print(chunk["text"][:preview_chars])
        print("-" * 100)
    if len(chunks) > limit:
        print(f"... {len(chunks) - limit} more chunks")


def fixed_size_chunks(pages, words_per_chunk=180):
    chunks = []
    for page in pages:
        words = page["text"].split()
        for start in range(0, len(words), words_per_chunk):
            end = min(start + words_per_chunk, len(words))
            chunks.append({
                "id": f"fixed-{len(chunks) + 1}",
                "page_start": page["page"],
                "page_end": page["page"],
                "start_word": start,
                "end_word": end,
                "text": " ".join(words[start:end]),
            })
    return chunks


def sliding_window_chunks(pages, size=180, overlap=45):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks = []
    step = size - overlap
    for page in pages:
        words = page["text"].split()
        for start in range(0, len(words), step):
            end = min(start + size, len(words))
            chunks.append({
                "id": f"window-{len(chunks) + 1}",
                "page_start": page["page"],
                "page_end": page["page"],
                "start_word": start,
                "end_word": end,
                "text": " ".join(words[start:end]),
            })
            if end == len(words):
                break
    return chunks


def split_sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def sentence_chunks(pages, max_words=180):
    chunks = []
    for page in pages:
        current, current_words = [], 0
        for sentence in split_sentences(page["text"]):
            count = len(sentence.split())
            if current and current_words + count > max_words:
                chunks.append({
                    "id": f"sentence-{len(chunks) + 1}",
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "text": " ".join(current),
                })
                current, current_words = [], 0
            current.append(sentence)
            current_words += count
        if current:
            chunks.append({
                "id": f"sentence-{len(chunks) + 1}",
                "page_start": page["page"],
                "page_end": page["page"],
                "text": " ".join(current),
            })
    return chunks


def paragraph_chunks(pages, max_words=220):
    chunks = []
    for page in pages:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", page["text"]) if part.strip()]
        for paragraph in paragraphs:
            words = paragraph.split()
            if len(words) <= max_words:
                chunks.append({
                    "id": f"paragraph-{len(chunks) + 1}",
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "text": paragraph,
                })
            else:
                for start in range(0, len(words), max_words):
                    chunks.append({
                        "id": f"paragraph-{len(chunks) + 1}",
                        "page_start": page["page"],
                        "page_end": page["page"],
                        "text": " ".join(words[start:start + max_words]),
                    })
    return chunks


def looks_like_heading(line):
    stripped = line.strip()
    if not stripped or len(stripped) > 90:
        return False
    words = stripped.split()
    if len(words) > 12:
        return False
    letters = [char for char in stripped if char.isalpha()]
    uppercase_ratio = sum(char.isupper() for char in letters) / max(1, len(letters))
    return uppercase_ratio > 0.65 or bool(re.match(r"^(\d+\.|[A-Z][A-Za-z]+:)", stripped))


def heading_aware_chunks(pages, max_words=220):
    chunks = []
    for page in pages:
        heading = f"Page {page['page']}"
        current = []

        def flush():
            if current:
                text = "\n".join(current).strip()
                chunks.append({
                    "id": f"section-{len(chunks) + 1}",
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "heading": heading,
                    "text": f"{heading}\n{text}",
                })

        for line in page["text"].splitlines():
            stripped = line.strip()
            if looks_like_heading(stripped):
                flush()
                heading = stripped
                current = []
            elif stripped:
                current.append(stripped)
                if len(" ".join(current).split()) >= max_words:
                    flush()
                    current = []
        flush()
    return chunks


def semantic_chunks(pages, max_words=220, min_shared_terms=2, min_words=40):
    chunks = []
    for page in pages:
        current, current_terms, current_words = [], set(), 0
        for sentence in split_sentences(page["text"]):
            terms = content_terms(sentence)
            count = len(sentence.split())
            topic_shift = current and current_words >= 80 and len(current_terms & terms) < min_shared_terms
            too_large = current and current_words + count > max_words
            if (topic_shift or too_large) and current_words >= min_words:
                chunks.append({
                    "id": f"semantic-{len(chunks) + 1}",
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "text": " ".join(current),
                })
                current, current_terms, current_words = [], set(), 0
            current.append(sentence)
            current_terms.update(terms)
            current_words += count
        if current:
            text = " ".join(current)
            if chunks and len(text.split()) < min_words and chunks[-1]["page_end"] == page["page"]:
                chunks[-1]["text"] = f"{chunks[-1]['text']} {text}"
            else:
                chunks.append({
                    "id": f"semantic-{len(chunks) + 1}",
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "text": text,
                })
    return chunks


def content_terms(text):
    stopwords = {
        "the", "and", "or", "a", "an", "to", "of", "in", "for", "on", "by", "with",
        "is", "are", "was", "were", "be", "this", "that", "from", "as", "at", "it",
    }
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in stopwords and len(word) > 2}


def chunk_stats(chunks):
    lengths = [len(chunk["text"].split()) for chunk in chunks]
    if not lengths:
        return {"chunks": 0, "min_words": 0, "avg_words": 0, "max_words": 0}
    return {
        "chunks": len(chunks),
        "min_words": min(lengths),
        "avg_words": round(sum(lengths) / len(lengths), 1),
        "max_words": max(lengths),
    }


def top_terms(chunks, n=12):
    counts = Counter()
    for chunk in chunks:
        counts.update(content_terms(chunk["text"]))
    return counts.most_common(n)
