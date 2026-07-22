# План имплементации: автообновление справочника из OpenAPI-спек WB

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Конвейер автообновления таблиц эндпоинтов в references/*.md из официальных OpenAPI-спек dev.wildberries.ru через ежедневный GitHub Actions workflow с PR на ревью человеку.

**Architecture:** Три python-скрипта (fetch → generate → drift-report) + mapping.yaml как единый конфиг + маркеры AUTO-зон в md-файлах. Генератор переписывает только текст между маркерами; рукописные знания вне маркеров физически недостижимы для него. Workflow ночью качает спеки (двухступенчато: requests → Playwright), перегенерирует зоны и открывает PR при диффе.

**Tech Stack:** Python 3.12, requests, PyYAML, Playwright (только CI/фолбэк), pytest, GitHub Actions, peter-evans/create-pull-request.

**Spec:** `docs/design/2026-07-22-auto-update-design.md` — читать перед работой.

## Global Constraints

- Репозиторий: `C:\Users\Hohoho\.claude\skills\wb-api` (= github.com/mkrvas/wb-seller-api-reference), ветка `master`.
- Запускать python как `python3`. Зависимости ставить через `pip`.
- НИКАКИХ упоминаний сторонних SDK/зеркал и их авторов ни в коде, ни в доках, ни в коммитах. Единственный источник спек — официальный dev.wildberries.ru.
- Рукописный текст вне маркеров `AUTO:BEGIN`/`AUTO:END` не должен меняться ни одним скриптом (побайтово).
- Скачивание спек — политика all-or-nothing: не скачались все — папка `specs/` не тронута.
- Весь пользовательский контент (README, справочник, описания PR) — на русском.
- Коммиты завершать строкой `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Не пушить до Task 6 (там первый push всего пакета).

---

### Task 1: Каркас + fetch_specs.py

**Files:**
- Create: `scripts/mapping.yaml`
- Create: `scripts/fetch_specs.py`
- Create: `tests/test_fetch_specs.py`
- Create: `.gitignore`

**Interfaces:**
- Produces: `scripts/mapping.yaml` со схемой `{base_url: str, specs: [{name: str, files: [{path: str, include_prefixes?: [str], exclude_prefixes?: [str]}]}]}` — читают Task 2, 3.
- Produces: `fetch_specs.py --out specs [--only NAME]` — скачивает все спеки из mapping.yaml в `--out`.

- [ ] **Step 1: Создать .gitignore**

```gitignore
__pycache__/
.pytest_cache/
pr_body.md
```

- [ ] **Step 2: Создать scripts/mapping.yaml (черновой маппинг — файлы уточняет Task 4)**

```yaml
# Единый конфиг конвейера: откуда качать спеки и в какие файлы справочника
# раскладывать их эндпоинты. include/exclude_prefixes — фильтры по префиксу пути.
base_url: "https://dev.wildberries.ru/api/swagger/yaml/ru/{name}.yaml?region=ru"
specs:
  - name: 01-general
    files: [{path: references/00-overview.md}]
  - name: 02-items
    files: [{path: references/10-content.md}]
  - name: 03-orders-fbs
    files: [{path: references/11-marketplace.md}]
  - name: 04-orders-dbw
    files: [{path: references/22-orders-dbw.md}]
  - name: 05-orders-dbs
    files: [{path: references/23-orders-dbs.md}]
  - name: 06-in-store-pickup
    files: [{path: references/24-in-store-pickup.md}]
  - name: 07-orders-fbw
    files: [{path: references/11-marketplace.md}]
  - name: 08-promotion
    files: [{path: references/15-advertising.md}]
  - name: 09-communications
    files: [{path: references/16-feedbacks.md}]
  - name: 10-rates
    files: [{path: references/17-tariffs.md}]
  - name: 11-analytics
    files: [{path: references/13-analytics.md}]
  - name: 12-reports
    files: [{path: references/12-statistics.md}]
  - name: 13-finances
    files: [{path: references/12a-finance.md}]
  - name: 14-wbd
    files: [{path: references/25-wbd.md}]
```

- [ ] **Step 3: Написать падающий тест валидации**

`tests/test_fetch_specs.py`:

```python
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
```

- [ ] **Step 4: Запустить тест — убедиться, что падает**

Run: `cd "/c/Users/Hohoho/.claude/skills/wb-api" && python3 -m pip install pytest requests pyyaml -q && python3 -m pytest tests/test_fetch_specs.py -v`
Expected: FAIL / ERROR — `No module named 'fetch_specs'`.

- [ ] **Step 5: Написать scripts/fetch_specs.py**

```python
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
```

- [ ] **Step 6: Тесты зелёные, синтаксис**

Run: `python3 -m pytest tests/test_fetch_specs.py -v && python3 -m py_compile scripts/fetch_specs.py`
Expected: 5 passed.

- [ ] **Step 7: Живой зонд одной спеки**

Run: `python3 scripts/fetch_specs.py --out /tmp/wb-specs-probe --only 01-general && head -5 /tmp/wb-specs-probe/01-general.yaml`
Expected: файл начинается с `openapi:`. Если HTTP-ступень не прошла и Playwright не установлен: `python3 -m pip install playwright -q && python3 -m playwright install chromium`, повторить. Если имя `01-general` даёт 404 — свериться с фактическими именами категорий на dev.wildberries.ru/openapi и поправить `name:`-поля mapping.yaml (это ожидаемая точка коррекции: имена в mapping черновые).

- [ ] **Step 8: Commit**

```bash
git add .gitignore scripts/mapping.yaml scripts/fetch_specs.py tests/test_fetch_specs.py
git commit -m "feat: скачивалка официальных OpenAPI-спек (all-or-nothing, playwright-фолбэк)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: generate_tables.py — генератор авто-зон

**Files:**
- Create: `scripts/generate_tables.py`
- Create: `tests/test_generate_tables.py`

**Interfaces:**
- Consumes: `scripts/mapping.yaml` из Task 1.
- Produces: `extract_rows(spec: dict) -> list[tuple[str, str, str, bool]]` — (METHOD, path, summary, deprecated), сортировка по (path, method) — импортирует Task 3.
- Produces: `process_file(md_file: Path, mapping: dict, specs_dir) -> None`; CLI `python3 scripts/generate_tables.py [--specs specs --refs references]` и режим `--list NAME` (печать строк спеки — нужен Task 4 для маппинга).
- Формат маркера (точный, менять нельзя): `<!-- AUTO:BEGIN spec=<имя-спеки> section=endpoints -->` … `<!-- AUTO:END -->`.

- [ ] **Step 1: Написать падающие тесты**

`tests/test_generate_tables.py`:

```python
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
```

- [ ] **Step 2: Запустить — убедиться, что падают**

Run: `python3 -m pytest tests/test_generate_tables.py -v`
Expected: ERROR — `No module named 'generate_tables'`.

- [ ] **Step 3: Написать scripts/generate_tables.py**

```python
#!/usr/bin/env python3
"""Перегенерация авто-зон (таблиц эндпоинтов) в references/*.md из specs/*.yaml.

Меняется ТОЛЬКО текст между маркерами
<!-- AUTO:BEGIN spec=<имя> section=endpoints --> ... <!-- AUTO:END -->
Всё вне маркеров не читается и не пишется.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

MARKER_RE = re.compile(
    r"(?P<begin><!-- AUTO:BEGIN spec=(?P<spec>[\w-]+) section=endpoints -->)"
    r"(?P<body>.*?)"
    r"(?P<end><!-- AUTO:END -->)",
    re.S,
)
METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
MAX_SUMMARY = 120


def extract_rows(spec):
    """dict спеки -> отсортированный список (METHOD, path, summary, deprecated)."""
    rows = []
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method in METHODS:
            op = item.get(method)
            if not isinstance(op, dict):
                continue
            summary = (op.get("summary") or op.get("description") or "").strip()
            summary = summary.splitlines()[0].strip() if summary else ""
            if len(summary) > MAX_SUMMARY:
                summary = summary[: MAX_SUMMARY - 1] + "…"
            rows.append((method.upper(), path, summary, bool(op.get("deprecated"))))
    rows.sort(key=lambda r: (r[1], r[0]))
    return rows


def apply_filters(rows, rule):
    inc = rule.get("include_prefixes")
    exc = rule.get("exclude_prefixes") or []
    out = []
    for r in rows:
        if inc is not None and not any(r[1].startswith(p) for p in inc):
            continue
        if any(r[1].startswith(p) for p in exc):
            continue
        out.append(r)
    return out


def render_table(rows):
    if not rows:
        return "\n_(в спеке нет эндпоинтов для этого файла)_\n"
    lines = ["", "| Метод | Путь | Назначение |", "|---|---|---|"]
    for m, p, s, dep in rows:
        note = " ⚠️ deprecated" if dep else ""
        lines.append(f"| {m} | `{p}` | {s.replace('|', chr(92) + '|')}{note} |")
    lines.append("")
    return "\n".join(lines)


def _rule_for(mapping, spec_name, md_rel_path):
    for s in mapping["specs"]:
        if s["name"] != spec_name:
            continue
        for f in s.get("files", []):
            if f["path"] == md_rel_path:
                return f
    return None


def process_file(md_file, mapping, specs_dir):
    with md_file.open(encoding="utf-8", newline="") as f:
        text = f.read()
    posix = md_file.as_posix()
    rel = posix[posix.index("references/"):]

    def repl(m):
        spec_name = m.group("spec")
        rule = _rule_for(mapping, spec_name, rel)
        if rule is None:
            print(f"ВНИМАНИЕ: {rel}: маркер spec={spec_name} не описан в mapping.yaml",
                  file=sys.stderr)
            return m.group(0)
        spec_path = Path(specs_dir) / f"{spec_name}.yaml"
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        rows = apply_filters(extract_rows(spec), rule)
        return m.group("begin") + render_table(rows) + m.group("end")

    new = MARKER_RE.sub(repl, text)
    if new != text:
        with md_file.open("w", encoding="utf-8", newline="") as f:
            f.write(new)
        print(f"обновлён: {rel}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", default="specs")
    ap.add_argument("--refs", default="references")
    ap.add_argument("--list", help="показать извлечённые строки одной спеки и выйти")
    args = ap.parse_args()

    if args.list:
        spec_path = Path(args.specs) / f"{args.list}.yaml"
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        print(f"servers: {[s.get('url') for s in spec.get('servers', [])]}")
        for m, p, s, dep in extract_rows(spec):
            print(f"{m:7} {p}  {s}{'  [deprecated]' if dep else ''}")
        return

    mapping = yaml.safe_load(Path("scripts/mapping.yaml").read_text(encoding="utf-8"))
    for md_file in sorted(Path(args.refs).glob("*.md")):
        process_file(md_file, mapping, args.specs)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Тесты зелёные**

Run: `python3 -m pytest tests/test_generate_tables.py -v && python3 -m py_compile scripts/generate_tables.py`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_tables.py tests/test_generate_tables.py
git commit -m "feat: генератор авто-зон таблиц эндпоинтов из спек

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: check_drift.py — описание изменений для PR

**Files:**
- Create: `scripts/check_drift.py`
- Create: `tests/test_check_drift.py`

**Interfaces:**
- Consumes: `extract_rows` из `generate_tables` (Task 2), `scripts/mapping.yaml` (Task 1).
- Produces: `diff_rows(old: dict, new: dict) -> dict` с ключами added/removed/changed; CLI `python3 scripts/check_drift.py` печатает markdown-отчёт (HEAD vs рабочая копия specs/) в stdout — использует workflow Task 6.

- [ ] **Step 1: Падающий тест**

`tests/test_check_drift.py`:

```python
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
```

- [ ] **Step 2: Запустить — падает** (`No module named 'check_drift'`).

Run: `python3 -m pytest tests/test_check_drift.py -v`

- [ ] **Step 3: Написать scripts/check_drift.py**

```python
#!/usr/bin/env python3
"""Дифф спек (git HEAD vs рабочая копия specs/) -> markdown-отчёт для тела PR."""
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from generate_tables import extract_rows  # noqa: E402


def head_version(repo_path):
    r = subprocess.run(["git", "show", f"HEAD:{repo_path}"],
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def rows_dict(spec_text):
    if not spec_text:
        return {}
    return {(m, p): (s, d) for m, p, s, d in extract_rows(yaml.safe_load(spec_text))}


def diff_rows(old, new):
    return {
        "added": sorted(k for k in new if k not in old),
        "removed": sorted(k for k in old if k not in new),
        "changed": sorted(k for k in new if k in old and new[k] != old[k]),
    }


def main():
    mapping = yaml.safe_load(Path("scripts/mapping.yaml").read_text(encoding="utf-8"))
    out = ["## Обновление официальных спек WB", ""]
    for s in mapping["specs"]:
        name = s["name"]
        new_file = Path("specs") / f"{name}.yaml"
        if not new_file.exists():
            continue
        old = rows_dict(head_version(f"specs/{name}.yaml"))
        new = rows_dict(new_file.read_text(encoding="utf-8"))
        if old == new:
            continue
        out.append(f"### {name}")
        if not old:
            out.append(f"Первичное заполнение: {len(new)} эндпоинтов.")
        d = diff_rows(old, new)
        for title, keys in (("Новые", d["added"]), ("Удалены", d["removed"]),
                            ("Изменены описания", d["changed"])):
            if keys and old:
                out.append(f"**{title}:**")
                out += [f"- `{m} {p}`" for m, p in keys]
        out.append("")
    if len(out) == 2:
        out.append("Набор эндпоинтов не изменился (правки в описаниях/служебных частях спек).")
    out.append("_Проверь глазами: рукописные примечания под изменёнными таблицами"
               " могли устареть._")
    print("\n".join(out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Тесты зелёные**

Run: `python3 -m pytest tests/ -v && python3 -m py_compile scripts/check_drift.py`
Expected: все тесты (Task 1–3) passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/check_drift.py tests/test_check_drift.py
git commit -m "feat: drift-отчёт изменений спек для описания PR

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Скачать все спеки, финализировать маппинг, разметить существующие файлы

Это самая содержательная задача — здесь спеки встречаются с рукописным справочником. Работать вдумчиво, файл за файлом.

**Files:**
- Create: `specs/*.yaml` (все категории из mapping.yaml)
- Modify: `scripts/mapping.yaml` (финальный маппинг: сверенные имена, фильтры путей)
- Modify: `references/*.md` — существующие 13 файлов семейств (вставка AUTO-зон)

**Interfaces:**
- Consumes: `fetch_specs.py` (Task 1), `generate_tables.py --list` и `process_file` (Task 2).
- Produces: размеченные файлы и финальный mapping.yaml — на них опираются Task 5, 6.

- [ ] **Step 1: Скачать все спеки**

Run: `python3 scripts/fetch_specs.py --out specs && ls specs/`
Expected: по одному yaml на каждую запись mapping.yaml. Если какие-то имена дали 404 — открыть dev.wildberries.ru/openapi в браузере, выписать фактические имена категорий, поправить `name:` в mapping.yaml, повторить. ЗАФИКСИРОВАТЬ коммитом сразу: `git add specs scripts/mapping.yaml && git commit -m "feat: снапшот официальных спек" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"`.

- [ ] **Step 2: Изучить содержимое спек и финализировать маппинг**

Для каждой спеки: `python3 scripts/generate_tables.py --list <имя>` — смотреть servers и пути. Сверить с существующими файлами справочника (в каком md-файле сейчас описаны эти пути). Правила решения:
- Хост спеки совпадает с хостом в шапке md-файла → спека кормит этот файл.
- Одна спека покрывает эндпоинты из двух файлов справочника (кандидаты: 02-items ↔ content+prices; 08-promotion ↔ advertising+calendar; 09-communications ↔ feedbacks+chat) → две записи в `files:` с `include_prefixes`/`exclude_prefixes` по фактическим префиксам путей. Фильтры обязаны разбивать множество путей БЕЗ пересечений и БЕЗ потерь (каждый путь спеки попадает ровно в один файл).
- Эндпоинты returns (19) и documents (20) искать по всем спекам через `--list | grep -i`; не нашлись — файлы остаются полностью ручными, в mapping их не включать.
- Обновить mapping.yaml до финального вида.

- [ ] **Step 3: Разметить существующие файлы AUTO-зонами**

Для каждого файла из mapping.yaml (существующие 13; новые 22–25 делает Task 5): вставить пару маркеров вокруг места, где сейчас живут таблицы эндпоинтов. Порядок работы с одним файлом:
1. Прочитать файл целиком.
2. Вставить `<!-- AUTO:BEGIN spec=<имя> section=endpoints -->` / `<!-- AUTO:END -->` вместо существующих таблиц эндпоинтов (маркеры пустые внутри — заполнит генератор).
3. Всю рукописную фактуру из старых таблиц, которой нет в авто-колонках (колонки «Тело запроса», «Тип: асинхронный», пометки «АКТУАЛЬНАЯ», зачёркнутые отключённые эндпоинты с датами) — перенести ТЕКСТОМ в примечания сразу под зоной. Ничего не выбрасывать: правило — старый файл содержал факт → новый файл содержит тот же факт (в таблице или в примечании).
4. Разделы файла, не являющиеся таблицами эндпоинтов (rate limits, грабли, примеры) — не трогать вообще.

- [ ] **Step 4: Прогнать генератор и сверить глазами**

Run: `python3 scripts/generate_tables.py && git diff --stat`
Затем для минимум трёх файлов (обязательно 13-analytics.md — воронка) построчно сверить `git diff`: таблицы заполнились, пути совпадают с тем, что было в справочнике, рукописные разделы не изменились. Расхождение таблиц со старым справочником — норма, если новые данные из спеки (это и есть смысл конвейера), но КАЖДОЕ расхождение осмыслить: спека права или фильтр маппинга кривой?

- [ ] **Step 5: Контроль сохранности знаний**

Run (все обязаны найтись):
```bash
grep -l "3 запр/мин" references/13-analytics.md
grep -l "асинхрон" references/13-analytics.md
grep -l "09.12.2025" references/13-analytics.md
python3 -m pytest tests/ -v
```
Expected: файлы находятся, тесты зелёные. Повторный прогон `python3 scripts/generate_tables.py && git diff --quiet references/ && echo IDEMPOTENT` печатает IDEMPOTENT (после первого прогона diff уже застейджен — сравнивать рабочую копию с собой повторным запуском: второй запуск не меняет файлы).

- [ ] **Step 6: Commit**

```bash
git add scripts/mapping.yaml references/
git commit -m "feat: авто-зоны в существующих файлах справочника, финальный маппинг

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Новые семейства (DBW, DBS, самовывоз, WBD) + SKILL.md + README

**Files:**
- Create: `references/22-orders-dbw.md`, `references/23-orders-dbs.md`, `references/24-in-store-pickup.md`, `references/25-wbd.md`
- Modify: `SKILL.md` (таблица навигации)
- Modify: `README.md` (структура + раздел про автообновление)

**Interfaces:**
- Consumes: mapping.yaml и генератор из Task 2/4; хосты брать из `--list` (строка servers).

- [ ] **Step 1: Создать четыре файла по шаблону**

Шаблон (подставить имя спеки, заголовок, хост из `python3 scripts/generate_tables.py --list <имя>`; пример для 22-orders-dbw.md):

```markdown
# Orders DBW — заказы с доставкой силами WB

## Назначение

Раздел добавлен автоконвейером: таблица ниже генерируется из официальной
спеки. Рукописные заметки (лимиты, грабли) наполняются по мере боевого
использования — пока считать файл справочным, не боевым.

**Хост:** `<из servers спеки>`

## Эндпоинты

<!-- AUTO:BEGIN spec=04-orders-dbw section=endpoints -->
<!-- AUTO:END -->
```

- [ ] **Step 2: Прогнать генератор, проверить заполнение**

Run: `python3 scripts/generate_tables.py && grep -c "^| " references/22-orders-dbw.md references/23-orders-dbs.md references/24-in-store-pickup.md references/25-wbd.md`
Expected: в каждом файле больше 1 строки таблицы.

- [ ] **Step 3: Обновить SKILL.md**

В таблицу «Семейства API» добавить четыре строки (по образцу существующих):

```markdown
| [22-orders-dbw.md](references/22-orders-dbw.md) | Orders DBW (доставка силами WB) | см. файл |
| [23-orders-dbs.md](references/23-orders-dbs.md) | Orders DBS (доставка продавцом) | см. файл |
| [24-in-store-pickup.md](references/24-in-store-pickup.md) | Самовывоз из магазина | см. файл |
| [25-wbd.md](references/25-wbd.md) | WBD (Wildberries Digital) | см. файл |
```

(«см. файл» заменить фактическими хостами из спек.)

- [ ] **Step 4: Обновить README.md**

В таблицу «Структура» добавить те же четыре файла. После раздела «Уровень детализации» добавить раздел:

```markdown
## Автообновление

Таблицы эндпоинтов между маркерами `<!-- AUTO:BEGIN ... -->` / `<!-- AUTO:END -->`
генерируются из официальных OpenAPI-спек `dev.wildberries.ru` (снапшот — в
[specs/](specs/)). GitHub Actions ежедневно скачивает свежие спеки и, если WB
что-то поменял, открывает PR с перегенерированными таблицами и списком
изменений — мерж делает человек. Рукописные заметки (лимиты, грабли, даты
отключений) живут вне маркеров, генератор их не касается.

Обновить локальную копию скилла: `git pull` в папке скилла.
```

- [ ] **Step 5: Проверка и Commit**

Run: `python3 scripts/generate_tables.py && git diff --quiet references/ && echo IDEMPOTENT && python3 -m pytest tests/ -q`
Expected: IDEMPOTENT, тесты зелёные.

```bash
git add references/2*.md SKILL.md README.md
git commit -m "feat: семейства DBW/DBS/самовывоз/WBD, навигация, раздел про автообновление

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Workflow update.yml, push, живой прогон

**Files:**
- Create: `.github/workflows/update.yml`

**Interfaces:**
- Consumes: все три скрипта и mapping.yaml.

- [ ] **Step 1: Создать .github/workflows/update.yml**

```yaml
name: update-specs
on:
  schedule:
    - cron: "30 3 * * *"   # ежедневно 03:30 UTC
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Установка зависимостей
        run: |
          pip install -q requests pyyaml playwright
          python -m playwright install --with-deps chromium

      - name: Скачивание спек (all-or-nothing)
        run: python scripts/fetch_specs.py --out specs

      - name: Перегенерация авто-зон
        run: python scripts/generate_tables.py

      - name: Дифф и описание PR
        id: drift
        run: |
          python scripts/check_drift.py > pr_body.md
          if git diff --quiet; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi
          echo "date=$(date -u +%Y-%m-%d)" >> "$GITHUB_OUTPUT"

      - name: PR с обновлением
        if: steps.drift.outputs.changed == 'true'
        uses: peter-evans/create-pull-request@v6
        with:
          branch: auto/spec-update-${{ steps.drift.outputs.date }}
          title: "Спеки WB обновились — ${{ steps.drift.outputs.date }}"
          body-path: pr_body.md
          commit-message: "auto: обновление снапшота спек и таблиц эндпоинтов"
          add-paths: |
            specs/
            references/
          delete-branch: true
```

- [ ] **Step 2: Финальный локальный прогон перед пушем**

Run: `python3 -m pytest tests/ -q && python3 -m py_compile scripts/*.py && git status --short`
Expected: тесты зелёные, рабочая директория чистая (всё закоммичено), незакоммиченным остаётся только update.yml.

- [ ] **Step 3: Commit + push**

```bash
git add .github/workflows/update.yml
git commit -m "ci: ежедневное автообновление спек с PR на ревью

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push origin master
```

- [ ] **Step 4: Живой прогон workflow (happy path)**

Run: `gh workflow run update-specs --repo mkrvas/wb-seller-api-reference && sleep 30 && gh run list --repo mkrvas/wb-seller-api-reference --workflow update-specs --limit 1`
Дождаться завершения: `gh run watch --repo mkrvas/wb-seller-api-reference <run-id>`.
Expected: зелёный. PR скорее всего НЕ создан (спеки не изменились с Task 4) — это правильно; в логе шага «Дифф» должно быть changed=false.

- [ ] **Step 5: Живой прогон пути с PR (синтетический дрифт)**

Симулировать изменение WB: локально удалить из `specs/14-wbd.yaml` последний путь (блок одного эндпоинта в `paths:`), прогнать `python3 scripts/generate_tables.py`, закоммитить (`git commit -am "test: синтетический дрифт для проверки PR" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"`), запушить, запустить workflow ещё раз. Fetch восстановит реальную спеку → дифф непустой → должен появиться PR.
Run: `gh pr list --repo mkrvas/wb-seller-api-reference`
Expected: PR `auto/spec-update-<дата>` с телом из check_drift (упоминает 14-wbd). Смержить его: `gh pr merge --repo mkrvas/wb-seller-api-reference <номер> --squash`, затем `git pull`. Итог: спека восстановлена, механика PR доказана боем.

---

### Task 7: Финальная приёмка по критериям спеки

**Files:** только проверки, новых файлов нет (кроме возможных фиксов).

- [ ] **Step 1: Прогнать все критерии приёмки из дизайна**

```bash
python3 -m pytest tests/ -v                                  # 1, 4, 5
python3 -m py_compile scripts/*.py                           # 1
python3 scripts/generate_tables.py && git diff --quiet && echo IDEMPOTENT   # 4
grep -riE "esl[a]zarev|wildberries[-]sdk|raw\.githubusercont[e]nt" -r . --exclude-dir=.git && echo "ПРОВАЛ" || echo "ЧИСТО"   # 7 (скобки в паттерне — чтобы grep не ловил сам себя в этом плане)
grep -rE "eyJ[A-Za-z0-9_-]{20,}" --exclude-dir=.git -r . && echo "ПРОВАЛ: токен" || echo "СЕКРЕТОВ НЕТ"   # 7
```
Expected: тесты зелёные, IDEMPOTENT, ЧИСТО, СЕКРЕТОВ НЕТ. Критерии 2, 3, 6 уже закрыты живыми прогонами в Task 4 и Task 6 — перепроверить, что они отмечены в этом плане выполненными.

- [ ] **Step 2: Финальный push и сверка с GitHub**

```bash
git push origin master
gh repo view mkrvas/wb-seller-api-reference --web
```
Убедиться в браузере: README отображает раздел «Автообновление», в Actions есть зелёный запуск update-specs, вкладка PR пустая (тестовый смержен).

- [ ] **Step 3: Обновить память проекта**

В `C:\Users\Hohoho\.claude\projects\...\memory\` обновить/создать заметку о репо wb-seller-api-reference: конвейер автообновления работает, где лежит mapping.yaml, как дебажить красный workflow (см. риски в дизайне). Добавить строку в MEMORY.md.

---

## Self-Review (выполнен при написании плана)

- Покрытие спеки: цели 1–4 → Task 1–3 (конвейер), Task 4 (защита рукописного, маппинг), Task 5 (новые категории), Task 6 (PR-цикл), критерии приёмки → Task 7. Пробелов не нашёл.
- Заглушки: имена категорий спек и фильтры маппинга намеренно финализируются по живым данным в Task 1 (Step 7) и Task 4 (Step 2) — это отражено в самой спеке дизайна, не заглушка.
- Согласованность типов: `extract_rows` -> `(METHOD, path, summary, deprecated)` — одинаково в Task 2 (определение), Task 3 (импорт), тестах.
