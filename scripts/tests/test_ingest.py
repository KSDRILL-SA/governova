"""Tests for the source-corpus extractor (`governova_ingest`).

Every fixture here is **synthetic**. The real corpus is third-party, gitignored, and
absent from CI (ADR-007 constraint 3), so a suite that depended on it would be a suite
that only ever ran on one machine. The one test that does touch the real corpus skips
itself when the corpus is not present.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from governova_ingest import (
    ExtractionError,
    extract_corpus,
    extract_document,
    extract_legacy_doc,
    extract_pdf,
    extract_text,
    source_documents,
)

_OLE2_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 24


def _build_pdf(text: str) -> bytes:
    """A minimal but structurally valid PDF carrying one line of text.

    Built by hand with a correct cross-reference table: pypdf rejects a PDF whose
    xref offsets are wrong, so the offsets are computed rather than hard-coded.
    """
    stream = f"BT /F1 12 Tf 20 120 Td ({text}) Tj ET".encode()
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 200]/Contents 4 0 R"
        b"/Resources<</Font<</F1 5 0 R>>>>>>",
        b"<</Length " + str(len(stream)).encode() + b">>stream\n" + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj" + body + b"endobj\n"
    xref_at = len(out)
    out += b"xref\n0 " + str(len(objects) + 1).encode() + b"\n0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += b"trailer<</Size " + str(len(objects) + 1).encode() + b"/Root 1 0 R>>\n"
    out += b"startxref\n" + str(xref_at).encode() + b"\n%%EOF\n"
    return bytes(out)


def _write_doc(path: Path, payload: bytes) -> Path:
    path.write_bytes(_OLE2_HEADER + payload)
    return path


# ─── PDF ─────────────────────────────────────────────────────────────────────


def test_extract_pdf_reads_page_text(tmp_path):
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(_build_pdf("GOVERNOVA INGEST PROBE"))
    assert extract_pdf(pdf) == "GOVERNOVA INGEST PROBE"


def test_extract_pdf_rejects_a_file_that_is_not_a_pdf(tmp_path):
    # The negative case: a readable file that is simply not a PDF must fail loudly
    # rather than yield empty text that looks like a document with no content.
    bad = tmp_path / "deck.pdf"
    bad.write_bytes(b"this is plainly not a PDF at all")
    with pytest.raises(ExtractionError, match="not readable as a PDF"):
        extract_pdf(bad)


# ─── Legacy .doc ─────────────────────────────────────────────────────────────


def test_extract_legacy_doc_reads_utf16_runs(tmp_path):
    payload = "A sentence of ordinary prose.".encode("utf-16-le")
    payload += b"\x00\x01\x02" * 8
    payload += "A second readable paragraph.".encode("utf-16-le")
    doc = _write_doc(tmp_path / "notes.doc", payload)
    assert extract_legacy_doc(doc) == "A sentence of ordinary prose.\nA second readable paragraph."


def test_extract_legacy_doc_falls_back_to_cp1252(tmp_path):
    # Not every .doc stores runs as UTF-16LE. Whichever decoding yields more text
    # wins, which is why guessing wrong is self-correcting rather than silent.
    doc = _write_doc(tmp_path / "old.doc", b"\x01\x02Single byte encoded prose runs here.\x00")
    assert extract_legacy_doc(doc) == "Single byte encoded prose runs here."


def test_extract_legacy_doc_rejects_a_docx(tmp_path):
    # `python-docx` cannot open a .doc and this cannot open a .docx. Saying which
    # one you actually have is the difference between a fixable error and a mystery.
    docx = tmp_path / "modern.doc"
    docx.write_bytes(b"PK\x03\x04" + b"\x00" * 40)
    with pytest.raises(ExtractionError, match="Open XML"):
        extract_legacy_doc(docx)


def test_extract_legacy_doc_rejects_a_non_ole2_file(tmp_path):
    plain = tmp_path / "plain.doc"
    plain.write_bytes(b"just some text pretending to be a Word document")
    with pytest.raises(ExtractionError, match="not an OLE2"):
        extract_legacy_doc(plain)


def test_short_runs_are_discarded_but_real_prose_is_kept(tmp_path):
    # The negative half of run filtering: field names and style ids are noise, and
    # a threshold that also dropped short headings would be a threshold set wrong.
    payload = b"\x01ab\x02cd\x03" + b"A heading here" + b"\x04ef\x05"
    doc = _write_doc(tmp_path / "mixed.doc", payload)
    assert extract_legacy_doc(doc) == "A heading here"


# ─── Dispatch, description, and corpus walking ───────────────────────────────


def test_extract_text_rejects_an_unsupported_extension(tmp_path):
    other = tmp_path / "notes.rtf"
    other.write_text("content", encoding="utf-8")
    with pytest.raises(ExtractionError, match="unsupported extension"):
        extract_text(other)


def test_extract_text_rejects_a_missing_file(tmp_path):
    with pytest.raises(ExtractionError, match="not a file"):
        extract_text(tmp_path / "absent.pdf")


def test_extraction_is_deterministic(tmp_path):
    # The property the whole module exists for: a conversion whose inputs shift
    # under it cannot be audited.
    doc = _write_doc(tmp_path / "stable.doc", "Repeatable prose content.".encode("utf-16-le"))
    first, second = extract_document(doc), extract_document(doc)
    assert first.digest == second.digest
    assert first.characters == second.characters == len("Repeatable prose content.")


def test_digest_changes_when_the_document_changes(tmp_path):
    a = _write_doc(tmp_path / "a.doc", "The first document body.".encode("utf-16-le"))
    b = _write_doc(tmp_path / "b.doc", "The second document body.".encode("utf-16-le"))
    assert extract_document(a).digest != extract_document(b).digest


def test_source_documents_are_sorted_and_filtered(tmp_path):
    _write_doc(tmp_path / "b.doc", "Bravo document body.".encode("utf-16-le"))
    (tmp_path / "a.pdf").write_bytes(_build_pdf("ALPHA"))
    (tmp_path / "ignored.rtf").write_text("skip me", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    assert [p.name for p in source_documents(tmp_path)] == ["a.pdf", "b.doc"]


def test_source_documents_rejects_a_non_directory(tmp_path):
    with pytest.raises(ExtractionError, match="not a directory"):
        source_documents(tmp_path / "nowhere")


def test_corpus_reports_an_unreadable_document_without_abandoning_the_run(tmp_path):
    (tmp_path / "good.pdf").write_bytes(_build_pdf("READABLE"))
    (tmp_path / "broken.doc").write_bytes(b"not an OLE2 container at all")
    results = {d.name: d for d in extract_corpus(tmp_path)}
    assert results["good.pdf"].characters > 0
    # Visible as zero characters in the summary rather than silently missing —
    # a corpus that quietly shrank is a conversion built on an unknown input set.
    assert results["broken.doc"].characters == 0
    assert results["broken.doc"].digest == ""


def test_empty_directory_yields_no_documents(tmp_path):
    assert extract_corpus(tmp_path) == []


# ─── The real corpus, when it happens to be present ──────────────────────────

_CORPUS = Path(__file__).resolve().parents[2] / "planning" / "SDLC&DBLC"


@pytest.mark.skipif(not _CORPUS.is_dir(), reason="source corpus is not committed (ADR-007 §3)")
def test_real_corpus_extracts_completely():
    documents = extract_corpus(_CORPUS)
    assert documents, "corpus directory present but held no supported documents"
    unreadable = [d.name for d in documents if not d.characters]
    assert unreadable == [], f"unreadable source documents: {unreadable}"
