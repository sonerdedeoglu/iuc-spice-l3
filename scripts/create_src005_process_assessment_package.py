#!/usr/bin/env python3
"""Create the local SRÇ.005 package and its shared plan/report artifacts.

This script is local-only. It does not call Confluence APIs. Existing page ids are
preserved; new pages are materialized with empty ids for a later reviewed publish.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import yaml

from rework_src004_process_establishment import CSS, e, p, table


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE = ROOT / "confluence"
PAGE_ROOT_REL = "pages/000-root-iuc-bidb-spice-2026-level-3"
PAGE_ROOT = CONFLUENCE / PAGE_ROOT_REL
INDEX_PATH = CONFLUENCE / "index.yaml"

ROOT_ID = "137265781"
TEMPLATES_ID = "137265785"
PROCEDURES_ID = "137265790"
PLANS_ID = "137265791"
REVIEWS_ID = "137265917"
SRC005_ID = "137265863"

PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
PROCESS_OWNER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
REVIEWED_BY = "Levent Bayezit - Proje Yöneticisi"
APPROVED_BY = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

SRC005 = "İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci"
PRS003 = "İÜC.BİDB.PRS.003 - Süreç Değerlendirme Prosedürü"
PRS004 = "İÜC.BİDB.PRS.004 - Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü"
PLN001 = "İÜC.BİDB.PLN.001 - Süreç Kalite Planı"
RPR001 = "İÜC.BİDB.RPR.001 - Süreç Performansları Raporu"
PLN001_TEMPLATE_CODE = "İÜC.BİDB.PLN.001.Ş"
PLN001_TEMPLATE_TITLE = "İÜC.BİDB.PLN.001.Ş - Süreç Kalite Planı Şablonu"
PLN001_TEMPLATE_SLUG = "iuc-bidb-pln-001-s-surec-kalite-plani-sablonu"
PLN002_TEMPLATE_CODE = "İÜC.BİDB.PLN.002.Ş"
PLN002_TEMPLATE_TITLE = "İÜC.BİDB.PLN.002.Ş - Süreç İyileştirme Planı Şablonu"
RPR001_TEMPLATE_CODE = "İÜC.BİDB.RPR.001.Ş"
RPR001_TEMPLATE_TITLE = "İÜC.BİDB.RPR.001.Ş - Süreç Performansları Raporu Şablonu"
RPR001_TEMPLATE_SLUG = "iuc-bidb-rpr-001-s-surec-performanslari-raporu-sablonu"
LST006 = "İÜC.BİDB.LST.006 - Standart Süreç Envanteri"
FRM001_ASSESSMENT = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.XXX) - Değerlendirme #1"
PROCESS_PACKAGE = (
    "İÜC.BİDB.SRÇ.XXX - [Süreç Adı]; "
    "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.XXX); "
    "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.XXX); "
    "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.XXX); "
    "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.XXX)"
)

SRC005_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/iuc-bidb-src-005-surec-degerlendirme-sureci"
TEMPLATES_REL = f"{PAGE_ROOT_REL}/02-sablonlar"
PROCEDURES_REL = f"{PAGE_ROOT_REL}/07-prosedurler"
PLANS_REL = f"{PAGE_ROOT_REL}/08-planlar"
REPORTS_REL = f"{PAGE_ROOT_REL}/09-raporlar"
REVIEWS_REL = f"{PAGE_ROOT_REL}/91-ic-denetimler/surec-gozden-gecirmeleri"

FLOW_PNG = "İÜC.BİDB.SRÇ.005 - Flowchart.png"
FLOW_MMD = "src005-surec-akisi.mmd"
INTERACTION_PNG = "src005-surec-etkilesim.png"
INTERACTION_MMD = "src005-surec-etkilesim.mmd"

LABELS = [
    ("YOK", "Beklentiyi karşılayan tanım veya kullanılabilir kanıt bulunmuyor."),
    ("ZAYIF", "Başlangıç düzeyinde tanım veya kanıt var; uygulama yeterli değil."),
    ("DAĞINIK", "Kanıt var; ancak sistematik, tutarlı veya tamamlanmış değil."),
    ("VAR", "Beklenti yeterli, tutarlı ve izlenebilir biçimde karşılanıyor."),
    ("KAPSAM DIŞI", "Beklenti değerlendirme bağlamında uygulanmıyor."),
]

PIM2_BPS = [
    ("PIM.2.BP1", "Değerlendirme hedeflerini tanımla", "Kurumsal iş hedeflerine dayalı değerlendirme hedeflerini ve başarı ölçütlerini belirlemek ve doğrulamak."),
    ("PIM.2.BP2", "Değerlendirmeyi planla", "Değerlendirme yaklaşımını, kapsamını, zamanlamasını ve kayıtlarını planlamak."),
    ("PIM.2.BP3", "Taahhüt al", "Değerlendirme sponsoru ve değerlendirilecek birimlerle takvim ve kaynak taahhüdü sağlamak."),
    ("PIM.2.BP4", "Değerlendirmeyi gerçekleştir ve veri topla", "Kapsamdaki süreçleri değerlendirmek için gerekli tanım ve kanıt verilerini toplamak."),
    ("PIM.2.BP5", "Değerlendirme verisini doğrula", "Toplanan verinin değerlendirme hedefini yeterince kapsadığını ve doğru yorumlandığını doğrulamak."),
    ("PIM.2.BP6", "Değerlendirme verisini analiz et", "Doğrulanan veriyi süreçlerin güçlü ve zayıf yönlerini anlamak üzere analiz etmek."),
    ("PIM.2.BP7", "Değerlendirme sonuçlarını raporla", "Planlanan değerlendirme çıktılarını değerlendirme sponsoruna ve ilgili taraflara raporlamak."),
    ("PIM.2.BP8", "Değerlendirme kaydını sürdür", "Güncel ve doğru değerlendirme sonuçlarını erişilebilir yer ve biçimde saklamak ve sürdürmek."),
]

GPS = [
    ("PA 2.1", "GP.2.1.1", "Süreç performansı hedeflerini belirleme"),
    ("PA 2.1", "GP.2.1.2", "Süreç performansını planlama ve izleme"),
    ("PA 2.1", "GP.2.1.3", "Süreç performansını ayarlama"),
    ("PA 2.1", "GP.2.1.4", "Sorumluluk ve yetkileri tanımlama"),
    ("PA 2.1", "GP.2.1.5", "Kaynakları belirleme ve kullanıma sunma"),
    ("PA 2.1", "GP.2.1.6", "İlgili taraflar arasındaki arayüzleri yönetme"),
    ("PA 2.2", "GP.2.2.1", "İş ürünü gereksinimlerini tanımlama"),
    ("PA 2.2", "GP.2.2.2", "İş ürünlerinin dokümantasyon ve kontrol gereksinimlerini tanımlama"),
    ("PA 2.2", "GP.2.2.3", "İş ürünlerini belirleme, belgeleme ve kontrol etme"),
    ("PA 2.2", "GP.2.2.4", "İş ürünlerini gözden geçirme ve düzenleme"),
    ("PA 3.1", "GP.3.1.1", "Tanımlı süreci destekleyecek standart süreci tanımlama"),
    ("PA 3.1", "GP.3.1.2", "Süreç sırası ve etkileşimlerini belirleme"),
    ("PA 3.1", "GP.3.1.3", "Rol ve yetkinlikleri belirleme"),
    ("PA 3.1", "GP.3.1.4", "Altyapı ve çalışma ortamını belirleme"),
    ("PA 3.1", "GP.3.1.5", "Etkinlik ve uygunluk izleme yöntemlerini belirleme"),
    ("PA 3.2", "GP.3.2.1", "Bağlama uygun tanımlı süreci devreye alma"),
    ("PA 3.2", "GP.3.2.2", "Rol, sorumluluk ve yetkileri atama ve duyurma"),
    ("PA 3.2", "GP.3.2.3", "Gerekli yetkinlikleri sağlama"),
    ("PA 3.2", "GP.3.2.4", "Kaynak ve bilgiyi sağlama"),
    ("PA 3.2", "GP.3.2.5", "Yeterli süreç altyapısını sağlama"),
    ("PA 3.2", "GP.3.2.6", "Performans verisini toplama ve analiz etme"),
]


def build_view(title: str, body: str) -> str:
    css = CSS + ".diagram{max-width:100%;height:auto;border:1px solid #c9d1d9;border-radius:6px;margin:16px 0}.note{background:#f6f8fa;border-left:4px solid #0c66e4;padding:10px 14px}"
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{css}</style></head><body><main class="confluence-page"><h1>{e(title)}</h1>{body}</main></body></html>'''


def metadata(page_dir: Path, title: str, parent_id: str, parent_title: str, depth: int) -> dict:
    meta_path = page_dir / "page.yaml"
    current = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {} if meta_path.exists() else {}
    rel = str(page_dir.relative_to(CONFLUENCE)).replace("\\", "/")
    current.update({
        "space": "SSSS", "title": title, "parent_id": parent_id, "parent_title": parent_title,
        "depth": depth, "status": "active", "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": current.get("children_count", 0), "relative_path": rel, "slug": page_dir.name,
        "has_view_html": True, "view_file": "body.view.html", "storage_file": "body.storage.xhtml",
    })
    current.setdefault("page_id", "")
    current.setdefault("version", "")
    current.setdefault("url", "")
    return current


def write_page(page_dir: Path, title: str, parent_id: str, parent_title: str, depth: int, storage: str, view: str | None = None) -> None:
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "body.storage.xhtml").write_text(storage.strip() + "\n", encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, (view or storage).strip()), encoding="utf-8")
    (page_dir / "page.yaml").write_text(yaml.safe_dump(metadata(page_dir, title, parent_id, parent_title, depth), allow_unicode=True, sort_keys=False), encoding="utf-8")


def history(name: str, reviewer: str = REVIEWED_BY, approver: str = APPROVED_BY, draft_only: bool = False) -> str:
    rows = [["v0.1", "10 Jan 2025", "İlk taslak oluşturuldu.", PREPARED_BY, "-", "-"]]
    if not draft_only:
        rows.append(["v1.0", "15 Feb 2025", f"{name} onaylanarak yürürlüğe girmiştir.", PREPARED_BY, reviewer, approver])
    return table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], rows)


def info_macro(title: str, lines: list[str]) -> str:
    codes = "<br />".join(f'<code class="language-mermaid">{e(line)}</code>' for line in lines)
    return f'<ac:structured-macro ac:name="info" ac:schema-version="1"><ac:parameter ac:name="icon">false</ac:parameter><ac:parameter ac:name="title">{e(title)}</ac:parameter><ac:rich-text-body><p style="margin-left:40px">{codes}</p></ac:rich-text-body></ac:structured-macro>'


def info_view(title: str, lines: list[str]) -> str:
    codes = "<br />".join(f'<code class="language-mermaid">{e(line)}</code>' for line in lines)
    return f'<div class="confluence-information-macro has-no-icon confluence-information-macro-information"><p class="title"><strong>{e(title)}</strong></p><div class="confluence-information-macro-body"><p style="margin-left:40px">{codes}</p></div></div>'


FLOW_LINES = [
    "flowchart TD",
    "A[Yıllık takvim veya değerlendirme tetikleyicisi] --> B[Değerlendirme hedefi ve kapsamı belirlenir]",
    "B --> C[Süreç sahibi ve ilgili taraflarla takvim ve kaynaklar netleştirilir]",
    "C --> D[BP ve PA/GP için mevcut tanım ve kanıtlar toplanır]",
    "D --> E[Değerlendirme verileri doğrulanır]",
    "E --> F[Veriler analiz edilir ve etiketler atanır]",
    "F --> G[Bulgular sınıflandırılır]",
    "G --> H{Bulgu türü}",
    "H -- Uygunsuzluk --> I[SRÇ.017 üzerinden düzeltici ve iyileştirici faaliyet]",
    "H -- İyileştirme fırsatı --> J[SRÇ.018'e aktarım]",
    "H -- Gözlem veya güçlü uygulama --> K[Değerlendirme kaydında izleme]",
    "I --> L[Sonuçlar gözden geçirilir ve onaylanır]",
    "J --> L",
    "K --> L",
    "L --> M[Değerlendirme kaydı ve RPR.001 güncellenir]",
]

INTERACTION_LINES = [
    "flowchart LR",
    "PLN[PLN.001 Süreç Kalite Planı] --> SRC[SRÇ.005 Süreç Değerlendirme]",
    "SET[LST.006 ve süreç paketleri] --> SRC",
    "AUD[SRÇ.026 Denetim sonuçları] --> SRC",
    "SRC --> FRM[FRM.001 Değerlendirme Kaydı]",
    "FRM --> RPR[RPR.001 Süreç Performansları Raporu]",
    "FRM --> PRB[SRÇ.017 Uygunsuzluklar]",
    "FRM --> CHG[SRÇ.018 İyileştirme fırsatları]",
    "RPR --> QA[SRÇ.002 Kalite Güvencesi]",
    "RPR --> IMP[SRÇ.006 Süreç İyileştirme]",
]


def process_body(view: bool = False) -> str:
    related = "<br />".join([
        "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci",
        "İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci",
        "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci",
        "İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci",
        "İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci",
        "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "İÜC.BİDB.SRÇ.025 - Ölçüm Süreci",
        "İÜC.BİDB.SRÇ.026 - Denetim Süreci",
    ])
    image = (f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(FLOW_PNG)}" alt="{e(SRC005)} süreç akışı" /></p>' if view else f'<p><ac:image ac:width="1000"><ri:attachment ri:filename="{e(FLOW_PNG)}" /></ac:image></p>')
    mermaid = info_view("Mermaid Kodu", FLOW_LINES) if view else info_macro("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "Değerlendirme hedeflerini belirle", "Kurumsal hedeflerle uyumlu değerlendirme amacı, kapsamı ve başarı ölçütleri belirlenir. (PIM.2.BP1)", f"{PLN001}; değerlendirme kapsamı"],
        ["F2", "Değerlendirmeyi planla", "Yıllık yaklaşım, dönem, roller, kullanılacak yöntem ve kayıtlar belirlenir. (PIM.2.BP2)", PLN001],
        ["F3", "Taahhüt ve katılımı sağla", "Süreç sahibi, kanıt sahipleri, gözden geçiren ve onaylayan ile takvim ve kaynaklar netleştirilir. (PIM.2.BP3)", "Mutabık kalınan değerlendirme kapsamı ve takvimi"],
        ["F4", "Değerlendirmeyi gerçekleştir", "İlgili tüm BP'ler ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 göstergeleri için mevcut tanım ve kanıtlar toplanır. (PIM.2.BP4)", "FRM.001 değerlendirme kaydı; mevcut kanıt bağlantıları"],
        ["F5", "Değerlendirme verisini doğrula", "Toplanan verinin kapsamı, güncelliği, doğruluğu ve hedefi karşılama yeterliliği kontrol edilir. (PIM.2.BP5)", "Doğrulanmış değerlendirme verisi"],
        ["F6", "Veriyi analiz et ve etiketle", "Her BP ve GP için YOK, ZAYIF, DAĞINIK, VAR veya KAPSAM DIŞI etiketi atanır; tek bir toplam süreç puanı üretilmez. (PIM.2.BP6)", "Etiket dağılımı; güçlü ve zayıf yönler"],
        ["F7", "Sonuçları raporla ve yönlendir", "Bulgular sınıflandırılır; uygunsuzluklar SRÇ.017'ye, iyileştirme fırsatları SRÇ.018'e yönlendirilir ve kümülatif rapor güncellenir. (PIM.2.BP7)", f"{RPR001}; bulgu yönlendirmeleri"],
        ["F8", "Değerlendirme kaydını sürdür", "Gözden geçirilen ve onaylanan değerlendirme kaydı erişilebilir konumda tutulur; aynı değerlendirme kaydı çalışma boyunca güncellenir. (PIM.2.BP8)", "FRM.001 Değerlendirme kaydı; değerlendirme bağlantısı"],
    ]
    parts = [
        "<h2>1. Süreç Bilgileri</h2>",
        table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", SRC005], ["Süreç Referansı", "ISO/IEC 15504-5:2006 PIM.2 - Process assessment"],
            ["Süreç Sahibi", PROCESS_OWNER],
            ["Hedef Kitle", "Süreç sahipleri, kanıt sahipleri, Kalite Danışmanı, gözden geçirenler, onaylayanlar ve süreç iyileştirme rolleri"],
            ["Yayın ve Erişim Ortamı", "Confluence ve Google Drive; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"],
            ["Son Gözden Geçirme Tarihi", "14-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya önemli süreç değişikliği ya da denetim bulgusu oluştuğunda"],
        ]),
        "<h2>2. Amaç</h2>",
        p("Bu sürecin amacı, İÜC BİDB standart süreçlerinin kurumsal hedeflere katkısını belirlemek, göreli güçlü ve zayıf yönlerini görünür kılmak ve sürekli süreç iyileştirmesinin odaklarını belirlemektir."),
        "<h3>2.1. Süreç Sonuçları</h3>",
        table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Standart süreçlerin belirli proje, hizmet veya kurumsal bağlamlardaki kullanımına ilişkin bilgi ve veriler oluşturulur ve sürdürülür."],
            ["S2", "Kurumsal standart süreçlerin göreli güçlü ve zayıf yönleri anlaşılır."],
            ["S3", "Doğru, güncel ve erişilebilir değerlendirme kayıtları tutulur ve sürdürülür."],
        ]),
        "<h2>3. Kapsam</h2>",
        table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "LST.006 içinde tanımlanan güncel standart süreç setinin iç süreç değerlendirmeleri; ilgili sürecin tüm BP'leri ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 genel uygulamaları; mevcut tanım, kayıt ve kanıtların incelenmesi; bulguların sınıflandırılması, yönlendirilmesi ve raporlanması"],
            ["Kapsam Dışı", "Resmî veya dış değerlendirmeler ve kurumsal denetim faaliyetleri; bunlar SRÇ.026 - Denetim Süreci kapsamında yürütülür. İlk yürürlüğe alma sırasında zorunlu değerlendirme yapılması ve ayrı bir GAP analizi kaydı oluşturulması da bu kapsamda değildir."],
            ["Uygulama Alanı", "İÜC BİDB standart süreç seti ve bu süreçlerin kullanımına ilişkin kurumsal kayıtlar"],
        ]),
        "<h2>4. Referanslar</h2>",
        table(["Referans", "Açıklama"], [
            ["ISO/IEC 15504-5:2006 PIM.2 - Process assessment", "Süreç amacı, sonuçları, BP1-BP8 temel uygulamaları ve ilişkili iş ürünleri"],
            ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"],
        ]),
        "<h2>5. Terimler ve Kısaltmalar</h2>",
        table(["Terim / Kısaltma", "Açıklama"], [
            ["PIM.2", "ISO/IEC 15504-5 içindeki Process assessment süreci"],
            ["BP", "Base Practice; sürecin amacını ve sonuçlarını gerçekleştirmesi beklenen temel uygulama"],
            ["PA / GP", "Process Attribute / Generic Practice; sürecin yönetim, iş ürünü, tanım ve yaygınlaştırma yeteneğini değerlendiren göstergeler"],
            ["Değerlendirme kaydı", "BP ve GP bazındaki etiket, açıklama, mevcut kanıt ve tamamlayıcı aksiyon bilgilerinin tutulduğu doldurulmuş FRM.001"],
            ["Kanıt", "İlgili beklentiyi destekleyen süreç tanımı, doküman, kayıt, bağlantı, sistem verisi veya gözlemlenebilir uygulama"],
        ]),
        "<h2>6. Süreç Aktivitesi</h2>",
        table(["Alan", "Açıklama"], [
            ["Süreç Başlatıcısı", "Yıllık Süreç Kalite Planı; önemli süreç değişikliği veya denetim bulgusu sonrasında ihtiyaç duyulan ek değerlendirme"],
            ["Süreç Başlangıcı", "Değerlendirme hedefi, kapsamı ve ilgili sürecin belirlenmesi"],
            ["Süreç Bitişi", "BP ve GP kapsamının tamamlanması; mevcut kanıtların kaydedilmesi; bulguların sınıflandırılıp yönlendirilmesi; sonucun gözden geçirilmesi, onaylanması ve RPR.001'e işlenmesi"],
            ["Ana Faaliyetler", "Hedef belirleme; planlama; taahhüt sağlama; veri toplama; doğrulama; analiz ve etiketleme; raporlama ve yönlendirme; kayıtların sürdürülmesi"],
            ["İlgili Süreçler", related],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>", p("Bu süreç kapsamındaki rol, sorumluluk, yetki, yetkinlik ve RACI bilgileri İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.005) dokümanında yönetilir."),
        "<h2>8. Araçlar ve Altyapı</h2>",
        table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "Süreç tanımları, değerlendirme kayıtları, plan, rapor ve ilişkili dokümanların yayımlanması", "Kurumsal hesap ve atanmış okuma/yazma yetkisi; uzaktan erişimde VPN", "Proje Geliştirme Yönetimi / Confluence Yöneticisi"],
            ["Altyapı", "Google Drive", "Değerlendirme ekleri, destekleyici kanıtlar ve kontrollü dosyaların saklanması", "Kurumsal hesap ve rol bazlı klasör yetkisi", "Repository Sorumlusu"],
            ["Araç", "Jira", "Bulgu, uygunsuzluk, iyileştirme fırsatı ve ilgili aksiyon bağlantılarının izlenmesi", "Proje veya süreç bazlı yetkilendirme", "İlgili Süreç Sahibi / Jira Yöneticisi"],
            ["Araç", "Bitbucket", "Sürüm kontrollü dokümantasyon kaynakları, otomasyon ve değişiklik geçmişinin yönetilmesi", "Repository yetkisi ve tanımlı değişiklik kuralları", "Proje Geliştirme Yönetimi / Bitbucket Yöneticisi"],
            ["İletişim", "Kurumsal e-posta", "Değerlendirme takvimi, katılım, gözden geçirme ve sonuç bilgilendirmeleri", "Kurumsal hesap ve ilgili dağıtım listeleri", "Süreç Sahibi / Kalite Danışmanı"],
            ["Altyapı", "İÜC VPN ve kurumsal kimlik altyapısı", "Kurum dışından kayıt ve kanıt sistemlerine güvenli erişim", "Geçerli hesap, VPN yetkisi ve bilgi güvenliği kuralları", "İÜC BİDB Altyapı ve Erişim Yönetimi"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", p("Sürecin girdi ve çıktı iş ürünleri ile bunların kalite kriterleri İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.005) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", image + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities),
        "<h2>12. Ölçüm ve İzleme</h2>", p("Az sayıda yönetilebilir performans ölçümü İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.005) dokümanında tanımlanır. Gerçekleşen sonuçlar değerlendirme kayıtları ve RPR.001 içinde raporlanır; ayrı bir takip registerı oluşturulmaz."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Değerlendirme Dönemi</h3>" + p("Planlı süreç değerlendirmeleri her yılın ilk üç ayına yayılır. Önemli süreç değişikliği veya denetim bulgusu oluştuğunda ihtiyaç bazlı ek değerlendirme yapılabilir. Sürecin ilk yürürlüğe alınması zorunlu bir değerlendirme tetikleyicisi değildir."),
        "<h3>13.2. Değerlendirme Kapsamı</h3>" + p("Her değerlendirmede ilgili ISO/IEC 15504-5 sürecinin tüm BP'leri ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 göstergeleri ele alınır. Gerçek kanıt bulunması ön koşul değildir; mevcut kanıt kullanılır, eksiklik açıklanır ve uygun etiket atanır."),
        "<h3>13.3. Etiketleme ve Sonuçlandırma</h3>" + p("Yalnızca YOK, ZAYIF, DAĞINIK, VAR ve KAPSAM DIŞI etiketleri kullanılır. Sayısal puan ve tek bir toplam süreç etiketi üretilmez. Sonuç, etiket dağılımları, kritik bulgular ve güçlü uygulamalarla özetlenir."),
        "<h3>13.4. Bulgu Yönlendirme</h3>" + p("Uygunsuzluklar önce SRÇ.017 - Problem Çözüm Yönetimi üzerinden düzeltici ve iyileştirici faaliyete dönüştürülür; çözüm gerektirirse SRÇ.018'e aktarılır. İyileştirme fırsatları doğrudan SRÇ.018'e aktarılır. Gözlemler değerlendirme kaydında izlenir; güçlü uygulamalar korunma ve yaygınlaştırma önerisiyle kaydedilir."),
        "<h3>13.5. Uyarlama Kuralları</h3>",
        table(["Kural", "Açıklama"], [
            ["Zorunlu Adımlar", "Tüm BP ve tanımlı PA/GP kapsamı değerlendirilir; mevcut kanıt ve açıklamalar kaydedilir; bulgular sınıflandırılır; değerlendirme gözden geçirilip onaylanır."],
            ["Uyarlanabilir Adımlar", "Görüşme yöntemi, kanıt toplama sırası, oturum sayısı ve değerlendirme süresi; sürecin karmaşıklığı ve kanıt erişimine göre uyarlanabilir."],
            ["Onay Gerektiren Durumlar", "Değerlendirme kapsamından bir BP veya GP'nin çıkarılması, KAPSAM DIŞI kararı ya da yıllık takvimde önemli değişiklik yapılması süreç sahibi onayı gerektirir."],
        ]),
        "<h2>14. Süreç Etkileşimleri</h2>", p("Sürecin diğer süreç ve dokümanlarla girdi/çıktı etkileşimleri İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.005) dokümanında yönetilir."),
        "<h2>15. Sürüm Geçmişi</h2>", history("Süreç Değerlendirme Süreci"),
    ]
    return "".join(parts)


def lst007_body(view: bool = False) -> str:
    image = (f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(INTERACTION_PNG)}" alt="SRÇ.005 süreç etkileşim diyagramı" /></p>' if view else f'<p><ac:image ac:width="1000"><ri:attachment ri:filename="{INTERACTION_PNG}" /></ac:image></p>')
    mermaid = info_view("Mermaid Kodu", INTERACTION_LINES) if view else info_macro("Mermaid Kodu", INTERACTION_LINES)
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC005], ["Kullanım Amacı", "SRÇ.005'in süreç ve doküman arayüzlerini, girdilerini ve çıktı yönlendirmelerini tanımlamak"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Girdi", "Değerlendirmenin başlatılması veya yürütülmesi için kullanılan süreç, plan, kayıt ya da kanıt"], ["Çıktı", "Değerlendirme sonucunda oluşan kayıt, rapor veya süreç yönlendirmesi"], ["Çift yönlü", "Bilgi, doğrulama veya geri bildirim alışverişi bulunan etkileşim"]]),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", image + mermaid,
        "<h2>4. Girdi Etkileşimleri Matrisi</h2>", table(["Kaynak Süreç / Doküman", "Etkileşim Türü", "Girdi / Bilgi", "Kayıt / Kanıt", "Açıklama"], [
            ["İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci", "Kalite planlama girdisi", "Kurumsal kalite hedefleri ve kalite yaklaşımı", PLN001, "Süreç değerlendirmelerinin kalite çerçevesini sağlar."],
            ["İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci", "Süreç varlığı girdisi", "Standart süreç tanımları, iş ürünleri, ölçümler, roller ve etkileşimler", "İlgili süreç paketi; LST.006", "Değerlendirilecek standart süreç temelini sağlar."],
            ["İÜC.BİDB.SRÇ.025 - Ölçüm Süreci", "Performans verisi girdisi", "Süreç performans ölçüm sonuçları", "Süreç özel LST.009 ve doğal kaynak kayıtları", "Etkinlik ve uygunluk değerlendirmesini destekler."],
            ["İÜC.BİDB.SRÇ.026 - Denetim Süreci", "Denetim girdisi", "Kurumsal denetim sonuçları ve bulguları", "Denetim raporları ve bulgu kayıtları", "İhtiyaç bazlı ek değerlendirmeyi tetikleyebilir."],
            [PLN001, "Plan girdisi", "Değerlendirme yaklaşımı, takvim, kriterler, roller ve tamamlanma ölçütleri", PLN001, "Yıllık süreç kalitesi değerlendirmesini yönlendirir."],
            ["İlgili süreç tanımı ve alt dokümanları", "Kanıt girdisi", "BP ve PA/GP'yi destekleyen tanım, kayıt ve bağlantılar", "SRÇ; LST.007-LST.010; FRM.001; doğal kaynak kayıtları", "Mevcut kanıt kadar kullanılır; eksiklik etiketle gösterilir."],
        ]),
        "<h2>5. Çıktı Etkileşimleri Matrisi</h2>", table(["Hedef Süreç / Doküman", "Etkileşim Türü", "Çıktı / Yönlendirme", "Kayıt / Kanıt", "Açıklama"], [
            ["İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Uygunsuzluk yönlendirmesi", "Uygunsuzluk ve düzeltici/iyileştirici faaliyet ihtiyacı", "FRM.001 bulgusu ve problem kaydı bağlantısı", "Uygunsuzluklar önce SRÇ.017 kapsamında ele alınır."],
            ["İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "İyileştirme yönlendirmesi", "İyileştirme fırsatı veya SRÇ.017 çözümünden doğan değişiklik ihtiyacı", "FRM.001 bulgusu ve değişiklik bağlantısı", "İyileştirme fırsatları doğrudan SRÇ.018'e aktarılır."],
            ["İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci", "İyileştirme girdisi", "Güçlü/zayıf yönler, etiket dağılımları ve iyileştirme odakları", RPR001, "Süreç iyileştirme önceliklerini destekler."],
            ["İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci", "Kalite raporlama çıktısı", "Süreç kalitesi sonuçları ve eğilimleri", RPR001, "Kalite yaklaşımının uygulanmasını ve gözden geçirilmesini destekler."],
            ["İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu", "Değerlendirme kaydı", "BP ve PA/GP etiketleri, kanıtlar, açıklamalar ve bulgular", "Değerlendirme Bağlantısı", "Doldurulmuş kayıt 91 - İç Denetimler / Süreç Gözden Geçirmeleri altında tutulur."],
            [RPR001, "Kümülatif rapor", "Tamamlanan süreçlerin sonuç özeti", RPR001, "Her süreç tamamlandığında aynı rapor güncellenir."],
        ]),
        "<h2>6. Etkileşim Notları</h2>", p("Resmî veya dış değerlendirmeler SRÇ.026 kapsamında kalır. SRÇ.005, bu sonuçları iç süreç değerlendirmesine girdi olarak kullanabilir. Ayrı bir değerlendirme takip registerı oluşturulmaz."),
        "<h2>7. Sürüm Geçmişi</h2>", history("SRÇ.005 Süreç Etkileşim Matrisi"),
    ])


def lst008_body() -> str:
    inputs = [
        [LST006, "Girdi", "Değerlendirilecek süreç kimliği, referansı ve sahipliği", "Güncel ve onaylı süreç satırı; süreç kodu ve referansı tutarlı", "Zorunlu", "PIM.2.BP1-BP2"],
        [PLN001, "Girdi", "Değerlendirme yaklaşımı, yıllık takvim, kapsam, roller ve ölçütler", "Yürürlükteki plan; ilk üç aylık dönem ve grup dağılımı tanımlı", "Zorunlu", "PIM.2.BP1-BP3"],
        [PROCESS_PACKAGE, "Girdi", "BP/GP'yi destekleyen standart süreç varlıkları", "Güncel sürüm, doğru süreç kodu ve izlenebilir bağlantılar", "Zorunlu", "PIM.2.BP4-BP6"],
        ["Doğal kaynak kayıtları ve denetim sonuçları", "Girdi", "Mevcut uygulama, performans, iletişim, yetkinlik ve denetim kanıtları", "Kaynağı, bağlamı ve güncelliği açıklanabilir; kanıt yokluğu değerlendirmeyi durdurmaz", "Koşullu", "PIM.2.BP4-BP5"],
    ]
    outputs = [
        [FRM001_ASSESSMENT, "Çıktı", "BP ve PA/GP etiketleri, kanıtlar, açıklamalar ve tamamlayıcı aksiyonlar", "Tüm kapsam değerlendirilmiş; etiketler gerekçeli; bağlantılar erişilebilir; bulgular sınıflandırılmış; gözden geçirme ve onay tamamlanmış", "Zorunlu", "PIM.2.BP4-BP8"],
        [RPR001, "Çıktı", "Tamamlanan süreçlerin kümülatif performans özeti", "Yalnızca tamamlanan süreçleri içerir; sayısal toplam puan üretmez; etiket dağılımı ve önemli bulgular izlenebilir", "Zorunlu", "PIM.2.BP6-BP8"],
        ["İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci yönlendirme kaydı", "Çıktı", "SRÇ.017 altında ele alınacak problem ve düzeltici/iyileştirici faaliyet ihtiyacı", "Kaynak değerlendirme ve ilgili BP/GP bağlantısı mevcut", "Koşullu", "PIM.2.BP7"],
        ["İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci yönlendirme kaydı", "Çıktı", "SRÇ.018'e aktarılacak değişiklik/iyileştirme fırsatı", "Gerekçe, beklenen fayda ve kaynak değerlendirme bağlantısı mevcut", "Koşullu", "PIM.2.BP7"],
    ]
    quality = [
        [FRM001_ASSESSMENT, "Kapsam Tamlığı", "İlgili tüm BP'ler ve PA 2.1, PA 2.2, PA 3.1, PA 3.2 göstergeleri değerlendirilmiş olmalı", f"{FRM001_ASSESSMENT} tablo kontrolü", "Kalite Danışmanı / Gözden Geçiren", "Tamamlanmadan önce"],
        [FRM001_ASSESSMENT, "Kanıt ve Gerekçe", "Mevcut kanıt veya kanıt eksikliği açıkça yazılmalı; her etiket açıklamayla desteklenmeli", "Kayıt ve bağlantı kontrolü", "Gözden Geçiren", "Gözden geçirme sırasında"],
        [FRM001_ASSESSMENT, "Bulgu Yönlendirme", "Uygunsuzluk, iyileştirme fırsatı, gözlem ve güçlü uygulama doğru süreçte ele alınmalı", "Bulgu türü ve bağlantı kontrolü", "Süreç Sahibi", "Onay öncesi"],
        [RPR001, "Kümülatiflik", "Aynı rapor tamamlanan her süreçten sonra güncellenmeli; taslak ara güncellemeler sürüm geçmişinde çoğaltılmamalı", "Rapor kapsam ve sürüm kontrolü", "Kalite Danışmanı", "Her süreç tamamlandığında"],
        [RPR001, "Puanlama Kuralı", "Sayısal puan veya tek bir toplam süreç etiketi kullanılmamalı", "Rapor içerik kontrolü", "Gözden Geçiren", "Her güncellemede"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC005], ["Kullanım Amacı", "SRÇ.005 girdi/çıktı iş ürünlerini ve kalite kriterlerini tanımlamak"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Zorunlu", "Sürecin tamamlanması için bulunması gereken iş ürünü"], ["Koşullu", "Bulgu, denetim, değişiklik veya mevcut kanıt durumuna göre kullanılan iş ürünü"], ["Girdi", "Değerlendirmede kullanılan iş ürünü"], ["Çıktı", "Değerlendirme sonucunda üretilen veya güncellenen iş ürünü"]]),
        "<h2>3. Girdi İş Ürünleri Matrisi</h2>", table(["İş Ürünü", "Tür", "Beklenen İçerik", "Kalite / Kabul Kriteri", "Zorunluluk", "İlgili BP / GP"], inputs),
        "<h2>4. Çıktı İş Ürünleri Matrisi</h2>", table(["İş Ürünü", "Tür", "Beklenen İçerik", "Kalite / Kabul Kriteri", "Zorunluluk", "İlgili BP / GP"], outputs),
        "<h2>5. Kalite Kriterleri Kontrol Matrisi</h2>", table(["İş Ürünü", "Kalite Boyutu", "Kontrol Kriteri", "Kontrol Yöntemi", "Kontrol Sorumlusu", "Kontrol Zamanı"], quality),
        "<h2>6. Sürüm Geçmişi</h2>", history("SRÇ.005 İş Ürünleri ve Kalite Kriterleri Listesi"),
    ])


def lst009_body() -> str:
    metrics = [
        ["SRÇ.005-Ö01", "Planlanan değerlendirmelerin zamanında tamamlanma oranı", "Planlanan dönemde tamamlanan değerlendirme sayısı / aynı dönemde tamamlanması planlanan değerlendirme sayısı × 100", f"{PLN001}; Değerlendirme Bağlantıları; {RPR001}", "Yıllık değerlendirme dönemi", "En az %90", "Kalite Danışmanı", "Aktif"],
        ["SRÇ.005-Ö02", "Tamamlama ölçütlerini karşılayan değerlendirme kayıtlarının oranı", "Tamamlama ölçütlerini karşılayan değerlendirme sayısı / tamamlanan değerlendirme sayısı × 100", "FRM.001 değerlendirme kayıtları", "Her değerlendirme sonrası; yıllık özet", "%100", "Kalite Danışmanı / Gözden Geçiren", "Aktif"],
        ["SRÇ.005-Ö03", "Bulguların zamanında yönlendirilme oranı", "Onaydan sonra 5 iş günü içinde ilgili sürece yönlendirilen bulgu sayısı / yönlendirilmesi gereken bulgu sayısı × 100", "FRM.001 bulguları; SRÇ.017 ve SRÇ.018 bağlantıları", "Her değerlendirme sonrası; yıllık özet", "5 iş günü içinde %100", "Kalite Danışmanı / Süreç Sahibi", "Aktif"],
    ]
    collection = [
        ["SRÇ.005-Ö01", "Planlanan dönem ve tamamlanma tarihi", f"{PLN001}; FRM.001; {RPR001}", "Değerlendirme bağlantısı ve tamamlanma tarihi kontrolü", "Zamanında tamamlanan / planlanan × 100", "Kalite Danışmanı", RPR001],
        ["SRÇ.005-Ö02", "BP/GP kapsamı, kanıt, bulgu yönlendirme, gözden geçirme ve onay bilgileri", "FRM.001 değerlendirme kaydı", "Tamamlama ölçütleri kontrolü", "Tam kayıt / tamamlanan değerlendirme × 100", "Kalite Danışmanı / Gözden Geçiren", RPR001],
        ["SRÇ.005-Ö03", "Değerlendirme onay tarihi ve yönlendirme bağlantı/tarihi", "FRM.001; SRÇ.017; SRÇ.018", "İş günü ve bağlantı kontrolü", "5 iş gününde yönlendirilen / yönlendirilecek bulgu × 100", "Kalite Danışmanı", RPR001],
    ]
    monitoring = [
        ["SRÇ.005-Ö01", "En az %90", "Mart sonu", RPR001, "İzleniyor", "Gecikme gerekçesi ve yeni tarih değerlendirme kaydında/plan notunda açıklanır; ayrı register oluşturulmaz.", "İlk gerçek yıllık dönemde sonuç oluşturulur."],
        ["SRÇ.005-Ö02", "%100", "Her değerlendirme sonrası", RPR001, "İzleniyor", "Eksik kapsam veya onay tamamlanmadan değerlendirme tamamlandı sayılmaz.", "Tamamlama ölçütleri SRÇ.005 ve PRS.003'te tanımlıdır."],
        ["SRÇ.005-Ö03", "5 iş günü içinde %100", "Her değerlendirme sonrası", RPR001, "İzleniyor", "Geciken yönlendirme tamamlanır ve nedeni değerlendirme kaydında açıklanır.", "Yalnızca yönlendirme gerektiren bulgular paydaya alınır."],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC005], ["Liste Kapsamı", "Değerlendirmelerin zamanında tamamlanması, kayıt tamlığı ve bulgu yönlendirme performansı"], ["Listeyi Hazırlayan", PREPARED_BY], ["Listeyi Gözden Geçiren", REVIEWED_BY], ["Listeyi Onaylayan", APPROVED_BY], ["Genel Not", "Yalnızca düzenli üretilebilen üç ölçüm kullanılır; gerçek sonuçlar oluştukça RPR.001 içinde raporlanır."]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Aktif", "Ölçüm yürürlükte ve veri oluştuğunda izlenecek."], ["Askıda", "Ölçüm tanımlı ancak veri toplama geçici olarak başlamamış veya durdurulmuş."], ["Kapsam Dışı", "Ölçüm ilgili dönem veya bağlamda uygulanmıyor."]]),
        "<h2>3. Performans Ölçüm Matrisi</h2>", table(["Ölçüm ID", "Ölçüm Adı", "Hesaplama / Ölçüm Tanımı", "Veri Kaynağı", "Sıklık", "Hedef / Eşik", "Sorumlu", "Durum"], metrics),
        "<h2>4. Veri Toplama ve Hesaplama Matrisi</h2>", table(["Ölçüm ID", "Veri Alanı", "Veri Kaynağı", "Toplama Yöntemi", "Hesaplama Yöntemi", "Veri Sahibi", "Kayıt / Kanıt"], collection),
        "<h2>5. Hedef ve İzleme Matrisi</h2>", table(["Ölçüm ID", "Hedef / Eşik", "İzleme Sıklığı", "Raporlama / Gözden Geçirme Yeri", "Sapma Durumu", "Tamamlayıcı Aksiyon Yaklaşımı", "Açıklama / Not"], monitoring),
        "<h2>6. Sürüm Geçmişi</h2>", history("SRÇ.005 Süreç Performans Ölçüm Seti"),
    ])


def lst010_body() -> str:
    # LST.010 is maintained in the SRÇ.006 role-column structure.
    from align_lst010_to_src006_structure import process_body, src005
    return process_body(src005())

    roles = [
        ["SRÇ.005 Süreç Sahibi", "Değerlendirme yaklaşımını, kapsamı ve sonuçlarını kurumsal düzeyde sahiplenmek; değerlendirmeyi sonuçlandırmak", "Süreç yönetimi, kalite ve kurumsal karar bilgisi", "Bilgi İşlem Daire Başkanı", PROCESS_OWNER],
        ["Kalite Danışmanı / Değerlendiren", "Değerlendirmeyi planlamak, kanıtları toplamak, BP/GP analizini yapmak, etiketleri ve raporu güncellemek", "ISO/IEC 15504-5, süreç değerlendirme, kanıt analizi ve dokümantasyon yetkinliği", "Yetkilendirilmiş kalite uzmanı", PREPARED_BY],
        ["İlgili Süreç Sahibi / Kanıt Sahibi", "Değerlendirilen sürece ilişkin tanım, kayıt ve mevcut kanıtları sağlamak; açıklamaları doğrulamak", "İlgili süreç ve operasyon bilgisi", "İlgili birimde yetkilendirilmiş rol", "Her süreçte ayrıca belirlenir"],
        ["Gözden Geçiren", "Değerlendirme kapsamı, kanıt yorumu, etiket ve bulgu sınıflandırmasını kontrol etmek", "Süreç, proje ve kalite gözden geçirme bilgisi", "Yetkilendirilmiş proje yöneticisi", REVIEWED_BY],
        ["Onaylayan", "Gözden geçirilen değerlendirme sonucunu onaylamak", "Kurumsal onay ve kaynak yönlendirme yetkisi", "Bilgi İşlem Daire Başkanı", APPROVED_BY],
        ["Bulgu Süreç Sorumlusu", "Uygunsuzluk veya iyileştirme fırsatını SRÇ.017 ya da SRÇ.018 kapsamında ele almak", "Problem çözümü, değişiklik ve iyileştirme yönetimi bilgisi", "İlgili süreç sahibi tarafından atanır", "Bulgu türüne göre belirlenir"],
    ]
    activities = [
        ["F1 Hedefleri belirle", "R", "C", "C", "C", "I"], ["F2 Planla", "R", "C", "C", "C", "I"],
        ["F3 Taahhüt ve katılımı sağla", "R", "A", "R", "C", "I"], ["F4 Değerlendir ve veri topla", "R", "A", "R", "C", "I"],
        ["F5 Veriyi doğrula", "R", "A", "C", "R", "I"], ["F6 Analiz et ve etiketle", "R", "A", "C", "C", "I"],
        ["F7 Raporla ve yönlendir", "R", "A", "C", "C", "I"], ["F8 Kaydı sürdür", "R", "A", "I", "C", "I"],
    ]
    products = [
        [PLN001, "F1-F3", "Kalite Danışmanı", "SRÇ.002 süreç sahibi", "SRÇ.005 süreç sahibi; Gözden Geçiren", "İlgili Süreç Sahipleri", "Plan bir çetele değildir; yaklaşımı ve yıllık takvimi tanımlar."],
        ["FRM.001 Değerlendirme Kaydı", "F4-F8", "Kalite Danışmanı", "SRÇ.005 Süreç Sahibi", "İlgili Süreç Sahibi; Gözden Geçiren", "Onaylayan; Bulgu Süreç Sorumlusu", "Değerlendirme #1 çalışma boyunca aynı kayıt üzerinde güncellenir."],
        [RPR001, "F6-F8", "Kalite Danışmanı", "SRÇ.005 Süreç Sahibi", "Gözden Geçiren", "Onaylayan; SRÇ.002; SRÇ.006", "Kümülatif rapordur; ara taslak güncellemeler sürüm geçmişine eklenmez."],
        ["Bulgu yönlendirmesi", "F7", "Kalite Danışmanı; Bulgu Süreç Sorumlusu", "SRÇ.005 Süreç Sahibi", "İlgili Süreç Sahibi", "Gözden Geçiren; Onaylayan", "Uygunsuzluk SRÇ.017'ye, iyileştirme fırsatı SRÇ.018'e yönlendirilir."],
    ]
    authority = [
        ["Değerlendirme kapsamını onaylama", "SRÇ.005 Süreç Sahibi", "Evet", "Onaylayan", "PLN.001 ve değerlendirme kaydı", "KAPSAM DIŞI kararları dahil"],
        ["BP/GP etiketi önerme", "Kalite Danışmanı", "Evet", "Gözden Geçiren", "FRM.001", "Sayısal puan kullanılmaz"],
        ["Değerlendirmeyi sonuçlandırma", "SRÇ.005 Süreç Sahibi", "Evet", "Onaylayan", "FRM.001", "Tamamlama ölçütleri karşılanmalıdır"],
        ["RPR.001'i güncelleme", "Kalite Danışmanı", "Evet", "Gözden Geçiren / Onaylayan", RPR001, "Her tamamlanan süreç sonrası"],
        ["Uygunsuzluğu veya iyileştirme fırsatını yönlendirme", "Kalite Danışmanı / SRÇ.005 Süreç Sahibi", "Evet", "İlgili hedef süreç sahibi", "FRM.001 ve yönlendirme bağlantısı", "Beş iş günü hedefi uygulanır"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC005], ["Liste Kapsamı", "SRÇ.005 rol, yetki, yetkinlik, RACI ve onay yapısı"], ["Listeyi Hazırlayan", PREPARED_BY], ["Listeyi Gözden Geçiren", REVIEWED_BY], ["Listeyi Onaylayan", APPROVED_BY]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["R", "Responsible / Sorumlu"], ["A", "Accountable / Hesap veren ve nihai sorumlu"], ["C", "Consulted / Danışılan"], ["I", "Informed / Bilgilendirilen"]]),
        "<h2>3. Rol ve Yetkinlik Matrisi</h2>", table(["Rol", "Sorumluluk", "Asgari Yetkinlik", "Atama / Yetkilendirme", "Açıklama"], roles),
        "<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>", table(["Faaliyet", "Kalite Danışmanı", "SRÇ.005 Süreç Sahibi", "İlgili Süreç Sahibi / Kanıt Sahibi", "Gözden Geçiren", "Onaylayan"], activities),
        "<h2>5. İş Ürünleri RACI Matrisi</h2>", table(["İş Ürünü", "İlgili Faaliyet", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"], products),
        "<h2>6. Yetki ve Onay Matrisi</h2>", table(["Karar / Yetki Alanı", "Yetkili Rol", "Karar Yetkisi", "Onaylayan", "Kayıt / Kanıt", "Açıklama"], authority),
        "<h2>7. Sürüm Geçmişi</h2>", history("SRÇ.005 Süreç Rol Yetki ve RACI Matrisi"),
    ])


def blank_review_body() -> str:
    bp_rows = [[bp, title, "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Mevcut kanıt veya kanıt eksikliği yazılır.</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Gerekirse tamamlayıcı aksiyon yazılır.</em>"] for bp, title, _ in PIM2_BPS]
    gp_rows = [[pa, gp, title, "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Mevcut kanıt veya kanıt eksikliği yazılır.</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Gerekirse tamamlayıcı aksiyon yazılır.</em>"] for pa, gp, title in GPS]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Değerlendirilen Süreç", SRC005], ["Süreç Referansı", "ISO/IEC 15504-5 PIM.2 - Process assessment"], ["Süreç Durumu", "Aktif"], ["Süreç Sürümü", "v1.0"], ["Değerlendirme Kapsamı", "PIM.2 BP1-BP8; PA 2.1; PA 2.2; PA 3.1; PA 3.2"], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendirmeyi Yapan", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Değerlendirmeyi Onaylayan", APPROVED_BY], ["Değerlendirme Sonucu", "<em>Etiket dağılımları, kritik bulgular ve güçlü uygulamalarla özetlenir; toplam puan veya tek bir süreç etiketi yazılmaz.</em>"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>1</em>", "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / Değerlendirme Kaydı</em>"]]),
    ])


def assessment_body() -> str:
    bp_status = {
        "PIM.2.BP1": ("VAR", "Değerlendirme hedefi ve kapsamı SRÇ.005, PLN.001 ve PRS.003 içinde kurumsal hedeflerle ilişkilendirilmiştir.", f"{SRC005}; {PLN001}; {PRS003}", "-"),
        "PIM.2.BP2": ("VAR", "Yıllık değerlendirme yaklaşımı, ilk üç aylık dönem, süreç grupları, roller, etiketler ve tamamlama ölçütleri PLN.001 içinde tanımlanmıştır.", PLN001, "-"),
        "PIM.2.BP3": ("DAĞINIK", "Süreç sahibi, değerlendiren, gözden geçiren ve onaylayan atanmıştır; ancak süreç bazlı gerçek yıllık takvim ve kaynak taahhüt kayıtları henüz oluşmamıştır.", f"{SRC005}; İÜC.BİDB.LST.010 (SRÇ.005); {PLN001}", "İlk yıllık değerlendirme döneminde süreç bazlı mutabakat ve kaynak uygunluğu doğal iletişim kayıtlarıyla doğrulanmalıdır."),
        "PIM.2.BP4": ("VAR", "SRÇ.001 ve SRÇ.004 değerlendirmeleri mevcut tanım ve kanıtlar kullanılarak Değerlendirme #1 üzerinde yürütülmüş; SRÇ.005 için de aynı yöntem uygulanmıştır.", "SRÇ.001, SRÇ.004 ve bu FRM.001 Değerlendirme #1 kayıtları", "-"),
        "PIM.2.BP5": ("DAĞINIK", "Kanıt yeterliliği ve etiket açıklamaları yerel kontrolle doğrulanmaktadır; yetkili gözden geçirenin formal doğrulama kaydı henüz tamamlanmamıştır.", "FRM.001 kayıtları; yerel doğrulama raporları", "Gözden geçirenin değerlendirme kapsamı, kanıt yorumu ve etiketleri doğruladığı kayıt tamamlanmalıdır."),
        "PIM.2.BP6": ("VAR", "Değerlendirme verileri etiket dağılımları, güçlü/zayıf yönler ve bulgu türleriyle analiz edilmektedir; toplam puan üretilmemektedir.", f"FRM.001 değerlendirme kayıtları; {RPR001}", "-"),
        "PIM.2.BP7": ("VAR", "Tamamlanan süreçlerin sonuçları tek ve kümülatif RPR.001 içinde raporlanacak biçimde tanımlanmış ve ilk içerik oluşturulmuştur.", RPR001, "-"),
        "PIM.2.BP8": ("VAR", "Değerlendirme kayıtları süreç altındaki boş formdan üretilmekte ve 91 - İç Denetimler / Süreç Gözden Geçirmeleri altında Değerlendirme Bağlantısıyla saklanmaktadır.", "FRM.001 boş form; Değerlendirme #1 kayıtları; Confluence/repository yapısı", "-"),
    }
    bp_rows = [[bp, title, bp_status[bp][1], bp_status[bp][2], bp_status[bp][0], bp_status[bp][3]] for bp, title, _ in PIM2_BPS]
    gp_labels = {
        "GP.2.1.1": "VAR", "GP.2.1.2": "VAR", "GP.2.1.3": "ZAYIF", "GP.2.1.4": "VAR", "GP.2.1.5": "DAĞINIK", "GP.2.1.6": "DAĞINIK",
        "GP.2.2.1": "VAR", "GP.2.2.2": "VAR", "GP.2.2.3": "VAR", "GP.2.2.4": "DAĞINIK",
        "GP.3.1.1": "VAR", "GP.3.1.2": "VAR", "GP.3.1.3": "VAR", "GP.3.1.4": "VAR", "GP.3.1.5": "VAR",
        "GP.3.2.1": "DAĞINIK", "GP.3.2.2": "DAĞINIK", "GP.3.2.3": "YOK", "GP.3.2.4": "DAĞINIK", "GP.3.2.5": "DAĞINIK", "GP.3.2.6": "ZAYIF",
    }
    gp_evidence = {
        "VAR": ("Standart süreç paketi içinde ilgili hedef, yöntem, rol, iş ürünü, etkileşim veya altyapı tanımı yeterli ve izlenebilir biçimde oluşturulmuştur.", f"{SRC005}; PRS.003; PLN.001; süreç özel LST.007-LST.010; RPR.001", "-"),
        "DAĞINIK": ("Gerekli tanım veya altyapı vardır; ancak gerçek iletişim, kaynak tahsisi, gözden geçirme/onay ya da kullanım kanıtı henüz sistematik olarak tamamlanmamıştır.", "SRÇ.005 süreç paketi; mevcut yerel ve Confluence kayıtları", "İlk gerçek değerlendirme döneminde doğal kaynak kanıtları tamamlanmalı ve değerlendirme kaydına bağlanmalıdır."),
        "ZAYIF": ("Yaklaşım tanımlıdır; ancak gerçek sapma/yeniden planlama veya süreç performans verisi henüz oluşmamıştır.", "LST.009 (SRÇ.005); PLN.001", "İlk gerçek değerlendirme döneminde sonuç, sapma ve karar kayıtları oluşturulmalıdır."),
        "YOK": ("Rol yetkinlikleri tanımlanmış olsa da süreç değerlendirmesine özgü yetkinlik doğrulaması ve eğitim/katılım kaydı bulunmamaktadır.", "LST.010 (SRÇ.005); SRÇ.020", "Yetkinlik ihtiyacı doğrulanmalı; gerekiyorsa SRÇ.020 kapsamında eğitim ve katılım kaydı oluşturulmalıdır."),
    }
    gp_rows = []
    for pa, gp, title in GPS:
        label = gp_labels[gp]
        current, evidence, action = gp_evidence[label]
        gp_rows.append([pa, gp, title, current, evidence, label, action])
    completion = [
        ["1", "İlk yıllık değerlendirme döneminde süreç bazlı katılım, takvim ve kaynak taahhüdünü doğal iletişim kayıtlarıyla doğrulamak", "Gözlem", "PIM.2.BP3; GP.2.1.5; GP.2.1.6", "Değerlendirme #1"],
        ["2", "Değerlendirme kapsamı, kanıt yorumu, etiket ve bulgu sınıflandırması için formal gözden geçirme/onay kaydını tamamlamak", "Gözlem", "PIM.2.BP5; GP.2.2.4", "Değerlendirme #1"],
        ["3", "İlk gerçek ölçüm sonuçlarını toplamak, sapmaları ve yeniden planlamaları kaydetmek", "Gözlem", "GP.2.1.3; GP.3.2.6", RPR001],
        ["4", "Süreç değerlendirme rollerinin yetkinlik ihtiyacını doğrulamak ve gerekiyorsa eğitim kaydı oluşturmak", "Gözlem", "GP.3.2.3", "SRÇ.020 / Değerlendirme #1"],
        ["5", "Etiket ve bulgu dağılımlarının süreçler ilerledikçe kümülatif raporda karşılaştırılabilir biçimde sürdürülmesini sağlamak", "İyileştirme Fırsatı", "PIM.2.BP6-BP8", "SRÇ.018"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Değerlendirilen Süreç", SRC005], ["Süreç Referansı", "ISO/IEC 15504-5 PIM.2 - Process assessment"], ["Süreç Durumu", "Yerel gözden geçirmede"], ["Süreç Sürümü", "v1.0"], ["Değerlendirme Kapsamı", "PIM.2 BP1-BP8; PA 2.1; PA 2.2; PA 3.1; PA 3.2"], ["Değerlendirme Tarihi", "14-07-2026"], ["Değerlendirmeyi Yapan", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Değerlendirmeyi Onaylayan", APPROVED_BY], ["Değerlendirme Sonucu", "PIM.2 BP dağılımı 6 VAR ve 2 DAĞINIK; PA/GP dağılımı 11 VAR, 7 DAĞINIK, 2 ZAYIF ve 1 YOK'tur. Süreç yaklaşımı, plan, prosedür, etiket sistemi, iş ürünleri, roller ve kümülatif raporlama yapısı tanımlanmıştır. Gerçek yıllık dönem taahhütleri, formal veri doğrulama/gözden geçirme, yetkinlik/eğitim ve ilk performans sonuçları henüz tamamlanmamıştır. Toplam puan veya tek bir süreç etiketi üretilmemiştir."]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion),
    ])


def procedure_body() -> str:
    principles = [
        ["Kapsam bütünlüğü", "İlgili ISO/IEC 15504-5 sürecinin tüm BP'leri ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 göstergeleri değerlendirilir."],
        ["Etiket temelli değerlendirme", "YOK, ZAYIF, DAĞINIK, VAR ve KAPSAM DIŞI etiketleri kullanılır; sayısal puan ve tek toplam süreç etiketi kullanılmaz."],
        ["Mevcut kanıt yaklaşımı", "Gerçek kanıt bulunması değerlendirmeyi başlatma ön koşulu değildir. Mevcut kanıt kullanılır; bulunmayan kanıt açıkça yazılır ve etikete yansıtılır."],
        ["Tek değerlendirme kaydı", "Süreç çalışması boyunca aynı Değerlendirme #1 kaydı güncellenir; ayrı GAP analizi veya Değerlendirme #2 oluşturulmaz."],
        ["İzlenebilir bulgu", "Her bulgu ilgili BP/GP, açıklama ve değerlendirme bağlantısıyla ilişkilendirilir."],
        ["Ayrıştırılmış yönlendirme", "Uygunsuzluklar SRÇ.017'ye, iyileştirme fırsatları doğrudan SRÇ.018'e yönlendirilir."],
        ["Kümülatif raporlama", "Tamamlanan her süreçten sonra aynı RPR.001 güncellenir; ara taslaklar sürüm geçmişinde çoğaltılmaz."],
    ]
    rules = [
        ["Değerlendirme tetikleyicisi", "Yıllık Süreç Kalite Planı veya önemli süreç değişikliği/denetim bulgusu", "Zorunlu", "İlk yürürlüğe alma tetikleyici değildir."],
        ["Değerlendirme hedefi", "Kapsam, beklenen çıktı ve başarı ölçütü değerlendirme öncesinde belirlenir.", "Zorunlu", "PIM.2.BP1"],
        ["Kanıt toplama", "Süreç paketi, doğal kaynak kayıtları ve mevcut denetim sonuçları incelenir.", "Zorunlu", "Kanıt yokluğu açıkça kaydedilir."],
        ["Veri doğrulama", "Kanıtın güncelliği, bağlamı, kapsamı ve yorum tutarlılığı gözden geçirilir.", "Zorunlu", "Gözden geçiren doğrulaması aranır."],
        ["Etiket atama", "Her BP/GP için tek bir etiket ve açıklayıcı gerekçe yazılır.", "Zorunlu", "Yüzde veya puan yazılmaz."],
        ["Tamamlama", "Tüm kapsam, kanıt/açıklama, bulgu sınıflandırma/yönlendirme, gözden geçirme ve onay tamamlanır.", "Zorunlu", "Koşulların biri eksikse tamamlandı sayılmaz."],
    ]
    steps = [
        ["1. Hedef ve kapsam", "Değerlendirilecek süreç, hedef, dönem ve kapsam belirlenir.", "Kalite Danışmanı / Süreç Sahibi", PLN001, "Kapsam tüm BP ve tanımlı PA/GP'leri içerir."],
        ["2. Katılım ve kaynak", "Süreç sahibi, kanıt sahipleri, gözden geçiren ve onaylayanla katılım ve kaynak uygunluğu netleştirilir.", "SRÇ.005 Süreç Sahibi", "Takvim/iletişim kaydı", "Ayrı register zorunlu değildir."],
        ["3. Veri toplama", "Süreç ve destek dokümanları ile erişilebilen doğal kaynak kanıtları incelenir.", "Kalite Danışmanı / Kanıt Sahibi", "FRM.001 taslak kaydı", "Erişilemeyen kanıt eksik olarak yazılır."],
        ["4. Veri doğrulama", "Kanıt yeterliliği ve değerlendirme hedefini kapsama durumu kontrol edilir.", "Kalite Danışmanı / Gözden Geçiren", "FRM.001 kanıt ve açıklama alanları", "Yorum farklılıkları sonuçlandırılır."],
        ["5. Analiz ve etiketleme", "Her BP/GP için etiket atanır; güçlü/zayıf yönler ve bulgular belirlenir.", "Kalite Danışmanı", "FRM.001", "Toplam puan üretilmez."],
        ["6. Bulgu yönlendirme", "Uygunsuzluk, iyileştirme fırsatı, gözlem ve güçlü uygulama uygun izleme yerine aktarılır.", "Kalite Danışmanı / Süreç Sahibi", "SRÇ.017 veya SRÇ.018 bağlantısı", "Yönlendirme hedefi onaydan sonra beş iş günüdür."],
        ["7. Gözden geçirme ve onay", "Kapsam, kanıt, etiket ve bulgular gözden geçirilir; süreç sahibi sonuçlandırır ve onaylayan onaylar.", "Gözden Geçiren / Süreç Sahibi / Onaylayan", "FRM.001", "Tamamlama ölçütleri kontrol edilir."],
        ["8. Raporlama ve saklama", "Değerlendirme kaydı erişilebilir konumda tutulur ve RPR.001 güncellenir.", "Kalite Danışmanı", RPR001, "Aynı kümülatif rapor kullanılır."],
    ]
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Prosedür Kodu ve Adı", PRS003], ["Prosedür Referansı", SRC005], ["Prosedür Sahibi", PROCESS_OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "14-07-2026"]]),
        "<h2>2. Amaç</h2>", p("Bu prosedürün amacı, İÜC BİDB standart süreçlerinin iç süreç değerlendirmelerinin ortak, izlenebilir ve etiket temelli bir yöntemle planlanması, yürütülmesi, doğrulanması, analiz edilmesi, raporlanması ve kayıtlarının sürdürülmesi için uygulanacak kuralları tanımlamaktır."),
        "<h2>3. Kapsam</h2>", p("Bu prosedür, LST.006 içinde tanımlanan güncel standart süreç setinin SRÇ.005 kapsamında yürütülen iç süreç değerlendirmelerine uygulanır."),
        "<ul><li>yıllık ve ihtiyaç bazlı süreç değerlendirmeleri,</li><li>BP ve PA/GP kapsamının belirlenmesi,</li><li>mevcut tanım ve kanıtların toplanması ve doğrulanması,</li><li>etiketleme, bulgu sınıflandırma ve yönlendirme,</li><li>değerlendirme kayıtlarının gözden geçirilmesi, onaylanması, raporlanması ve saklanması.</li></ul>",
        "<h2>4. Kapsam Dışı</h2>", "<ul><li>SRÇ.026 kapsamında yürütülen resmî veya dış değerlendirmeler ve kurumsal denetimler,</li><li>ayrı bir GAP analizi kaydı veya değerlendirme takip registerı oluşturulması,</li><li>bulguların SRÇ.017 ve SRÇ.018 kapsamındaki çözüm/değişiklik uygulamaları,</li><li>sayısal yetenek puanı veya tek toplam süreç etiketi üretimi.</li></ul>",
        "<h2>5. Referanslar</h2>", table(["Referans", "Açıklama"], [[SRC005, "Süreç amacı, sonuçları, faaliyetleri ve temel uygulama kuralları"], ["İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Bu prosedürün zorunlu doküman yapısı"], [PLN001, "Yıllık değerlendirme yaklaşımı, takvim, roller ve tamamlanma ölçütleri"], ["İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu", "BP ve PA/GP bazlı değerlendirme kaydı"], [RPR001, "Kümülatif süreç performans raporu"], ["İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Uygunsuzlukların ele alınması"], ["İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "İyileştirme fırsatları ve gerekli değişiklikler"], ["İÜC.BİDB.SRÇ.026 - Denetim Süreci", "Resmî denetim sonuçlarının girdi olarak kullanılması"]]),
        "<h2>6. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [["Değerlendirme", "Sürecin BP ve PA/GP beklentilerine göre mevcut tanım ve kanıtlarıyla incelenmesi"], ["Değerlendirme Bağlantısı", "Doldurulmuş ve gözden geçirilmiş süreç değerlendirme kaydına erişim bağlantısı"], ["Uygunsuzluk", "Tanımlı gereksinim veya süreç beklentisine aykırı durum"], ["İyileştirme Fırsatı", "Bir problem olmaksızın sürecin etkinlik, uygunluk veya verimliliğini geliştirme olanağı"], ["Gözlem", "Takip edilmesi yararlı ancak doğrudan uygunsuzluk veya değişiklik gerektirmeyen bulgu"], ["Güçlü Uygulama", "Korunması veya yaygınlaştırılması önerilen tutarlı uygulama"]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki"], [["SRÇ.005 Süreç Sahibi", "Değerlendirme yaklaşımını sahiplenmek, katılımı sağlamak ve sonucu sonuçlandırmak", "Kapsam, KAPSAM DIŞI ve sonuçlandırma kararları"], ["Kalite Danışmanı", "Planı hazırlamak/güncellemek, değerlendirmeyi yürütmek, kanıt ve etiketleri kaydetmek, RPR.001'i güncellemek", "Etiket ve bulgu sınıflandırması önermek"], ["İlgili Süreç Sahibi / Kanıt Sahibi", "Mevcut tanım ve kanıtları sağlamak, açıklamaları doğrulamak", "Kendi süreç alanında kanıt ve bağlam doğrulaması"], ["Gözden Geçiren", "Kapsam, kanıt yorumu, etiket ve bulguları kontrol etmek", "Düzeltme istemek ve gözden geçirme görüşü vermek"], ["Onaylayan", "Gözden geçirilen sonucu onaylamak", "Değerlendirmeyi yürürlüğe almak"]]),
        "<h2>8. Genel İlkeler</h2>", table(["İlke", "Açıklama"], principles),
        "<h2>9. Prosedür Esasları</h2>", table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], rules),
        "<h2>10. Uygulama / Strateji Matrisi</h2>", table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], steps),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>", table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [["Yayın", "Onaylı süreç dokümanları Confluence'ta yayımlanır; değerlendirme ekleri kontrollü ortamda tutulur.", "Yayımlayan / Repository Sorumlusu", "Confluence sayfa geçmişi"], ["Erişim", "Değerlendirme kayıtları ilgili süreç sahibi, değerlendiren, gözden geçiren ve onaylayan tarafından erişilebilir olmalıdır.", "SRÇ.005 Süreç Sahibi", "Erişim yetkileri"], ["Bakım", "Değerlendirme #1 süreç geliştirme boyunca aynı kayıt üzerinde güncellenir.", "Kalite Danışmanı", "FRM.001"], ["Rapor bakımı", "RPR.001 her tamamlanan süreçten sonra güncellenir; ara v0.1 güncellemeleri sürüm geçmişine eklenmez.", "Kalite Danışmanı", RPR001], ["Arşiv", "Nihai değerlendirme kayıtları doküman kontrol ve saklama kurallarına göre korunur.", "Doküman Sorumlusu", "Confluence / Google Drive"]]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>", table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [[PLN001, "Değerlendirme yaklaşımı ve yıllık takvim", "08 - Planlar", "Kalite Danışmanı", "SRÇ.002 sorumluluğunda ortak plan"], ["Boş FRM.001", "Yeni değerlendirmelerin standart yapısı", "İlgili süreç sayfası altında", "Kalite Danışmanı", "Puan içermez"], ["FRM.001 Değerlendirme Kaydı", "BP/GP etiket, kanıt ve bulgu kaydı", "91 - İç Denetimler / Süreç Gözden Geçirmeleri", "Kalite Danışmanı", "Değerlendirme Bağlantısı ile referanslanır"], [RPR001, "Kümülatif süreç sonuçlarının yönetim özeti", "09 - Raporlar", "Kalite Danışmanı", "Tamamlanan süreçlerle büyür"], ["SRÇ.017 / SRÇ.018 bağlantıları", "Bulgu yönlendirme ve izlenebilirlik", "İlgili süreç/doğal kaynak sistemi", "İlgili Süreç Sahibi", "Kaynak değerlendirme bağlantısı korunur"]]),
        "<h2>13. Sürüm Geçmişi</h2>", history("Süreç Değerlendirme Prosedürü"),
    ])


def plan_template_body() -> str:
    return "".join([
        "<h2>0. Şablon Hakkında</h2>",
        "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", PLN001_TEMPLATE_CODE], ["Doküman Türü", "Doküman Şablonu"], ["Kullanım Alanı", PLN001], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Güncelleme Sıklığı", "Süreç kalitesi değerlendirme ve planlama yaklaşımı değiştiğinde"]]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", p("Bu şablon yalnızca İÜC.BİDB.PLN.001 - Süreç Kalite Planının hazırlanması için kullanılır. Süreç kalitesinin değerlendirilmesine ilişkin hedef, yaklaşım, yıllık takvim, rol, kriter, tamamlama, bulgu yönetimi, raporlama ve kayıt yapısını tanımlamak üzere tasarlanmıştır. Plan bir takip registerı değildir."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", p(PLN001),
        "<h3>0.4. Sürüm Geçmişi</h3>", history("Süreç Kalite Planı Şablonu"),
        "<h2>1. Plan Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Plan Kodu ve Adı", PLN001], ["Plan Referansı", "İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci; İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci"], ["Plan Sahibi", PREPARED_BY], ["Kurumsal Sorumluluk", "SRÇ.002 Süreç Sahibi"], ["Gözden Geçiren", REVIEWED_BY], ["Onaylayan", APPROVED_BY], ["Kapsadığı Dönem", "<em>Yıl / dönem</em>"], ["Durum", "<em>Taslak / Onaylı / Aktif</em>"], ["Sürüm", "<em>v0.1 / v1.0</em>"], ["Yürürlük Tarihi", "<em>GG-AA-YYYY</em>"]]),
        "<h2>2. Amaç ve Kapsam</h2>", p("Süreç kalite planının amacı, kapsadığı standart süreçler ve kapsam dışı resmî/dış değerlendirmeler açıklanır."),
        "<h2>3. Kalite Hedefleri</h2>", table(["Hedef", "Başarı Ölçütü", "İlgili Süreç / Kayıt"], [["<em>Süreç kalitesi hedefi</em>", "<em>Ölçüt</em>", "<em>Referans</em>"]]),
        "<h2>4. Değerlendirme Yaklaşımı</h2>", p("Değerlendirme kapsamı, kullanılan BP ve PA/GP göstergeleri, etiketler, kanıt yaklaşımı ve temel uygulama ilkeleri açıklanır."),
        "<h2>5. Yıllık Değerlendirme Takvimi</h2>", table(["Dönem", "Süreç Grubu", "Kapsam", "Çıktı"], [["<em>Ocak / Şubat / Mart</em>", "<em>Süreç grubu</em>", "<em>Süreçler</em>", "<em>Değerlendirme bağlantıları / rapor</em>"]]),
        "<h2>6. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki / Katkı"], [["<em>Rol</em>", "<em>Sorumluluk</em>", "<em>Yetki</em>"]]),
        "<h2>7. Değerlendirme Kriterleri ve Etiketler</h2>", table(["Etiket", "Kriter"], [["<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Etiket kriteri</em>"]]),
        "<h2>8. Tamamlama Ölçütleri</h2>", table(["Ölçüt", "Doğrulama Yöntemi", "Sorumlu"], [["<em>Kapsam / kanıt / bulgu / gözden geçirme / onay</em>", "<em>Yöntem</em>", "<em>Rol</em>"]]),
        "<h2>9. Bulguların Yönetimi</h2>", table(["Bulgu Türü", "Yönlendirme", "İzleme Kuralı"], [["<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>İlgili süreç</em>", "<em>İzlenebilirlik kuralı</em>"]]),
        "<h2>10. Raporlama</h2>", p("İÜC.BİDB.RPR.001 - Süreç Performansları Raporunun güncellenme, yıllık yönetim özeti ve sürüm yönetimi kuralları açıklanır."),
        "<h2>11. Kayıtların Saklanması</h2>", table(["Kayıt", "Saklama Yeri", "Sorumlu", "Erişim / Bakım Kuralı"], [["<em>Kayıt</em>", "<em>Konum</em>", "<em>Rol</em>", "<em>Kural</em>"]]),
        "<h2>12. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [["<em>v0.1</em>", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]),
    ])


def plan_body() -> str:
    schedule = [
        ["Ocak", "Süreç yönetimi, kalite ve yönetişim süreçleri", "SRÇ.001 Dokümantasyon; SRÇ.002 Kalite Güvencesi; SRÇ.003 Doğrulama; SRÇ.004 Süreç Kurulumu; SRÇ.005 Süreç Değerlendirme; SRÇ.006 Süreç İyileştirme; SRÇ.023 Organizasyonel Yönetim; SRÇ.024 Kalite Yönetimi; SRÇ.025 Ölçüm; SRÇ.026 Denetim", "İlgili süreçlerin Değerlendirme Bağlantıları"],
        ["Şubat", "Proje, risk, değişiklik, konfigürasyon ve kurumsal kaynak süreçleri", "SRÇ.007 Proje Yönetimi; SRÇ.008 Risk Yönetimi; SRÇ.016 Yapılandırma Yönetimi; SRÇ.017 Problem Çözüm Yönetimi; SRÇ.018 Değişiklik Talebi Yönetimi; SRÇ.019 İnsan Kaynakları Yönetimi; SRÇ.020 Eğitim; SRÇ.021 Bilgi Yönetimi; SRÇ.022 Altyapı", "İlgili süreçlerin Değerlendirme Bağlantıları"],
        ["Mart", "Yazılım mühendisliği yaşam döngüsü süreçleri", "SRÇ.009 Gereksinimlerin Toplanması; SRÇ.010 Yazılım Gereksinim Analizi; SRÇ.011 Yazılım Tasarımı; SRÇ.012 Yazılım Geliştirme; SRÇ.013 Yazılım Entegrasyonu; SRÇ.014 Yazılım Test; SRÇ.015 Ürün Yayınlama - Sürüm", "İlgili süreçlerin Değerlendirme Bağlantıları ve yıllık RPR.001 özeti"],
    ]
    return "".join([
        "<h2>1. Plan Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Plan Kodu ve Adı", PLN001], ["Plan Referansı", "İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci; İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci"], ["Plan Sahibi", PREPARED_BY], ["Kurumsal Sorumluluk", "SRÇ.002 Süreç Sahibi"], ["Gözden Geçiren", REVIEWED_BY], ["Onaylayan", APPROVED_BY], ["Kapsadığı Dönem", "Yıllık; planlı süreç değerlendirmeleri Ocak-Mart döneminde"], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"]]),
        "<h2>2. Amaç ve Kapsam</h2>", p("Bu planın amacı, İÜC BİDB standart süreçlerinin kalitesinin hangi hedef, yöntem, dönem, rol, kriter ve kayıt yapısıyla değerlendirileceğini tanımlamaktır. Plan günlük takip çizelgesi değildir; süreç kalitesinin değerlendirilmesine yön veren ortak çerçevedir."),
        p("Plan, LST.006 içinde tanımlanan güncel standart süreç setinin iç süreç değerlendirmelerini kapsar. Resmî/dış değerlendirmeler ve kurumsal denetimler SRÇ.026 kapsamında yürütülür."),
        "<h2>3. Kalite Hedefleri</h2>", table(["Hedef", "Başarı Ölçütü", "İlgili Süreç / Kayıt"], [["Planlı değerlendirmeleri zamanında tamamlamak", "Planlanan değerlendirmelerin en az %90'ı ilgili ay içinde tamamlanır.", "LST.009 (SRÇ.005); RPR.001"], ["Eksiksiz değerlendirme kaydı üretmek", "Tamamlanan değerlendirmelerin %100'ü tanımlı tamamlama ölçütlerini karşılar.", "FRM.001; LST.009 (SRÇ.005)"], ["Bulguları zamanında yönlendirmek", "Yönlendirilmesi gereken bulguların %100'ü onaydan sonra beş iş günü içinde ilgili sürece aktarılır.", "SRÇ.017; SRÇ.018; RPR.001"]]),
        "<h2>4. Değerlendirme Yaklaşımı</h2>", "<ul><li>Değerlendirmeler yıllık planlı dönem veya önemli süreç değişikliği/denetim bulgusu üzerine ihtiyaç bazlı yürütülür.</li><li>Her süreç için tüm BP'ler ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 değerlendirilir.</li><li>Mevcut kanıt kullanılır; kanıt eksikliği değerlendirmeyi durdurmaz ve etikete yansıtılır.</li><li>YOK, ZAYIF, DAĞINIK, VAR ve KAPSAM DIŞI etiketleri kullanılır; sayısal puan ve toplam süreç etiketi üretilmez.</li><li>Çalışma boyunca aynı Değerlendirme #1 kaydı güncellenir; ayrı GAP kaydı oluşturulmaz.</li></ul>",
        "<h2>5. Yıllık Değerlendirme Takvimi</h2>", table(["Dönem", "Süreç Grubu", "Kapsam", "Çıktı"], schedule),
        p("Planlanan tarihte tamamlanamayan bir değerlendirme için yeni tarih, gecikme gerekçesi ve güncel durum aynı değerlendirme kaydı veya plan notu içinde açıklanır; ayrı bir takip registerı oluşturulmaz."),
        "<h2>6. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki / Katkı"], [["Plan Sahibi / Kalite Danışmanı", "Planı hazırlamak, güncellemek; değerlendirmeleri yürütmek ve sonuçları raporlamak", "Yıllık takvim ve yöntem güncellemesi önermek"], ["SRÇ.002 Süreç Sahibi", "Planın kurumsal sorumluluğunu taşımak ve kalite yaklaşımıyla uyumunu sağlamak", "Planın kalite güvence çerçevesini onay sürecine sunmak"], ["SRÇ.005 Süreç Sahibi", "Süreç değerlendirmelerinin kapsamını ve sonuçlandırılmasını yönetmek", "Kapsam ve sonuçlandırma kararı"], ["İlgili Süreç Sahibi / Kanıt Sahibi", "Mevcut kanıt ve açıklamaları sağlamak", "Kendi süreç alanında doğrulama"], ["Gözden Geçiren", "Kapsam, kanıt, etiket ve bulguları gözden geçirmek", "Düzeltme istemek ve görüş vermek"], ["Onaylayan", "Planı ve tamamlanan değerlendirmeleri onaylamak", "Kurumsal onay"]]),
        "<h2>7. Değerlendirme Kriterleri ve Etiketler</h2>", table(["Etiket", "Kriter"], LABELS),
        "<h2>8. Tamamlama Ölçütleri</h2>", table(["Ölçüt", "Doğrulama Yöntemi", "Sorumlu"], [["Kapsam", "İlgili tüm BP'ler ve PA 2.1, PA 2.2, PA 3.1, PA 3.2 göstergeleri değerlendirilmiş olmalı.", "Kalite Danışmanı"], ["Kanıt ve açıklama", "Mevcut kanıt veya kanıt eksikliği ile etiket gerekçesi kaydedilmiş olmalı.", "Kalite Danışmanı / Kanıt Sahibi"], ["Bulgu yönetimi", "Bulgular sınıflandırılmış ve gerekiyorsa ilgili sürece yönlendirilmiş olmalı.", "Kalite Danışmanı / Süreç Sahibi"], ["Gözden geçirme", "Kapsam, veri yorumu ve etiketler gözden geçirilmiş olmalı.", "Gözden Geçiren"], ["Onay", "Süreç sahibi değerlendirmeyi sonuçlandırmış ve onaylayan onaylamış olmalı.", "Süreç Sahibi / Onaylayan"]]),
        "<h2>9. Bulguların Yönetimi</h2>", table(["Bulgu Türü", "Yönlendirme", "İzleme Kuralı"], [["Uygunsuzluk", "Önce SRÇ.017 Problem Çözüm Yönetimi; çözüm gerekli kılarsa SRÇ.018", "Kaynak değerlendirme ve ilgili BP/GP bağlantısı korunur."], ["İyileştirme Fırsatı", "Doğrudan SRÇ.018", "Beklenen fayda ve gerekçe belirtilir."], ["Gözlem", "Değerlendirme #1", "Bir sonraki değerlendirmede yeniden ele alınır."], ["Güçlü Uygulama", "Değerlendirme #1 ve RPR.001", "Korunma veya yaygınlaştırma önerisiyle kaydedilir."]]),
        "<h2>10. Raporlama</h2>", p("RPR.001, tamamlanan her süreç değerlendirmesinden sonra güncellenen tek ve kümülatif rapordur. Yıllık planlı dönem mart sonunda tamamlandığında yönetim özeti olarak kullanılır. Rapor, çalışma boyunca v0.1 Taslak kalır; ara güncellemeler sürüm geçmişine eklenmez. Süreç çalışmaları tamamlandığında v1.0 Onaylı sürüme geçirilir."),
        "<h2>11. Kayıtların Saklanması</h2>", table(["Kayıt", "Saklama Yeri", "Sorumlu", "Erişim / Bakım Kuralı"], [["Boş FRM.001", "İlgili SRÇ süreç sayfası altında", "Kalite Danışmanı", "Yeni değerlendirmeler için güncel yapı"], ["FRM.001 Değerlendirme Kaydı", "91 - İç Denetimler / Süreç Gözden Geçirmeleri", "Kalite Danışmanı", "Değerlendirme Bağlantısı ile referanslanır"], [RPR001, "09 - Raporlar", "Kalite Danışmanı", "Her tamamlanan süreçte aynı rapor güncellenir"], ["Bulgu bağlantıları", "SRÇ.017 / SRÇ.018 ve doğal kaynak sistemi", "İlgili Süreç Sahibi", "Kaynak değerlendirmeye geri bağlantı korunur"]]),
        "<h2>12. Sürüm Geçmişi</h2>", history("Süreç Kalite Planı"),
    ])


def report_template_body() -> str:
    from update_rpr001_layout_and_maturity_placeholder import align_rpr001_layout
    return align_rpr001_layout("".join([
        "<h2>0. Şablon Hakkında</h2>",
        "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", RPR001_TEMPLATE_CODE], ["Doküman Türü", "Doküman Şablonu"], ["Kullanım Alanı", RPR001], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Güncelleme Sıklığı", "Süreç değerlendirme ve performans raporlama yaklaşımı değiştiğinde"]]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", p("Bu şablon yalnızca İÜC.BİDB.RPR.001 - Süreç Performansları Raporunun hazırlanması için kullanılır. Tamamlanan süreç değerlendirmelerinin BP ve PA/GP etiket dağılımlarını, önemli bulgularını, iyileştirme fırsatlarını, güçlü uygulamalarını, ölçüm sonuçlarını ve SRÇ.018 kapsamında doğrulanmış iyileştirme sonuçlarını kümülatif biçimde raporlamak üzere tasarlanmıştır."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", p(RPR001),
        "<h3>0.4. Sürüm Geçmişi</h3>", history("Süreç Performansları Raporu Şablonu"),
        "<h2>1. Rapor Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Rapor Kodu ve Adı", RPR001], ["Rapor Referansı", f"{PLN001}; {SRC005}; İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci; İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"], ["Rapor Sahibi", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Onaylayan", APPROVED_BY], ["Raporlama Dönemi", "Süreç çalışmaları boyunca kümülatif; yıllık yönetim özeti mart sonunda"], ["Durum", "<em>Taslak / Onaylı</em>"], ["Sürüm", "<em>v0.1 / v1.0</em>"], ["Son Güncelleme", "<em>GG-AA-YYYY</em>"]]),
        "<h2>2. Yönetici Özeti</h2>", p("Değerlendirmesi tamamlanan süreçler, ortak güçlü yönler, ortak gelişim alanları ve yönetim dikkati gerektiren konular özetlenir. Toplam puan veya tek bir genel süreç etiketi üretilmez."),
        "<h2>3. Kapsam ve Yöntem</h2>", p("Rapora alınan tamamlanmış süreç değerlendirmeleri, kullanılan BP ve PA/GP kapsamı, etiket sözlüğü, veri kaynakları ve kanıt sınırlamaları açıklanır."),
        "<h2>4. Süreç Sonuç Özeti</h2>", table(["Süreç", "Değerlendirme Kapsamı", "BP Dağılımı", "PA / GP Dağılımı", "Değerlendirme Bağlantısı", "Özet"], [["<em>İÜC.BİDB.SRÇ.XXX - Süreç Adı</em>", "<em>BP ve PA/GP kapsamı</em>", "<em>Etiket dağılımı</em>", "<em>Etiket dağılımı</em>", "<em>FRM.001 Değerlendirme #1</em>", "<em>Güçlü ve gelişime açık yönlerin özeti</em>"]]),
        "<h2>5. Etiket Dağılımları ve Eğilimler</h2>", table(["Gösterge", "Süreç / Dönem Sonucu", "Karşılaştırma", "Yorum"], [["<em>BP veya PA/GP etiketi</em>", "<em>Sonuç</em>", "<em>Önceki süreç/dönem veya kümülatif karşılaştırma</em>", "<em>Eğilim yorumu</em>"]]),
        "<h2>6. Önemli Bulgular</h2>", table(["Bulgu", "Tür", "Kaynak", "Yönlendirme / Durum", "Açıklama"], [["<em>Bulgu</em>", "<em>Tür</em>", "<em>Kaynak</em>", "<em>Yönlendirme</em>", "<em>Açıklama</em>"]]),
        "<h2>7. İyileştirme Fırsatları</h2>", table(["Fırsat", "Beklenen Fayda", "İlgili Süreç", "Yönlendirme"], [["<em>Fırsat</em>", "<em>Fayda</em>", "<em>Süreç</em>", "<em>Bağlantı</em>"]]),
        "<h2>8. Güçlü Uygulamalar</h2>", table(["Güçlü Uygulama", "Kaynak", "Koruma / Yaygınlaştırma Önerisi"], [["<em>Uygulama</em>", "<em>Kaynak</em>", "<em>Öneri</em>"]]),
        "<h2>9. Ölçüm Sonuçları</h2>", table(["Ölçüm", "Hedef", "Sonuç", "Durum / Yorum", "Veri Kaynağı"], [["<em>Ölçüm</em>", "<em>Hedef</em>", "<em>Sonuç</em>", "<em>Yorum</em>", "<em>Kaynak</em>"]]),
        "<h2>10. Doğrulanmış İyileştirme Sonuçları</h2>", p("Yalnızca SRÇ.018 kapsamında uygulanan değişikliğin SRÇ.018 değişiklik gözden geçirmesi tamamlanmış iyileştirmeler raporlanır. RPR.001 yeniden değerlendirme yapmaz; doğrulanmış sonucu ve kazanımı yönetim görünürlüğü için özetler."), table(["İyileştirme", "İlgili Süreç", "Etki", "Uygulama Önceliği", "Değişiklik Kaydı / Plan", "SRÇ.018 Gözden Geçirme Sonucu", "Doğrulanmış Kazanım", "Yaygınlaştırma"], [["<em>İyileştirme</em>", "<em>Süreç</em>", "<em>Yüksek / Orta / Düşük</em>", "<em>Yüksek / Orta / Düşük</em>", "<em>SRÇ.018 kaydı / PLN.002</em>", "<em>SRÇ.018 değişiklik gözden geçirme sonucu</em>", "<em>Gerçekleşen fayda</em>", "<em>LST.012 / doğal kanıt</em>"]]),
        "<h2>11. Sonuç ve Öneriler</h2>", p("Yönetim kararı, önceliklendirme ve sonraki dönem için öneriler yazılır."),
        "<h2>12. Sürüm Geçmişi</h2>", p("Taslak rapor güncellemeleri sürüm geçmişine kaydedilmez. İlk sürüm geçmişi kaydı, rapor onaylanıp v1.0 sürümüne geçirildiğinde oluşturulur."),
    ]), template=True)


def report_body() -> str:
    from update_rpr001_layout_and_maturity_placeholder import align_rpr001_layout
    return align_rpr001_layout("".join([
        "<h2>1. Rapor Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Rapor Kodu ve Adı", RPR001], ["Rapor Referansı", f"{PLN001}; {SRC005}; İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci; İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"], ["Rapor Sahibi", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Onaylayan", APPROVED_BY], ["Raporlama Dönemi", "Süreç çalışmaları boyunca kümülatif; yıllık yönetim özeti mart sonunda"], ["Durum", "Taslak"], ["Sürüm", "v0.1"], ["Son Güncelleme", "14-07-2026"]]),
        "<h2>2. Yönetici Özeti</h2>", p("Bu kümülatif rapor, değerlendirmesi tamamlanan süreçlerin BP ve PA/GP etiket dağılımlarını, önemli bulgularını, iyileştirme fırsatlarını ve güçlü uygulamalarını bir arada gösterir. Şu aşamada SRÇ.001, SRÇ.004 ve SRÇ.005 değerlendirmeleri rapora alınmıştır. Toplam puan veya tek bir genel süreç etiketi üretilmemiştir."),
        p("Ortak güçlü yönler; süreç ve destek dokümanlarının güncel şablonlarla tanımlanması, rol/iş ürünü/etkileşim yapısının kurulması ve Confluence ile sürüm kontrollü kaynakların birlikte kullanılmasıdır. Ortak gelişim alanları; gerçek dönemsel performans verisi, formal gözden geçirme/onay, hedef kitle bilgilendirmesi, yetkinlik/eğitim ve kaynak tahsis kanıtlarıdır."),
        "<h2>3. Kapsam ve Yöntem</h2>", p("Rapor yalnızca tamamlanan süreç değerlendirmelerini ve SRÇ.018 değişiklik gözden geçirmesiyle doğrulanmış iyileştirme sonuçlarını içerir. Her süreç için ilgili temel uygulamalar ile PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 göstergeleri değerlendirilmiş; YOK, ZAYIF, DAĞINIK, VAR ve KAPSAM DIŞI etiketleri kullanılmıştır. Kanıt eksikliği değerlendirmeyi durdurmamış, açıklama ve etikete yansıtılmıştır. İyileştirme başarısı RPR.001 içinde yeniden değerlendirilmez; kaynak SRÇ.018 sonucu özetlenir."),
        "<h2>4. Süreç Sonuç Özeti</h2>", table(["Süreç", "Değerlendirme Kapsamı", "BP Dağılımı", "PA / GP Dağılımı", "Değerlendirme Bağlantısı", "Özet"], [
            ["İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci", "SUP.7 BP1-BP8; PA 2.1-PA 3.2", "5 VAR; 3 DAĞINIK", "9 VAR; 9 DAĞINIK; 3 ZAYIF", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001) - Değerlendirme #1", "Doküman standartları, şablonlar ve teknik yayın/bakım yapısı güçlü; formal gözden geçirme, gerçek ölçüm, yetkinlik ve bilgilendirme kanıtları geliştirilmelidir."],
            ["İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci", "PIM.1 BP1-BP6; PA 2.1-PA 3.2", "4 VAR; 1 DAĞINIK; 1 YOK", "10 VAR; 7 DAĞINIK; 1 ZAYIF; 3 YOK", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.004) - Değerlendirme #1", "Süreç mimarisi, süreç paketleri, uyarlama, rol ve ölçüm tanımları güçlü; gerçek kullanım/performans, bilgilendirme ve yetkinlik kanıtları eksiktir."],
            [SRC005, "PIM.2 BP1-BP8; PA 2.1-PA 3.2", "6 VAR; 2 DAĞINIK", "11 VAR; 7 DAĞINIK; 2 ZAYIF; 1 YOK", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.005) - Değerlendirme #1", "Değerlendirme yöntemi, plan, etiketler, iş ürünleri ve kümülatif raporlama tanımlı; gerçek dönem taahhütleri, doğrulama, eğitim ve ilk performans sonuçları tamamlanmalıdır."],
        ]),
        "<h2>5. Etiket Dağılımları ve Eğilimler</h2>", table(["Gösterge", "SRÇ.001", "SRÇ.004", "SRÇ.005", "Yorum"], [["BP - VAR", "5", "4", "6", "Tanım ve doküman paketi bulunan alanlarda güçlü karşılama vardır."], ["BP - DAĞINIK", "3", "1", "2", "Uygulama, iletişim veya formal doğrulama kanıtları dağınıktır."], ["BP - YOK", "0", "1", "0", "SRÇ.004 kullanım verisi henüz oluşmamıştır."], ["PA/GP - VAR", "9", "10", "11", "Tanım, rol, iş ürünü, etkileşim ve altyapı bileşenleri güçlenmektedir."], ["PA/GP - DAĞINIK", "9", "7", "7", "Uygulama kanıtları ve formal kayıt bütünlüğü ortak gelişim alanıdır."], ["PA/GP - ZAYIF", "3", "1", "2", "Performans ayarlama, veri analizi ve bazı uygulama kanıtları başlangıç düzeyindedir."], ["PA/GP - YOK", "0", "3", "1", "Gerçek veri ve yetkinlik/eğitim kanıtı eksikleri görülmektedir."]]),
        "<h2>6. Önemli Bulgular</h2>", table(["Bulgu", "Tür", "Kaynak", "Yönlendirme / Durum", "Açıklama"], [["Gerçek performans verisi ve analiz sonuçlarının henüz oluşmaması", "Gözlem", "SRÇ.001, SRÇ.004 ve SRÇ.005 değerlendirmeleri", "İlgili Değerlendirme #1 kayıtlarında izleniyor", "LST.009 ölçümleri ilk gerçek dönemlerde işletilmelidir."], ["Formal gözden geçirme, bulgu ve kapanış kayıtlarının yetersizliği", "Gözlem", "SRÇ.001, SRÇ.004 ve SRÇ.005 değerlendirmeleri", "İlgili Değerlendirme #1 kayıtlarında izleniyor", "Yetkili gözden geçiren doğrulaması ve kapanış bilgileri tamamlanmalıdır."], ["Rol bazlı yetkinlik ve eğitim/katılım kanıtlarının eksikliği", "Gözlem", "PA 3.2 GP.3.2.3 sonuçları", "SRÇ.020 ihtiyacı değerlendirilecek", "Gerçek ihtiyaç oluştuğunda eğitim ve katılım kayıtları oluşturulmalıdır."], ["Hedef kitle ve rol/sorumluluk bilgilendirmelerinin doğrulanmaması", "Gözlem", "SRÇ.001 ve SRÇ.004 değerlendirmeleri", "LST.012 veya doğal kaynak kayıtlarıyla tamamlanacak", "Yayın kaydı ile gerçek bilgilendirme kanıtı ayrıştırılmalıdır."]]),
        "<h2>7. İyileştirme Fırsatları</h2>", table(["Fırsat", "Beklenen Fayda", "İlgili Süreç", "Yönlendirme"], [["Değerlendirme ve süreç sonuçlarının tek kümülatif raporda karşılaştırılabilir biçimde sürdürülmesi", "Yönetim görünürlüğü ve süreçler arası önceliklendirme", "SRÇ.005", "SRÇ.018'e aktarılacak"], ["PLN ve RPR doküman türleri için ortak şablon ve kodlama yapısının kurulması", "Plan ve raporların tutarlı, izlenebilir ve yeniden kullanılabilir olması", "SRÇ.001", "Bu çalışma kapsamında uygulanıyor"], ["Süreç değerlendirme sonuçlarının SRÇ.002 kalite yaklaşımına düzenli girdi sağlaması", "Kalite güvencesi ve süreç iyileştirmenin ortak veriyle yürütülmesi", "SRÇ.002 / SRÇ.005", "SRÇ.002 çalışmasında ele alınacak"]]),
        "<h2>8. Güçlü Uygulamalar</h2>", table(["Güçlü Uygulama", "Kaynak", "Koruma / Yaygınlaştırma Önerisi"], [["Güncel süreç şablonu ve süreç özel LST.007-LST.010/FRM.001 paket yapısı", "SRÇ.001 ve SRÇ.004 paketleri", "Sıradaki tüm süreçlerde aynı aktif şablon ailesi kullanılmalı."], ["Mermaid kaynak ve PNG görsellerinin birlikte saklanması", "SRÇ.001 ve SRÇ.004 süreç akışı/etkileşim sayfaları", "SRÇ.005 ve sonraki süreçlerde aynı düzen korunmalı."], ["Sayısal puan yerine gerekçeli etiket kullanılması", "PLN.001, PRS.003 ve FRM.001", "Değerlendirmelerde etiket sözlüğü ve kanıt açıklaması birlikte kullanılmalı."], ["Yerel viewer, dry-run ve kontrollü Confluence yayın zinciri", "Repository çalışma akışı", "Her süreç paketi yayınında aynı doğrulama zinciri uygulanmalı."]]),
        "<h2>9. Ölçüm Sonuçları</h2>", table(["Ölçüm", "Hedef", "Mevcut Sonuç", "Durum / Yorum", "Veri Kaynağı"], [["Planlanan değerlendirmelerin zamanında tamamlanma oranı", "En az %90", "Henüz yıllık gerçek dönem sonucu yok", "İlk planlı dönemde hesaplanacak", "PLN.001; RPR.001"], ["Tamamlama ölçütlerini karşılayan değerlendirme kayıtlarının oranı", "%100", "Henüz onaylı yıllık gerçek dönem sonucu yok", "Tamamlanan değerlendirmelerde kontrol edilecek", "FRM.001"], ["Bulguların zamanında yönlendirilme oranı", "5 iş günü içinde %100", "Henüz yönlendirme dönemi sonucu yok", "Gerçek yönlendirmeler oluştukça hesaplanacak", "FRM.001; SRÇ.017; SRÇ.018"]]),
        "<h2>10. Doğrulanmış İyileştirme Sonuçları</h2>", p("Bu bölüm yalnızca SRÇ.018 kapsamında uygulanan değişikliğin SRÇ.018 değişiklik gözden geçirmesi tamamlandığında güncellenir."), table(["İyileştirme", "İlgili Süreç", "Etki", "Uygulama Önceliği", "Değişiklik Kaydı / Plan", "SRÇ.018 Gözden Geçirme Sonucu", "Doğrulanmış Kazanım", "Yaygınlaştırma"], [["Henüz doğrulanmış tamamlanmış iyileştirme bulunmamaktadır.", "-", "-", "-", "-", "-", "-", "-"]]),
        "<h2>11. Sonuç ve Öneriler</h2>", p("Süreç tanım ve destek paketleri ilerledikçe kümülatif değerlendirme tabanı güçlenmektedir. Sıradaki süreçlerde aynı etiket, tamamlama ve yönlendirme kuralları uygulanmalı; gerçek kullanıma geçişle birlikte performans, bilgilendirme, yetkinlik ve formal gözden geçirme kanıtları doğal kaynak sistemlerden toplanmalıdır. RPR.001 her tamamlanan süreçten sonra ve doğrulanmış iyileştirme sonucu oluştukça güncellenmeli; tüm süreç çalışmaları tamamlandığında v1.0 Onaylı nihai rapora dönüştürülmelidir."),
        "<h2>12. Sürüm Geçmişi</h2>", p("Taslak güncellemeler sürüm geçmişinde tutulmaz. Rapor tüm süreç çalışmaları tamamlanarak onaylandığında v1.0 kaydı oluşturulacaktır."),
    ]))


def parent_register_body(kind: str, items: list[tuple[str, str, str]]) -> str:
    rows = []
    for i, (code, name, title) in enumerate(items, 1):
        link = f'<ac:link><ri:page ri:space-key="SSSS" ri:content-title="{e(title)}" /><ac:plain-text-link-body><![CDATA[İncele]]></ac:plain-text-link-body></ac:link>'
        rows.append([str(i), code, name, "Aktif" if kind != "Rapor" else "Taslak", link])
    return p(f"Bu sayfa, İÜC BİDB çalışmasında kullanılan {kind.lower()} dokümanları için kayıt tablosunu içerir.") + table(["Sıra No", f"{kind} Kodu", f"{kind} Adı", "Durum", "Erişim Linki"], rows)


def template_register_body() -> str:
    items = [
        ("İÜC.BİDB.FRM.001.Ş", "Süreç Gözden Geçirme Formu Şablonu", "İÜC.BİDB.FRM.001.Ş - Süreç Gözden Geçirme Formu Şablonu"),
        ("İÜC.BİDB.KLV.XXX.Ş", "Kılavuz ve Talimat Tanımı Şablonu", "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu"),
        ("İÜC.BİDB.LST.001.Ş", "Aktif Dokümanlar Listesi Şablonu", "İÜC.BİDB.LST.001.Ş - Aktif Dokümanlar Listesi Şablonu"),
        ("İÜC.BİDB.LST.003.Ş", "Doküman Gözden Geçirme Kaydı Şablonu", "İÜC.BİDB.LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu"),
        ("İÜC.BİDB.LST.005.Ş", "Yaşam Döngüsü Doküman Üretim Matrisi Şablonu", "İÜC.BİDB.LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu"),
        ("İÜC.BİDB.LST.006.Ş", "Standart Süreç Envanteri Şablonu", "İÜC.BİDB.LST.006.Ş - Standart Süreç Envanteri Şablonu"),
        ("İÜC.BİDB.LST.007.Ş", "Süreç Etkileşim Matrisi Şablonu", "İÜC.BİDB.LST.007.Ş - Süreç Etkileşim Matrisi Şablonu"),
        ("İÜC.BİDB.LST.008.Ş", "İş Ürünleri ve Kalite Kriterleri Listesi Şablonu", "İÜC.BİDB.LST.008.Ş - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu"),
        ("İÜC.BİDB.LST.009.Ş", "Süreç Performans Ölçüm Seti Şablonu", "İÜC.BİDB.LST.009.Ş - Süreç Performans Ölçüm Seti Şablonu"),
        ("İÜC.BİDB.LST.010.Ş", "Süreç Rol Yetki ve RACI Matrisi Şablonu", "İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu"),
        ("İÜC.BİDB.LST.011.Ş", "Repository Yapısı Şablonu", "İÜC.BİDB.LST.011.Ş - Repository Yapısı Şablonu"),
        ("İÜC.BİDB.LST.012.Ş", "Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu", "İÜC.BİDB.LST.012.Ş - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu"),
        (PLN001_TEMPLATE_CODE, "Süreç Kalite Planı Şablonu", PLN001_TEMPLATE_TITLE),
        (PLN002_TEMPLATE_CODE, "Süreç İyileştirme Planı Şablonu", PLN002_TEMPLATE_TITLE),
        ("İÜC.BİDB.PRS.XXX.Ş", "Prosedür Tanımı Şablonu", "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu"),
        (RPR001_TEMPLATE_CODE, "Süreç Performansları Raporu Şablonu", RPR001_TEMPLATE_TITLE),
        ("İÜC.BİDB.SRÇ.XXX.Ş", "Süreç Tanımı Şablonu", "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu"),
    ]
    rows = []
    for i, (code, name, title) in enumerate(items, 1):
        link = f'<ac:link><ri:page ri:content-title="{e(title)}" /><ac:plain-text-link-body><![CDATA[İncele]]></ac:plain-text-link-body></ac:link>'
        rows.append([str(i), code, name, "Aktif", link])
    return p("Bu sayfa, İÜC BİDB çalışmasında kullanılan doküman, kayıt ve form şablonları için kayıt tablosunu içerir.") + table(["Sıra No", "Şablon Kodu", "Şablon Adı", "Durum", "Erişim Linki"], rows)


def replace_section_table_rows(storage: str, heading_fragment: str, rows_html: str) -> str:
    headings = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.I | re.S))
    target = None
    for i, match in enumerate(headings):
        plain = re.sub(r"<[^>]+>", "", html.unescape(match.group(1)))
        if heading_fragment.casefold() in plain.casefold():
            target = (match.end(), headings[i + 1].start() if i + 1 < len(headings) else len(storage))
            break
    if target is None:
        raise RuntimeError(f"Section not found: {heading_fragment}")
    start, end = target
    section = storage[start:end]
    body_match = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
    if not body_match:
        raise RuntimeError(f"Table body not found in section: {heading_fragment}")
    new_section = section[:body_match.start(2)] + rows_html + section[body_match.end(2):]
    return storage[:start] + new_section + storage[end:]


def td_row(cells: list[str]) -> str:
    return "<tr>" + "".join(f'<td class="confluenceTd">{cell}</td>' for cell in cells) + "</tr>"


def update_lst001(storage: str) -> str:
    procedures = [
        ["İÜC.BİDB.PRS.001", "Yazılım Projeleri Dokümantasyon Prosedürü", "SRÇ.001", "Levent BAYEZİT - Proje Yöneticisi", "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"],
        ["İÜC.BİDB.PRS.002", "Süreç Tasarım Prosedürü", "SRÇ.004", PROCESS_OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"],
        ["İÜC.BİDB.PRS.003", "Süreç Değerlendirme Prosedürü", "SRÇ.005", PROCESS_OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"],
        ["İÜC.BİDB.PRS.004", "Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü", "SRÇ.006 / SRÇ.018", PROCESS_OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"],
    ]
    storage = replace_section_table_rows(storage, "4. Prosedürler", "".join(td_row(row) for row in procedures))
    storage = storage.replace("İÜC.BİDB.RPR.XXX.Ş", RPR001_TEMPLATE_CODE)
    storage = storage.replace(">Rapor Şablonu</td>", ">Süreç Performansları Raporu Şablonu</td>")
    storage = storage.replace(
        f'<td class="confluenceTd">{RPR001_TEMPLATE_CODE}</td><td class="confluenceTd">Süreç Performansları Raporu Şablonu</td><td class="confluenceTd">Doküman üretimi</td>',
        f'<td class="confluenceTd">{RPR001_TEMPLATE_CODE}</td><td class="confluenceTd">Süreç Performansları Raporu Şablonu</td><td class="confluenceTd">RPR.001 üretimi</td>',
    )
    # Keep the plan and report template records inside the Section 6 table. Earlier
    # generator versions appended these rows after the closing table tag.
    for code_pattern in [r"BİDB\.PLN\.(?:XXX|001|002)\.Ş", r"BİDB\.RPR\.(?:XXX|001)\.Ş"]:
        storage = re.sub(
            rf'<tr>(?:(?!</tr>).)*{code_pattern}(?:(?!</tr>).)*</tr>',
            "",
            storage,
            flags=re.I | re.S,
        )
    additions = "".join([
        td_row([PLN001_TEMPLATE_CODE, "Süreç Kalite Planı Şablonu", "PLN.001 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"]),
        td_row([PLN002_TEMPLATE_CODE, "Süreç İyileştirme Planı Şablonu", "PLN.002 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"]),
        td_row([RPR001_TEMPLATE_CODE, "Süreç Performansları Raporu Şablonu", "RPR.001 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"]),
    ])
    headings = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.I | re.S))
    for i, match in enumerate(headings):
        if "6. Şablonlar" in html.unescape(re.sub(r"<[^>]+>", "", match.group(1))):
            start, end = match.end(), headings[i + 1].start()
            section = storage[start:end]
            body_match = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
            if not body_match:
                raise RuntimeError("Table body not found in section: 6. Şablonlar")
            section = section[:body_match.end(2)] + additions + section[body_match.end(2):]
            storage = storage[:start] + section + storage[end:]
            break
    plan_row = td_row(["İÜC.BİDB.PLN.001", "Süreç Kalite Planı", "Süreç kalitesi değerlendirme yaklaşımı", PREPARED_BY, "Aktif", "v1.0", "08 - Planlar"])
    storage = replace_section_table_rows(storage, "9. Planlar", plan_row)
    if "10. Raporlar" not in html.unescape(storage):
        storage = storage.replace("<h2>10. Kapsam Dışı Dokümanlar</h2>", "<h2>10. Raporlar</h2>" + table(["Doküman Kodu", "Doküman Adı", "Kapsam", "Sahibi", "Durum", "Sürüm", "Konum"], [["İÜC.BİDB.RPR.001", "Süreç Performansları Raporu", "Tamamlanan süreç değerlendirmelerinin kümülatif raporu", PREPARED_BY, "Taslak", "v0.1", "09 - Raporlar"]]) + "<h2>11. Kapsam Dışı Dokümanlar</h2>")
        storage = storage.replace("<h2>11. Sürüm Geçmişi</h2>", "<h2>12. Sürüm Geçmişi</h2>")
    return storage


def update_documentation_assets() -> None:
    targets = [
        PAGE_ROOT / "07-prosedurler/iuc-bidb-prs-001-yazilim-projeleri-dokumantasyon-proseduru",
        PAGE_ROOT / "05-kilavuzlar/iuc-bidb-klv-001-dokuman-yazim-kurallari-talimati",
        PAGE_ROOT / "03-kayitlar-ve-listeler/iuc-bidb-lst-011-repository-yapisi",
    ]
    for page_dir in targets:
        storage_path = page_dir / "body.storage.xhtml"
        storage = storage_path.read_text(encoding="utf-8")
        if "prs-001" in str(page_dir):
            storage = storage.replace("politika, plan ve genel listeler", "politika, plan, rapor ve genel listeler")
            storage = storage.replace("Süreç, prosedür, kılavuz, politika ve plan</td>", "Süreç, prosedür, kılavuz, politika, plan ve rapor</td>")
            storage = storage.replace("S&uuml;re&ccedil;, prosed&uuml;r, kılavuz, politika ve plan</td>", "S&uuml;re&ccedil;, prosed&uuml;r, kılavuz, politika, plan ve rapor</td>")
        elif "klv-001" in str(page_dir):
            storage = storage.replace("<li>planlar,</li><li>süreçlere bağlı", "<li>planlar,</li><li>raporlar,</li><li>süreçlere bağlı")
            storage = storage.replace("<li>planlar,</li><li>s&uuml;re&ccedil;lere bağlı", "<li>planlar,</li><li>raporlar,</li><li>s&uuml;re&ccedil;lere bağlı")
            storage = storage.replace("liste, plan, politika ve kayıt dok&uuml;manlarında", "liste, plan, politika, rapor ve kayıt dok&uuml;manlarında")
            storage = storage.replace("kılavuz, plan, politika veya benzeri", "kılavuz, plan, politika, rapor veya benzeri")
            storage = storage.replace("İ&Uuml;C.BİDB.PLN.XXX.Ş - Plan Şablonu", "İ&Uuml;C.BİDB.PLN.001.Ş - S&uuml;re&ccedil; Kalite Planı Şablonu")
            storage = storage.replace("İÜC.BİDB.PLN.XXX.Ş - Plan Şablonu", PLN001_TEMPLATE_TITLE)
            storage = storage.replace(
                "İ&Uuml;C.BİDB.PLN.001.Ş - S&uuml;re&ccedil; Kalite Planı Şablonu</td><td>Plan dok&uuml;manları i&ccedil;in yapı referansı",
                "İ&Uuml;C.BİDB.PLN.001.Ş - S&uuml;re&ccedil; Kalite Planı Şablonu</td><td>İ&Uuml;C.BİDB.PLN.001 i&ccedil;in yapı referansı",
            )
            storage = storage.replace(
                f"{PLN001_TEMPLATE_TITLE}</td><td>Plan dokümanları için yapı referansı",
                f"{PLN001_TEMPLATE_TITLE}</td><td>İÜC.BİDB.PLN.001 için yapı referansı",
            )
            storage = storage.replace("İ&Uuml;C.BİDB.RPR.XXX.Ş - Rapor Şablonu", "İ&Uuml;C.BİDB.RPR.001.Ş - S&uuml;re&ccedil; Performansları Raporu Şablonu")
            storage = storage.replace("İÜC.BİDB.RPR.XXX.Ş - Rapor Şablonu", RPR001_TEMPLATE_TITLE)
            storage = storage.replace(
                "İ&Uuml;C.BİDB.RPR.001.Ş - S&uuml;re&ccedil; Performansları Raporu Şablonu</td><td>Rapor dok&uuml;manları i&ccedil;in yapı referansı",
                "İ&Uuml;C.BİDB.RPR.001.Ş - S&uuml;re&ccedil; Performansları Raporu Şablonu</td><td>İ&Uuml;C.BİDB.RPR.001 i&ccedil;in yapı referansı",
            )
            storage = storage.replace(
                f"{RPR001_TEMPLATE_TITLE}</td><td>Rapor dokümanları için yapı referansı",
                f"{RPR001_TEMPLATE_TITLE}</td><td>İÜC.BİDB.RPR.001 için yapı referansı",
            )
            structure_rows = "<tr><td>Plan</td><td><code>1. Plan Bilgileri</code> bölümüyle başlar.</td><td>Hedef, yaklaşım, takvim, rol, tamamlama, raporlama ve kayıt yapısını tanımlar; takip registerı değildir.</td></tr><tr><td>Rapor</td><td><code>1. Rapor Bilgileri</code> bölümüyle başlar.</td><td>Kapsam, sonuç, bulgu, ölçüm ve önerileri izlenebilir biçimde sunar.</td></tr>"
            while structure_rows + structure_rows in storage:
                storage = storage.replace(structure_rows + structure_rows, structure_rows)
            if structure_rows not in storage:
                storage = storage.replace("<tr><td>Şablon</td><td><code>0. Şablon Hakkında</code>", structure_rows + "<tr><td>Şablon</td><td><code>0. Şablon Hakkında</code>")
            storage = storage.replace("<tr><td>Liste</td><td>1. Liste Özeti</td>", "<tr><td>Plan</td><td>1. Plan Bilgileri</td><td>Kurum; plan kodu ve adı; plan referansı; plan sahibi; dönem; durum; sürüm; yürürlük tarihi</td></tr><tr><td>Rapor</td><td>1. Rapor Bilgileri</td><td>Kurum; rapor kodu ve adı; rapor referansı; rapor sahibi; dönem; durum; sürüm</td></tr><tr><td>Liste</td><td>1. Liste Özeti</td>")
            storage = storage.replace("<tr><td>Şablon</td><td>İÜC.BİDB.[TÜR].XXX.Ş</td>", "<tr><td>Plan</td><td>İÜC.BİDB.PLN.XXX</td><td>İÜC.BİDB.PLN.001 - Süreç Kalite Planı</td></tr><tr><td>Rapor</td><td>İÜC.BİDB.RPR.XXX</td><td>İÜC.BİDB.RPR.001 - Süreç Performansları Raporu</td></tr><tr><td>Şablon</td><td>İÜC.BİDB.[TÜR].XXX.Ş</td>")
            if "İ&Uuml;C.BİDB.PLN.001.Ş" not in storage:
                marker = "<tr><td>İ&Uuml;C.BİDB.LST.008.Ş / LST.009.Ş / LST.010.Ş</td>"
                additions = (
                    "<tr><td>İ&Uuml;C.BİDB.PLN.001.Ş - S&uuml;re&ccedil; Kalite Planı Şablonu</td><td>İ&Uuml;C.BİDB.PLN.001 i&ccedil;in yapı referansı</td></tr>"
                    "<tr><td>İ&Uuml;C.BİDB.RPR.001.Ş - S&uuml;re&ccedil; Performansları Raporu Şablonu</td><td>İ&Uuml;C.BİDB.RPR.001 i&ccedil;in yapı referansı</td></tr>"
                )
                storage = storage.replace(marker, additions + marker)
            if "İ&Uuml;C.BİDB.PLN.XXX</td>" not in storage:
                marker = "<tr><td>Şablon</td><td>İ&Uuml;C.BİDB.[T&Uuml;R].XXX.Ş</td>"
                additions = (
                    "<tr><td>Plan</td><td>İ&Uuml;C.BİDB.PLN.XXX</td><td>İ&Uuml;C.BİDB.PLN.001 - S&uuml;re&ccedil; Kalite Planı</td></tr>"
                    "<tr><td>Rapor</td><td>İ&Uuml;C.BİDB.RPR.XXX</td><td>İ&Uuml;C.BİDB.RPR.001 - S&uuml;re&ccedil; Performansları Raporu</td></tr>"
                )
                storage = storage.replace(marker, additions + marker)
            if "<td>1. Plan Bilgileri</td>" not in storage:
                marker = "<tr><td>Liste</td><td>1. Liste &Ouml;zeti</td>"
                additions = (
                    "<tr><td>Plan</td><td>1. Plan Bilgileri</td><td>Kurum; plan kodu ve adı; plan referansı; plan sahibi; d&ouml;nem; durum; s&uuml;r&uuml;m; y&uuml;r&uuml;rl&uuml;k tarihi</td></tr>"
                    "<tr><td>Rapor</td><td>1. Rapor Bilgileri</td><td>Kurum; rapor kodu ve adı; rapor referansı; rapor sahibi; d&ouml;nem; durum; s&uuml;r&uuml;m</td></tr>"
                )
                storage = storage.replace(marker, additions + marker)
        else:
            storage = storage.replace("26 süreç alt klasörü", "LST.006 içinde tanımlanan güncel süreç setinin alt klasörleri")
            storage = storage.replace("26 s&uuml;re&ccedil; alt klas&ouml;r&uuml;", "LST.006 i&ccedil;inde tanımlanan g&uuml;ncel s&uuml;re&ccedil; setinin alt klas&ouml;rleri")
            if "<code>09 - Raporlar</code>" not in storage:
                additions = "".join([
                    td_row(["<code>04 - Formlar</code>", "Genel form dok&uuml;manları", "FRM şablon ve ortak formlar", "Dok&uuml;man Sorumlusu", "Form yapısı değiştiğinde g&uuml;ncellenir"]),
                    td_row(["<code>05 - Kılavuzlar</code>", "Kurumsal kılavuz ve talimatlar", "KLV dok&uuml;manları", "İlgili S&uuml;re&ccedil; Sahibi", "Kılavuz değiştiğinde g&uuml;ncellenir"]),
                    td_row(["<code>06 - Politikalar</code>", "Kurumsal politikalar", "PLT dok&uuml;manları", "İlgili S&uuml;re&ccedil; Sahibi", "Politika değiştiğinde g&uuml;ncellenir"]),
                    td_row(["<code>07 - Prosed&uuml;rler</code>", "Kurumsal prosed&uuml;rler", "PRS dok&uuml;manları", "İlgili S&uuml;re&ccedil; Sahibi", "Prosed&uuml;r değiştiğinde g&uuml;ncellenir"]),
                    td_row(["<code>08 - Planlar</code>", "Kurumsal planlar", "PLN dok&uuml;manları", "İlgili Plan Sahibi", "Plan değiştiğinde g&uuml;ncellenir"]),
                    td_row(["<code>09 - Raporlar</code>", "Kurumsal raporlar", "RPR dok&uuml;manları", "İlgili Rapor Sahibi", "Rapor g&uuml;ncellendik&ccedil;e s&uuml;rd&uuml;r&uuml;l&uuml;r"]),
                ])
                storage = re.sub(
                    r"<tr>\s*<td>\s*<code>90 - Denetim Hazırlık</code>",
                    lambda match: additions + match.group(0),
                    storage,
                    count=1,
                )
            storage = storage.replace("<tr>\n<td>90 - Denetim Hazırlık</td>", "<tr><td>04 - Formlar</td><td>Genel form dokümanları</td><td>FRM şablon ve ortak formlar</td><td>Doküman Sorumlusu</td><td>Form yapısı değiştiğinde güncellenir</td></tr><tr><td>06 - Politikalar</td><td>Kurumsal politikalar</td><td>PLT dokümanları</td><td>İlgili Süreç Sahibi</td><td>Politika değiştiğinde güncellenir</td></tr><tr><td>07 - Prosedürler</td><td>Kurumsal prosedürler</td><td>PRS dokümanları</td><td>İlgili Süreç Sahibi</td><td>Prosedür değiştiğinde güncellenir</td></tr><tr><td>08 - Planlar</td><td>Kurumsal planlar</td><td>PLN dokümanları</td><td>İlgili Plan Sahibi</td><td>Plan değiştiğinde güncellenir</td></tr><tr><td>09 - Raporlar</td><td>Kurumsal raporlar</td><td>RPR dokümanları</td><td>İlgili Rapor Sahibi</td><td>Rapor güncellendiğinde sürdürülür</td></tr><tr>\n<td>90 - Denetim Hazırlık</td>")
            storage = re.sub(r"<tr>\s*<td>91 - İç Denetimler/Süreç Gözden Geçirmeleri</td>.*?</tr>", "<tr><td>91 - İç Denetimler/Süreç Gözden Geçirmeleri</td><td>Doldurulmuş süreç değerlendirme kayıtları</td><td>İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu ([SRÇ.xxx]) - Değerlendirme #1</td><td>Kalite Danışmanı</td><td>Değerlendirme yürütüldükçe aynı kayıt üzerinde güncellenir</td></tr>", storage, flags=re.S)
            storage = re.sub(r"<tr>(?:(?!</tr>).)*S&uuml;re&ccedil; bazlı LST\.004(?:(?!</tr>).)*</tr>", td_row(["<code>91 - İ&ccedil; Denetimler/S&uuml;re&ccedil; G&ouml;zden Ge&ccedil;irmeleri</code>", "Doldurulmuş s&uuml;re&ccedil; değerlendirme kayıtları", "<code>İ&Uuml;C.BİDB.FRM.001 - S&uuml;re&ccedil; G&ouml;zden Ge&ccedil;irme Formu ([SR&Ccedil;.xxx]) - Değerlendirme #1</code>", "Kalite Danışmanı", "Değerlendirme y&uuml;r&uuml;t&uuml;ld&uuml;k&ccedil;e aynı kayıt &uuml;zerinde g&uuml;ncellenir"]), storage, flags=re.S)
            storage = re.sub(r"<tr>(?:(?!</tr>).)*S&uuml;re&ccedil; g&ouml;zden ge&ccedil;irme matrisi(?:(?!</tr>).)*</tr>", td_row(["S&uuml;re&ccedil; g&ouml;zden ge&ccedil;irme formu", "<code>İ&Uuml;C.BİDB.FRM.001 - S&uuml;re&ccedil; G&ouml;zden Ge&ccedil;irme Formu (İ&Uuml;C.BİDB.SR&Ccedil;.xxx) - Değerlendirme #1</code>", "<code>91 - İ&ccedil; Denetimler/S&uuml;re&ccedil; G&ouml;zden Ge&ccedil;irmeleri</code>"]), storage, flags=re.S)
            storage = storage.replace("LST.001, LST.002, LST.003 veya LST.004", "LST.001, LST.002, LST.003 veya FRM.001")
            storage = storage.replace("Süreç gözden geçirme matrisi", "Süreç gözden geçirme formu")
            storage = storage.replace("İÜC.BİDB.LST.004 - Süreç Gözden Geçirme Matrisi (İÜC.BİDB.SRÇ.xxx).md", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.xxx) - Değerlendirme #1")
            storage = storage.replace("03 - Kayıtlar ve Listeler | PIM.1.BP1, GP 3.1.2", "İlgili süreç sayfası | PIM.1.BP1, GP 3.1.2")
            storage = storage.replace("Ortak kayıt ve şablonlar kendi ana klasörlerinde tutulmaya devam eder. Örneğin LST.001, LST.006, LST.007, LST.011 ve LST.012 03 - Kayıtlar ve Listeler altında; ŞBL dokümanları 02 - Şablonlar altında tutulur.", "Ortak kayıt, şablon, prosedür, plan ve raporlar kendi ana klasörlerinde tutulur. Süreç özel LST.007-LST.010 ve boş FRM.001 ilgili süreç altında; doldurulmuş değerlendirmeler 91 - İç Denetimler / Süreç Gözden Geçirmeleri altında saklanır.")
        storage_path.write_text(storage, encoding="utf-8")
        title = (yaml.safe_load((page_dir / "page.yaml").read_text(encoding="utf-8")) or {})["title"]
        (page_dir / "body.view.html").write_text(build_view(title, storage), encoding="utf-8")

    lst001_dir = PAGE_ROOT / "03-kayitlar-ve-listeler/iuc-bidb-lst-001-aktif-dokumanlar-listesi"
    storage = update_lst001((lst001_dir / "body.storage.xhtml").read_text(encoding="utf-8"))
    (lst001_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (lst001_dir / "body.view.html").write_text(build_view("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi", storage), encoding="utf-8")


def normalize_src001_assessment_to_labels() -> None:
    page_dir = PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001-degerlendirme-1"
    for name in ["body.storage.xhtml", "body.view.html"]:
        path = page_dir / name
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"%\d+\s*-\s*(VAR|ZAYIF|DAĞINIK|YOK|KAPSAM DIŞI)", r"\1", content)
        content = content.replace("BP karşılama ortalaması %79, PA/GP karşılama ortalaması %68 ve birleşik gösterge %74 - VAR'dır.", "BP dağılımı 5 VAR ve 3 DAĞINIK; PA/GP dağılımı 9 VAR, 9 DAĞINIK ve 3 ZAYIF'tır. Toplam puan veya tek bir süreç etiketi üretilmemiştir.")
        path.write_text(content, encoding="utf-8")


def upsert_index(page_dirs: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(d.relative_to(CONFLUENCE)).replace("\\", "/") for d in page_dirs}
    legacy_pln_template_rel = f"{TEMPLATES_REL}/iuc-bidb-pln-xxx-s-plan-sablonu"
    legacy_rpr_template_rel = f"{TEMPLATES_REL}/iuc-bidb-rpr-xxx-s-rapor-sablonu"
    pages[:] = [
        x for x in pages
        if x.get("relative_path") not in rels
        and x.get("relative_path") != legacy_pln_template_rel
        and x.get("relative_path") != legacy_rpr_template_rel
    ]
    for d in page_dirs:
        meta = yaml.safe_load((d / "page.yaml").read_text(encoding="utf-8")) or {}
        rel = meta["relative_path"]
        pages.append({"page_id": str(meta.get("page_id") or ""), "title": meta["title"], "parent_id": str(meta.get("parent_id") or ""), "depth": meta["depth"], "relative_path": rel, "slug": meta["slug"], "storage_file": f"{rel}/body.storage.xhtml", "view_file": f"{rel}/body.view.html"})
    pages.sort(key=lambda x: (int(x.get("depth") or 0), str(x.get("relative_path") or "")))
    index["total_page_count"] = len(pages)
    index["exported_at"] = datetime.now(timezone.utc).isoformat()
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for parent in [PAGE_ROOT / "02-sablonlar", PAGE_ROOT / "07-prosedurler", PAGE_ROOT / "08-planlar", PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri", CONFLUENCE / SRC005_REL, PAGE_ROOT, CONFLUENCE / REPORTS_REL]:
        meta_path = parent / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        parent_stable = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
        meta["children_count"] = sum(1 for x in pages if str(x.get("parent_id") or "") == parent_stable)
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def validate(new_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC005_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if headings != expected:
        raise RuntimeError(f"SRÇ.005 heading mismatch: {headings}")
    reference = process.split("<h2>4. Referanslar</h2>", 1)[1].split("<h2>5.", 1)[0]
    if len(re.findall(r"<tr>", reference)) != 4:
        raise RuntimeError("SRÇ.005 must have exactly three process references")
    if any(term in process for term in ["26 süreç", "LST.004", "Soru Bankası"]):
        raise RuntimeError("SRÇ.005 contains a forbidden fixed count, legacy LST.004 or project name")
    for bp, _, _ in PIM2_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    report = (CONFLUENCE / REPORTS_REL / "iuc-bidb-rpr-001-surec-performanslari-raporu/body.storage.xhtml").read_text(encoding="utf-8")
    if "toplam puan" not in report.casefold() or "Değerlendirme Bağlantısı" not in report:
        raise RuntimeError("RPR.001 scoring/link rules missing")
    for d in new_dirs:
        for filename in ["page.yaml", "body.storage.xhtml", "body.view.html"]:
            if not (d / filename).exists():
                raise RuntimeError(f"Missing page artifact: {d / filename}")


def write_report() -> None:
    report = ROOT / "reports/src005_process_assessment_package_report.md"
    report.write_text("""# SRÇ.005 Süreç Değerlendirme Paketi Yerel Raporu

