#!/usr/bin/env python3
"""Create the local PRS.004 combined process improvement/change procedure."""
from __future__ import annotations

from create_src005_process_assessment_package import (
    CONFLUENCE,
    PAGE_ROOT,
    PRS003,
    PRS004,
    PROCEDURES_ID,
    PROCEDURES_REL,
    PROCESS_OWNER,
    REVIEWED_BY,
    APPROVED_BY,
    PREPARED_BY,
    build_view,
    history,
    p,
    parent_register_body,
    table,
    update_lst001,
    upsert_index,
    write_page,
)


SRC006 = "SRÇ.006 - Süreç İyileştirme Süreci"
SRC018 = "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"
PLN002 = "PLN.002 - Süreç İyileştirme Planı"
RPR001 = "RPR.001 - Süreç Performansları Raporu"
LST012 = "LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
TITLE = PRS004
SLUG = "prs-004-surec-iyilestirme-ve-degisiklik-yonetimi-proseduru"


def procedure_body() -> str:
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>",
        table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Prosedür Kodu ve Adı", TITLE],
            ["Prosedür Referansı", f"{SRC006}; {SRC018}"],
            ["Prosedür Sahibi", PROCESS_OWNER],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "15-02-2025"],
            ["Son Gözden Geçirme Tarihi", "14-07-2026"],
        ]),
        "<h2>2. Amaç</h2>",
        p("Bu prosedürün amacı, süreç değişikliklerinin ve süreç iyileştirme fırsatlarının tek bir izlenebilir yaşam döngüsü içinde kaydedilmesi, analiz edilmesi, sınıflandırılması, önceliklendirilmesi, planlanması, onaylanması, uygulanması, sonuçlarının gözden geçirilmesi, raporlanması ve uygun olduğunda diğer süreçlere yaygınlaştırılması için uygulanacak kuralları tanımlamaktır."),
        "<h2>3. Kapsam</h2>",
        p("Bu prosedür, LST.006 içinde tanımlanan güncel standart süreç setini etkileyen değişiklik ve iyileştirme fırsatlarına uygulanır."),
        "<ul><li>değişiklik kaydının SRÇ.018 kapsamında açılması ve ön değerlendirilmesi,</li><li>etki analizi ile normal değişiklik / iyileştirme fırsatı ayrımı,</li><li>iyileştirme hedefi, etki ve uygulama önceliğinin belirlenmesi,</li><li>planlama uyarlaması, kaynak taahhüdü ve onay,</li><li>değişikliğin SRÇ.018 kapsamında kontrollü uygulanması,</li><li>SRÇ.018 değişiklik gözden geçirmesiyle sonucun doğrulanması,</li><li>iyileştirme sonucunun raporlanması, duyurulması ve başka süreçlerde kullanılabilirliğinin değerlendirilmesi.</li></ul>",
        "<h2>4. Kapsam Dışı</h2>",
        "<ul><li>SRÇ.005 kapsamındaki süreç değerlendirmesinin yürütülmesi,</li><li>SRÇ.017 kapsamındaki problem kök neden analizi ve düzeltici faaliyet yönetimi,</li><li>SRÇ.026 kapsamındaki denetim faaliyetlerinin yürütülmesi,</li><li>değişiklikten bağımsız proje görev ve iş takibi,</li><li>ayrı bir iyileştirme fırsatı registerı veya sayısal öncelik puanı oluşturulması.</li></ul>",
        "<h2>5. Referanslar</h2>",
        table(["Referans", "Açıklama"], [
            [SRC006, "İyileştirme hedefi, önceliği, planı, sonuç takibi ve yeniden kullanım değerlendirmesi"],
            [SRC018, "Değişiklik kaydı, etki analizi, onay, kontrollü uygulama ve değişiklik gözden geçirmesi"],
            ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Bu prosedürün zorunlu doküman yapısı"],
            [PRS003, "Süreç değerlendirmelerinden doğan iyileştirme fırsatlarının kaynağı"],
            [PLN002, "Yüksek etkili, çoklu süreç kapsamlı veya önemli kaynak gerektiren iyileştirmelerin planı"],
            [RPR001, "Doğrulanmış iyileştirme kazanımlarının kümülatif yönetim özeti"],
            [LST012, "Süreç kullanıcılarını etkileyen sonuçların yaygınlaştırma ve bilgilendirme kaydı"],
        ]),
        "<h2>6. Terimler ve Kısaltmalar</h2>",
        table(["Terim / Kısaltma", "Açıklama"], [
            ["Değişiklik", "Süreç, doküman, araç, yöntem, rol veya uygulama üzerinde kontrollü olarak gerçekleştirilen düzenleme"],
            ["İyileştirme Fırsatı", "Bir problem bulunması zorunlu olmaksızın süreç etkinliği, verimliliği, uygunluğu veya risk durumunu geliştirme olanağı"],
            ["Etki", "İyileştirmenin beklenen fayda, risk, kapsam veya kurumsal sonuç büyüklüğü"],
            ["Uygulama Önceliği", "Yasal/denetim tarihi, risk aciliyeti, bağımlılık, gecikme sonucu, kaynak uygunluğu ve etki dikkate alınarak belirlenen ele alınma sırası"],
            ["SRÇ.018 Değişiklik Gözden Geçirmesi", "Uygulanan değişikliğin hedeflenen sonucu üretip üretmediğinin SRÇ.018 kapsamında incelenmesi"],
            ["Yeniden Kullanım", "Doğrulanmış iyileştirme çözümünün başka süreç veya birimlerde uygulanabilirliğinin değerlendirilmesi"],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>",
        table(["Rol", "Sorumluluk", "Yetki"], [
            ["Bilgi İşlem Daire Başkanı", "Kurumsal iyileştirme taahhüdünü ve gerekli kaynakları sağlamak; yetki sınırı dışındaki değişiklik ve iyileştirmeleri onaylamak", "Asıl onay ve kaynak tahsis mercii; uygun alanlarda rol bazlı yetki devri"],
            ["Proje Yöneticisi", "Proje Geliştirme Yönetimi kapsamındaki değişiklikleri ve iyileştirmeleri gözden geçirmek, uygulamayı koordine etmek", "İlave bütçe gerektirmeyen, organizasyon yapısını değiştirmeyen ve kurum genelinde önemli etki oluşturmayan çalışmalar için devredilmiş onay"],
            ["Kalite Danışmanı", "İyileştirme fırsatının gerekçesini, hedefini, etki ve uygulama önceliğini hazırlamak; sonuç ve yeniden kullanım değerlendirmesini koordine etmek", "Sınıflandırma, hedef ve raporlama önerisi"],
            ["İlgili Süreç Sahibi", "Etki analizine katılmak, plan ve kaynak ihtiyacını doğrulamak, uygulama kanıtlarını sağlamak", "Kendi süreç alanında uygulanabilirlik ve teknik/operasyonel uygunluk görüşü"],
            ["Değişiklik Sorumlusu", "Onaylanan değişikliği planlanan kapsamda uygulamak ve kanıtlarını kaydetmek", "Onaylı kapsam içinde uygulama"],
            ["Gözden Geçiren", "SRÇ.018 değişiklik gözden geçirmesi kapsamında uygulama sonucunu ve hedef gerçekleşmesini gözden geçirmek", "Ek kanıt veya düzeltme istemek; sonucu uygun/uygun değil olarak değerlendirmek"],
        ]),
        "<h2>8. Genel İlkeler</h2>",
        table(["İlke", "Açıklama"], [
            ["Tek giriş noktası", "Her değişiklik veya iyileştirme adayı önce SRÇ.018 kapsamında değişiklik kaydı olarak açılır."],
            ["Tekrarsız analiz", "Ön değerlendirme ve etki analizi SRÇ.018 kaydında yürütülür; SRÇ.006 aynı analizi tekrar etmez."],
            ["Ayrı sınıflandırma", "Normal değişiklikler SRÇ.018 akışında kalır; iyileştirme fırsatı olarak sınıflandırılan kayıtlar SRÇ.006 yönetişimiyle devam eder."],
            ["Etki ve öncelik ayrımı", "Etki ve uygulama önceliği farklı alanlardır; ikisi de sayısal puan olmadan Yüksek, Orta veya Düşük etiketiyle gösterilir."],
            ["Kontrollü uygulama", "Süreç, doküman, araç veya uygulama üzerindeki gerçek değişiklik SRÇ.018 kapsamında uygulanır."],
            ["Kanıta dayalı kapanış", "SRÇ.018 değişiklik gözden geçirmesi sonucu olumlu olmadan iyileştirme tamamlanmış sayılmaz."],
            ["Kümülatif görünürlük", "Doğrulanmış önemli kazanımlar RPR.001'de özetlenir; ilgili hedef kitle bilgilendirmeleri LST.012'de tutulur."],
        ]),
        "<h2>9. Prosedür Esasları</h2>",
        table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [
            ["Girdi kaynakları", "Değerlendirme, denetim, problem çözüm, performans/ölçüm, risk, kullanıcı-paydaş geri bildirimi, proje kapanış öğrenilmiş dersleri, müşteri memnuniyeti ve Yönetim Gözden Geçirme çıktıları kullanılabilir.", "Koşullu", "Kaynak bağlantısı değişiklik kaydında korunur."],
            ["Etki analizi", "Etkilenen süreç/dokümanlar, mevcut durum, beklenen fayda, risk, kaynak ve bağımlılıklar incelenir.", "Zorunlu", "SRÇ.018 kaydında yürütülür."],
            ["İyileştirme hedefi", "İyileştirme fırsatında beklenen sonuç ve doğrulama ölçütü belirlenir.", "Zorunlu", "PIM.3.BP3"],
            ["Önceliklendirme", "Uygulama önceliği yasal/denetim tarihi, risk aciliyeti, bağımlılık, gecikme sonucu, kaynak uygunluğu ve etki dikkate alınarak belirlenir.", "Zorunlu", "PIM.3.BP4"],
            ["Planlama", "Faaliyet, sorumlu, kaynak, takvim, başarı ölçütü ve doğrulama yöntemi tanımlanır.", "Zorunlu", "SRÇ.018 kaydı veya PLN.002"],
            ["Sonuç doğrulama", "Uygulanan değişiklik, SRÇ.018 değişiklik gözden geçirmesi kapsamında önceden tanımlı hedef ve kanıtlarla incelenir.", "Zorunlu", "Olumsuz sonuç yeniden analize döner."],
            ["Yaygınlaştırma", "Hedef kitleyi etkileyen sonuçlar duyurulur; önemli doğrulanmış kazanımlar raporlanır.", "Koşullu", "LST.012 ve RPR.001"],
            ["Yeniden kullanım", "Başarılı çözümün başka süreçlere uygulanabilirliği değerlendirilir.", "Zorunlu", "Yeni kapsam için ayrı SRÇ.018 kaydı açılır."],
        ]),
        "<h2>10. Uygulama / Strateji Matrisi</h2>",
        table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], [
            ["1. İhtiyacı kaydet", "Değişiklik veya iyileştirme adayı SRÇ.018 kaydı olarak açılır ve kaynak bağlantısı eklenir.", "Talep Sahibi / İlgili Süreç Sahibi", "SRÇ.018 değişiklik kaydı", "Ayrı iyileştirme registerı oluşturulmaz."],
            ["2. Ön değerlendirme ve etki analizi", "Mevcut durum, kapsam, etkilenen varlıklar, fayda, risk, kaynak ve bağımlılıklar analiz edilir.", "İlgili Süreç Sahibi / Kalite Danışmanı", "SRÇ.018 analiz çıktısı", "Analiz kuralları bu prosedürde uygulanır."],
            ["3. Sınıflandır", "Kayıt normal değişiklik veya iyileştirme fırsatı olarak sınıflandırılır.", "Kalite Danışmanı / İlgili Süreç Sahibi", "Sınıflandırma kararı", "İyileştirme fırsatı SRÇ.006 yönetişimine geçer."],
            ["4. Etki ve uygulama önceliğini belirle", "İki alan ayrı ayrı Yüksek, Orta veya Düşük etiketiyle kaydedilir.", "Kalite Danışmanı / Proje Yöneticisi", "SRÇ.018 analiz çıktısı", "Sayısal puan kullanılmaz."],
            ["5. Onay ve kaynak taahhüdü", "Onay ve kaynak kararı rol bazlı genel yetki sınırına göre verilir.", "Proje Yöneticisi / Bilgi İşlem Daire Başkanı", "Onay ve taahhüt kaydı", "Yetki sınırı dışı kararlar Bilgi İşlem Daire Başkanına sunulur."],
            ["6. Planlama uyarlaması", "Sınırlı çalışma SRÇ.018 kaydında; yüksek etkili, çoklu süreçli veya önemli kaynak gerektiren çalışma PLN.002 ile planlanır.", "İlgili Süreç Sahibi / Kalite Danışmanı", "SRÇ.018 kaydı veya PLN.002", "Plan seçimi etkiye, kapsama ve kaynağa göre yapılır."],
            ["7. Uygula", "Onaylı değişiklik kontrollü biçimde gerçekleştirilir; sürüm ve uygulama kanıtları kaydedilir.", "Değişiklik Sorumlusu", "Değişiklik ve sürüm kayıtları", "Uygulama SRÇ.018 sorumluluğundadır."],
            ["8. Sonucu gözden geçir", "SRÇ.018 değişiklik gözden geçirmesi kapsamında hedef, kanıt ve gerçekleşen sonuç karşılaştırılır.", "Gözden Geçiren / İlgili Süreç Sahibi", "SRÇ.018 değişiklik gözden geçirme sonucu", "Başarısız sonuç yeniden analize döner."],
            ["9. Raporla ve duyur", "Doğrulanmış kazanım RPR.001'e; hedef kitleyi etkileyen sonuç LST.012'ye eklenir.", "Kalite Danışmanı / Yayımlayan", "RPR.001; LST.012", "RPR.001 sonucu yeniden değerlendirmez."],
            ["10. Yeniden kullanımı değerlendir", "Çözümün başka süreçlerde uygulanabilirliği ilgili süreç sahipleriyle incelenir.", "Kalite Danışmanı / İlgili Süreç Sahipleri", "Yeniden kullanım kararı", "Uygulanabilir her yeni kapsam için ayrı SRÇ.018 kaydı açılır."],
        ]),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>",
        table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [
            ["Yayın", "Onaylı prosedür ve süreç değişiklikleri Confluence'ta yayımlanır.", "Yayımlayan / Proje Yöneticisi", "Confluence sayfa geçmişi"],
            ["Erişim", "Değişiklik ve iyileştirme kayıtları ilgili karar, uygulama ve gözden geçirme rollerince erişilebilir olmalıdır.", "İlgili Süreç Sahibi", "Erişim yetkileri"],
            ["Bakım", "Prosedür SRÇ.006 veya SRÇ.018 yaklaşımı değiştiğinde ve yılda en az bir kez gözden geçirilir.", "Kalite Danışmanı / Prosedür Sahibi", "Doküman gözden geçirme kaydı"],
            ["Duyuru", "Hedef kitleyi etkileyen onaylı değişiklikler e-posta veya uygun kurumsal kanal ile duyurulur.", "Proje Yöneticisi / Yayımlayan", LST012],
            ["Arşiv", "Kapanan değişiklik, gözden geçirme ve plan kayıtları doküman kontrol kurallarına göre korunur.", "Doküman Sorumlusu", "Confluence / kontrollü kayıt ortamı"],
        ]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>",
        table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [
            ["SRÇ.018 değişiklik kaydı ve etki analizi", "Talep, kaynak, sınıflandırma, etki, öncelik, onay ve uygulama izlenebilirliği", "SRÇ.018 kapsamında tanımlı kayıt ortamı", "İlgili Süreç Sahibi / Değişiklik Sorumlusu", "Her çalışma için temel kayıt"],
            [PLN002, "Yüksek etkili, çoklu süreç kapsamlı veya önemli kaynak gerektiren iyileştirmelerin planlanması", "08 - Planlar", "Kalite Danışmanı / İlgili Süreç Sahibi", "Uyarlama koşulu oluştuğunda"],
            ["SRÇ.018 değişiklik gözden geçirme sonucu", "Uygulanan değişikliğin hedefe ulaştığını doğrulamak", "SRÇ.018 değişiklik kaydı", "Gözden Geçiren", "Olumlu sonuç olmadan iyileştirme kapatılmaz"],
            [RPR001, "Doğrulanmış önemli iyileştirme kazanımlarını kümülatif olarak raporlamak", "09 - Raporlar", "Kalite Danışmanı", "Başarı yeniden değerlendirilmez"],
            [LST012, "Hedef kitleyi etkileyen değişiklik ve iyileştirme sonuçlarını duyurmak", "03 - Kayıtlar ve Listeler", "Proje Yöneticisi / Yayımlayan", "Doğal iletişim kanıtı bağlantısı korunur"],
            ["Yeniden kullanım kararı ve yeni SRÇ.018 bağlantıları", "Başarılı çözümün diğer süreçlere aktarımını izlemek", "Kaynak değişiklik kaydı / ilgili yeni kayıtlar", "Kalite Danışmanı / İlgili Süreç Sahipleri", "Her yeni kapsam ayrı değerlendirilir"],
        ]),
        "<h2>13. Sürüm Geçmişi</h2>",
        history("Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü", REVIEWED_BY, APPROVED_BY),
    ])


