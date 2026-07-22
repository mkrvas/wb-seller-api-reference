import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generate_tables import apply_filters, extract_rows, process_file, render_table

SPEC = {
    "openapi": "3.0.1",
    "paths": {
        "/api/v1/b": {"post": {"summary": "Второй"}},
        "/api/v1/a": {
            "get": {"summary": "Первый | с палкой"},
            "delete": {"summary": "Удаление", "deprecated": True},
        },
        "/api/v1/c": {"get": {"description": "Из description\nвторая строка"}},
    },
}


def test_extract_rows_sorted_and_flags():
    assert extract_rows(SPEC) == [
        ("DELETE", "/api/v1/a", "Удаление", True),
        ("GET", "/api/v1/a", "Первый | с палкой", False),
        ("POST", "/api/v1/b", "Второй", False),
        ("GET", "/api/v1/c", "Из description", False),
    ]


def test_filters():
    rows = extract_rows(SPEC)
    only_a = apply_filters(rows, {"include_prefixes": ["/api/v1/a"]})
    assert {r[1] for r in only_a} == {"/api/v1/a"}
    no_a = apply_filters(rows, {"exclude_prefixes": ["/api/v1/a"]})
    assert {r[1] for r in no_a} == {"/api/v1/b", "/api/v1/c"}


def test_render_escapes_and_marks_deprecated():
    table = render_table(extract_rows(SPEC))
    assert "Первый \\| с палкой" in table
    assert "⚠️ deprecated" in table


def _make_repo(tmp_path):
    refs = tmp_path / "references"
    refs.mkdir()
    md = refs / "13-analytics.md"
    md.write_text(
        "РУЧНОЕ ДО\n"
        "<!-- AUTO:BEGIN spec=11-analytics section=endpoints -->\nстарьё\n<!-- AUTO:END -->\n"
        "РУЧНОЕ ПОСЛЕ: лимит 3 запр/мин\n",
        encoding="utf-8",
    )
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "11-analytics.yaml").write_text(
        yaml.safe_dump(SPEC, allow_unicode=True), encoding="utf-8"
    )
    mapping = {"specs": [{"name": "11-analytics",
                          "files": [{"path": "references/13-analytics.md"}]}]}
    return md, mapping, specs


def test_process_preserves_manual_zones_and_is_idempotent(tmp_path):
    md, mapping, specs = _make_repo(tmp_path)
    process_file(md, mapping, specs)
    first = md.read_bytes()
    text = first.decode("utf-8")
    assert "РУЧНОЕ ДО" in text
    assert "РУЧНОЕ ПОСЛЕ: лимит 3 запр/мин" in text
    assert "старьё" not in text
    assert "| GET | `/api/v1/a` |" in text
    process_file(md, mapping, specs)
    assert md.read_bytes() == first  # идемпотентность побайтово
