import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_specs import is_valid_spec


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
