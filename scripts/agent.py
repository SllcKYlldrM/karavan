import os
import re
import json
import glob
import random
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
os.makedirs("public/images", exist_ok=True)

# 2. Kategoriler ve Kapsam Tanımı
CATEGORIES = {
    "Power & Solar Systems": "Lityum (LiFePO4) Akü Teknolojileri, BMS Koruma, MPPT Isıl Kısıtlama, DC-DC Şarj Verimliliği, İnverter Bekleme Kayıpları, Taşınabilir Güç İstasyonları",
    "Engineering Calculators": "12V/24V Kablo Kesiti ve Voltaj Düşümü Hesapları, Çekme Kapasitesi, Ağırlık Dağılımı (Towing Ratio), Solar Açı Optimizasyonu",
    "Build & Conversion": "Panelvan Armaflex İzolasyon Hesapları, Şasi Güçlendirme, Tavan Havalandırma (MaxxFan), Overlanding Donanım Entegrasyonu",
    "Water & Plumbing Systems": "Basınçlı 12V Su Pompaları, Akümülatör Tankı Optimizasyonu, Gri/Temiz Su Isıtıcı Bantları, UV Filtreleme ve Su Arıtma",
    "HVAC & Climate Control": "12V/24V Inverter Klima Gerçek Akü Tüketimi, Dizel Park Isıtıcıları Yüksek Rakım Bakımı, Çadır ve Karavan Altı Isıtma",
    "Smart RV & IoT": "ESP32 Röle Kartları ile 12V Otomasyon, MQTT ile SoC ve Tank Seviye Takibi, PIR Sensörlü Alarm Devreleri"
}

# 3. Akıllı Çağrı Fonksiyonu (Gemini -> OpenRouter Fallback)
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
        
    res_data = res.json()
    
    if "choices" in res_data and len(res_data["choices"]) > 0:
        choice = res_data["choices"]
        if isinstance(choice, dict) and "message" in choice:
            content = choice["message"].get("content", "")
        elif isinstance(choice, str):
            content = choice
        else:
            content = str(choice)
    else:
        raise RuntimeError(f"OpenRouter geçersiz yanıt döndürdü: {res_data}")

    return content.strip() if isinstance(content, str) else str(content).strip()

# 4. Hafıza Kontrolü
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

# Rastgele bir kategori seçerek ajana hedef verelim
selected_category = random.choice(list(CATEGORIES.keys()))
category_focus = CATEGORIES[selected_category]

# 5. Konu Araştırması (Kategori Odaklı ve Esnek)
research_prompt = (
    "Sen bir Off-Grid Karavan ve Kamp Mühendisliği SEO Stratejistisin. Genel kelimeler YASAKTIR.\n"
    f"Seçilen Kategori: {selected_category} ({category_focus})\n"
    f"Daha önce yayınlanmış konular (Bunları TEKRARLAMA):\n{titles_context}\n\n"
    "GÖREV:\n"
    "Bu kategori altında, düşük rekabetli, teknik detay ve pratik mühendislik/kamp çözümleri gerektiren TEK bir \"Long-Tail\" konu belirle.\n\n"
    "ÇIKTI FORMATI (Sadece saf JSON, markdown blokları veya başka açıklama kesinlikle yazma):\n"
    "{\n"
    "  \"title\": \"İngilizce SEO uyumlu başlık\",\n"
    "  \"slug\": \"url-slug\",\n"
    "  \"tags\": [\"tag1\", \"tag2\", \"" + selected_category.lower().replace(" & ", "-") + "\"]\n"
    "}"
)
research_raw = call_ai(research_prompt, system_instruction="Sadece ve sadece saf JSON nesnesi üret. Markdown kod blokları (```) kullanma.", json_mode=True)

research_raw = research_raw.strip()
if research_raw.startswith("```json"):
    research_raw = research_raw[7:]
elif research_raw.startswith("```"):
    research_raw = research_raw[3:]
if research_raw.endswith("```"):
    research_raw = research_raw[:-3]
research_raw = research_raw.strip()

json_start = research_raw.find("{")
json_end = research_raw.rfind("}")
if json_start != -1 and json_end != -1:
    research_raw = research_raw[json_start:json_end+1]

topic_data = json.loads(research_raw)
print(f"-> Seçilen Kategori: {selected_category}")
print(f"-> Konu: {topic_data['title']}")