def verify(storage: str) -> None:
    required = [
        SRC006,
        SRC018,
        "PRS.XXX.Ş - Prosedür Tanımı Şablonu",
        "Etki ve öncelik ayrımı",
        "Planlama uyarlaması",
        PLN002,
        "SRÇ.018 değişiklik gözden geçirmesi",
        RPR001,
        LST012,
        "Yeniden kullanım",
        "SRÇ.007",
        "müşteri memnuniyeti",
        "Yönetim Gözden Geçirme",
    ]
    # The source list is expressed in prose and must preserve the agreed inputs.
    source_aliases = [
        "proje kapanış öğrenilmiş dersleri",
        "müşteri memnuniyeti",
        "Yönetim Gözden Geçirme",
    ]
    missing = [item for item in required if item not in storage]
    missing.extend(item for item in source_aliases if item not in storage and item not in missing)
    if missing:
        raise RuntimeError(f"PRS.004 zorunlu içerik eksik: {missing}")
    if "sayısal öncelik puanı" not in storage:
        raise RuntimeError("PRS.004 sayısal puan yasağı eksik")


def main() -> None:
    storage = procedure_body()
    # Keep explicit process codes in the source paragraph for full traceability.
    storage = storage.replace(
        "proje kapanış öğrenilmiş dersleri, müşteri memnuniyeti",
        "SRÇ.007 proje kapanış öğrenilmiş dersleri, SRÇ.002 müşteri memnuniyeti",
    )
    verify(storage)

    procedure_dir = CONFLUENCE / PROCEDURES_REL / SLUG
    write_page(procedure_dir, TITLE, PROCEDURES_ID, "07 - Prosedürler", 2, storage)

    procedures_dir = PAGE_ROOT / "07-prosedurler"
    parent_storage = parent_register_body("Prosedür", [
        ("PRS.001", "Yazılım Projeleri Dokümantasyon Prosedürü", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"),
        ("PRS.002", "Süreç Tasarım Prosedürü", "PRS.002 - Süreç Tasarım Prosedürü"),
        ("PRS.003", "Süreç Değerlendirme Prosedürü", PRS003),
        ("PRS.004", "Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü", PRS004),
    ])
    (procedures_dir / "body.storage.xhtml").write_text(parent_storage + "\n", encoding="utf-8")
    (procedures_dir / "body.view.html").write_text(build_view("07 - Prosedürler", parent_storage), encoding="utf-8")

    lst001_dir = PAGE_ROOT / "03-kayitlar-ve-listeler/lst-001-aktif-dokumanlar-listesi"
    lst001_storage = update_lst001((lst001_dir / "body.storage.xhtml").read_text(encoding="utf-8"))
    (lst001_dir / "body.storage.xhtml").write_text(lst001_storage, encoding="utf-8")
    (lst001_dir / "body.view.html").write_text(
        build_view("LST.001 - Aktif Dokümanlar Listesi", lst001_storage),
        encoding="utf-8",
    )

    upsert_index([procedure_dir, procedures_dir, lst001_dir])
    print("[PASS] PRS.004 birleşik süreç iyileştirme ve değişiklik yönetimi prosedürü oluşturuldu.")


if __name__ == "__main__":
    main()
