from pathlib import Path

import yaml

from confluence_publisher import ConfluencePublisher


PROCESS_REGISTER_ROWS = [
    {
        "sequence_no": 1,
        "corporate_code": "İÜC.BİDB.SRÇ.001",
        "corporate_process_name": "Dokümantasyon Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 2,
        "corporate_code": "İÜC.BİDB.SRÇ.002",
        "corporate_process_name": "Kalite Güvencesi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 3,
        "corporate_code": "İÜC.BİDB.SRÇ.003",
        "corporate_process_name": "Doğrulama Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 4,
        "corporate_code": "İÜC.BİDB.SRÇ.004",
        "corporate_process_name": "Süreç Kurulumu Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 5,
        "corporate_code": "İÜC.BİDB.SRÇ.005",
        "corporate_process_name": "Süreç Değerlendirme Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 6,
        "corporate_code": "İÜC.BİDB.SRÇ.006",
        "corporate_process_name": "Süreç İyileştirme Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 7,
        "corporate_code": "İÜC.BİDB.SRÇ.007",
        "corporate_process_name": "Proje Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 8,
        "corporate_code": "İÜC.BİDB.SRÇ.008",
        "corporate_process_name": "Risk Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 9,
        "corporate_code": "İÜC.BİDB.SRÇ.009",
        "corporate_process_name": "Gereksinimlerin Toplanması Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 10,
        "corporate_code": "İÜC.BİDB.SRÇ.010",
        "corporate_process_name": "Yazılım Gereksinim Analizi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 11,
        "corporate_code": "İÜC.BİDB.SRÇ.011",
        "corporate_process_name": "Yazılım Tasarımı Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 12,
        "corporate_code": "İÜC.BİDB.SRÇ.012",
        "corporate_process_name": "Yazılım Geliştirme Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 13,
        "corporate_code": "İÜC.BİDB.SRÇ.013",
        "corporate_process_name": "Yazılım Entegrasyonu Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 14,
        "corporate_code": "İÜC.BİDB.SRÇ.014",
        "corporate_process_name": "Yazılım Test Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 15,
        "corporate_code": "İÜC.BİDB.SRÇ.015",
        "corporate_process_name": "Ürün Yayınlama / Sürüm Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 16,
        "corporate_code": "İÜC.BİDB.SRÇ.016",
        "corporate_process_name": "Yapılandırma Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 17,
        "corporate_code": "İÜC.BİDB.SRÇ.017",
        "corporate_process_name": "Problem Çözüm Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 18,
        "corporate_code": "İÜC.BİDB.SRÇ.018",
        "corporate_process_name": "Değişiklik Talebi Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 19,
        "corporate_code": "İÜC.BİDB.SRÇ.019",
        "corporate_process_name": "İnsan Kaynakları Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 20,
        "corporate_code": "İÜC.BİDB.SRÇ.020",
        "corporate_process_name": "Eğitim Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 21,
        "corporate_code": "İÜC.BİDB.SRÇ.021",
        "corporate_process_name": "Bilgi Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 22,
        "corporate_code": "İÜC.BİDB.SRÇ.022",
        "corporate_process_name": "Altyapı Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 23,
        "corporate_code": "İÜC.BİDB.SRÇ.023",
        "corporate_process_name": "Organizasyonel Yönetim Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 24,
        "corporate_code": "İÜC.BİDB.SRÇ.024",
        "corporate_process_name": "Kalite Yönetimi Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 25,
        "corporate_code": "İÜC.BİDB.SRÇ.025",
        "corporate_process_name": "Ölçüm Süreci",
        "status": "Planlandı",
    },
    {
        "sequence_no": 26,
        "corporate_code": "İÜC.BİDB.SRÇ.026",
        "corporate_process_name": "Denetim Süreci",
        "status": "Planlandı",
    },
]


REGISTER_DEFINITIONS = [
    {
        "code": "ROOT-00",
        "paragraph": "Bu sayfa, İÜC BİDB SPICE 2026 Level 3 çalışmasına ait genel bilgi kayıtlarını içerir.",
        "columns": [
            "Sıra No",
            "Bilgi Başlığı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-01",
        "paragraph": "Bu sayfa, İÜC BİDB süreç dokümanları için süreç kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Kurumsal Kod",
            "Kurumsal Süreç Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [
            [
                process["sequence_no"],
                process["corporate_code"],
                process["corporate_process_name"],
                process["status"],
                "",
            ]
            for process in PROCESS_REGISTER_ROWS
        ],
    },
    {
        "code": "ROOT-02",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan doküman, kayıt ve form şablonları için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Şablon Kodu",
            "Şablon Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-03",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan kayıt ve liste dokümanları için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Kayıt/Listesi Kodu",
            "Kayıt/Listesi Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-04",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan formlar için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Form Kodu",
            "Form Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-05",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan kılavuzlar için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Kılavuz Kodu",
            "Kılavuz Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-06",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan politika dokümanları için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Politika Kodu",
            "Politika Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-07",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan prosedür dokümanları için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Prosedür Kodu",
            "Prosedür Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-08",
        "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan plan dokümanları için kayıt tablosunu içerir.",
        "columns": [
            "Sıra No",
            "Plan Kodu",
            "Plan Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-90",
        "paragraph": "Bu sayfa, İÜC BİDB SPICE 2026 Level 3 denetim hazırlık çalışmalarına ait kayıtları içerir.",
        "columns": [
            "Sıra No",
            "Çalışma Kodu",
            "Çalışma Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
    {
        "code": "ROOT-91",
        "paragraph": "Bu sayfa, İÜC BİDB iç denetim çalışmalarına ait kayıtları içerir.",
        "columns": [
            "Sıra No",
            "Denetim Kodu",
            "Denetim Adı",
            "Durum",
            "Erişim Linki",
        ],
        "rows": [],
    },
]


def main():
    manifest_path = Path(__file__).resolve().parent.parent / "manifest.yaml"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    publisher = ConfluencePublisher()
    updated_registers = publisher.sync_registers(
        manifest,
        REGISTER_DEFINITIONS,
    )

    for register in updated_registers:
        print(f'[UPDATE] {register["code"]} Register')

    print("[DONE]")


if __name__ == "__main__":
    main()
