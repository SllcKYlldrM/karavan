import os
import re
import json
import glob
from datetime import datetime, timezone
from google import genai
from google.genai import types
import requests

# 1. Ortam Değişkenleri ve İstemciler
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

if not gemini_api_key and not openrouter_api_key:
    raise ValueError("Hiçbir AI API anahtarı (GEMINI_API_KEY veya OPENROUTER_API_KEY) bulunamadı.")

# Gemini İstemcisi
gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

POSTS_DIR = "src/content/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# 2. Akıllı Çağrı Fonksiyonu (Gemini -> OpenRouter Fallback)
def call_ai(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """Önce Gemini ile dener, kota/hata durumunda OpenRouter'a geçer."""
    
    # --- YÖNTEM 1: GEMINI API ---
    if gemini_client:
        try:
            print("-> AI isteği Gemini API ile deneniyor...")
            config_kwargs = {}
            if system_instruction:
                config_kwargs["system_instruction"] = system_instruction
            if json_mode:
                config_kwargs["response_mime_type"] = "application/json"
                
            response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs)
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini API hataya takıldı / limite ulaştı: {e}")
            print("-> OpenRouter yedek sistemine geçiliyor...")

    # --- YÖNTEM 2: OPENROUTER FALLBACK ---
    if not openrouter_api_key:
        raise RuntimeError("Gemini başarısız oldu ve yedek olarak kullanılacak OPENROUTER_API_KEY bulunamadı.")
        
    print("-> AI isteği OpenRouter (google/gemini-3.6-flash) üzerinden yapılıyor...")
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "google/gemini-3.6-flash",
        "messages": messages
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"OpenRouter API Hatası: {res.status_code} - {res.text}")
        
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()

# 3. Mevcut Yazıları Hafızaya Alma
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

# 4. Aşama 1: Düşük Rekabetli Long-Tail Konu Araştırması
research_prompt = f"""
Sen bir Off-Grid Karavan SEO ve Teknik İçerik Stratejistisin.
Sitemiz yeni ve otoritesi henüz düşük. Bu yüzden genel kelimeler (örn: "karavan güneş paneli") YASAKTIR.

Şu ana kadar sitede yayınlanmış konular:
{titles_context}

GÖREV:
Yukarıdakilerden FARKLI, Google'da aranma rekabeti düşük ama kullanıcıların forumlarda/aramalarda teknik yanıt aradığı TEK bir "Long-Tail" konu ve çalışan bir "Mini Hesaplayıcı/Araç" fikri belirle.

ÇIKTI FORMATI:
Sadece saf JSON formatında şu anahtarlarla yanıt ver (markdown code block ekleme):
{{
  "title": "İngilizce SEO uyumlu ve ilgi çekici başlık",
  "slug": "url-uyumlu-kisa-slug",
  "tags": ["etiket1", "etiket2", "calculator"],
  "calculator_concept": "Yazıya eklenecek mini form ve hesaplama mantığı özeti"
}}
"""

research_system = "Sen profesyonel bir SEO stratejistisin. Sadece geçerli JSON çıktısı üretebilirsin."
print("-> Niş konu araştırması başlatılıyor...")
research_raw = call_ai(research_prompt, system_instruction=research_system, json_mode=True)

# Markdown temizliği (eğer model block eklediyse)
if research_raw.startswith("```json"):
    research_raw = research_raw[7:]
if research_raw.startswith("```"):
    research_raw = research_raw[3:]
if research_raw.endswith("```"):
    research_raw = research_raw[:-3]

topic_data = json.loads(research_raw.strip())
print(f"-> Belirlenen Konu: {topic_data['title']}")

# 5. Aşama 2: Kapsamlı İçerik ve Hesaplayıcı Üretimi
content_prompt = f"""
Sen profesyonel bir Off-Grid Karavan Mühendisi ve Teknik Yazarısın.
Konu: "{topic_data['title']}"
Hesaplayıcı Konsepti: "{topic_data['calculator_concept']}"

GÖREV:
Bu konu için teknik, son derece doyurucu, formüller içeren kapsamlı bir rehber yaz.

KURALLAR:
1. Kesinlikle Astro Markdown formatında olmalı.
2. Yazının içine kullanıcıların tarayıcıda doğrudan değer girip anında sonuç alabileceği temiz, inline CSS ile stillendirilmiş bir HTML ve Vanilla JavaScript `<script>` mini hesaplayıcı bileşeni ekle.
3. Dil: İngilizce.
4. Yanıtta SADECE makalenin ana gövdesini ver (Frontmatter `---` bloklarını SEN EKLEME). Başlığı `# {topic_data['title']}` ile başlat.
"""

content_system = "Sen uzman bir teknik yazarsın. Sadece Markdown formatında içerik üretirsin."
print("-> Makale ve hesaplayıcı kodu üretiliyor...")
article_body = call_ai(content_prompt, system_instruction=content_system)

if article_body.startswith("```markdown"):
    article_body = article_body[11:]
if article_body.startswith("```"):
    article_body = article_body[3:]
if article_body.endswith("```"):
    article_body = article_body[:-3]
article_body = article_body.strip()

# 6. Frontmatter Oluşturma
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

# 7. Dosyayı Kaydetme
file_name = f"{topic_data['slug']}.md"
output_path = os.path.join(POSTS_DIR, file_name)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"-> Yeni yazı başarıyla oluşturuldu: {output_path}")
