import os
import re
import json
import glob
from datetime import datetime, timezone
from google import genai
from google.genai import types

# 1. API İstemcisi
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı.")

client = genai.Client(api_key=api_key)

POSTS_DIR = "src/content/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# 2. Mevcut Yazıları Hafızaya Alma
def get_existing_titles():
    titles = []
    for file_path in glob.glob(f"{POSTS_DIR}/*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
                if match:
                    titles.append(match.group(1).strip())
        except Exception:
            continue
    return titles

existing_titles = get_existing_titles()
titles_context = "\n".join([f"- {t}" for t in existing_titles]) if existing_titles else "Henüz yayınlanmış yazı yok."

# 3. Aşama 1: Düşük Rekabetli Long-Tail Konu Araştırması
research_prompt = f"""
Sen bir Off-Grid Karavan SEO ve Teknik İçerik Stratejistisin.
Sitemiz yeni ve otoritesi henüz düşük. Bu yüzden genel/rekabetçi kelimeler (örn: "karavan güneş paneli", "karavan akü seçimi") YASAKTIR.

Şu ana kadar sitede yayınlanmış konular:
{titles_context}

GÖREV:
Yukarıdakilerden FARKLI, Google'da aranma rekabeti düşük ama kullanıcıların forumlarda/aramalarda teknik yanıt aradığı TEK bir "Long-Tail" konu ve çalışan bir "Mini Hesaplayıcı/Araç" fikri belirle.

Örnek niş şablonlar:
- "12V X Ah Akü ile Y Watt Buzdolabı Kaç Saat Çalışır? (+Hesaplayıcı)"
- "X Metre Kabloda Y Amper Akım İçin Minimum Kablo Kesiti (mm²) Hesabı"
- "-5 Derecede Karavan Gri Su Deposunun Donmaması İçin Kaç Watt Isıtıcı Gerekir?"

ÇIKTI FORMATI:
Sadece saf JSON formatında şu anahtarlarla yanıt ver (markdown code block ekleme):
{{
  "title": "İngilizce SEO uyumlu ve ilgi çekici başlık",
  "slug": "url-uyumlu-kisa-slug",
  "tags": ["etiket1", "etiket2", "etiket3", "calculator"],
  "calculator_concept": "Yazıya eklenecek mini form ve hesaplama mantığı özeti"
}}
"""

print("-> Niş konu araştırması yapılıyor...")
research_res = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=research_prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)

topic_data = json.loads(research_res.text.strip())
print(f"-> Belirlenen Konu: {topic_data['title']}")

# 4. Aşama 2: Kapsamlı İçerik ve Hesaplayıcı Üretimi
content_prompt = f"""
Sen profesyonel bir Off-Grid Karavan Mühendisi ve Teknik Yazarısın.
Konu: "{topic_data['title']}"
Hesaplayıcı Konsepti: "{topic_data['calculator_concept']}"

GÖREV:
Bu konu için teknik, son derece doyurucu, formüller içeren kapsamlı bir rehber yaz.

KURALLAR:
1. Kesinlikle Astro Markdown formatında olmalı.
2. Yazının içine kullanıcıların tarayıcıda doğrudan değer girip anında sonuç alabileceği temiz, inline CSS ile stillendirilmiş bir HTML ve Vanilla JavaScript `<script>` mini hesaplayıcı bileşeni ekle.
3. Hesaplayıcı sade, mobil uyumlu ve modern bir kart görünümünde olsun.
4. Dil: İngilizce (küresel kitle ve yüksek CPC için).
5. Yanıtta SADECE makalenin ana gövdesini ver (Frontmatter `---` bloklarını SEN EKLEME, ben kod ile ekleyeceğim). Başlığı `# {topic_data['title']}` ile başlat.
"""

print("-> Makale ve hesaplayıcı kodu üretiliyor...")
content_res = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=content_prompt
)

article_body = content_res.text.strip()
if article_body.startswith("```markdown"):
    article_body = article_body[11:]
if article_body.startswith("```"):
    article_body = article_body[3:]
if article_body.endswith("```"):
    article_body = article_body[:-3]
article_body = article_body.strip()

# 5. Frontmatter Oluşturma (Astro Şeması Uyumlu)
pub_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
tags_formatted = "\n".join([f"  - {tag.strip()}" for tag in topic_data.get("tags", ["caravan", "off-grid"])])
safe_description = f"Complete guide and interactive calculator for {topic_data['title']}."

post_content = f"""---
author: AI Editorial
pubDatetime: {pub_datetime}
title: "{topic_data['title']}"
postSlug: "{topic_data['slug']}"
featured: false
draft: false
tags:
{tags_formatted}
description: "{safe_description}"
---

{article_body}
"""

# 6. Dosyayı Kaydetme
file_name = f"{topic_data['slug']}.md"
output_path = os.path.join(POSTS_DIR, file_name)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"-> Yeni yazı başarıyla oluşturuldu: {output_path}")
