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
    try:
        spec = yaml.safe_load(spec_text)
    except yaml.YAMLError:
        return None
    return {(m, p): (s, d) for m, p, s, d in extract_rows(spec)}


def diff_rows(old, new):
    return {
        "added": sorted(k for k in new if k not in old),
        "removed": sorted(k for k in old if k not in new),
        "changed": sorted(k for k in new if k in old and new[k] != old[k]),
    }


def main():
    if not Path("specs").is_dir():
        print("ОШИБКА: папка specs/ не найдена — сначала запусти fetch_specs.py",
              file=sys.stderr)
        sys.exit(1)
    mapping = yaml.safe_load(Path("scripts/mapping.yaml").read_text(encoding="utf-8"))
    out = ["## Обновление официальных спек WB", ""]
    for s in mapping["specs"]:
        name = s["name"]
        new_file = Path("specs") / f"{name}.yaml"
        if not new_file.exists():
            continue
        old = rows_dict(head_version(f"specs/{name}.yaml"))
        new = rows_dict(new_file.read_text(encoding="utf-8"))
        if old is None or new is None:
            out.append(f"### {name}")
            out.append("⚠️ Спека не распарсилась — сравнение пропущено, проверь файл руками.")
            out.append("")
            continue
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