# 6. Kapsamlı İçerik Üretimi
content_prompt = (
    "Sen uzman bir Karavan ve Kamp Sistemleri Mühendisisin.\n"
    f"Kategori: {selected_category}\n"
    f"Konu: \"{topic_data['title']}\"\n\n"
    "GÖREV:\n"
    "Bu konu için son derece kapsamlı, uzun (en az 1200 kelime), derinlemesine teknik ve pratik bir rehber yaz.\n\n"
    "KESİN KURALLAR:\n"
    "1. ASLA ham HTML, CSS veya JavaScript kod bloğu EKLEME.\n"
    "2. Matematiksel formülleri LaTeX (`$...$`) şeklinde YAZMA. Düz metin olarak yaz (Örn: Voltage Drop = (2 x Current x Length x Resistance) / Area).\n"
    "3. İçerikte en az 2 adet detaylı **Markdown Veri/Karşılaştırma Tablosu** bulunsun.\n"
    "4. Okuyucunun kendi kendine hesap yapabilmesi için somut, sayısal **Adım Adım Hesaplama Örnekleri** ekle.\n"
    "5. Yazının ortasındaki önemli alt başlıkların (h2 veya h3) altına, yazıyı zenginleştirmek için tam olarak şu formatta 2 adet görsel yerleştir: `[IMAGE: Kısa ingilizce görsel açıklaması]` (Örn: `[IMAGE: Detailed close-up of caravan electrical wiring and fuse box]`).\n"
    "6. Yazının sonunda en az 4 soruluk detaylı bir **FAQ (Sık Sorulan Sorular)** bölümü olsun.\n"
    f"7. Dil: İngilizce. Sadece makale gövdesini ver, frontmatter ekleme. Başlığı `# {topic_data['title']}` ile başlat."
)
article_body = call_ai(content_prompt, system_instruction="Uzun ve teknik Markdown makaleleri yazarsın. HTML ve LaTeX kullanmazsın.")
if article_body.startswith("```markdown"): article_body = article_body[11:]
if article_body.startswith("```"): article_body = article_body[3:]
if article_body.endswith("```"): article_body = article_body[:-3]
article_body = article_body.strip()

# 7. Ana Kapak Görseli Üretimi ve Kaydı
main_visual_prompt = f"Professional technical photograph of a modern off-grid caravan system or outdoor camping setup related to {topic_data['title']}, photorealistic, high detail, engineering style, no text, no watermark"
encoded_main_prompt = urllib.parse.quote(main_visual_prompt)
main_image_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){encoded_main_prompt}?width=1200&height=630&nologo=true&seed={random.randint(1, 10000)}"

main_image_filename = f"{topic_data['slug']}.jpg"
main_image_path = os.path.join("public/images", main_image_filename)
cover_image = f"/images/{main_image_filename}"

try:
    print(f"-> Ana kapak görseli indiriliyor...")
    img_res = requests.get(main_image_url)
    if img_res.status_code == 200:
        with open(main_image_path, "wb") as img_file:
            img_file.write(img_res.content)
        print("-> Ana kapak görseli kaydedildi.")
    else:
        cover_image = "/images/default-og.jpg"
except Exception as e:
    print(f"⚠️ Ana kapak indirilemedi: {e}")
    cover_image = "/images/default-og.jpg"

# 8. Ana Kapak Görseli Üretimi ve Kaydı
main_visual_prompt = f"Professional technical photograph of a modern off-grid caravan system or outdoor camping setup related to {topic_data['title']}, photorealistic, high detail, engineering style, no text, no watermark"
encoded_main_prompt = urllib.parse.quote(main_visual_prompt)
main_image_url = f"https://image.pollinations.ai/prompt/{encoded_main_prompt}?width=1200&height=630&nologo=true&seed={random.randint(1, 10000)}"

main_image_filename = f"{topic_data['slug']}.jpg"
main_image_path = os.path.join("public/images", main_image_filename)
cover_image = f"/images/{main_image_filename}"

try:
    print(f"-> Ana kapak görseli indiriliyor...")
    img_res = requests.get(main_image_url)
    if img_res.status_code == 200:
        with open(main_image_path, "wb") as img_file:
            img_file.write(img_res.content)
        print("-> Ana kapak görseli kaydedildi.")
    else:
        # Eğer indirme başarısız olursa boş bırakmak yerine yerel geçerli bir isim ata
        print("⚠️ Görsel indirilemedi, alternatif yol atanıyor.")
except Exception as e:
    print(f"⚠️ Ana kapak indirilemedi: {e}")

# 9. Frontmatter ve Dosya Kaydı
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
ogImage: "{cover_image}"
description: "{safe_description}"
---

{article_body}
"""

output_path = os.path.join(POSTS_DIR, f"{topic_data['slug']}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"-> Yeni kategori tabanlı yazı ve görseller oluşturuldu: {output_path}")
