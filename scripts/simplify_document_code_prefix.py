#!/usr/bin/env python3
"""Remove the redundant corporate prefix from visible document codes.

Technical directory slugs are intentionally preserved. Text artifacts, metadata,
generated viewer data, scripts, reports, and visible attachment filenames are
updated together so the local documentation remains internally consistent.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/document_code_prefix_simplification_report.md"
PLAIN_PREFIX = "İÜC" + ".BİDB."
PREFIX_VARIANTS = (
    PLAIN_PREFIX,
    unicodedata.normalize("NFD", PLAIN_PREFIX),
    "İ&Uuml;C" + ".BİDB.",
    "&#304;&Uuml;C" + ".BİDB.",
    "I&#775;&Uuml;C" + ".BI&#775;DB.",
)
TEXT_SUFFIXES = {
    ".conf", ".csv", ".html", ".ini", ".json", ".md", ".mmd", ".py",
    ".sh", ".toml", ".tsv", ".txt", ".xhtml", ".xml", ".yaml", ".yml",
}
SKIP_PARTS = {".git", ".venv", ".migration-inbox", "__pycache__"}


def replace_prefixes(value: str) -> tuple[str, int]:
    changed = value
    total = 0
    for prefix in PREFIX_VARIANTS:
        count = changed.count(prefix)
        if count:
            changed = changed.replace(prefix, "")
            total += count
    return changed, total


def candidates() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            result.append(path)
    return sorted(result)


def renamed_path(path: Path) -> Path:
    name, _ = replace_prefixes(path.name)
    return path.with_name(name)


def validate_yaml_and_title_collisions(transformed: dict[Path, str]) -> None:
    prospective_titles: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for path, content in transformed.items():
        if path.name not in {"page.yaml", "index.yaml"}:
            continue
        data = yaml.safe_load(content) or {}
        if path.name == "page.yaml":
            old_data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            title = str(data.get("title") or "")
            old_title = str(old_data.get("title") or "")
            if title:
                prospective_titles[title].append((old_title, path))

    collisions = []
    for title, items in prospective_titles.items():
        if len(items) > 1 and len({old for old, _ in items}) > 1:
            collisions.append((title, items))
    if collisions:
        details = "; ".join(
            f"{title}: {', '.join(str(path.relative_to(ROOT)) for _, path in items)}"
            for title, items in collisions
        )
        raise RuntimeError(f"Ön ek kaldırma yeni sayfa başlığı çakışması üretiyor: {details}")


def validate_json(transformed: dict[Path, str]) -> None:
    for path, content in transformed.items():
        if path.suffix.lower() == ".json":
            json.loads(content)


def write_report(changed: list[tuple[Path, int]], renamed: list[Path], dry_run: bool) -> None:
    by_area: dict[str, int] = defaultdict(int)
    for path, _ in changed:
        relative = path.relative_to(ROOT)
        by_area[relative.parts[0] if relative.parts else "."] += 1
    lines = [
        "# Doküman Kodu Ön Ek Sadeleştirme Raporu",
        "",
        f"Çalışma modu: {'DRY-RUN' if dry_run else 'YEREL UYGULAMA'}",
        "",
        f"- Değişen metin dosyası: {len(changed)}",
        f"- Kaldırılan ön ek kullanımı: {sum(count for _, count in changed)}",
        f"- Yeniden adlandırılan görünür ek dosyası: {len(renamed)}",
        "- Teknik `iuc-bidb-...` klasör slugları korunmuştur.",
        "- Confluence üzerinde herhangi bir değişiklik yapılmamıştır.",
        "",
        "## Alan Dağılımı",
        "",
    ]
    for area, count in sorted(by_area.items()):
        lines.append(f"- `{area}`: {count} dosya")
    if renamed:
        lines.extend(["", "## Yeni Ek Dosyası Adları", ""])
        lines.extend(f"- `{path.relative_to(ROOT)}`" for path in renamed)
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Doküman kodlarındaki kurumsal ön eki yerelde kaldır")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    transformed: dict[Path, str] = {}
    changed: list[tuple[Path, int]] = []
    for path in candidates():
        content = path.read_text(encoding="utf-8")
        updated, count = replace_prefixes(content)
        transformed[path] = updated
        if count:
            changed.append((path, count))

    validate_yaml_and_title_collisions(transformed)
    validate_json(transformed)

    rename_plan: list[tuple[Path, Path]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        target = renamed_path(path)
        if target != path:
            if target.exists():
                raise RuntimeError(f"Ek dosyası yeniden adlandırma çakışması: {target}")
            rename_plan.append((path, target))

    if not args.dry_run:
        for path, _ in changed:
            path.write_text(transformed[path], encoding="utf-8")
        for source, target in rename_plan:
            source.rename(target)

        leftovers = []
        for path in candidates():
            content = path.read_text(encoding="utf-8")
            if any(prefix in content for prefix in PREFIX_VARIANTS):
                leftovers.append(path)
        if leftovers:
            raise RuntimeError(
                "Ön ek kullanımı kalan dosyalar: "
                + ", ".join(str(path.relative_to(ROOT)) for path in leftovers[:20])
            )

    renamed = [target for _, target in rename_plan]
    write_report(changed, renamed, args.dry_run)
    print(
        f"[{'DRY-RUN' if args.dry_run else 'DONE'}] "
        f"{len(changed)} metin dosyası, {sum(count for _, count in changed)} kullanım, "
        f"{len(rename_plan)} ek dosyası"
    )


if __name__ == "__main__":
    main()
