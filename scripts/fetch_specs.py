#!/usr/bin/env python3
"""Скачивание официальных OpenAPI-спек WB Seller API.

Политика all-or-nothing: либо скачались и валидны ВСЕ спеки из mapping.yaml,
либо папка назначения не изменяется вообще.
Ступень 1 — HTTP с браузерными заголовками; ступень 2 — headless Playwright
(портал прикрыт анти-бот защитой).
"""
import argparse
import shutil
import sys
import tempfile
import time
from pathlib import Path

import requests
import yaml

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/yaml,text/plain,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def load_mapping(path="scripts/mapping.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_valid_spec(text):
    if not text or not text.lstrip().startswith("openapi:"):
        return False
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return False
    return isinstance(doc, dict) and "paths" in doc


def fetch_http(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
    except requests.RequestException as e:
        print(f"  http: {e}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"  http: status {resp.status_code}", file=sys.stderr)
        return None
    resp.encoding = "utf-8"
    return resp.text


def fetch_playwright(url):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(5_000)  # даём JS-защите отработать
        try:
            text = page.inner_text("pre")
        except Exception:
            text = page.inner_text("body")
        browser.close()
    return text


def fetch_one(url):
    text = fetch_http(url)
    if is_valid_spec(text):
        return text
    print("  фолбэк: playwright", file=sys.stderr)
    try:
        text = fetch_playwright(url)
    except Exception as e:
        print(f"  playwright: {e}", file=sys.stderr)
        return None
    return text if is_valid_spec(text) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="specs")
    ap.add_argument("--only", help="скачать одну спеку по имени (для отладки)")
    args = ap.parse_args()

    mapping = load_mapping()
    names = [s["name"] for s in mapping["specs"]]
    if args.only:
        names = [n for n in names if n == args.only]
        if not names:
            sys.exit(f"нет спеки с именем {args.only} в mapping.yaml")

    tmp = Path(tempfile.mkdtemp(prefix="wb-specs-"))
    for name in names:
        url = mapping["base_url"].format(name=name)
        print(f"{name}: {url}", file=sys.stderr)
        text = fetch_one(url)
        if text is None:
            sys.exit(f"ОШИБКА: {name} не скачалась или невалидна — {args.out}/ не тронут")
        (tmp / f"{name}.yaml").write_text(text, encoding="utf-8", newline="\n")
        time.sleep(1)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    for f in sorted(tmp.glob("*.yaml")):
        shutil.copy(f, out / f.name)
    print(f"OK: {len(names)} спек -> {out}/", file=sys.stderr)


if __name__ == "__main__":
    main()
