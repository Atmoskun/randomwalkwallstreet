import os
from pathlib import Path
from pypdf import PdfReader

# Base directory of the project (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# All documents must live under the "data" folder at the project root
DATA_DIR = (BASE_DIR / "data").resolve()


def _assert_under_data(path: Path) -> None:
    """
    Safety check: ensure the file is inside the DATA_DIR.
    Prevents reading random files on the server (path traversal attack prevention).
    """
    real = path.resolve()
    if not str(real).startswith(str(DATA_DIR)):
        raise PermissionError(f"Access to path outside data directory is not allowed: {real}")


def build_doc_path(filename: str) -> Path:
    """
    Map a filename like 'Amazon_2020Q1.txt' to DATA_DIR / filename.
    """
    path = (DATA_DIR / filename).resolve()
    _assert_under_data(path)
    return path


def read_text_from_path(path: Path) -> str:
    """
    Read text content from a .txt or .pdf file.
    """
    _assert_under_data(path)

    if not path.exists():
        raise FileNotFoundError(str(path))

    ext = path.suffix.lower()

    if ext == ".txt":
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == ".pdf":
        reader = PdfReader(str(path))
        chunks = []
        # Attempt to extract text from each page
        for page in reader.pages:
            try:
                # Use .extract_text() and default to empty string if extraction fails
                chunks.append(page.extract_text() or "")
            except Exception:
                chunks.append("")
        return "\n".join(chunks)

    raise ValueError(f"Unsupported file type: {ext}")