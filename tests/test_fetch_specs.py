import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_specs import is_valid_spec, shrink_error


def test_valid_spec_passes():
    text = "openapi: 3.0.1\ninfo:\n  title: Тест\npaths:\n  /a:\n    get: {}\n"
    assert is_valid_spec(text)


def test_html_challenge_page_fails():
    assert not is_valid_spec("<!DOCTYPE html><html>challenge</html>")


def test_empty_and_none_fail():
    assert not is_valid_spec("")
    assert not is_valid_spec(None)


def test_yaml_without_paths_fails():
    assert not is_valid_spec("openapi: 3.0.1\ninfo: {}\n")


def test_broken_yaml_fails():
    assert not is_valid_spec("openapi: 3.0.1\npaths: [unclosed")


def test_truncated_spec_still_passes_validation(tmp_path):
    """Обрыв внутри многострочного скаляра оставляет YAML валидным.

    Именно поэтому нужен отдельный страж по размеру: на этом 01-general
    молча похудела вдвое и уехала в PR.
    """
    truncated = "openapi: 3.0.1\npaths:\n  /a:\n    get:\n      description: |\n        Стати"
    assert is_valid_spec(truncated)


def test_shrink_error_catches_truncation(tmp_path):
    (tmp_path / "01-general.yaml").write_text("x" * 1000, encoding="utf-8")
    err = shrink_error("01-general", "x" * 400, tmp_path)
    assert err and "ужалась" in err


def test_shrink_error_allows_normal_edit(tmp_path):
    (tmp_path / "01-general.yaml").write_text("x" * 1000, encoding="utf-8")
    assert shrink_error("01-general", "x" * 900, tmp_path) is None


def test_shrink_error_allows_growth(tmp_path):
    (tmp_path / "01-general.yaml").write_text("x" * 1000, encoding="utf-8")
    assert shrink_error("01-general", "x" * 5000, tmp_path) is None


def test_shrink_error_skips_new_spec(tmp_path):
    assert shrink_error("14-brand-new", "openapi: 3.0.1\npaths: {}\n", tmp_path) is None
