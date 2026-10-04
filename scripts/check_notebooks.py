"""Validate and run each lesson in a fresh kernel; leave checked-in files unchanged."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
notebooks = sorted((ROOT / "notebooks" / "foundations").glob("*.ipynb"))
if not notebooks:
    raise SystemExit("No foundation notebooks found")

for path in notebooks:
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    ).execute()
    count = sum(cell.cell_type == "code" for cell in notebook.cells)
    print(f"PASS {path.name}: {count} code cells")
