import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_drift import diff_rows

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
