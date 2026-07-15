#!/usr/bin/env python3
"""Align the active LST.010 template and completed process records to SRÇ.006.

This script is local-only. It keeps Confluence ids and page metadata intact and
only replaces the LST.010 storage/view bodies plus their local update timestamp.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAGE_ROOT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
PROCESS_ROOT = PAGE_ROOT / "01-surec-dokumanlari"
TEMPLATE_DIR = PAGE_ROOT / "02-sablonlar/lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu"
REFERENCE_DIR = PROCESS_ROOT / "src-006-surec-iyilestirme-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-006"

PREPARED = "Soner DEDEOĞLU - Kalite Danışmanı"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1200px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
blockquote{margin:16px 0;padding:8px 16px;border-left:4px solid #c9d1d9;color:#57606a;background:#f6f8fa}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def em(value: str) -> str:
    return f"<em>{esc(value)}</em>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{esc(item)}</th>" for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def history(process_name: str, reviewer: str, approver: str) -> list[list[str]]:
    return [
        ["v0.1", "10-01-2025", "İlk taslak oluşturuldu.", PREPARED, "-", "-"],
        ["v1.0", "15-02-2025", f"{process_name} rol, yetki ve RACI matrisi onaylanarak yürürlüğe girmiştir.", PREPARED, reviewer, approver],
    ]


def build_view(title: str, storage: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f"<title>{esc(title)}</title><style>{CSS}</style></head>"
        f'<body><main class="confluence-page"><h1>{esc(title)}</h1>{storage}</main></body></html>\n'
    )


def process_body(spec: dict[str, Any]) -> str:
    usage = [["R", "Faaliyeti gerçekleştiren / iş ürününü hazırlayan"], ["A", "Nihai hesap veren ve onaylayan"], ["C", "Görüşüne başvurulan"], ["I", "Bilgilendirilen"]]
    usage.extend(spec.get("usage_extra", []))
    headers = ["Faaliyet / İş Ürünü", *spec["raci_roles"]]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [
            ["İlgili Süreç", spec["process"]],
            ["Kullanım Amacı", spec["purpose"]],
            ["Sorumlu", spec["owner"]],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
        ]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], usage),
        "<h2>3. Rol ve Yetkinlik Matrisi</h2>", table(["Rol", "Sorumluluk", "Yetki", "Asgari Yetkinlik", "Süreçteki Konum"], spec["roles"]),
        "<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>", table(headers, spec["activities"]),
        "<h2>5. İş Ürünleri RACI Matrisi</h2>", table(headers, spec["products"]),
        "<h2>6. Yetki ve Onay Matrisi</h2>", table(["Karar / Onay", "Hazırlayan", "Gözden Geçiren", "Onaylayan", "Yetki Sınırı / Kural"], spec["authority"]),
        "<h2>7. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], history(spec["name"], spec["reviewer"], spec["approver"])),
    ]) + "\n"


def src001() -> dict[str, Any]:
    roles = [
        ["Süreç Sahibi", "Dokümantasyon Sürecinin uygulanmasını ve sürdürülmesini sahiplenmek", "Süreç kapsamında karar vermek ve onaylı dokümanların yayımlanmasını sağlamak", "Süreç yönetimi, dokümantasyon kuralları ve kurumsal yayın yapısı", "Süreç sahibi / hesap veren"],
        ["Doküman Hazırlayan", "Yeni dokümanları ve güncellemeleri aktif şablonlara göre hazırlamak", "Kendisine verilen kapsamda içerik oluşturmak ve güncellemek", "İlgili süreç/proje bilgisi, yazım kuralları ve şablon kullanımı", "Hazırlayan"],
        ["Doküman Gözden Geçiren", "İçerik, biçim, izlenebilirlik ve kalite kriterlerini kontrol etmek", "Düzeltme istemek ve gözden geçirme görüşü vermek", "Doküman gözden geçirme, kalite kriterleri ve süreç bilgisi", "Gözden geçiren"],
        ["Doküman Sorumlusu", "Aktif doküman, değişiklik, yayın ve arşiv kayıtlarını güncel tutmak", "Onaylı kapsamda kayıt, yayın ve arşiv işlemlerini yürütmek", "Confluence/repository, doküman kodlama ve kayıt yönetimi", "Kayıt ve yayın sorumlusu"],
        ["Kalite Danışmanı", "Şablon, kontrol ve SPICE uyum yaklaşımını desteklemek", "Uygunluk görüşü vermek ve kalite düzeltmesi önermek", "ISO/IEC 15504-5, süreç dokümantasyonu ve kalite güvence", "Kalite desteği / hazırlayan"],
        ["Bilgi İşlem Daire Başkanı", "Kurumsal yürürlük ve kritik doküman kararlarını onaylamak", "Nihai kurumsal onay vermek", "Kurumsal yetki sınırları ve yönetim sistemi", "Onaylayan"],
        ["İlgili Paydaş", "İçerik ve uygulama açısından görüş vermek ve bilgilendirilmek", "Kendi görev alanında uygunluk görüşü vermek", "Kendi görev alanına ilişkin süreç/proje bilgisi", "Danışılan / bilgilendirilen"],
    ]
    rr = ["Süreç Sahibi", "Doküman Hazırlayan", "Doküman Gözden Geçiren", "Doküman Sorumlusu", "Kalite Danışmanı", "BİD Başkanı", "İlgili Paydaş"]
    activities = [
        ["F1 Dokümantasyon stratejisini ve kapsamını uygula", "R/A", "I", "I", "C", "R", "I", "C"],
        ["F2 Doküman standardı ve şablonu belirle", "A", "C", "C", "R", "R", "I", "I"],
        ["F3 Üretilecek dokümanı tanımla", "A", "R", "C", "I", "R", "I", "C"],
        ["F4 Dokümanı hazırla veya güncelle", "A", "R", "I", "R", "C", "I", "C"],
        ["F5 Dokümanı gözden geçir ve onaylat", "A", "I", "R", "I", "C", "C", "C"],
        ["F6 Dokümanı yayımla ve erişime aç", "A", "I", "R", "R", "C", "C", "I"],
        ["F7 Dokümanı sürdür ve arşivle", "A", "C", "C", "R", "C", "I", "I"],
    ]
    products = [
        ["PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "A", "I", "C", "C", "R", "I", "C"],
        ["Aktif doküman şablonları", "A", "C", "C", "R", "R", "I", "I"],
        ["KLV.001 - Doküman Yazım Kuralları Talimatı", "A", "I", "C", "R", "R", "I", "I"],
        ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.001)", "A", "I", "C", "I", "R", "I", "I"],
        ["LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "R/A", "I", "I", "R", "C", "I", "C"],
        ["Hazırlanmış veya güncellenmiş doküman", "A", "R", "C", "I", "C", "I", "C"],
        ["LST.003 - Doküman Gözden Geçirme Kaydı", "A", "I", "R", "C", "C", "I", "I"],
        ["LST.001 - Aktif Dokümanlar Listesi", "A", "I", "C", "R", "C", "I", "I"],
        ["LST.002 - Doküman Değişiklik Kaydı", "A", "I", "C", "R", "C", "I", "I"],
        ["LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "A", "I", "I", "R", "C", "I", "I"],
        ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.001)", "A", "I", "C", "I", "R", "I", "I"],
    ]
    return {"process": "SRÇ.001 - Dokümantasyon Süreci", "name": "Dokümantasyon Süreci", "purpose": "SRÇ.001 rol, yetki, yetkinlik ve RACI yapısını tanımlamak", "owner": "Levent BAYEZİT - Proje Yöneticisi", "reviewer": "Levent BAYEZİT - Proje Yöneticisi", "approver": "Mustafa Nusret SARISAKAL - BİD Başkanı", "raci_roles": rr, "roles": roles, "activities": activities, "products": products, "authority": [
        ["Dokümantasyon stratejisi ve prosedür yaklaşımı", "Süreç Sahibi / Kalite Danışmanı", "Doküman Gözden Geçiren", "Bilgi İşlem Daire Başkanı", "Strateji ve prosedür değişiklikleri onaya ve sürüm izlenebilirliğine tabidir."],
        ["Şablon oluşturma veya güncelleme", "Doküman Sorumlusu / Kalite Danışmanı", "Doküman Gözden Geçiren", "Süreç Sahibi", "Aktif şablon değişikliği izlenebilir olmalıdır."],
        ["Doküman hazırlama veya güncelleme", "Doküman Hazırlayan", "Doküman Gözden Geçiren", "Süreç Sahibi; kritik/yürürlük kararında BİD Başkanı", "Yeni yayın veya kritik güncelleme onay gerektirir."],
        ["Doküman yayımlama ve erişime açma", "Doküman Sorumlusu", "Kalite Danışmanı", "Süreç Sahibi", "Yalnızca gözden geçirilmiş ve onaylı sürüm aktif alanda yayımlanır."],
        ["Doküman pasife alma veya arşivleme", "Doküman Sorumlusu", "Kalite Danışmanı", "Süreç Sahibi", "Gerekçe LST.002 üzerinde izlenir."],
    ]}


def src004() -> dict[str, Any]:
    rr = ["BİD Başkanı", "Kalite Danışmanı / Süreç Mimarı", "Proje Yöneticisi", "İlgili Süreç Sahibi", "Ölçüm Sorumlusu", "Doküman Sorumlusu", "Sistem / Eğitim Sorumlusu"]
    roles = [
        ["Bilgi İşlem Daire Başkanı", "Standart süreç setinin kurulmasını ve sürdürülmesini sahiplenmek", "Süreç mimarisi, paket ve kritik uyarlama kararlarını onaylamak", "Süreç yönetimi, kurumsal karar ve ISO/IEC 15504-5 yaklaşımı", "Süreç sahibi / onaylayan"],
        ["Kalite Danışmanı / Süreç Mimarı", "Süreç mimarisi, süreç tanımları, iş ürünleri, ölçümler ve uyarlama kurallarını tasarlamak", "Tasarım, sınıflandırma ve uygunluk önerisi vermek", "ISO/IEC 15504-5, süreç modelleme, BP/PA/GP ve şablonlar", "Hazırlayan / süreç mimarı"],
        ["Proje Yöneticisi", "Tasarım paketini uygulanabilirlik yönünden gözden geçirmek ve yayını koordine etmek", "Düzeltme istemek ve onaylı içeriği yayımlamak", "Proje yönetimi, Confluence, paydaş iletişimi ve doküman kontrolü", "Gözden geçiren / yayımlayan"],
        ["İlgili Süreç Sahibi", "Kendi sürecinin kapsam, faaliyet, iş ürünü, rol ve uygulama koşullarını doğrulamak", "Kendi süreç alanında uygunluk görüşü vermek", "İlgili iş alanı ve operasyonel uygulama", "Danışılan / uygulama sahibi"],
        ["Ölçüm Sorumlusu", "Ölçümleri tanımlamak, veriyi toplamak ve sapmaları raporlamak", "Onaylı ölçüm tanımı içinde veri toplamak ve hesaplamak", "Veri kaynağı, temel analiz ve ölçüm hesaplama", "Ölçüm hazırlayan / uygulayan"],
        ["Doküman Sorumlusu", "Kod, ad, sürüm, bağlantı ve repository tutarlılığını sağlamak", "Onaylı kapsamda kayıt ve yayın işlemi yürütmek", "SRÇ.001, aktif şablonlar, Confluence ve repository", "Kayıt sorumlusu"],
        ["Sistem / Eğitim Sorumlusu", "Gerekli erişim, çalışma ortamı, eğitim ve katılım desteğini sağlamak", "Kendi yetkilendirme alanında erişim/eğitim işlemi yürütmek", "Kurumsal araçlar, yetkilendirme veya eğitim yönetimi", "Koşullu destek rolü"],
    ]
    activities = [
        ["F1 Süreç mimarisini tanımla", "A", "R", "C", "C", "I", "I", "I"],
        ["F2 Süreçlerin kurumsal kullanımını destekle", "A", "C", "R", "I", "I", "C", "C"],
        ["F3 Standart süreçleri tanımla ve sürdür", "A", "R", "C", "R", "I", "C", "I"],
        ["F4 Performans beklentilerini belirle", "A", "R", "I", "C", "R", "I", "I"],
        ["F5 Süreç uyarlama kılavuzlarını oluştur", "A", "R", "C", "C", "I", "I", "I"],
        ["F6 Süreç kullanım verisini sürdür", "A", "C", "I", "R", "R", "I", "I"],
    ]
    products = [
        ["LST.006 - Standart Süreç Envanteri", "A", "R", "I", "C", "I", "C", "I"],
        ["LST.007 - Süreç Etkileşim Matrisi (SRÇ.004)", "A", "R", "C", "C", "I", "I", "I"],
        ["İlgili SRÇ.XXX - Süreç Tanımı", "A", "R", "C", "R", "I", "C", "I"],
        ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.004)", "A", "R", "I", "C", "I", "C", "I"],
        ["LST.009 - Süreç Performans Ölçüm Seti (SRÇ.004)", "A", "R", "I", "C", "R", "I", "I"],
        ["LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.004)", "A", "R", "C", "C", "I", "I", "I"],
        ["KLV.002 - Süreç Uyarlama Kılavuzu", "A", "R", "C", "C", "I", "I", "I"],
        ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.004)", "A", "R", "C", "C", "I", "I", "I"],
        ["Onaylı süreç varlıkları ve LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "A", "C", "R", "I", "I", "R", "C"],
        ["Süreç kullanım ve performans kayıtları", "A", "C", "I", "R", "R", "I", "I"],
    ]
    return {"process": "SRÇ.004 - Süreç Kurulumu Süreci", "name": "Süreç Kurulumu Süreci", "purpose": "SRÇ.004 rol, yetki, yetkinlik ve RACI yapısını tanımlamak", "owner": "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı", "reviewer": "Levent Bayezit - Proje Yöneticisi", "approver": "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı", "raci_roles": rr, "roles": roles, "activities": activities, "products": products, "authority": [
        ["Standart süreç mimarisi ve kapsamı", "Kalite Danışmanı / Süreç Mimarı", "Proje Yöneticisi / İlgili Süreç Sahipleri", "Bilgi İşlem Daire Başkanı", "Değişiklik ihtiyacı SRÇ.018 kapsamında yönetilir."],
        ["Süreç tasarım paketi", "Kalite Danışmanı / İlgili Süreç Sahibi", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı", "SRÇ ve süreç özel LST.007-LST.010 ile boş FRM.001 birlikte değerlendirilir."],
        ["Süreç uyarlaması veya zorunlu kontrol sapması", "Kalite Danışmanı / İlgili Süreç Sahibi", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı", "Süreç amacı ve zorunlu sonuçlar kaldırılamaz."],
        ["Onaylı dokümanı yayımlama ve duyurma", "Proje Yöneticisi / Doküman Sorumlusu", "Kalite Danışmanı", "Bilgi İşlem Daire Başkanı", "Yayın yetkisi yalnızca onaylı sürüm için kullanılır."],
        ["Ölçüm seti veya hedef/eşik değişikliği", "Ölçüm Sorumlusu / Kalite Danışmanı", "İlgili Süreç Sahibi", "SRÇ.004 Süreç Sahibi", "Düzenli üretilemeyen ölçüm eklenmez; değişiklik SRÇ.018 ile izlenir."],
        ["Repository erişim ve yetkisi", "Sistem Yöneticisi", "Proje Yöneticisi", "SRÇ.004 Süreç Sahibi", "Kurumsal yetkilendirme, güvenlik ve VPN kuralları uygulanır."],
    ]}


def src005() -> dict[str, Any]:
    rr = ["Kalite Danışmanı", "SRÇ.005 Süreç Sahibi", "İlgili Süreç Sahibi / Kanıt Sahibi", "Gözden Geçiren", "Onaylayan", "Bulgu Süreç Sorumlusu"]
    roles = [
        ["SRÇ.005 Süreç Sahibi", "Değerlendirme yaklaşımını, kapsamını ve sonuçlarını kurumsal düzeyde sahiplenmek", "Değerlendirmeyi sonuçlandırmak ve yönlendirme kararı vermek", "Süreç yönetimi, kalite ve kurumsal karar bilgisi", "Süreç sahibi / hesap veren"],
        ["Kalite Danışmanı / Değerlendiren", "Planlama, kanıt toplama, BP/GP analizi, etiketleme ve rapor güncellemesini yürütmek", "Etiket ve bulgu sınıflandırması önermek", "ISO/IEC 15504-5, kanıt analizi ve dokümantasyon", "Hazırlayan / değerlendiren"],
        ["İlgili Süreç Sahibi / Kanıt Sahibi", "Süreç tanımı, kayıt ve mevcut kanıtları sağlamak; açıklamaları doğrulamak", "Kendi süreç alanında kanıt ve uygulanabilirlik görüşü vermek", "İlgili süreç ve operasyon bilgisi", "Katılımcı / kanıt sahibi"],
        ["Gözden Geçiren", "Kapsam, kanıt yorumu, etiket ve bulgu sınıflandırmasını kontrol etmek", "Düzeltme ve ek kanıt istemek", "Süreç, proje ve kalite gözden geçirme bilgisi", "Gözden geçiren"],
        ["Onaylayan", "Gözden geçirilen değerlendirme sonucunu onaylamak", "Nihai kurumsal onay ve kaynak yönlendirme kararı vermek", "Kurumsal onay ve kaynak yönlendirme yetkisi", "Onaylayan"],
        ["Bulgu Süreç Sorumlusu", "Bulguyu SRÇ.017 veya SRÇ.018 kapsamında ele almak", "Onaylı kapsam içinde problem/değişiklik çalışmasını yürütmek", "Problem çözümü, değişiklik ve iyileştirme yönetimi", "Hedef süreç uygulama sorumlusu"],
    ]
    activities = [
        ["F1 Hedefleri belirle", "R", "C", "C", "C", "I", "I"], ["F2 Planla", "R", "C", "C", "C", "I", "I"],
        ["F3 Taahhüt ve katılımı sağla", "R", "A", "R", "C", "I", "I"], ["F4 Değerlendir ve veri topla", "R", "A", "R", "C", "I", "I"],
        ["F5 Veriyi doğrula", "R", "A", "C", "R", "I", "I"], ["F6 Analiz et ve etiketle", "R", "A", "C", "C", "I", "I"],
        ["F7 Raporla ve yönlendir", "R", "A", "C", "C", "I", "R"], ["F8 Kaydı sürdür", "R", "A", "I", "C", "I", "I"],
    ]
    products = [
        ["PLN.001 - Süreç Kalite Planı", "R", "C", "A", "C", "I", "I"],
        ["FRM.001 - Süreç Gözden Geçirme Formu", "R", "A", "C", "C", "I", "I"],
        ["RPR.001 - Süreç Performansları Raporu", "R", "A", "I", "C", "I", "I"],
        ["SRÇ.017 / SRÇ.018 bulgu yönlendirmesi", "R", "A", "C", "I", "I", "R"],
    ]
    return {"process": "SRÇ.005 - Süreç Değerlendirme Süreci", "name": "Süreç Değerlendirme Süreci", "purpose": "SRÇ.005 rol, yetki, yetkinlik ve RACI yapısını tanımlamak", "owner": "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı", "reviewer": "Levent Bayezit - Proje Yöneticisi", "approver": "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı", "raci_roles": rr, "roles": roles, "activities": activities, "products": products, "authority": [
        ["Değerlendirme kapsamı", "Kalite Danışmanı / SRÇ.005 Süreç Sahibi", "Gözden Geçiren", "Onaylayan", "KAPSAM DIŞI kararları dahil kapsam FRM.001 üzerinde izlenir."],
        ["BP/GP etiketi", "Kalite Danışmanı", "Gözden Geçiren", "SRÇ.005 Süreç Sahibi", "Sayısal puan veya tek toplam süreç etiketi kullanılmaz."],
        ["Değerlendirmeyi sonuçlandırma", "Kalite Danışmanı / SRÇ.005 Süreç Sahibi", "Gözden Geçiren", "Onaylayan", "Tanımlı tamamlama ölçütleri karşılanmalıdır."],
        ["RPR.001 güncellemesi", "Kalite Danışmanı", "Gözden Geçiren", "SRÇ.005 Süreç Sahibi / Onaylayan", "Her tamamlanan süreç sonrasında aynı kümülatif rapor güncellenir."],
        ["Bulgu yönlendirmesi", "Kalite Danışmanı / Bulgu Süreç Sorumlusu", "SRÇ.005 Süreç Sahibi", "İlgili hedef süreç sahibi", "Uygunsuzluk SRÇ.017'ye, iyileştirme fırsatı SRÇ.018'e yönlendirilir."],
    ]}


def src021() -> dict[str, Any]:
    rr = ["Proje Yöneticisi", "Kalite Danışmanı", "İlgili Uzman / Birim", "Süreç / Proje / Sistem Sahibi", "BİD Başkanı", "Bilgi Kullanıcısı"]
    roles = [
        ["Proje Yöneticisi", "Bilgi yönetimi stratejisini ve LST.004'ü sürdürmek; kaynak sistemleri koordine etmek", "Rutin katalog kaydı oluşturmak, güncellemek ve arşivlemek", "Proje, bilgi kaynağı, erişim ve bağlantı yönetimi", "Süreç sahibi / katalog sorumlusu"],
        ["Kalite Danışmanı", "Standart, mevzuat, kalite ve süreç bilgisini izlemek; kataloğa katkı sağlamak", "Standart/kalite bilgisini doğrulamak ve süreç etkisi önermek", "Standart, mevzuat, kalite ve süreç yönetimi", "Ana katkı rolü / danışılan"],
        ["İlgili Uzman / Birim", "Teknik veya alan bilgisinin doğruluğunu teyit etmek", "Kendi uzmanlık alanında teknik uygunluk görüşü vermek", "İlgili teknik veya iş alanı bilgisi", "Doğrulayan / katkı sağlayan"],
        ["Süreç / Proje / Sistem Sahibi", "Kaynak değişikliğini bildirmek ve yetkili kaynağı korumak", "Kendi alanındaki kaynak içerik ve erişim kararını vermek", "Kaynak sistem, süreç veya proje alanı bilgisi", "Kaynak sahibi"],
        ["Bilgi İşlem Daire Başkanı", "Süreci ve prosedürü onaylamak; kurumsal kaynak/yetki sağlamak", "Kurumsal kapsam ve süreç değişikliği kararını onaylamak", "Kurumsal karar ve yetkilendirme", "Onaylayan"],
        ["Bilgi Kullanıcısı", "Kataloğu kullanmak ve hata/güncellik sorunlarını bildirmek", "Geri bildirim ve düzeltme talebi iletmek", "Katalog kullanımı ve kendi bilgi ihtiyacı", "Kullanıcı / bilgilendirilen"],
    ]
    activities = [
        ["Bilgi yönetimi stratejisini sürdür", "R/A", "C", "I", "C", "I", "I"],
        ["Bilgi adayını ve kaynak sistemi belirle", "A", "C", "R/C", "R/C", "I", "C"],
        ["LST.004 kaydını oluştur veya güncelle", "R/A", "C", "C", "C", "I", "I"],
        ["Teknik bilgiyi doğrula", "A", "I", "R", "C", "I", "I"],
        ["Standart, mevzuat ve kalite bilgisini doğrula", "A", "R", "C", "C", "I", "I"],
        ["Bilgiyi yaygınlaştır", "R/A", "C", "C", "C", "I", "I"],
        ["Yıllık ve olay bazlı gözden geçir", "R/A", "R/C", "C", "C", "I", "C"],
        ["Süreç etkisi için SRÇ.018'e aktar", "R", "R/C", "C", "C", "A/I", "I"],
    ]
    products = [
        ["LST.004 - Bilgi Kataloğu", "R/A", "C", "C", "C", "I", "I"],
        ["PRS.005 - Bilgi Yönetimi Prosedürü", "R", "R", "C", "C", "A", "I"],
        ["LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "R/A", "C", "I", "C", "I", "I"],
        ["SRÇ.018 etki / değişiklik kaydı", "R", "R", "C", "C", "A", "I"],
        ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021)", "R/A", "R", "C", "C", "I", "I"],
    ]
    return {"process": "SRÇ.021 - Bilgi Yönetimi Süreci", "name": "Bilgi Yönetimi Süreci", "purpose": "SRÇ.021 rol, yetki, yetkinlik ve RACI yapısını tanımlamak", "owner": "Levent BAYEZİT - Proje Yöneticisi", "reviewer": "Levent BAYEZİT - Süreç Sahibi", "approver": "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı", "raci_roles": rr, "roles": roles, "activities": activities, "products": products, "authority": [
        ["Bilgi yönetimi süreci ve prosedürü", "Proje Yöneticisi / Kalite Danışmanı", "Süreç Sahibi", "Bilgi İşlem Daire Başkanı", "Kurumsal kapsam ve yönetişim değişiklikleri onaya tabidir."],
        ["Bilgi Kataloğu yapısı ve sınıflandırma kuralları", "Proje Yöneticisi / Kalite Danışmanı", "İlgili Uzman / Birim", "Süreç Sahibi", "Kategori, erişim sınıfı veya zorunlu alan değişikliği kontrollü yapılır."],
        ["Rutin katalog kaydı oluşturma, güncelleme veya arşivleme", "Proje Yöneticisi", "Gerektiğinde İlgili Uzman / Kaynak Sahibi", "Proje Yöneticisi", "Sürekli resmî onay aranmaz; bağlantı, sahiplik ve gerekçe LST.004 üzerinde izlenir."],
        ["Teknik bilgi doğrulaması", "İlgili Uzman / Birim", "Kaynak Sistem Sahibi / Proje Yöneticisi", "Proje Yöneticisi", "Doğrulama yalnızca ilgili uzmanlık alanı içinde yapılır."],
        ["Standart, mevzuat ve kalite etkisinin SRÇ.018'e aktarılması", "Kalite Danışmanı", "Proje Yöneticisi", "SRÇ.018 yetkili rolü", "Etki ve değişiklik kararı SRÇ.018 kapsamında verilir."],
    ]}


def template_body() -> str:
    current = (TEMPLATE_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    prefix = current.split("<h2>1. Liste Özeti</h2>", 1)[0]
    role_headers = [em("Rol 1"), em("Rol 2"), em("Rol 3"), em("Rol 4"), em("Rol 5"), em("Rol 6")]
    headers = ["Faaliyet / İş Ürünü", *role_headers]
    return prefix + "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", em("SRÇ.XXX - Süreç Adı")], ["Kullanım Amacı", em("Sürece özel rol, yetki, yetkinlik ve RACI yapısını tanımlamak")], ["Sorumlu", em("Süreç sahibi / rol")], ["Durum", em("Taslak / Aktif / Pasif")], ["Sürüm", em("v1.0")]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["R", "Faaliyeti gerçekleştiren / iş ürününü hazırlayan"], ["A", "Nihai hesap veren ve onaylayan"], ["C", "Görüşüne başvurulan"], ["I", "Bilgilendirilen"], ["R/A", "Aynı rolün hem uygulayan hem nihai hesap veren olduğu durum"]]),
        "<h2>3. Rol ve Yetkinlik Matrisi</h2>", table(["Rol", "Sorumluluk", "Yetki", "Asgari Yetkinlik", "Süreçteki Konum"], [[em("Rol adı"), em("Temel sorumluluk") , em("Karar / uygulama yetkisi"), em("Gerekli bilgi ve deneyim"), em("Süreç sahibi / hazırlayan / uygulayan / gözden geçiren / onaylayan")], [em("Rol adı"), em("Temel sorumluluk"), em("Karar / uygulama yetkisi"), em("Gerekli bilgi ve deneyim"), em("Süreçteki konum")]]),
        "<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>", table(headers, [[em("F1 Faaliyet adı"), "R", "A", "C", "I", "I", "I"], [em("F2 Faaliyet adı"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I")]]),
        "<h2>5. İş Ürünleri RACI Matrisi</h2>", table(headers, [[em("Tam kodu ve adıyla iş ürünü") , "R", "A", "C", "I", "I", "I"], [em("Tam kodu ve adıyla iş ürünü"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I"), em("R/A/C/I")]]),
        "<h2>6. Yetki ve Onay Matrisi</h2>", table(["Karar / Onay", "Hazırlayan", "Gözden Geçiren", "Onaylayan", "Yetki Sınırı / Kural"], [[em("Karar veya onay konusu"), em("Rol"), em("Rol"), em("Rol"), em("Yetki sınırı, koşul ve izleme kuralı")], [em("Karar veya onay konusu"), em("Rol"), em("Rol"), em("Rol"), em("Yetki sınırı, koşul ve izleme kuralı")]]),
        "<h2>7. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", em("GG-AA-YYYY"), "İlk taslak oluşturuldu.", em("Rol / kişi"), "-", "-"], ["v1.0", em("GG-AA-YYYY"), em("Süreç adı rol, yetki ve RACI matrisi onaylanarak yürürlüğe girmiştir."), em("Rol / kişi"), em("Rol / kişi"), em("Rol / kişi")]]),
    ]) + "\n"


PAGES = {
    "SRÇ.001": (PROCESS_ROOT / "src-001-dokumantasyon-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-001", src001),
    "SRÇ.004": (PROCESS_ROOT / "src-004-surec-kurulumu-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-004", src004),
    "SRÇ.005": (PROCESS_ROOT / "src-005-surec-degerlendirme-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-005", src005),
    "SRÇ.021": (PROCESS_ROOT / "src-021-bilgi-yonetimi-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-021", src021),
}


def write_page(page_dir: Path, title: str, storage: str) -> None:
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, storage), encoding="utf-8")
    meta_path = page_dir / "page.yaml"
    meta = meta_path.read_text(encoding="utf-8")
    stamp = datetime.now(timezone.utc).isoformat()
    if re.search(r"^updated_at:", meta, flags=re.M):
        meta = re.sub(r"^updated_at:.*$", f"updated_at: '{stamp}'", meta, flags=re.M)
    else:
        meta = meta.rstrip() + f"\nupdated_at: '{stamp}'\n"
    meta_path.write_text(meta, encoding="utf-8")


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def validate(page_dir: Path, *, template: bool = False) -> None:
    storage = (page_dir / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [plain(item) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.I | re.S)]
    expected = [
        "1. Liste Özeti", "2. Kullanım Değerleri", "3. Rol ve Yetkinlik Matrisi",
        "4. Süreç Faaliyetleri RACI Matrisi", "5. İş Ürünleri RACI Matrisi",
        "6. Yetki ve Onay Matrisi", "7. Sürüm Geçmişi",
    ]
    actual = headings[-7:] if template else headings
    if actual != expected:
        raise RuntimeError(f"Unexpected LST.010 sections in {page_dir}: {actual}")

    tables = re.findall(r"<table[^>]*>(.*?)</table>", storage, flags=re.I | re.S)
    relevant = tables[-7:] if template else tables
    if len(relevant) != 7:
        raise RuntimeError(f"Expected seven record tables in {page_dir}, got {len(relevant)}")
    expected_headers = [
        ["Alan", "Değer"], ["Değer", "Anlamı"],
        ["Rol", "Sorumluluk", "Yetki", "Asgari Yetkinlik", "Süreçteki Konum"],
        None, None,
        ["Karar / Onay", "Hazırlayan", "Gözden Geçiren", "Onaylayan", "Yetki Sınırı / Kural"],
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"],
    ]
    for index, table_html in enumerate(relevant):
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.I | re.S)
        parsed = [[plain(cell) for cell in re.findall(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", row, flags=re.I | re.S)] for row in rows]
        if not parsed or any(len(row) != len(parsed[0]) for row in parsed):
            raise RuntimeError(f"Inconsistent table width in {page_dir}, section {index + 1}")
        if expected_headers[index] and parsed[0] != expected_headers[index]:
            raise RuntimeError(f"Unexpected headers in {page_dir}, section {index + 1}: {parsed[0]}")
        if index in (3, 4) and (parsed[0][0] != "Faaliyet / İş Ürünü" or len(parsed[0]) < 6):
            raise RuntimeError(f"RACI table is not role-oriented in {page_dir}, section {index + 1}")
    if len(relevant[3].split("<th")) != len(relevant[4].split("<th")):
        raise RuntimeError(f"Activity/work-product role columns differ in {page_dir}")


def main() -> None:
    for code, (page_dir, factory) in PAGES.items():
        title = f"LST.010 - Süreç Rol Yetki ve RACI Matrisi ({code})"
        write_page(page_dir, title, process_body(factory()))
        print(f"[UPDATED] {code} LST.010")

    # SRÇ.006 is the approved structural reference; it is intentionally not rewritten.
    write_page(TEMPLATE_DIR, "LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu", template_body())
    print("[UPDATED] Active LST.010 template")
    print("[REFERENCE] SRÇ.006 LST.010 preserved without content change")

    for code, (page_dir, _) in PAGES.items():
        validate(page_dir)
        print(f"[VALID] {code} LST.010")
    validate(REFERENCE_DIR)
    print("[VALID] SRÇ.006 LST.010")
    validate(TEMPLATE_DIR, template=True)
    print("[VALID] Active LST.010 template")


if __name__ == "__main__":
    main()
