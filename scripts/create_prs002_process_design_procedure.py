#!/usr/bin/env python3
"""Create the local PRS.002 Process Design Procedure draft from PRS.XXX.Ş."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE = ROOT / "confluence"
INDEX_PATH = CONFLUENCE / "index.yaml"
SLUG = "prs-002-surec-tasarim-proseduru"
RELATIVE_PATH = f"pages/000-root-iuc-bidb-spice-2026-level-3/07-prosedurler/{SLUG}"
PAGE_DIR = CONFLUENCE / RELATIVE_PATH
REPORT = ROOT / "reports/prs002_process_design_local_draft.md"

TITLE = "PRS.002 - Süreç Tasarım Prosedürü"
PARENT_ID = "137265790"
PARENT_TITLE = "07 - Prosedürler"
PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
OWNER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
REVIEWER = "Levent Bayezit - Proje Yöneticisi"
APPROVER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
DRAFT_DATE = "14-07-2026"


CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3{color:#0f172a;line-height:1.25}h1{margin:0 0 24px;padding-bottom:12px;border-bottom:1px solid #d8dee4}h2{margin:1.45em 0 .55em}
p{margin:0 0 12px}ul{margin:8px 0 16px;padding-left:24px}li{margin:4px 0}
.table-wrap{overflow-x:auto;margin:16px 0}table{width:100%;border-collapse:collapse;table-layout:auto}th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}th{background:#f6f8fa;font-weight:600;text-align:left}
code{background:#f6f8fa;border:1px solid #d8dee4;border-radius:4px;padding:1px 4px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em}
.draft{display:inline-block;border-radius:3px;padding:2px 7px;background:#fff3cd;color:#664d03;font-weight:600}
""".strip()


def e(value: Any) -> str:
    return escape(str(value), quote=True)


def text(value: Any) -> str:
    return e(value)


def code(value: Any) -> str:
    return f"<code>{e(value)}</code>"