Tarih: 14-07-2026

## Oluşturulan / Güncellenen Yapı

- SRÇ.005 süreç tanımı PIM.2 amacı, üç sonucu ve BP1-BP8 izlenebilirliğiyle oluşturuldu.
- Süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 aktif şablon yapılarına göre oluşturuldu.
- SRÇ.005 Değerlendirme #1 aynı kayıt yaklaşımıyla oluşturuldu; sayısal puan kullanılmadı.
- PRS.003 Süreç Değerlendirme Prosedürü oluşturuldu.
- PLN.001.Ş Süreç Kalite Planı Şablonu ve PLN.001 Süreç Kalite Planı oluşturuldu; plan takip registerı olarak kurgulanmadı.
- RPR.001.Ş Süreç Performansları Raporu Şablonu ve kümülatif RPR.001 Süreç Performansları Raporu oluşturuldu.
- SRÇ.001 değerlendirmesindeki sayısal puan önekleri kaldırılarak etiket-only yapıya geçirildi.
- SRÇ.001 dokümantasyon varlıklarında PLN/RPR kodları ve 09 - Raporlar yerleşimi işlendi; LST.004 ve sabit süreç sayısı ifadeleri temizlendi.

## Görsel Doğrulama

- SRÇ.005 süreç akışı ve LST.007 etkileşim diyagramı Mermaid Online Editor çıktısı temel alınarak PNG biçiminde attachment klasörlerine yerleştirildi.
- Her iki sayfada da üstte PNG görseli, altta Mermaid kaynak kodu korunmaktadır.

