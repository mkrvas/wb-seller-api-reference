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
