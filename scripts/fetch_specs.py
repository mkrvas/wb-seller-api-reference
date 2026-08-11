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
ATTEMPTS = 3                 # попыток на спеку
MIN_SIZE_RATIO = 0.7         # ниже этой доли от прошлого размера считаем обрезкой


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
    """Headed-Chromium с общей вкладкой на все спеки.

    Ленивый: браузер поднимается только когда HTTP-ступень не справилась.

    Тело спеки берётся НЕ из DOM, а через `fetch()` внутри страницы. Читать
    отрендеренный `<pre>` нельзя: для крупных спек рендер отстаёт от загрузки,
    и текст обрывается на полуслове. YAML при этом остаётся синтаксически
    валидным (обрыв попадает внутрь многострочного скаляра), `paths` на месте,
    и is_valid_spec такой огрызок пропускает — 01-general так похудела с 1742
    строк до 1007, потеряв components.examples и components.responses.
    Вкладка нужна ровно для одного: пройти челлендж и получить куку, дальше
    работает сетевой стек браузера.
    """

    def __init__(self):
        self._pw = None
        self._browser = None
        self._ctx = None
        self._page = None
        self._warm = False

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
        self._page = self._ctx.new_page()

    def _fetch_in_page(self, url):
        """Скачать URL сетевым стеком браузера, минуя рендеринг."""
        return self._page.evaluate(
            """async (u) => {
                const r = await fetch(u, {credentials: 'include'});
                return {status: r.status, body: await r.text()};
            }""",
            url,
        )

    def _pass_challenge(self, url):
        """Открыть URL вкладкой и дождаться, пока анти-бот пропустит."""
        self._page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        deadline = time.monotonic() + CHALLENGE_TIMEOUT_S
        while time.monotonic() < deadline:
            self._page.wait_for_timeout(CHALLENGE_POLL_S * 1000)
            try:
                if self._fetch_in_page(url)["status"] == 200:
                    self._warm = True
                    return True
            except Exception:
                continue    # страница ещё на челлендже — fetch оттуда не живёт
        return False

    def fetch(self, url):
        self._ensure()
        for attempt in range(1, ATTEMPTS + 1):
            try:
                if not self._warm and not self._pass_challenge(url):
                    print(f"  playwright: попытка {attempt}/{ATTEMPTS} — "
                          f"челлендж не пройден за {CHALLENGE_TIMEOUT_S} с",
                          file=sys.stderr)
                    continue
                r = self._fetch_in_page(url)
                if r["status"] == 200 and is_valid_spec(r["body"]):
                    return r["body"]
                print(f"  playwright: попытка {attempt}/{ATTEMPTS} — статус "
                      f"{r['status']}, {len(r['body'])} байт, начало "
                      f"{r['body'][:80]!r}", file=sys.stderr)
                self._warm = False   # куку могли отозвать — идём за новой
            except Exception as e:
                print(f"  playwright: попытка {attempt}/{ATTEMPTS} — "
                      f"{type(e).__name__}: {e}", file=sys.stderr)
                self._warm = False
        return None

    def close(self):
        for obj, meth in ((self._browser, "close"), (self._pw, "stop")):
            if obj is not None:
                try:
                    getattr(obj, meth)()
                except Exception:
                    pass
        self._pw = self._browser = self._ctx = None


def shrink_error(name, text, out_dir):
    """Спека резко похудела — вероятнее обрезка при скачивании, чем правка WB.

    is_valid_spec такое не ловит: обрыв внутри многострочного скаляра оставляет
    YAML синтаксически валидным и с `paths` на месте. Молча записать огрызок
    в справочник хуже, чем упасть.
    """
    prev = out_dir / f"{name}.yaml"
    if not prev.exists():
        return None
    old = len(prev.read_text(encoding="utf-8"))
    new = len(text)
    if old and new < old * MIN_SIZE_RATIO:
        return (f"ОШИБКА: {name} ужалась {old} -> {new} символов "
                f"(порог {MIN_SIZE_RATIO:.0%}) — похоже на обрезку при "
                f"скачивании. Если WB действительно урезал спеку, обнови "
                f"specs/{name}.yaml вручную.")
    return None


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
            err = shrink_error(name, text, Path(args.out))
            if err:
                sys.exit(f"{err} {args.out}/ не тронут")
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
