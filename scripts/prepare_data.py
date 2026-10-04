"""Fetch the pinned BEIR SciFact archive and extract only expected data files."""
import hashlib
import json
from pathlib import Path
import ssl
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
SHA256 = "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165"
MD5 = "5f7d1de60b170fc8027bb7898e2efca1"  # Published by BEIR; SHA256 pins our snapshot.
FILES = ("corpus.jsonl", "queries.jsonl", "qrels/train.tsv", "qrels/test.tsv")


def prepare():
    archive = ROOT / "data/scifact.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        temporary = archive.with_suffix(".part")
        try:
            # Honor normal platform certificate validation; never disable TLS checks.
            with urllib.request.urlopen(URL, timeout=60, context=ssl.create_default_context()) as response:
                with temporary.open("wb") as output:
                    size = 0
                    while block := response.read(1024 * 1024):
                        size += len(block)
                        if size > 20_000_000:
                            raise ValueError("Unexpected archive size")
                        output.write(block)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != SHA256:
                raise ValueError("Archive checksum mismatch; no data extracted")
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
    raw = archive.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256 or hashlib.md5(raw).hexdigest() != MD5:
        raise ValueError("Cached archive checksum mismatch; remove it and download again")
    folder = ROOT / "data/scifact"
    hashes = {}
    with zipfile.ZipFile(archive) as zipped:
        for relative in FILES:
            # Explicit allowlist avoids extracting arbitrary paths from an archive.
            contents = zipped.read("scifact/" + relative)
            destination = folder / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contents)
            hashes[relative] = hashlib.sha256(contents).hexdigest()
    manifest = {"dataset": "BEIR/SciFact", "url": URL, "archive_sha256": SHA256,
                "published_md5": MD5, "license": "CC-BY-SA-4.0 (dataset card)", "files": hashes}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Verified and prepared {folder}")


if __name__ == "__main__":
    prepare()
