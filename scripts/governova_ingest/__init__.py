"""Deterministic text extraction from a body of practice held outside the repository.

Phase 2 (ADR-007) converts established engineering practice into constitutional law.
The conversion is performed by hand — `protocols/practice-to-standard.md` records the
method — but it must be **reproducible**, and it cannot be reproducible if reading the
sources is a manual act nobody else can repeat.

Three constraints shape this module, and each one is a decision rather than a detail.

**The corpus is never committed.** It is third-party material, tens of megabytes of it,
and not ours to redistribute (ADR-007 constraint 3). So this tool takes a *path*: the
corpus lives outside the repository, `.gitignore` excludes the conventional location
explicitly, and nothing here writes into the source tree unless asked to.

**Extraction is deterministic.** The same document yields byte-identical text on every
run and every platform. A conversion whose inputs shift under it cannot be audited, and
the digest this module reports is what lets a later reader confirm they are reading what
the standard's author read — without either of them shipping the source.

**Extracted text is an input to writing, never an output of it.** What leaves this
module is working material. What reaches a constitution is a fresh statement in
Governova's own voice plus a `Grounded In` citation bounded at
`MAX_GROUNDED_IN_CHARS` (C0 §3.2 SR-7). Cite, never excerpt.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

# The printable set kept from a legacy binary document: visible ASCII plus the three
# whitespace characters that carry structure. Everything else in an OLE2 container is
# formatting, object tables, or padding.
_PRINTABLE = frozenset(chr(c) for c in range(0x20, 0x7F)) | {"\r", "\n", "\t"}

# A run shorter than this in a binary container is overwhelmingly a field name, a style
# id, or a coincidence — not prose. Eight is low enough to keep short real headings.
_MIN_RUN = 8

# OLE2 compound-file magic. Word 97-2003 `.doc` is an OLE2 container; `.docx` is a zip.
_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_ZIP_MAGIC = b"PK\x03\x04"

PDF_SUFFIXES = frozenset({".pdf"})
DOC_SUFFIXES = frozenset({".doc"})
SUPPORTED_SUFFIXES = PDF_SUFFIXES | DOC_SUFFIXES


class ExtractionError(RuntimeError):
    """A source document could not be read as the format its extension claims."""


@dataclass(frozen=True)
class Extracted:
    """One source document, reduced to text plus the digest that identifies it.

    `digest` is taken over the *extracted text*, never the source bytes. That is the
    deliberate choice: it can be published, compared, and cited without redistributing
    anything, and it is what makes a conversion reproducible by someone who holds the
    same source independently.
    """

    name: str
    suffix: str
    characters: int
    digest: str
    text: str


def _printable_runs(decoded: str, minimum: int = _MIN_RUN) -> str:
    """Keep runs of printable characters at least `minimum` long, in document order.

    Deliberately not a regex. Every quantifier in this repository is bounded — an
    unbounded one once cost 8.7 seconds on a single line — and the honest way to satisfy
    that rule here is to have no quantifier at all rather than to pick an arbitrary
    ceiling that would chop long paragraphs into fragments.
    """
    marked = "".join(ch if ch in _PRINTABLE else "\x00" for ch in decoded)
    return "\n".join(run for run in marked.split("\x00") if len(run) >= minimum)


def extract_pdf(path: Path) -> str:
    """Extract text from a PDF, page by page, in page order."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - exercised by the message, not CI
        raise ExtractionError(
            "PDF extraction needs the ingest extra — install `governova[ingest]`."
        ) from exc

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # pypdf raises a wide family for a malformed file
        raise ExtractionError(f"{path.name}: not readable as a PDF ({type(exc).__name__})") from exc
    return "\n".join(pages).strip()


def extract_legacy_doc(path: Path) -> str:
    """Extract text from a Word 97-2003 `.doc` — an OLE2 container, not a zip.

    `python-docx` cannot open these: it reads the Open XML `.docx` zip format, and a
    `.doc` predates it. Rather than parse the OLE2 directory structure, this recovers
    the text streams directly, which is enough for material that is being *read* rather
    than *re-rendered*.

    Two decodings are attempted because the encoding is not declared anywhere the caller
    can see: Word stores runs as UTF-16LE, but older and converted documents carry
    single-byte CP1252 runs instead. Both are tried and the one yielding more text wins.
    Guessing wrong produces near-empty output, so the comparison is a reliable
    discriminator rather than a heuristic.
    """
    raw = path.read_bytes()
    if raw.startswith(_ZIP_MAGIC):
        raise ExtractionError(
            f"{path.name}: this is Open XML (.docx) in a .doc extension — not an OLE2 document."
        )
    if not raw.startswith(_OLE2_MAGIC):
        raise ExtractionError(f"{path.name}: not an OLE2 (Word 97-2003) document.")

    wide = _printable_runs(raw.decode("utf-16-le", errors="ignore"))
    narrow = _printable_runs(raw.decode("cp1252", errors="ignore"))
    return (wide if len(wide) >= len(narrow) else narrow).strip()


def extract_text(path: Path) -> str:
    """Extract text from one source document, dispatching on its extension."""
    if not path.is_file():
        raise ExtractionError(f"{path}: not a file.")
    suffix = path.suffix.lower()
    if suffix in PDF_SUFFIXES:
        return extract_pdf(path)
    if suffix in DOC_SUFFIXES:
        return extract_legacy_doc(path)
    raise ExtractionError(
        f"{path.name}: unsupported extension {suffix!r} "
        f"(supported: {', '.join(sorted(SUPPORTED_SUFFIXES))})."
    )


def extract_document(path: Path) -> Extracted:
    """Extract one document and describe it."""
    text = extract_text(path)
    return Extracted(
        name=path.name,
        suffix=path.suffix.lower(),
        characters=len(text),
        digest=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        text=text,
    )


def source_documents(root: Path) -> list[Path]:
    """Every supported source document under `root`, in a stable order.

    Sorted by name rather than by filesystem order, which differs between platforms and
    would make the run non-reproducible for no benefit.
    """
    if not root.is_dir():
        raise ExtractionError(f"{root}: not a directory.")
    return sorted(
        (p for p in root.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES),
        key=lambda p: p.name,
    )


def extract_corpus(root: Path) -> list[Extracted]:
    """Extract every supported document under `root`, in stable name order.

    One unreadable document does not abandon the run — the remaining sources are still
    worth reading, and a corpus is usually mixed. The failure surfaces as an `Extracted`
    with zero characters, so it is visible in the summary rather than silently absent.
    """
    results: list[Extracted] = []
    for path in source_documents(root):
        try:
            results.append(extract_document(path))
        except ExtractionError:
            results.append(
                Extracted(
                    name=path.name,
                    suffix=path.suffix.lower(),
                    characters=0,
                    digest="",
                    text="",
                )
            )
    return results
