#!/usr/bin/env python3
"""Скачивание официальных OpenAPI-спек WB Seller API.

Политика all-or-nothing: либо скачались и валидны ВСЕ спеки из mapping.yaml,
либо папка назначения не изменяется вообще.
Ступень 1 — HTTP с браузерными заголовками; ступень 2 — Playwright
(портал прикрыт анти-бот защитой).

Про анти-бота (замер 2026-08-10). С ~06.08.2026 портал отдаёт HTTP 498 на
ЛЮБОЙ путь, включая корень: `Server: wbaas`, тело — челлендж
`/__wbaas/challenges/antibot/`. Пройти его может только НЕ headless-браузер:
headless-shell крутится в цикле «Проверяем браузер» → «Подозрительная
активность» бесконечно (проверено 3 минуты), а headed отдаёт спеку за ~10 с.
Поэтому launch(headless=False) — на CI запускать под `xvfb-run -a`.
Контекст браузера один на все спеки: кука `x_wbaas_token` выдаётся один раз,
и повторно проходить челлендж на каждой спеке не нужно.
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

CHALLENGE_TIMEOUT_S = 90     # сколько ждём прохождения челленджа на одной странице
CHALLENGE_POLL_S = 2         # шаг опроса содержимого страницы
ATTEMPTS = 3                 # попыток на спеку (каждая — новая вкладка)


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


class SpecBrowser:
    """Headed-Chromium с общим контекстом на все спеки.

    Ленивый: браузер поднимается только когда HTTP-ступень не справилась.
    """

    def __init__(self):
        self._pw = None
        self._browser = None
        self._ctx = None

    def _ensure(self):
        if self._ctx is not None:
            return
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        # headless=False — обязательное условие прохождения челленджа WBaaS.
        self._browser = self._pw.chromium.launch(headless=False)
        self._ctx = self._browser.new_context(
            user_agent=HEADERS["User-Agent"], locale="ru-RU"
        )

    @staticmethod
    def _page_text(page):
        try:
            return page.inner_text("pre")
        except Exception:
            try:
                return page.inner_text("body")
            except Exception:
                return ""

    def fetch(self, url):
        self._ensure()
        for attempt in range(1, ATTEMPTS + 1):
            page = self._ctx.new_page()
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                status = resp.status if resp else None
                deadline = time.monotonic() + CHALLENGE_TIMEOUT_S
                text = ""
                while time.monotonic() < deadline:
                    text = self._page_text(page)
                    if is_valid_spec(text):
                        if attempt > 1 or status != 200:
                            print(f"  playwright: ок (попытка {attempt}, "
                                  f"первый статус {status})", file=sys.stderr)
                        return text
                    page.wait_for_timeout(CHALLENGE_POLL_S * 1000)
                head = " | ".join(text.split("\n"))[:160]
                print(f"  playwright: попытка {attempt}/{ATTEMPTS} не прошла "
                      f"(статус {status}), на странице: {head!r}", file=sys.stderr)
            except Exception as e:
                print(f"  playwright: попытка {attempt}/{ATTEMPTS} — "
                      f"{type(e).__name__}: {e}", file=sys.stderr)
            finally:
                page.close()
        return None

    def close(self):
        for obj, meth in ((self._browser, "close"), (self._pw, "stop")):
            if obj is not None:
                try:
                    getattr(obj, meth)()
                except Exception:
                    pass
        self._pw = self._browser = self._ctx = None


def fetch_one(url, browser):
    text = fetch_http(url)
    if is_valid_spec(text):
        return text
    print("  фолбэк: playwright", file=sys.stderr)
    return browser.fetch(url)


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
    browser = SpecBrowser()
    try:
        for name in names:
            url = mapping["base_url"].format(name=name)
            print(f"{name}: {url}", file=sys.stderr)
            text = fetch_one(url, browser)
            if text is None:
                sys.exit(f"ОШИБКА: {name} не скачалась или невалидна — {args.out}/ не тронут")
            (tmp / f"{name}.yaml").write_text(text, encoding="utf-8", newline="\n")
            time.sleep(1)
    finally:
        browser.close()

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    for f in sorted(tmp.glob("*.yaml")):
        shutil.copy(f, out / f.name)
    print(f"OK: {len(names)} спек -> {out}/", file=sys.stderr)


if __name__ == "__main__":
    main()