## Yayın Durumu

- Bu çalışma yalnızca yerel repository ve viewer hazırlığıdır.
- Confluence yazma işlemi yapılmamıştır.
""", encoding="utf-8")


def main() -> None:
    src_dir = CONFLUENCE / SRC005_REL
    attachments = src_dir / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    (attachments / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")

    write_page(src_dir, SRC005, "137265784", "01 - Süreç Dokümanları", 2, process_body(False), process_body(True))

    pages: list[Path] = [src_dir]
    children = [
        ("iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-005", "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.005)", lst007_body(False), lst007_body(True)),
        ("iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-005", "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.005)", lst008_body(), None),
        ("iuc-bidb-lst-009-surec-performans-olcum-seti-iuc-bidb-src-005", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.005)", lst009_body(), None),
        ("iuc-bidb-lst-010-surec-rol-yetki-ve-raci-matrisi-iuc-bidb-src-005", "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.005)", lst010_body(), None),
    ]
    for slug, title, storage, view in children:
        d = src_dir / slug
        write_page(d, title, SRC005_ID, SRC005, 3, storage, view)
        pages.append(d)
        if "lst-007" in slug:
            ad = d / "attachments"
            ad.mkdir(exist_ok=True)
            (ad / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")

    blank_dir = src_dir / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-005"
    write_page(blank_dir, "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.005)", SRC005_ID, SRC005, 3, blank_review_body())
    pages.append(blank_dir)

    assessment_dir = CONFLUENCE / REVIEWS_REL / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-005-degerlendirme-1"
    write_page(assessment_dir, "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.005) - Değerlendirme #1", REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_body())
    pages.append(assessment_dir)

    prs_dir = CONFLUENCE / PROCEDURES_REL / "iuc-bidb-prs-003-surec-degerlendirme-proseduru"
    write_page(prs_dir, PRS003, PROCEDURES_ID, "07 - Prosedürler", 2, procedure_body())
    pages.append(prs_dir)

    pln_template_dir = CONFLUENCE / TEMPLATES_REL / PLN001_TEMPLATE_SLUG
    write_page(pln_template_dir, PLN001_TEMPLATE_TITLE, TEMPLATES_ID, "02 - Şablonlar", 2, plan_template_body())
    pages.append(pln_template_dir)
    rpr_template_dir = CONFLUENCE / TEMPLATES_REL / RPR001_TEMPLATE_SLUG
    write_page(rpr_template_dir, RPR001_TEMPLATE_TITLE, TEMPLATES_ID, "02 - Şablonlar", 2, report_template_body())
    pages.append(rpr_template_dir)

    plan_dir = CONFLUENCE / PLANS_REL / "iuc-bidb-pln-001-surec-kalite-plani"
    write_page(plan_dir, PLN001, PLANS_ID, "08 - Planlar", 2, plan_body())
    pages.append(plan_dir)

    reports_dir = CONFLUENCE / REPORTS_REL
    write_page(reports_dir, "09 - Raporlar", ROOT_ID, "İÜC BİDB SPICE 2026 Level 3", 1, parent_register_body("Rapor", [("İÜC.BİDB.RPR.001", "Süreç Performansları Raporu", RPR001)]))
    pages.append(reports_dir)
    report_dir = reports_dir / "iuc-bidb-rpr-001-surec-performanslari-raporu"
    report_parent = f"local:{REPORTS_REL}"
    write_page(report_dir, RPR001, report_parent, "09 - Raporlar", 2, report_body())
    pages.append(report_dir)

    # Refresh parent register pages with the complete active sets.
    parent_pages = [
        (PAGE_ROOT / "02-sablonlar", "02 - Şablonlar", template_register_body()),
        (PAGE_ROOT / "07-prosedurler", "07 - Prosedürler", parent_register_body("Prosedür", [("İÜC.BİDB.PRS.001", "Yazılım Projeleri Dokümantasyon Prosedürü", "İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), ("İÜC.BİDB.PRS.002", "Süreç Tasarım Prosedürü", "İÜC.BİDB.PRS.002 - Süreç Tasarım Prosedürü"), ("İÜC.BİDB.PRS.003", "Süreç Değerlendirme Prosedürü", PRS003), ("İÜC.BİDB.PRS.004", "Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü", PRS004)])),
        (PAGE_ROOT / "08-planlar", "08 - Planlar", parent_register_body("Plan", [("İÜC.BİDB.PLN.001", "Süreç Kalite Planı", PLN001)])),
    ]
    for d, title, storage in parent_pages:
        (d / "body.storage.xhtml").write_text(storage + "\n", encoding="utf-8")
        (d / "body.view.html").write_text(build_view(title, storage), encoding="utf-8")
        pages.append(d)

    normalize_src001_assessment_to_labels()
    update_documentation_assets()
    pages.extend([
        PAGE_ROOT / "03-kayitlar-ve-listeler/iuc-bidb-lst-001-aktif-dokumanlar-listesi",
        PAGE_ROOT / "03-kayitlar-ve-listeler/iuc-bidb-lst-011-repository-yapisi",
        PAGE_ROOT / "05-kilavuzlar/iuc-bidb-klv-001-dokuman-yazim-kurallari-talimati",
        PAGE_ROOT / "07-prosedurler/iuc-bidb-prs-001-yazilim-projeleri-dokumantasyon-proseduru",
        PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001-degerlendirme-1",
    ])

    # De-duplicate while preserving order.
    unique: list[Path] = []
    seen: set[Path] = set()
    for d in pages:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    upsert_index(unique)
    validate(unique)
    write_report()
    print(f"[DONE] SRÇ.005 package materialized: {len(unique)} page directories")


if __name__ == "__main__":
    main()
