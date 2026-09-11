import os
import re
import json
import glob
from datetime import datetime, timezone
from google import genai
from google.genai import types
import requests
import urllib.parse

# 1. Ortam Değişkenleri ve İstemciler
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

if not gemini_api_key and not openrouter_api_key:
    raise ValueError("Hiçbir AI API anahtarı bulunamadı.")

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

POSTS_DIR = "src/content/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# 2. Akıllı Çağrı Fonksiyonu (Gemini -> OpenRouter Fallback)
def call_ai(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    if gemini_client:
        try:
            print("-> AI isteği Gemini API (gemini-3.6-flash) ile deneniyor...")
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
            print(f"⚠️ Gemini API hatası: {e}. OpenRouter'a geçiliyor...")

    if not openrouter_api_key:
        raise RuntimeError("Gemini başarısız oldu ve OPENROUTER_API_KEY bulunamadı.")
        
    print("-> AI isteği OpenRouter üzerinden yapılıyor...")
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": messages
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"OpenRouter API Hatası: {res.status_code} - {res.text}")
        
    return res.json()["choices"][0]["message"]["content"].strip()

# 3. Hafıza Kontrolü
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

# 4. Konu Araştırması
research_prompt = f"""
Sen bir Off-Grid Karavan SEO Stratejistisin. Genel kelimeler YASAKTIR.
Yayınlanmış konular:
{titles_context}

GÖREV:
Düşük rekabetli, teknik detay ve pratik mühendislik çözümleri gerektiren TEK bir "Long-Tail" konu belirle.

ÇIKTI FORMATI (Sadece saf JSON):
{{
  "title": "İngilizce SEO uyumlu başlık",
  "slug": "url-slug",
  "tags": ["tag1", "tag2", "engineering"]
}}
"""
research_raw = call_ai(research_prompt, system_instruction="Sadece JSON üret.", json_mode=True)
if research_raw.startswith("```json"): research_raw = research_raw[7:]
if research_raw.startswith("```"): research_raw = research_raw[3:]
if research_raw.endswith("```"): research_raw = research_raw[:-3]
topic_data = json.loads(research_raw.strip())
print(f"-> Konu: {topic_data['title']}")

# 5. Kapsamlı İçerik Üretimi (HTML/JS Yok, Zengin Tablo + Adım Adım Hesaplama Örnekleri + FAQ)
content_prompt = f"""
Sen uzman bir Karavan Mühendisisin.
Konu: "{topic_data['title']}"

GÖREV:
Bu konu için son derece kapsamlı, uzun (en az 1200 kelime), derinlemesine teknik bir rehber yaz.

KESİN KURALLAR:
1. ASLA ham HTML, CSS veya JavaScript kod bloğu EKLEME (tarayıcıda düz metin gibi görünüyorlar, yasaktır).
2. Matematiksel formülleri LaTeX (`$...$`) şeklinde YAZMA. Bunun yerine düz metin olarak, örneğin (Voltage Drop = (2 x Current x Length x Resistance) / Area) formatında açıkça yaz.
3. İçerikte en az 2 adet detaylı **Markdown Veri/Karşılaştırma Tablosu** bulunsun.
4. Okuyucunun kendi kendine hesap yapabilmesi için somut, sayısal **Adım Adım Hesaplama Örnekleri (Step-by-Step Calculation Examples)** ekle.
5. Yazının sonunda en az 4 soruluk detaylı bir **FAQ (Sık Sorulan Sorular)** bölümü olsun.
6. Dil: İngilizce. Sadece makale gövdesini ver, frontmatter ekleme. Başlığı `# {topic_data['title']}` ile başlat.
"""
article_body = call_ai(content_prompt, system_instruction="Uzun ve teknik Markdown makaleleri yazarsın. HTML ve LaTeX kullanmazsın.")
if article_body.startswith("```markdown"): article_body = article_body[11:]
if article_body.startswith("```"): article_body = article_body[3:]
if article_body.endswith("```"): article_body = article_body[:-3]
article_body = article_body.strip()

# 6. Otomatik Kapak Görseli İndirme ve Kaydetme
encoded_title = urllib.parse.quote(topic_data['title'])
image_url = f"https://image.pollinations.ai/prompt/Professional%20off-grid%20caravan,%20{encoded_title}?width=1200&height=630&nologo=true"

image_filename = f"{topic_data['slug']}.jpg"
image_path = os.path.join("public/images", image_filename)
os.makedirs("public/images", exist_ok=True)

try:
    img_res = requests.get(image_url)
    if img_res.status_code == 200:
        with open(image_path, "wb") as img_file:
            img_file.write(img_res.content)
        cover_image = f"/images/{image_filename}"
        print(f"-> Görsel başarıyla indirildi ve kaydedildi: {cover_image}")
    else:
        cover_image = "/images/default-og.jpg" # Yedek görsel
except Exception as e:
    print(f"⚠️ Görsel indirilemedi: {e}")
    cover_image = "/images/default-og.jpg"

# 7. Frontmatter ve Dosya Kaydı
pub_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
tags_formatted = "\n".join([f"  - {tag.strip()}" for tag in topic_data.get("tags", ["caravan", "off-grid"])])
safe_description = f"Comprehensive technical guide and engineering standards for {topic_data['title']}."

post_content = f"""---
author: AI Editorial
pubDatetime: {pub_datetime}
title: "{topic_data['title']}"
postSlug: "{topic_data['slug']}"
featured: false
draft: false
tags:
{tags_formatted}
image: "{cover_image}"
description: "{safe_description}"
---

{article_body}
"""

output_path = os.path.join(POSTS_DIR, f"{topic_data['slug']}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"-> Yeni temiz yazı ve görsel oluşturuldu: {output_path}")