def strong(value: Any) -> str:
    return f"<strong>{e(value)}</strong>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        '<div class="table-wrap"><table class="wrapped"><thead><tr>'
        f"{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def build_storage() -> str:
    sections: list[str] = []

    sections.append("<h2>1. Prosedür Bilgileri</h2>")
    sections.append(table(["Alan", "Değer"], [
        [text("Kurum"), text("İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı")],
        [text("Prosedür Kodu ve Adı"), text(TITLE)],
        [text("Prosedür Referansı"), text("SRÇ.004 - Süreç Kurulumu Süreci")],
        [text("Prosedür Sahibi"), text(OWNER)],
        [text("Durum"), '<span class="draft">Taslak</span>'],
        [text("Sürüm"), text("v0.1")],
        [text("Yürürlük Tarihi"), text("-")],
        [text("Son Gözden Geçirme Tarihi"), text("-")],
    ]))

    sections.append("<h2>2. Amaç</h2>")
    sections.append(
        "<p>Bu prosedürün amacı, İÜC BİDB standart süreç setinde yer alan bir sürecin yeni oluşturulması veya "
        "onaylanmış bir değişiklik kapsamında yeniden tasarlanması sırasında izlenecek kurumsal yöntemi tanımlamaktır.</p>"
        "<p>Prosedür; süreç ihtiyacının SRÇ.018 kapsamında alınmasından başlayarak süreç mimarisinin, amaç ve "
        "sonuçların, faaliyetlerin, iş ürünlerinin, rollerin, ölçümlerin, uyarlama kurallarının ve etkileşimlerin "
        "tanımlanmasını; tasarımın kontrol edilmesini, onaylanmasını, yayımlanmasını ve hedef kitleye duyurulmasını kapsar.</p>"
    )

    sections.append("<h2>3. Kapsam</h2>")
    sections.append("<p>Bu prosedür, LST.006 içinde tanımlanan İÜC BİDB standart süreç setinin tasarlanması ve kontrollü olarak güncellenmesi için uygulanır.</p>")
    sections.append(bullets([
        text("Yeni bir standart sürecin tasarlanması"),
        text("SRÇ.018 kapsamında onaylanan bir değişikliğin süreç tasarımına yansıtılması"),
        text("Süreç amacı, sonuçları, faaliyetleri ve uygulama kurallarının tanımlanması"),
        text("Süreç mimarisi, etkileşimler, iş ürünleri, roller, ölçümler, araçlar ve altyapının belirlenmesi"),
        text("Süreç dokümanı ve ilişkili LST/FRM kayıtlarının hazırlanması"),
        text("Tasarım kontrolü, onay, yayın, bilgilendirme ve bakım başlangıcının gerçekleştirilmesi"),
    ]))

    sections.append("<h2>4. Kapsam Dışı</h2>")
    sections.append("<p>Aşağıdaki faaliyetler bu prosedürün kapsamı dışındadır:</p>")
    sections.append(bullets([
        text("Değişiklik talebinin alınması, önceliklendirilmesi ve kararının yönetilmesi; bu faaliyetler SRÇ.018 kapsamında yürütülür."),
        text("Tanımlanan süreçlerin günlük operasyonel icrası"),
        text("Süreç yetenek değerlendirmesinin yürütülmesi; bu faaliyet SRÇ.005 kapsamında ele alınır."),
        text("Süreç iyileştirme aksiyonlarının yönetilmesi; bu faaliyet SRÇ.006 kapsamında ele alınır."),
        text("Proje veya hizmet özelinde kontrollü uyarlamanın uygulanması; bu faaliyet KLV.002 kurallarına göre yürütülür."),
        text("Eğitim kayıtlarının yönetimi; eğitim kanıtları SRÇ.020 kapsamında tutulur."),
    ]))

    sections.append("<h2>5. Referanslar</h2>")
    references = [
        ("ISO/IEC 15504-5:2006 PIM.1 - Process establishment", "Süreç mimarisinin, standart süreçlerin, performans beklentilerinin, uyarlama yaklaşımının ve kullanım verisinin kurulmasına ilişkin süreç referansı"),
        ("PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Bu prosedürün hazırlanmasında kullanılan zorunlu prosedür yapısı"),
        ("SRÇ.004 - Süreç Kurulumu Süreci", "Süreç tasarımının amaç, sonuç ve temel faaliyetlerini tanımlayan ana süreç"),
        ("SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Yeni süreç ve süreç değişikliği taleplerinin alınması ve kararının yönetilmesi"),
        ("SRÇ.XXX.Ş - Süreç Tanımı Şablonu", "Her süreç dokümanının hazırlanmasında kullanılacak zorunlu süreç şablonu"),
        ("KLV.002 - Süreç Uyarlama Kılavuzu", "Kontrollü süreç uyarlama kuralları"),
        ("KLV.003 - Süreç Tasarımı Kontrol Kılavuzu", "Süreç tasarım kontrol kapıları ve kontrol listesi"),
        ("LST.006 - Standart Süreç Envanteri", "Standart ve kurumsal süreç kodları ile güncel standart süreç seti kapsamı"),
        ("LST.007 - Süreç Etkileşim Matrisi (İlgili Süreç)", "Sürece özel girdi, çıktı ve etkileşimlerin yönetimi"),
        ("LST.008 / LST.009 / LST.010", "Süreç iş ürünleri ve kalite kriterleri, az sayıda yönetilebilir performans ölçümü ve RACI kayıtları"),
        ("LST.011 - Repository Yapısı", "Süreç doküman ve kanıtlarının saklama yapısı"),
        ("LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "Yeni veya güncellenen süreçlerin hedef kitleye duyurulma kaydı"),
    ]
    sections.append(table(["Referans", "Açıklama"], [[text(a), text(b)] for a, b in references]))

    sections.append("<h2>6. Terimler ve Kısaltmalar</h2>")
    terms = [
        ("Standart Süreç Seti", "İÜC BİDB tarafından kurumsal olarak tanımlanan ve kapsamı LST.006 içinde izlenen süreçlerin bütünü"),
        ("Süreç Tasarımı", "Bir süreç beklentisinin kurum içinde uygulanabilir süreç dokümanı, faaliyet, iş ürünü, rol, ölçüm, araç ve etkileşim yapısına dönüştürülmesi"),
        ("Süreç Mimarisi", "Süreçlerin grupları, sırası, girdileri, çıktıları ve birbirleriyle etkileşimlerinin bütünü"),
        ("Tasarım Paketi", "SRÇ dokümanı ile süreç özel LST.007, LST.008, LST.009, LST.010 ve süreç altında tutulan boş FRM.001'den oluşan doküman seti"),
        ("Kontrol Kapısı", "Süreç tasarımı yayımlanmadan önce karşılanması gereken zorunlu kontrol noktası"),
        ("Kontrollü Uyarlama", "Süreç amacı ve zorunlu sonuçları korunarak bağlama göre yapılan, gerekçesi ve onayı izlenebilir düzenleme"),
        ("PIM.1", "ISO/IEC 15504-5 içindeki Process establishment süreci"),
    ]
    sections.append(table(["Terim / Kısaltma", "Açıklama"], [[text(a), text(b)] for a, b in terms]))

    sections.append("<h2>7. Roller ve Sorumluluklar</h2>")
    roles = [
        ("Prosedür Sahibi / Onaylayan", "Prosedürün kurumsal uygulanabilirliğini ve güncelliğini gözetir; süreç tasarım paketinin onaya sunulmasını değerlendirir.", "Süreç tasarım paketini onaylar veya düzeltme için geri gönderir."),
        ("Süreç Sahibi", "Tasarlanacak sürecin kapsamını, hedef kitlesini, uygulama koşullarını ve iş ihtiyaçlarını doğrular.", "Süreç içeriği için gözden geçirme görüşü verir ve tasarımın uygulanabilirliğini kabul eder."),
        ("Kalite Danışmanı / Süreç Mimarı", "Standart beklentilerini analiz eder; süreç tasarım paketini hazırlar ve izlenebilirliği kurar.", "Taslak içerik ve tamamlayıcı kayıtlar için teknik/kalite önerisi verir."),
        ("Gözden Geçiren", "Taslağı kapsam, uygulanabilirlik, tutarlılık ve şablon uyumu bakımından gözden geçirir.", f"Bu prosedür için gözden geçiren rol {REVIEWER} olarak belirlenmiştir."),
        ("Proje Yöneticisi / Yayımlayan", "Onaylı dokümanın Confluence üzerinde yayımlanmasını, bağlantıların kurulmasını ve bilgilendirmeyi koordine eder.", "Yayın ve erişim düzenini uygular."),
        ("Doküman Sorumlusu", "Kod, sürüm, şablon, üst bilgi, sürüm geçmişi ve repository kayıtlarının tutarlılığını sağlar.", "Eksik veya biçimsel olarak uygunsuz taslağı düzeltme için iade eder."),
        ("İlgili Paydaşlar", "Sürecin girdileri, çıktıları, arayüzleri ve uygulama koşulları hakkında bilgi sağlar.", "Kendi uzmanlık alanında görüş ve kanıt sunar."),
    ]
    sections.append(table(["Rol", "Sorumluluk", "Yetki"], [[text(a), text(b), text(c)] for a, b, c in roles]))

    sections.append("<h2>8. Genel İlkeler</h2>")
    principles = [
        ("Tek talep kanalı", "Yeni süreç ve süreç değişikliği ihtiyaçları SRÇ.018 kapsamında alınır ve karara bağlanır; bu prosedür kapsamında ayrı talep formu oluşturulmaz."),
        ("Şablon zorunluluğu", "Süreç dokümanı SRÇ.XXX.Ş - Süreç Tanımı Şablonu kullanılarak hazırlanır; şablonun zorunlu bölümleri gerekçesiz kaldırılmaz."),
        ("Standart izlenebilirliği", "Süreç amacı, sonuçları ve temel uygulamalar ilgili ISO/IEC 15504-5 süreç bölümü ile izlenebilir olmalıdır."),
        ("Tam süreç kapsamı", "LST.006 içinde yer alan süreçlerin tamamı standart süreç setinin parçasıdır; çekirdek/koşullu süreç ayrımı yapılmaz."),
        ("Kontrollü uyarlama", "Uyarlama, süreç amacı ve zorunlu sonuçları ortadan kaldıramaz; gerekçe, etki ve gerekli onay KLV.002 kurallarına göre izlenir."),
        ("Yönetilebilir ölçüm", "Her süreç için LST.009 içinde yalnızca düzenli veri üretilebilen, karar almaya yarayan az sayıda ölçüm tanımlanır; ölçüm sayısı gereksiz yere artırılmaz."),
        ("Tekil kanıt kaynağı", "Kayıtlar doğal olarak üretildikleri Confluence, Jira, Bitbucket, Drive veya diğer yetkili kaynak sistemde tutulur; gereksiz kopya kayıt oluşturulmaz."),
        ("Gerçek ve güncel kanıt", "Geçmiş tarihli sahte kayıt üretilmez; eksikler güncel doküman, tamamlayıcı kayıt veya açık GAP bilgisi ile yönetilir."),
        ("Yayın öncesi kontrol", "Süreç tasarım paketi KLV.003 kullanılarak kontrol edilir; doldurulan FRM.001, 91 - İç Denetimler / Süreç Gözden Geçirmeleri altında Değerlendirme #n adıyla saklanır."),
    ]
    sections.append(table(["İlke", "Açıklama"], [[text(a), text(b)] for a, b in principles]))

    sections.append("<h2>9. Prosedür Esasları</h2>")
    rules = [
        ("Başlatma koşulu", "SRÇ.018 kapsamında kabul edilmiş yeni süreç veya süreç değişikliği kararı bulunmalıdır.", "Zorunlu", "Talep ve karar kaydı SRÇ.018 kapsamındadır."),
        ("Tasarım paketi", "SRÇ dokümanı ile süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 birlikte ele alınır.", "Zorunlu", "Doldurulmuş değerlendirmeler İç Denetimler altında numaralandırılır."),
        ("Süreç şablonu", "Süreç tanımı SRÇ.XXX.Ş şablonuyla hazırlanır; 0. Şablon Hakkında bölümü gerçek dokümana taşınmaz.", "Zorunlu", "Gerçek süreç dokümanı 1. Süreç Bilgileri ile başlar."),
        ("Ölçüm seçimi", "LST.009 ölçümleri hesaplama yöntemi, veri kaynağı, hedef/eşik, sıklık ve sorumlusu tanımlı olacak şekilde sınırlı tutulur.", "Zorunlu", "Düzenli üretilemeyen ölçüm tasarım paketine alınmaz."),
        ("Tasarım kontrolü", "KLV.003 kontrol noktaları ve FRM.001 BP/PA izlenebilirliği tamamlanır.", "Zorunlu", "Eksik kayıtlar onay öncesinde giderilir veya açık GAP olarak gösterilir."),
        ("Onay", "Süreç sahibi gözden geçirmesi ve yetkili onayı tamamlanmadan süreç Aktif olarak yayımlanmaz.", "Zorunlu", "Taslaklar yerel çalışma alanında veya yetkili taslak alanında tutulur."),
        ("Değişiklik yolu", "Yayımlanmış süreçte yeni değişiklik ihtiyacı doğarsa işlem yeniden SRÇ.018 üzerinden başlatılır.", "Zorunlu", "Prosedür değişiklik talebini kendi içinde yönetmez."),
    ]
    sections.append(table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [[text(a), text(b), text(c), text(d)] for a, b, c, d in rules]))

    sections.append("<h2>10. Uygulama / Strateji Matrisi</h2>")
    steps = [
        ("1. Tasarım girdisini al", "SRÇ.018 kapsamında kabul edilen ihtiyaç, kapsam ve öncelik bilgisi alınır.", "Süreç Sahibi / Süreç Mimarı", "SRÇ.018 talep ve karar kaydı", "PIM.1 başlangıç girdisi"),
        ("2. Süreç kimliğini ve kapsamını doğrula", "Standart süreç kodu, kurumsal kod, Türkçe ad, kapsam ve süreç sahibi LST.006 üzerinden doğrulanır.", "Süreç Mimarı", "LST.006", "PIM.1.BP1"),
        ("3. Mimari etkiyi belirle", "Sürecin besleyen/beslenen süreçleri, temel girdileri, çıktıları ve arayüzleri belirlenir.", "Süreç Mimarı / İlgili Paydaşlar", "İlgili sürece ait LST.007 - Süreç Etkileşim Matrisi", "PIM.1.BP1"),
        ("4. Standart beklentilerini çözümle", "Süreç amacı, sonuçları, BP'ler ve ilgili PA/GP beklentileri analiz edilerek kurumsal tasarım kapsamı oluşturulur.", "Kalite Danışmanı / Süreç Mimarı", "Standart izlenebilirlik notları", "PIM.1.BP3"),
        ("5. Süreç dokümanını hazırla", "SRÇ.XXX.Ş şablonu kullanılarak amaç, sonuçlar, kapsam, faaliyetler, araçlar, altyapı, uyarlama ve etkileşimler yazılır.", "Kalite Danışmanı / Süreç Mimarı", "İlgili SRÇ dokümanı", "PIM.1.BP3"),
        ("6. İş ürünlerini tanımla", "Sürecin girdi ve çıktı iş ürünleri ile uygulanabilir kalite kriterleri belirlenir.", "Süreç Mimarı / Süreç Sahibi", "LST.008", "PA 2.2 ve PIM.1.BP3"),
        ("7. Rol ve yetkileri tanımla", "Süreç rolleri, sorumluluklar, yetkiler, RACI ve gerekli yetkinlikler belirlenir.", "Süreç Sahibi / Süreç Mimarı", "LST.010", "PA 2.1 ve PA 3.1"),
        ("8. Araç ve altyapıyı tanımla", "Sürecin uygulanması için gerekli araç, çalışma ortamı, erişim koşulu ve sorumlu birim belirlenir.", "Süreç Sahibi / Altyapı Sorumluları", "SRÇ Araçlar ve Altyapı bölümü", "PA 3.1"),
        ("9. Ölçümleri seç", "Düzenli veri kaynağı bulunan ve karar almaya yarayan az sayıda performans ölçümü tanımlanır.", "Süreç Sahibi / Ölçüm Sorumlusu", "LST.009", "PIM.1.BP4"),
        ("10. Uyarlama kurallarını belirle", "Amaç ve zorunlu sonuçları koruyan uyarlanabilir alanlar, onay koşulları ve kayıt yöntemi belirlenir.", "Süreç Sahibi / Süreç Mimarı", "KLV.002 ve SRÇ uyarlama bölümü", "PIM.1.BP5"),
        ("11. Tasarım kontrolünü yap", "Şablon, standart, iş ürünü, etkileşim, RACI, ölçüm ve uyarlama kontrolleri yürütülür; BP/PA kanıtları değerlendirilir.", "Gözden Geçiren / Kalite Danışmanı", "KLV.003 ve numaralandırılmış FRM.001 değerlendirmesi", "Kontrol kapısı"),
        ("12. Onayla ve yayımla", "Uygun bulunan tasarım yetkili onayına sunulur; onaylanan doküman Confluence üzerinde yayımlanır ve aktif doküman/repository kayıtları güncellenir.", "Onaylayan / Proje Yöneticisi", "Onay kaydı, LST.001, LST.011", "PIM.1.BP2"),
        ("13. Yaygınlaştır ve yetkinliği destekle", "Hedef kitleye e-posta ile bilgilendirme yapılır; gerekiyorsa eğitim planlanır ve kayıt altına alınır.", "Süreç Sahibi / Proje Yöneticisi", "LST.012 ve SRÇ.020 eğitim kayıtları", "PIM.1.BP2"),
        ("14. Kullanım verisini ve değişiklik ihtiyacını izle", "Süreç kullanım ve performans verisi ilgili mevcut kayıtlarda sürdürülür; yeni değişiklik ihtiyacı SRÇ.018'e aktarılır.", "Süreç Sahibi / Ölçüm Sorumlusu", "LST.009 ve ilgili kaynak sistem kayıtları", "PIM.1.BP6"),
    ]
    sections.append(table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], [[text(a), text(b), text(c), text(d), text(f)] for a, b, c, d, f in steps]))

    sections.append("<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>")
    publication = [
        ("Taslak çalışma", "Taslak süreç dokümanları yerel repository veya yetkili taslak alanında hazırlanır; onaylanmadan Aktif olarak işaretlenmez.", "Kalite Danışmanı / Doküman Sorumlusu", "Yerel repository ve Git diff"),
        ("Yayın", "Onaylanan süreç ve prosedür dokümanları Confluence üzerinde yayımlanır; gerekli dosya çıktıları Google Drive'da tutulabilir.", "Proje Yöneticisi / Yayımlayan", "Confluence sayfası ve LST.001"),
        ("Erişim", "Hedef kullanıcı gruplarına görevleri için gerekli erişim verilir; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme kullanılır.", "Repository / Sistem Yöneticisi", "Erişim ve yetkilendirme kayıtları"),
        ("Dağıtım", "Yeni veya güncellenen süreç bağlantısı hedef kitleye e-posta ile iletilir ve LST.012 güncellenir.", "Süreç Sahibi / Proje Yöneticisi", "E-posta ve LST.012"),
        ("Bakım", "Süreçler yılda en az bir kez ve organizasyon, standart, araç veya kapsam değişikliğinde ayrıca gözden geçirilir.", "Süreç Sahibi", "Gözden geçirme ve FRM.001 kayıtları"),
        ("Değişiklik", "Bakım sırasında belirlenen değişiklik ihtiyacı SRÇ.018 kapsamında kaydedilir ve karara bağlanır.", "Süreç Sahibi", "SRÇ.018 kapsamındaki kayıtlar"),
        ("Arşiv", "Geçerliliğini yitiren sürümler SRÇ.001 ve LST.011 kurallarına göre pasife alınır veya arşivlenir.", "Doküman Sorumlusu", "LST.001, LST.002 ve repository kayıtları"),
    ]
    sections.append(table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [[text(a), text(b), text(c), text(d)] for a, b, c, d in publication]))

    sections.append("<h2>12. Kayıtlar ve Kanıtlar</h2>")
    records = [
        ("SRÇ.018 kapsamındaki talep ve karar kayıtları", "Yeni süreç veya değişiklik ihtiyacının kaynağını ve kararını izlemek", "SRÇ.018 için tanımlanan kaynak sistem", "Değişiklik Talebi Sorumlusu", "Ayrı süreç tasarım talep formu oluşturulmaz."),
        ("İlgili SRÇ dokümanı", "Sürecin amaç, sonuç, faaliyet, araç, uyarlama ve etkileşimlerini tanımlamak", "01 - Süreç Dokümanları / Confluence", "Süreç Sahibi", "SRÇ.XXX.Ş şablonuyla hazırlanır."),
        ("LST.006", "Süreç kimliği ve standart süreç setini izlemek", "03 - Kayıtlar ve Listeler / Confluence", "Süreç Mimarı", "Ortak kayıt"),
        ("LST.007 - Süreç Etkileşim Matrisi", "Sürece özel mimari ve etkileşimleri izlemek", "İlgili süreç alt sayfası / Confluence", "Süreç Mimarı", "Süreç özel kayıt"),
        ("LST.008", "Süreç iş ürünleri ve kalite kriterlerini yönetmek", "İlgili süreç kayıt alanı / Confluence", "Süreç Sahibi", "Süreç özel kayıt"),
        ("LST.009", "Az sayıda yönetilebilir süreç ölçümünü izlemek", "İlgili süreç kayıt alanı / Confluence", "Ölçüm Sorumlusu", "Süreç özel kayıt"),
        ("LST.010", "Rol, yetki, RACI ve yetkinlikleri yönetmek", "İlgili süreç kayıt alanı / Confluence", "Süreç Sahibi", "Süreç özel kayıt"),
        ("KLV.003", "Tasarım kontrol noktalarının uygulandığını göstermek", "05 - Kılavuzlar / Confluence", "Kalite Danışmanı", "Kontrol kaynağı"),
        ("FRM.001", "Boş formu süreç altında tutmak; doldurulmuş değerlendirmede BP ve PA/GP kanıt durumunu izlemek", "Boş form: ilgili süreç altı; değerlendirme: 91 - İç Denetimler / Süreç Gözden Geçirmeleri", "Kalite Danışmanı", "Doldurulmuş kayıt Değerlendirme #n adıyla saklanır"),
        ("LST.012", "Yayın ve hedef kitle bilgilendirmesini izlemek", "03 - Kayıtlar ve Listeler / Confluence", "Proje Yöneticisi", "Ortak kayıt"),
        ("Eğitim kayıtları", "Gerekli yetkinlik geliştirme ve katılım kanıtını izlemek", "SRÇ.020 kapsamında belirlenen ortam", "Eğitim Sorumlusu", "Gerektiğinde"),
    ]
    sections.append(table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [[text(a), text(b), text(c), text(d), text(f)] for a, b, c, d, f in records]))

    sections.append("<h2>13. Sürüm Geçmişi</h2>")
    sections.append(table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        [[text("v0.1"), text(DRAFT_DATE), text("İlk taslak oluşturuldu."), text(PREPARED_BY), text("-"), text("-")]],
    ))
    return "".join(sections) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(TITLE)}</h1>
{storage}
</main>
</body>
</html>
"""


def page_yaml() -> dict[str, Any]:
    return {
        "page_id": "",
        "space": "SSSS",
        "title": TITLE,
        "parent_id": PARENT_ID,
        "parent_title": PARENT_TITLE,
        "version": "",
        "url": "",
        "depth": 2,
        "status": "draft",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": RELATIVE_PATH,
        "slug": SLUG,
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    }


def update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    existing = next((page for page in pages if page.get("relative_path") == RELATIVE_PATH), None)
    entry = {
        "page_id": "",
        "title": TITLE,
        "parent_id": PARENT_ID,
        "depth": 2,
        "relative_path": RELATIVE_PATH,
        "slug": SLUG,
        "storage_file": f"{RELATIVE_PATH}/body.storage.xhtml",
        "view_file": f"{RELATIVE_PATH}/body.view.html",
    }
    if existing:
        existing.update(entry)
    else:
        insert_at = len(pages)
        for position, page in enumerate(pages):
            if page.get("relative_path") == (
                "pages/000-root-iuc-bidb-spice-2026-level-3/07-prosedurler/"
                "prs-001-yazilim-projeleri-dokumantasyon-proseduru"
            ):
                insert_at = position + 1
                break
        pages.insert(insert_at, entry)
        index["total_page_count"] = int(index.get("total_page_count", len(pages) - 1)) + 1
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def validate(storage: str) -> None:
    expected_headings = [
        "1. Prosedür Bilgileri", "2. Amaç", "3. Kapsam", "4. Kapsam Dışı",
        "5. Referanslar", "6. Terimler ve Kısaltmalar", "7. Roller ve Sorumluluklar",
        "8. Genel İlkeler", "9. Prosedür Esasları", "10. Uygulama / Strateji Matrisi",
        "11. Yayın, Erişim ve Bakım Kuralları", "12. Kayıtlar ve Kanıtlar",
        "13. Sürüm Geçmişi",
    ]
    for heading in expected_headings:
        if f"<h2>{heading}</h2>" not in storage:
            raise RuntimeError(f"Eksik şablon başlığı: {heading}")
    required = [
        "PRS.XXX.Ş - Prosedür Tanımı Şablonu",
        "SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
        "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "yalnızca düzenli veri üretilebilen, karar almaya yarayan az sayıda ölçüm",
        "Ayrı süreç tasarım talep formu oluşturulmaz.",
    ]
    for phrase in required:
        if phrase not in storage:
            raise RuntimeError(f"Zorunlu karar metinde bulunamadı: {phrase}")
    if "<h2>0." in storage or "FRM.002" in storage:
        raise RuntimeError("Şablon notu veya oluşturulmaması kararlaştırılan FRM.002 taslağa taşındı")
    if "26 süreç" in storage or "26 sürec" in storage:
        raise RuntimeError("Resmî dokümanda sabit süreç sayısı kullanılmamalıdır")


def write_report() -> None:
    REPORT.write_text(
        "\n".join([
            "# PRS.002 Süreç Tasarım Prosedürü Yerel Taslak Raporu",
            "",
            f"Tarih: {DRAFT_DATE}",
            "",
            "- PRS.XXX.Ş şablonundaki 1-13 ana bölüm sırası kullanıldı.",
            "- Şablonun 0. bölümü gerçek prosedüre taşınmadı.",
            "- Süreç değişikliği ve talepleri SRÇ.018'e yönlendirildi; FRM.002 oluşturulmadı.",
            "- SRÇ.XXX.Ş süreç tanımı şablonu zorunlu referans ve uygulama girdisi olarak eklendi.",
            "- LST.009 için az sayıda, düzenli üretilebilir ve karar almaya yarayan ölçüm kuralı işlendi.",
            "- Taslak v0.1 olarak oluşturuldu; henüz Confluence'a yayımlanmadı.",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    storage = build_storage()
    validate(storage)
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    (PAGE_DIR / "page.yaml").write_text(
        yaml.safe_dump(page_yaml(), allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    update_index()
    write_report()
    print(f"[DONE] Yerel taslak oluşturuldu: {TITLE}")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
