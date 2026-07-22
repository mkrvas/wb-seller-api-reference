import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_drift import diff_rows, main, rows_dict

OLD = {("GET", "/a"): ("старое описание", False), ("POST", "/b"): ("б", False)}
NEW = {("GET", "/a"): ("новое описание", False), ("GET", "/c"): ("ц", False)}


def test_diff_rows():
    d = diff_rows(OLD, NEW)
    assert d["added"] == [("GET", "/c")]
    assert d["removed"] == [("POST", "/b")]
    assert d["changed"] == [("GET", "/a")]


def test_diff_rows_empty_old_means_all_added():
    d = diff_rows({}, NEW)
    assert len(d["added"]) == 2 and d["removed"] == [] and d["changed"] == []


def test_rows_dict_malformed_yaml_returns_none():
    assert rows_dict("openapi: 3.0.1\npaths: [unclosed") is None
    assert rows_dict("") == {}


def test_main_exits_when_specs_dir_missing(tmp_path, monkeypatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "mapping.yaml").write_text("specs: []\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code != 0
