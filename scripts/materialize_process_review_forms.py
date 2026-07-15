#!/usr/bin/env python3
"""Generate FRM.001 process review form files for all SPICE processes.

This script materializes review forms into the exported Confluence tree under:
confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri/

It uses only resources/standards/spice_practices.yaml as the SPICE BP/GP source.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPICE_YAML = ROOT / "resources/standards/spice_practices.yaml"
TARGET_PARENT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri"
INDEX_YAML = ROOT / "confluence/index.yaml"
DRAFTS = ROOT / "drafts/process-review-forms"
REPORT = ROOT / "reports/process_review_forms_materialization_report.md"

PROCESS_OWNER = {
    "SRÇ.001": "Levent BAYEZİT - Proje Yöneticisi",
}

BP_TITLE_TR = {
    "Develop documentation management strategy": "Dokümantasyon yönetim stratejisini geliştirme",
    "Establish standards for documents": "Dokümanlar için standartları oluşturma",
    "Specify document requirements": "Doküman gereksinimlerini belirleme",
    "Identify the documents to be produced": "Üretilecek dokümanları belirleme",
    "Develop documents": "Dokümanları geliştirme",
    "Check documents": "Dokümanları kontrol etme",
    "Distribute documents": "Dokümanları dağıtma",
    "Maintain documents": "Dokümanları sürdürme",
    "Develop a strategy for product and process quality assurance": "Ürün ve süreç kalite güvencesi stratejisini geliştirme",
    "Define quality records": "Kalite kayıtlarını tanımlama",
    "Assure the quality of project process activities and project work products": "Proje süreç faaliyetleri ve iş ürünlerinin kalitesini güvence altına alma",
    "Identify and record problems and non-conformances": "Problem ve uygunsuzlukları belirleme ve kaydetme",
    "Act on non-conformances": "Uygunsuzluklar için aksiyon alma",
    "Develop verification strategy": "Doğrulama stratejisini geliştirme",
    "Develop criteria for verification": "Doğrulama kriterlerini geliştirme",
    "Conduct verification": "Doğrulamayı gerçekleştirme",
    "Determine actions for verification results": "Doğrulama sonuçları için aksiyonları belirleme",
    "Make verification results available to the stakeholders": "Doğrulama sonuçlarını paydaşların erişimine sunma",
    "Define process architecture": "Süreç mimarisini tanımlama",
    "Support deployment of processes": "Süreçlerin yaygınlaştırılmasını destekleme",
    "Define standard processes": "Standart süreçleri tanımlama",
    "Identify performance expectations": "Performans beklentilerini belirleme",
    "Establish process tailoring guidelines: Establish organizational guidelines for tailoring the organization's standard processes to meet the specific needs of projects": "Süreç uyarlama kılavuzlarını oluşturma",
    "Maintain process data": "Süreç verilerini sürdürme",
    "Define assessment goals": "Değerlendirme hedeflerini tanımlama",
    "Plan the assessment": "Değerlendirmeyi planlama",
    "Obtain commitment": "Taahhüt alma",
    "Perform the assessment to collect data": "Veri toplamak için değerlendirmeyi gerçekleştirme",
    "Validate the assessment data": "Değerlendirme verilerini doğrulama",
    "Analyze the assessment data": "Değerlendirme verilerini analiz etme",
    "Report the assessment results": "Değerlendirme sonuçlarını raporlama",
    "Maintain assessment record": "Değerlendirme kaydını sürdürme",
    "Establish commitment": "Taahhüt oluşturma",
    "Identify issues": "Sorunları belirleme",
    "Establish process improvement objectives": "Süreç iyileştirme hedeflerini oluşturma",
    "Prioritize improvements": "İyileştirmeleri önceliklendirme",
    "Plan process changes": "Süreç değişikliklerini planlama",
    "Implement process changes": "Süreç değişikliklerini uygulama",
    "Confirm process improvement": "Süreç iyileştirmesini doğrulama",
    "Communicate results of improvement": "İyileştirme sonuçlarını duyurma",
    "Evaluate the results of the improvement project": "İyileştirme projesi sonuçlarını değerlendirme",
    "Define the scope of work": "İş kapsamını tanımlama",
    "Define project life cycle": "Proje yaşam döngüsünü tanımlama",
    "Evaluate feasibility of the project": "Projenin yapılabilirliğini değerlendirme",
    "Determine and maintain estimates for project attributes": "Proje özellikleri için tahminleri belirleme ve sürdürme",
    "Define project activities and tasks": "Proje faaliyet ve görevlerini tanımlama",
    "Define needs for experience, knowledge and skills": "Deneyim, bilgi ve beceri ihtiyaçlarını tanımlama",
    "Define project schedule": "Proje takvimini tanımlama",
    "Identify and monitor project interfaces": "Proje arayüzlerini belirleme ve izleme",
    "Allocate responsibilities": "Sorumlulukları atama",
    "Establish project plan": "Proje planını oluşturma",
    "Implement the project plan": "Proje planını uygulama",
    "Monitor project attributes": "Proje özelliklerini izleme",
    "Review progress of the project": "Proje ilerlemesini gözden geçirme",
    "Act to correct deviations": "Sapmaları düzeltmek için aksiyon alma",
    "Establish risk management scope": "Risk yönetimi kapsamını oluşturma",
    "Define risk management strategies": "Risk yönetimi stratejilerini tanımlama",
    "Identify risks": "Riskleri belirleme",
    "Analyze risks": "Riskleri analiz etme",
    "Define and perform risk treatment actions": "Risk işleme aksiyonlarını tanımlama ve gerçekleştirme",
    "Monitor risks": "Riskleri izleme",
    "Take preventive or corrective action": "Önleyici veya düzeltici aksiyon alma",
    "Obtain customer requirements and requests": "Müşteri gereksinim ve taleplerini alma",
    "Understand customer expectations": "Müşteri beklentilerini anlama",
    "Agree on requirements": "Gereksinimler üzerinde mutabakat sağlama",
    "Establish customer requirements baseline": "Müşteri gereksinimleri temel çizgisini oluşturma",
    "Manage customer requirements changes": "Müşteri gereksinimi değişikliklerini yönetme",
    "Establish customer query mechanism": "Müşteri soru mekanizmasını oluşturma",
    "Specify software requirements": "Yazılım gereksinimlerini belirleme",
    "Determine operating environment impact": "Çalışma ortamı etkisini belirleme",
    "Develop criteria for software testing": "Yazılım testi kriterlerini geliştirme",
    "Ensure consistency": "Tutarlılığı sağlama",
    "Evaluate and update software requirements": "Yazılım gereksinimlerini değerlendirme ve güncelleme",
    "Communicate software requirements": "Yazılım gereksinimlerini duyurma",
    "Describe software architecture": "Yazılım mimarisini açıklama",
    "Define interfaces": "Arayüzleri tanımlama",
    "Develop detailed design": "Ayrıntılı tasarımı geliştirme",
    "Analyze the design for testability": "Tasarımı test edilebilirlik açısından analiz etme",
    "Develop unit verification procedures": "Birim doğrulama prosedürlerini geliştirme",
    "Develop software units": "Yazılım birimlerini geliştirme",
    "Verify software units": "Yazılım birimlerini doğrulama",
    "Develop software integration strategy": "Yazılım entegrasyon stratejisini geliştirme",
    "Develop tests for integrated software items": "Entegre yazılım öğeleri için testleri geliştirme",
    "Integrate software item": "Yazılım öğesini entegre etme",
    "Test integrated software items": "Entegre yazılım öğelerini test etme",
    "Regression test integrated software items": "Entegre yazılım öğeleri için regresyon testi yapma",
    "Develop tests for integrated software product": "Entegre yazılım ürünü için testleri geliştirme",
    "Test integrated software product": "Entegre yazılım ürününü test etme",
    "Regression test integrated software": "Entegre yazılım için regresyon testi yapma",
    "Define release products": "Yayın ürünlerini tanımlama",
    "Prepare product for delivery": "Ürünü teslimata hazırlama",
    "Establish a product release classification and numbering scheme": "Ürün yayını sınıflandırma ve numaralandırma yapısını oluşturma",
    "Define the build activities and build environment": "Derleme faaliyetlerini ve derleme ortamını tanımlama",
    "Build the release from configured items": "Yayını yapılandırılmış öğelerden derleme",
    "The type, level and duration of support for a release are communicated": "Yayın desteğinin türünü, seviyesini ve süresini duyurma",
    "Determine the delivery media type for the release": "Yayın için teslim ortamı türünü belirleme",
    "Identify the packaging for the release media": "Yayın ortamı için paketlemeyi belirleme",
    "Define and produce the software product release documentation": "Yazılım ürün yayını dokümantasyonunu tanımlama ve üretme",
    "Ensure product release approval before delivery": "Teslimat öncesi ürün yayını onayını sağlama",
    "Deliver the release to the intended customer": "Yayını hedef müşteriye teslim etme",
    "Develop configuration management strategy": "Yapılandırma yönetimi stratejisini geliştirme",
    "Identify configuration items": "Yapılandırma öğelerini belirleme",
    "Establish branch management strategy": "Dal yönetimi stratejisini oluşturma",
    "Establish baselines": "Temel çizgileri oluşturma",
    "Maintain configuration item description": "Yapılandırma öğesi açıklamasını sürdürme",
    "Control modifications and releases": "Değişiklikleri ve yayınları kontrol etme",
    "Maintain configuration item history": "Yapılandırma öğesi geçmişini sürdürme",
    "Report configuration status": "Yapılandırma durumunu raporlama",
    "Verify the information about configured items": "Yapılandırılmış öğelere ilişkin bilgileri doğrulama",
    "Manage the backup, storage, archiving, handling and delivery of configured items": "Yapılandırılmış öğelerin yedekleme, saklama, arşivleme, işleme ve teslimatını yönetme",
    "Develop problem resolution strategy": "Problem çözüm stratejisini geliştirme",
    "Identify and record the problem": "Problemi belirleme ve kaydetme",
    "Provide initial support and classification": "İlk destek ve sınıflandırma sağlama",
    "Investigate and diagnose the cause of the problem": "Problemin nedenini araştırma ve teşhis etme",
    "Assess the impact of the problem to determine solution": "Çözümü belirlemek için problemin etkisini değerlendirme",
    "Execute urgent resolution action, where necessary": "Gerekli olduğunda acil çözüm aksiyonu yürütme",
    "Raise alert notifications, where necessary": "Gerekli olduğunda uyarı bildirimleri oluşturma",
    "Implement problem resolution": "Problem çözümünü uygulama",
    "Initiate change request": "Değişiklik talebi başlatma",
    "Track problem status": "Problem durumunu izleme",
    "Develop a change management strategy": "Değişiklik yönetimi stratejisini geliştirme",
    "Record the request for change": "Değişiklik talebini kaydetme",
    "Record the status of change requests": "Değişiklik taleplerinin durumunu kaydetme",
    "Establish the dependencies and relationships to other change requests": "Diğer değişiklik talepleriyle bağımlılık ve ilişkileri oluşturma",
    "Assess the impact of the change": "Değişikliğin etkisini değerlendirme",
    "Identify the verification and validation activities to be performed for implemented changes": "Uygulanan değişiklikler için doğrulama ve geçerleme faaliyetlerini belirleme",
    "Approve changes": "Değişiklikleri onaylama",
    "Implement the change": "Değişikliği uygulama",
    "Review the implemented change": "Uygulanan değişikliği gözden geçirme",
    "Identify needed skills and competencies": "Gerekli beceri ve yetkinlikleri belirleme",
    "Define evaluation criteria": "Değerlendirme kriterlerini tanımlama",
    "Recruit qualified staff": "Nitelikli personel temin etme",
    "Develop staff skills and competencies": "Personel beceri ve yetkinliklerini geliştirme",
    "Define team organization for projects and tasks": "Proje ve görevler için ekip organizasyonunu tanımlama",
    "Empower project teams": "Proje ekiplerini yetkilendirme",
    "Maintain project team interactions": "Proje ekibi etkileşimlerini sürdürme",
    "Evaluate staff performance": "Personel performansını değerlendirme",
    "Provide feedback on performance": "Performans hakkında geri bildirim sağlama",
    "Maintain staff records": "Personel kayıtlarını sürdürme",
    "Develop a strategy for training": "Eğitim stratejisini geliştirme",
    "Identify needs for training": "Eğitim ihtiyaçlarını belirleme",
    "Develop or acquire training": "Eğitimi geliştirme veya temin etme",
    "Prepare for training execution": "Eğitim uygulamasına hazırlık yapma",
    "Train personnel": "Personeli eğitme",
    "Maintain staff training records": "Personel eğitim kayıtlarını sürdürme",
    "Evaluate training effectiveness": "Eğitim etkinliğini değerlendirme",
    "Establish a knowledge management system": "Bilgi yönetim sistemini oluşturma",
    "Create the network of knowledge contributors": "Bilgi katkı sağlayıcıları ağını oluşturma",
    "Develop a knowledge management strategy": "Bilgi yönetimi stratejisini geliştirme",
    "Capture knowledge": "Bilgiyi yakalama",
    "Disseminate knowledge assets": "Bilgi varlıklarını yaygınlaştırma",
    "Improve knowledge assets": "Bilgi varlıklarını iyileştirme",
    "Identify infrastructure scope": "Altyapı kapsamını belirleme",
    "Define the infrastructure requirements": "Altyapı gereksinimlerini tanımlama",
    "Acquire infrastructure": "Altyapıyı temin etme",
    "Establish the infrastructure": "Altyapıyı kurma",
    "Provide support for the infrastructure": "Altyapı için destek sağlama",
    "Maintain the infrastructure": "Altyapıyı sürdürme",
    "Identify management infrastructure": "Yönetim altyapısını belirleme",
    "Provide management infrastructure: Provide the identified management infrastructure appropriate in organization's broader scope": "Yönetim altyapısını sağlama",
    "Identify and implement software management practices": "Yazılım yönetimi uygulamalarını belirleme ve uygulama",
    "Perform identified management practices": "Belirlenen yönetim uygulamalarını gerçekleştirme",
    "Evaluate effectiveness": "Etkinliği değerlendirme",
    "Provide support to adopt best practices": "En iyi uygulamaların benimsenmesi için destek sağlama",
    "Establish quality goals": "Kalite hedeflerini oluşturma",
    "Define overall strategy": "Genel stratejiyi tanımlama",
    "Define quality criteria": "Kalite kriterlerini tanımlama",
    "Establish a quality management system": "Kalite yönetim sistemini oluşturma",
    "Assess achievement of quality goals": "Kalite hedeflerine ulaşımı değerlendirme",
    "Collect feedback": "Geri bildirim toplama",
    "Monitor actual performance of quality": "Kalitenin gerçekleşen performansını izleme",
    "Establish organizational commitment for measurement": "Ölçüm için kurumsal taahhüt oluşturma",
    "Develop a measurement strategy": "Ölçüm stratejisini geliştirme",
    "Identify measurement information needs": "Ölçüm bilgi ihtiyaçlarını belirleme",
    "Specify measures": "Ölçümleri belirleme",
    "Collect and store measurement data": "Ölçüm verilerini toplama ve saklama",
    "Analyze measurement data": "Ölçüm verilerini analiz etme",
    "Use measurement information products for decision-making": "Ölçüm bilgi ürünlerini karar verme için kullanma",
    "Communicate measurement results": "Ölçüm sonuçlarını duyurma",
    "Evaluate and communicate information products and measurement activities to process owners": "Bilgi ürünleri ve ölçüm faaliyetlerini süreç sahiplerine değerlendirme ve duyurma",
    "Develop and implement an audit strategy": "Denetim stratejisini geliştirme ve uygulama",
    "Select auditors": "Denetçileri seçme",
    "Audit for conformance against the requirements": "Gereksinimlere uygunluğu denetleme",
    "Prepare and distribute an audit report": "Denetim raporunu hazırlama ve dağıtma",
    "Take corrective action": "Düzeltici aksiyon alma",
    "Track resolution": "Çözümün tamamlanmasını izleme",
}

GP_TITLE_TR = {
    "GP.2.1.1": "Süreç performansı için hedefleri belirleme",
    "GP.2.1.2": "Tanımlanan hedefleri karşılamak için süreç performansını planlama ve izleme",
    "GP.2.1.3": "Süreç performansını ayarlama",
    "GP.2.1.4": "Süreci gerçekleştirmek için sorumluluk ve yetkileri tanımlama",
    "GP.2.1.5": "Süreci plana göre gerçekleştirmek için kaynakları belirleme ve kullanıma sunma",
    "GP.2.1.6": "İlgili taraflar arasındaki arayüzleri yönetme",
    "GP.2.2.1": "İş ürünleri için gereksinimleri tanımlama",
    "GP.2.2.2": "İş ürünlerinin dokümantasyonu ve kontrolü için gereksinimleri tanımlama",
    "GP.2.2.3": "İş ürünlerini belirleme, dokümante etme ve kontrol etme",
    "GP.2.2.4": "İş ürünlerini tanımlı gereksinimleri karşılayacak şekilde gözden geçirme ve düzenleme",
    "GP.3.1.1": "Tanımlı sürecin uygulanmasını destekleyecek standart süreci tanımlama",
    "GP.3.1.2": "Süreçlerin bütünleşik bir sistem olarak çalışması için sıra ve etkileşimleri belirleme",
    "GP.3.1.3": "Standart süreci gerçekleştirmek için rol ve yetkinlikleri belirleme",
    "GP.3.1.4": "Standart sürecin gerçekleştirilmesi için gerekli altyapı ve çalışma ortamını belirleme",
    "GP.3.1.5": "Standart sürecin etkinliğini ve uygunluğunu izlemek için uygun yöntemleri belirleme",
    "GP.3.2.1": "Standart sürecin kullanım bağlamı gereksinimlerini karşılayan tanımlı süreci uygulamaya alma",
    "GP.3.2.2": "Tanımlı süreci gerçekleştirmek için rol, sorumluluk ve yetkileri atama ve duyurma",
    "GP.3.2.3": "Tanımlı süreci gerçekleştirmek için gerekli yetkinlikleri sağlama",
    "GP.3.2.4": "Tanımlı sürecin performansını desteklemek için kaynak ve bilgi sağlama",
    "GP.3.2.5": "Sürecin performansını desteklemek için yeterli süreç altyapısı sağlama",
    "GP.3.2.6": "Sürecin uygunluğunu ve etkinliğini göstermek için performans verilerini toplama ve analiz etme",
}

TR_MAP = str.maketrans({"İ":"i","I":"i","ı":"i","Ü":"u","ü":"u","Ç":"c","ç":"c","Ş":"s","ş":"s","Ö":"o","ö":"o","Ğ":"g","ğ":"g"})

CSS = """body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}h1,h2,h3{color:#0f172a;line-height:1.25}h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}th{background:#f6f8fa;font-weight:600;text-align:left}.small{font-size:.92em;color:#57606a}.nowrap{white-space:nowrap}"""


def slugify(value: str) -> str:
    value = value.translate(TR_MAP).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def weekdays(start: date, count: int) -> list[date]:
    out, cur = [], start
    while len(out) < count:
        if cur.weekday() < 5:
            out.append(cur)
        cur += timedelta(days=3)
    return out


def load_yaml() -> dict:
    with SPICE_YAML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    required_pas = {"PA_2_1": 6, "PA_2_2": 4, "PA_3_1": 5, "PA_3_2": 6}
    if len(data.get("processes", [])) != 26:
        raise SystemExit("resources/standards/spice_practices.yaml içinde 26 süreç bulunamadı.")
    gps = data.get("generic_practices", {})
    missing = [pa for pa, cnt in required_pas.items() if len(gps.get(pa, {}).get("practices", [])) != cnt]
    if missing:
        raise SystemExit(f"Eksik PA/GP tanımı: {', '.join(missing)}")
    return data


def process_status(code: str) -> str:
    return "Aktif" if code in {"SRÇ.001", "SRÇ.004"} else "Dokümantasyon Hazırlanıyor"


def owner(code: str) -> str:
    return PROCESS_OWNER.get(code, "Daha sonra süreç sahibi yazılacak")


def assessment_summary(proc: dict) -> str:
    code = proc["corporate_code"]
    name = proc["corporate_name"]
    if code == "SRÇ.001":
        return ("Dokümantasyon Süreci için mevcut süreç tanımı ve ilişkili alt dokümanlar üzerinden ön değerlendirme yapılmıştır. "
                "Süreç sayfası, aktif doküman listesi, iş ürünleri ve kalite kriterleri listesi, performans ölçüm seti ve RACI matrisi kanıt adayı olarak belirlenmiştir. "
                "Bu form, nihai uygunluk kararı vermek yerine BP ve PA/GP bazlı kanıt doğrulamasına temel oluşturmak amacıyla hazırlanmıştır.")
    if code == "SRÇ.004":
        return ("Süreç Kurulumu Süreci için mevcut süreç tanımı ve ilişkili süreç mimarisi/kayıt listeleri üzerinden ön değerlendirme yapılmıştır. "
                "Kanıt setleri aday düzeyde ele alınmış; süreç mimarisi, süreç kurulum yaklaşımı, iş ürünleri, ölçüm seti ve RACI kayıtlarının ayrıntılı doğrulanması sonraki gözden geçirmede sürdürülecektir.")
    return (f"{name} için süreç gözden geçirme kaydı hazırlık düzeyinde açılmıştır. Süreç dokümantasyonu ve ilişkili kanıt setleri tamamlandıkça BP ve PA/GP bazlı değerlendirme güncellenecektir.")


def evidence_for(code: str) -> str:
    if code == "SRÇ.001":
        return "Kanıt Adayı: SRÇ.001; LST.001; LST.008; LST.009; LST.010; PRS.001"
    if code == "SRÇ.004":
        return "Kanıt Adayı: SRÇ.004; LST.007; LST.008; LST.009; LST.010"
    return "Değerlendirilecek"


def current_coverage(code: str, kind: str) -> str:
    if code in {"SRÇ.001", "SRÇ.004"}:
        return "Mevcut dokümantasyon ve ilişkili alt dokümanlar aday kanıt olarak belirlenmiştir."
    if kind == "BP":
        return "Süreç dokümantasyonu tamamlandığında değerlendirilecektir."
    return "PA/GP karşılaması süreç dokümantasyonu ve uygulama kayıtları tamamlandığında değerlendirilecektir."


def status_for(code: str) -> str:
    return "ZAYIF" if code in {"SRÇ.001", "SRÇ.004"} else "YOK"


def action_for(code: str, ref: str) -> str:
    if code in {"SRÇ.001", "SRÇ.004"}:
        return f"{ref} için kanıt adayları ayrıntılı doğrulanmalı ve eksik kayıtlar tamamlanmalı."
    return f"{ref} için süreç dokümanı, iş ürünleri ve uygulama kanıtları oluşturulmalı."


def bp_rows(proc: dict) -> str:
    rows = []
    code = proc["corporate_code"]
    for bp in proc["base_practices"]:
        ref = bp["id"]
        title = BP_TITLE_TR.get(bp.get("title", ""), bp.get("title", ""))
        rows.append(f"<tr><td>{e(ref)}</td><td>{e(title)}</td><td>{e(current_coverage(code, 'BP'))}</td><td>{e(evidence_for(code))}</td><td>{e(status_for(code))}</td><td>{e(action_for(code, ref))}</td></tr>")
    return "\n".join(rows)


def gp_rows(proc: dict, gps: dict) -> str:
    rows = []
    code = proc["corporate_code"]
    for pa_key, pa_label in [("PA_2_1", "PA 2.1"), ("PA_2_2", "PA 2.2"), ("PA_3_1", "PA 3.1"), ("PA_3_2", "PA 3.2")]:
        for gp in gps[pa_key]["practices"]:
            ref = gp["id"]
            title = GP_TITLE_TR.get(ref, gp.get("title", ""))
            rows.append(f"<tr><td>{pa_label}</td><td>{e(ref)}</td><td>{e(title)}</td><td>{e(current_coverage(code, 'GP'))}</td><td>{e(evidence_for(code))}</td><td>{e(status_for(code))}</td><td>{e(action_for(code, ref))}</td></tr>")
    return "\n".join(rows)


def completion_rows(proc: dict) -> str:
    code = proc["corporate_code"]
    process_name = proc["corporate_name"]
    bp_first = proc["base_practices"][0]["id"]
    if code in {"SRÇ.001", "SRÇ.004"}:
        items = [
            (1, f"{process_name} için kanıt adaylarının BP ve PA/GP bazında doğrulanması", f"{bp_first}, GP.2.2.4", "30.09.2025"),
            (2, f"{process_name} kapsamındaki eksik gözden geçirme/onay kayıtlarının tamamlanması", "GP.2.2.3, GP.3.2.6", "15.10.2025"),
            (3, f"{process_name} performans ölçüm sonuçlarının toplanması ve analiz edilmesi", "GP.2.1.1, GP.3.1.5, GP.3.2.6", "31.10.2025"),
        ]
    else:
        items = [
            (1, f"{process_name} süreç tanımının hazırlanması", f"{bp_first}, GP.3.1.1", "31.10.2025"),
            (2, f"{process_name} için iş ürünleri ve kalite kriterleri listesinin oluşturulması", "GP.2.2.1, GP.2.2.2", "14.11.2025"),
            (3, f"{process_name} için rol, sorumluluk ve RACI bilgisinin tamamlanması", "GP.2.1.4, GP.3.1.3, GP.3.2.2", "28.11.2025"),
            (4, f"{process_name} için performans ölçüm seti ve izleme kayıtlarının oluşturulması", "GP.2.1.1, GP.3.1.5, GP.3.2.6", "12.12.2025"),
        ]
    return "\n".join(f"<tr><td style=\"text-align:right;\">{n}</td><td>{e(action)}</td><td>{e(refs)}</td><td>{date_}</td></tr>" for n, action, refs, date_ in items)


def body_inner(proc: dict, eval_date: date, gps: dict) -> str:
    code = proc["corporate_code"]
    title = f"FRM.001 - Süreç Gözden Geçirme Matrisi ({code})"
    bp_count = len(proc["base_practices"])
    return f"""<h1>{e(title)}</h1>
<h2>1. Değerlendirme Özeti</h2>
<table>
<thead><tr><th>Alan</th><th>Değer</th></tr></thead>
<tbody>
<tr><td>Değerlendirilen Süreç</td><td>{e(code)} - {e(proc['corporate_name'])}</td></tr>
<tr><td>Süreç Referansı</td><td>{e(proc['spice_code'])} - {e(proc['spice_name'])}</td></tr>
<tr><td>Süreç Durumu</td><td>{process_status(code)}</td></tr>
<tr><td>Süreç Sürümü</td><td>v1.0</td></tr>
<tr><td>Değerlendirme Kapsamı</td><td>SPICE Seviye 3<br/>PA 1.1 (BP.1 - BP.{bp_count})<br/>PA 2.1 (GP.2.1.1 - GP.2.1.6)<br/>PA 2.2 (GP.2.2.1 - GP.2.2.4)<br/>PA 3.1 (GP.3.1.1 - GP.3.1.5)<br/>PA 3.2 (GP.3.2.1 - GP.3.2.6)</td></tr>
<tr><td>Değerlendirme Tarihi</td><td>{eval_date.strftime('%d.%m.%Y')}</td></tr>
<tr><td>Değerlendirmeyi Yapan</td><td>Soner DEDEOĞLU - Kalite Denetleyicisi/Danışmanı</td></tr>
<tr><td>Değerlendirmeyi Onaylayan</td><td>{e(owner(code))}</td></tr>
<tr><td>Değerlendirme Sonucu</td><td>{e(assessment_summary(proc))}</td></tr>
</tbody>
</table>

<h2>2. Durum Değerleri</h2>
<table>
<thead><tr><th>Durum</th><th>Anlamı</th></tr></thead>
<tbody>
<tr><td>VAR</td><td>Beklenti mevcut doküman/kayıt setiyle büyük ölçüde karşılanıyor.</td></tr>
<tr><td>ZAYIF</td><td>Temel yapı var; ancak uygulama kaydı, onay, ölçüm, kapanış veya izlenebilirlik güçlendirilmeli.</td></tr>
<tr><td>DAĞINIK</td><td>Bilgi birden fazla yerde var; tekil ve tutarlı izlenebilirlik güçlendirilmeli.</td></tr>
<tr><td>YOK</td><td>Beklentiyi karşılayan yeterli kayıt veya tanım henüz yok.</td></tr>
<tr><td>KAPSAM DIŞI</td><td>Bu değerlendirme bağlamında uygulanmıyor.</td></tr>
</tbody>
</table>

<h2>3. BP Takip Matrisi</h2>
<table>
<thead><tr><th>BP</th><th>Standart Beklentisi</th><th>Mevcut Karşılama</th><th>Karşılayan Doküman / Kayıt</th><th>Durum</th><th>Eksik / Tamamlayıcı Aksiyon</th></tr></thead>
<tbody>
{bp_rows(proc)}
</tbody>
</table>

<h2>4. PA / GP Takip Matrisi</h2>
<table>
<thead><tr><th>PA</th><th>GP</th><th>Standart Beklentisi</th><th>Mevcut Karşılama</th><th>Karşılayan Doküman / Kayıt</th><th>Durum</th><th>Eksik / Tamamlayıcı Aksiyon</th></tr></thead>
<tbody>
{gp_rows(proc, gps)}
</tbody>
</table>

<h2>5. Öncelikli Tamamlama Listesi</h2>
<table>
<thead><tr><th style="text-align:right;">Öncelik</th><th>Aksiyon</th><th>İlgili BP / GP</th><th>Hedef Kapanış</th></tr></thead>
<tbody>
{completion_rows(proc)}
</tbody>
</table>"""


def view_html(title: str, inner: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
{inner}
</main>
</body>
</html>
"""


def write_page(proc: dict, eval_date: date, gps: dict) -> dict:
    code = proc["corporate_code"]
    title = f"FRM.001 - Süreç Gözden Geçirme Matrisi ({code})"
    slug = slugify(title)
    folder = TARGET_PARENT / slug
    folder.mkdir(parents=True, exist_ok=True)
    inner = body_inner(proc, eval_date, gps)
    (folder / "body.storage.xhtml").write_text(inner + "\n", encoding="utf-8")
    (folder / "body.view.html").write_text(view_html(title, inner), encoding="utf-8")
    meta = {
        "page_id": "",
        "space": "SSSS",
        "title": title,
        "parent_id": "137265917",
        "parent_title": "Süreç Gözden Geçirmeleri",
        "version": "draft",
        "url": "",
        "depth": 3,
        "status": "draft-ready",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": str(folder.relative_to(ROOT / "confluence")).replace("\\", "/"),
        "slug": slug,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
        "document_code": "FRM.001",
        "related_process_code": code,
        "related_process_name": proc["corporate_name"],
        "spice_reference": f"{proc['spice_code']} - {proc['spice_name']}",
    }
    (folder / "page.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return meta


def update_index(generated: list[dict]) -> None:
    if not INDEX_YAML.exists():
        return
    data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
    pages = data.get("pages", [])
    generated_titles = {item["title"] for item in generated}
    pages = [p for p in pages if p.get("title") not in generated_titles]
    for item in generated:
        pages.append({
            "page_id": item["page_id"],
            "title": item["title"],
            "parent_id": item["parent_id"],
            "depth": item["depth"],
            "relative_path": item["relative_path"],
            "slug": item["slug"],
            "storage_file": f"{item['relative_path']}/body.storage.xhtml",
            "view_file": f"{item['relative_path']}/body.view.html",
        })
    data["pages"] = pages
    data["total_page_count"] = len(pages)
    data["exported_at"] = datetime.now(timezone.utc).isoformat()
    INDEX_YAML.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    data = load_yaml()
    dates = weekdays(date(2025, 9, 1), len(data["processes"]))
    generated = []
    for proc, eval_date in zip(data["processes"], dates):
        generated.append(write_page(proc, eval_date, data["generic_practices"]))
    update_index(generated)
    if DRAFTS.exists():
        shutil.rmtree(DRAFTS)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Süreç Gözden Geçirme Formları Üretim Raporu",
        "",
        f"Üretilen form sayısı: {len(generated)}",
        f"Hedef klasör: `{TARGET_PARENT.relative_to(ROOT)}`",
        "",
        "## Üretilen Sayfalar",
        *[f"- {g['title']}" for g in generated],
        "",
    ]), encoding="utf-8")
    print(f"[DONE] {len(generated)} süreç gözden geçirme formu üretildi.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
