#!/usr/bin/env python3
"""Update RPR.001 and its dedicated template with verified improvement results."""
from __future__ import annotations

import argparse

from create_src005_process_assessment_package import (
    CONFLUENCE,
    REPORTS_REL,
    RPR001,
    RPR001_TEMPLATE_SLUG,
    RPR001_TEMPLATE_TITLE,
    TEMPLATES_REL,
    build_view,
    report_body,
    report_template_body,
)


def write(folder, title: str, storage: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "body.storage.xhtml").write_text(storage.strip() + "\n", encoding="utf-8")
    (folder / "body.view.html").write_text(build_view(title, storage.strip()), encoding="utf-8")


def verify(storage: str, *, template: bool) -> None:
    required = [
        "10. Doğrulanmış İyileştirme Sonuçları",
        "SRÇ.018 Gözden Geçirme Sonucu",
        "SRÇ.018 değişiklik gözden geçirmesi",
        "Etki",
        "Uygulama Önceliği",
        "Doğrulanmış Kazanım",
        "12. Sürüm Geçmişi",
    ]
    if not template:
        required.append("Henüz doğrulanmış tamamlanmış iyileştirme bulunmamaktadır.")
    missing = [item for item in required if item not in storage]
    if missing:
        raise RuntimeError(f"RPR.001 zorunlu iyileştirme içeriği eksik: {missing}")
    if "SUP.10.BP9" in storage:
        raise RuntimeError("RPR.001 kurumsal adlandırma yerine teknik SUP.10.BP9 ifadesi içeriyor")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update RPR.001 and/or its dedicated template")
    parser.add_argument("--template-only", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    if args.template_only and args.report_only:
        raise RuntimeError("--template-only ve --report-only birlikte kullanılamaz")

    template_storage = report_template_body()
    report_storage = report_body()
    verify(template_storage, template=True)
    verify(report_storage, template=False)

    template_folder = CONFLUENCE / TEMPLATES_REL / RPR001_TEMPLATE_SLUG
    report_folder = CONFLUENCE / REPORTS_REL / "iuc-bidb-rpr-001-surec-performanslari-raporu"
    if not args.report_only:
        write(template_folder, RPR001_TEMPLATE_TITLE, template_storage)
    if not args.template_only:
        write(report_folder, RPR001, report_storage)
    target = "RPR.001.Ş" if args.template_only else "RPR.001" if args.report_only else "RPR.001.Ş ve RPR.001"
    print(f"[PASS] {target} doğrulanmış iyileştirme sonuçları yapısıyla güncellendi.")


if __name__ == "__main__":
    main()
