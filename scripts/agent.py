import os
import re
import json
import glob
import random
import time
from datetime import datetime, timezone
from google import genai
from google.genai import types
import requests
import urllib.parse

# 1. İstemciler ve Anahtarlar
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY ortam değişkeni zorunludur.")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY ortam değişkeni zorunludur.")

gemini_client = genai.Client(api_key=gemini_api_key)

POSTS_DIR = "src/content/posts"
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs("public/images", exist_ok=True)

CATEGORIES = {
    "Power & Solar Systems": "LiFePO4 Akü, BMS, MPPT, DC-DC Şarj, İnverter Kayıpları",
    "Engineering Calculators": "12V Kablo Kesiti, Voltaj Düşümü, Ağırlık Dağılımı",
    "Build & Conversion": "Armaflex İzolasyon, Şasi, Tavan Havalandırma",
    "Water & Plumbing Systems": "Basınçlı Su Pompaları, Isıtıcı Bantlar, UV Filtre",
    "HVAC & Climate Control": "Inverter Klima Akü Tüketimi, Dizel Isıtıcı Bakımı",
    "Smart RV & IoT": "ESP32 Otomasyon, MQTT Takip, Alarm Devreleri"
}

CATEGORY_AUTHORS = {
    "Power & Solar Systems": "Alex Morgan",
    "Engineering Calculators": "Daniel Brooks",
    "Build & Conversion": "Oliver Reed",
    "Water & Plumbing Systems": "Maya Carter",
    "HVAC & Climate Control": "Ethan Cole",
    "Smart RV & IoT": "Nora Bennett",
}

def call_gemini(prompt: str, json_mode: bool = False) -> str:
    config_kwargs = {}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
        
    response = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs)
    )
    return response.text.strip()

def call_openrouter(prompt: str, system_instruction: str = None) -> str:
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
        "messages": messages,
        "temperature": 0.7
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=90)
    if res.status_code != 200:
        raise RuntimeError(f"OpenRouter Hatası: {res.status_code} - {res.text}")
        
    return res.json()["choices"][0]["message"]["content"].strip()

def download_image_safely(url, save_path, max_retries=3):
    """Görsel gerçekten inene ve doğrulanana kadar yeniden dener."""
    if os.path.exists(save_path):
        os.remove(save_path)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"-> Görsel indiriliyor (Deneme {attempt}/{max_retries}): {os.path.basename(save_path)}")
            res = requests.get(url, timeout=40)
            content_type = res.headers.get("Content-Type", "").lower()
            is_jpeg = res.content.startswith(b"\xff\xd8\xff")
            is_png = res.content.startswith(b"\x89PNG\r\n\x1a\n")
            if (
                res.status_code == 200
                and content_type.startswith("image/")
                and len(res.content) > 1000
                and (is_jpeg or is_png)
            ):
                with open(save_path, "wb") as f:
                    f.write(res.content)
                print(f"-> Başarıyla indirildi: {os.path.basename(save_path)}")
                return True
        except Exception as e:
            print(f"⚠️ İndirme hatası: {e}")
        
        if attempt < max_retries:
            time.sleep(4)
            
    if os.path.exists(save_path):
        os.remove(save_path)
    return False

def normalize_article_body(body: str) -> str:
    """Remove model fences and the duplicate leading H1 used by the page template."""
    body = body.strip()
    body = re.sub(r"^```(?:markdown)?\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\s*```$", "", body)
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", body, count=1, flags=re.DOTALL)
    body = re.sub(r"^\s*(?:image|ogImage):\s*[\"']?/images/[^\"'\s]+[\"']?\s*$", "", body, flags=re.IGNORECASE | re.MULTILINE)
    body = re.sub(r"^\s*#\s+[^\n]+\r?\n+", "", body, count=1)
    return body.strip()

def remove_missing_local_images(body: str) -> str:
    """Remove generated image references that do not exist in public/images."""
    html_image_pattern = re.compile(r"<img\b[^>]*\bsrc=[\"'](/images/[^\"']+)[\"'][^>]*>", re.IGNORECASE)
    markdown_image_pattern = re.compile(r"!\[([^\]]*)\]\((/images/[^)\s]+)(?:\s+[^)]*)?\)")

    def keep_existing(match):
        image_path = os.path.join("public", match.group(2).lstrip("/"))
        return match.group(0) if os.path.isfile(image_path) else ""

    body = html_image_pattern.sub(keep_existing, body)
    return markdown_image_pattern.sub(keep_existing, body)

def limit_inline_image_placeholders(body: str, maximum: int = 2) -> str:
    """Keep at most two generated inline image placeholders per article."""
    placeholders = list(re.finditer(r"\[IMAGE:\s*.*?\]", body, flags=re.IGNORECASE))
    for match in reversed(placeholders[maximum:]):
        body = body[:match.start()] + body[match.end():]
    return body

TURKISH_LANGUAGE_MARKERS = (
    " ve ", " bir ", " için ", " ile ", " olan ", " bu ", " şu ",
    " nasıl ", " olarak ", " gerekir ", " kullanılır ", " yapılır ",
    " pompası ", " akümülatör ", " basınç ", " gerilim ", " bağlantı ",
)

def contains_turkish_content(text: str) -> bool:
    normalized = f" {text.casefold()} "
    diacritic_count = sum(normalized.count(char) for char in "çğıöşü")
    marker_hits = sum(normalized.count(marker) for marker in TURKISH_LANGUAGE_MARKERS)
    return diacritic_count >= 3 or marker_hits >= 5

def require_english_content(title: str, body: str) -> None:
    if contains_turkish_content(f"{title}\n{body}"):
        raise RuntimeError(
            "Generated content failed the English-only language check; no post was written."
        )

def normalize_tags(raw_tags, category):
    """Keep the selected category as the canonical first tag and remove duplicates."""
    values = [category, "Caravan", "Off-Grid"] + (raw_tags or [])
    tags = []
    seen = set()
    for value in values:
        tag = str(value).strip()
        key = tag.casefold()
        if tag and key not in seen:
            tags.append(tag)
            seen.add(key)
    return tags[:8]

def get_existing_posts_summary():
    summaries = []
    for file_path in glob.glob(f"{POSTS_DIR}/*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
                desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
                if title_match:
                    summaries.append(f"- Başlık: {title_match.group(1).strip()} | Açıklama: {desc_match.group(1).strip() if desc_match else 'Yok'}")
        except Exception: continue
    return "\n".join(summaries) or "Henüz yayınlanmış yazı yok."

existing_posts_context = get_existing_posts_summary()
selected_category = random.choice(list(CATEGORIES.keys()))

# --- ADIM 1: Strateji, Tekrar Analizi ve Zengin Brief Üretimi (Gemini) ---
strategy_prompt = (
    f"Sen Kıdemli bir SEO ve İçerik Direktörüsün.\n"
    f"Seçilen Kategori: {selected_category} ({CATEGORIES[selected_category]})\n\n"
    f"Sitede Daha Önce Yayınlanmış Yazılar:\n{existing_posts_context}\n\n"
    "GÖREV:\n"
    "1. Sitedeki mevcut içerikleri analiz et. Bu kategoride tekrara (cannibalization) düşmeyecek, kullanıcıya tamamen yepyeni ve derinlemesine teknik/pratik değer katacak özgün bir 'Long-Tail' konu seç.\n"
    "2. Seçtiğin konunun kullanıcıya sağlayacağı ekstra faydayı stratejik olarak kurgula.\n"
    "3. Yazıyı yazacak olan mühendis yazar (OpenRouter) için kapsamlı bir içerik brief'i hazırla.\n\n"
    "ÇIKTI FORMATI (Saf JSON):\n"
    "{\n"
    "  \"title\": \"İngilizce SEO Uyumlu Başlık\",\n"
    "  \"slug\": \"url-slug\",\n"
    "  \"tags\": [\"tag1\", \"tag2\"],\n"
    "  \"brief\": \"Bu makalede işlenecek teknik detaylar, formüller, karşılaştırma parametreleri ve adım adım hesaplama senaryosunun detaylı açıklaması.\"\n"
    "}"
)

print(f"-> [Adım 1] Gemini site analizi yapıyor ve stratejik brief hazırlıyor ({selected_category})...")
strategy_raw = call_gemini(strategy_prompt, json_mode=True)
strategy_raw = re.sub(r"^```json\s*", "", strategy_raw)
strategy_raw = re.sub(r"\s*```$", "", strategy_raw)
topic_data = json.loads(strategy_raw)

print(f"-> Seçilen Konu: {topic_data['title']}")
print(f"-> Stratejik Brief: {topic_data['brief']}")

# --- ADIM 2: İçerik Üretimi ve 2 Haklı Revize Döngüsü (OpenRouter & Gemini QA) ---
content_prompt = (
    "IMPORTANT LANGUAGE RULE: The website is English-only. Write the title, article body, headings, tables, labels, image descriptions, and every sentence in clear professional English. Never write Turkish, even if this instruction or the brief contains Turkish text.\n\n"
    "Return only the article body. Do not return YAML frontmatter, a title line, or direct /images/*.jpg links; use the exact [IMAGE: English description] placeholder when an image is needed.\n\n"
    f"Kategori: {selected_category}\n"
    f"Konu Başlığı: \"{topic_data['title']}\"\n\n"
    f"TEKNİK BİRİEF / YÖNLENDİRME:\n{topic_data['brief']}\n\n"
    "GÖREV:\n"
    "Yukarıdaki stratejik brief'e sadık kalarak, en az 1200 kelime, son derece derinlemesine ve profesyonel bir teknik rehber yaz.\n\n"
    "KESİN KURALLAR:\n"
    "1. HTML veya LaTeX ($...$) KULLANMA. Formülleri düz metin yaz (Örn: Voltage Drop = ...).\n"
    "2. İçerikte en az 2 adet detaylı Markdown Veri/Karşılaştırma Tablosu bulunsun.\n"
    "3. Somut sayısal hesaplama adımları ekle.\n"
    "4. Every calculation must state inputs, units, formula, assumptions, and result. Never invent manufacturer specifications; mark unknown values as assumptions.\n"
    "5. End with a concise Sources and Assumptions section using official manufacturer or standards references when available.\n"
    "6. Görsel yerleri için tam olarak şu formatı kullan: [IMAGE: Kısa ingilizce görsel açıklaması]. En fazla 2 görsel işareti kullan.\n"
    "7. Sadece makale gövdesini yaz; `# Başlık` kullanma, çünkü sayfa şablonu başlığı zaten H1 olarak basıyor. Giriş paragrafı veya `##` başlığıyla başla."
)

print("-> [Adım 2] OpenRouter makaleyi kaleme alıyor...")
article_body = call_openrouter(content_prompt, system_instruction="Uzun, teknik ve profesyonel Markdown makaleleri yazarsın.")

max_revisions = 1
for revision_count in range(max_revisions + 1):
    qa_prompt = (
        "- The website is English-only. If any Turkish sentence, heading, table text, or Turkish language markers appear, return REVIZE_GEREKLI and require a complete English rewrite.\n"
        "Aşağıdaki makaleyi SEO uygunluğu, teknik doğruluk, kelime uzunluğu, tablo varlığı ve kurallara uyum açısından denetle.\n"
        "KURALLAR:\n"
        "- HTML etiketleri veya LaTeX ($...$) var mı? Varsa tamamen düz metne çevir.\n"
        "- Markdown tabloları ve başlık hiyerarşisi tam mı? İlk satırda H1 (`# Başlık`) var mı? Varsa kaldır.\n\n"
        "Eğer makale eksiksizse ve kurallara uyuyorsa, başa 'ONAYLANDI' yaz ve hemen ardından düzeltilmiş nihai makaleyi ver.\n"
        "Eğer eksikler veya kural ihlalleri varsa, başa 'REVIZE_GEREKLI' yaz ve nelerin düzeltilmesi gerektiğini OpenRouter için detaylıca açıkla.\n\n"
        f"{article_body}"
    )

    print(f"-> [Adım 3] Gemini kalite kontrol ve SEO denetimi yapıyor (Deneme {revision_count + 1}/{max_revisions + 1})...")
    qa_response = call_gemini(qa_prompt)

    if qa_response.startswith("ONAYLANDI"):
        print("-> ✅ İçerik Gemini kalite kontrolünden başarıyla geçti.")
        article_body = qa_response.replace("ONAYLANDI", "").strip()
        break
    elif "REVIZE_GEREKLI" in qa_response and revision_count < max_revisions:
        print(f"⚠️ İçerikte eksikler bulundu, OpenRouter'a revize gönderiliyor...")
        revision_feedback_prompt = (
            f"Önceki yazdığın makalede kalite kontrol (QA) uzmanı şu eksikleri buldu ve revize istiyor:\n\n"
            f"{qa_response}\n\n"
            f"Lütfen bu eleştirileri dikkate alarak makaleyi eksiksiz, kurallara tam uyumlu şekilde (HTML/LaTeX olmadan, tablolarla beraber) yeniden yaz. Sadece makale gövdesini ver."
        )
        article_body = call_openrouter(revision_feedback_prompt, system_instruction="Kıdemli teknik yazarsın, eleştirilere göre kusursuz makaleler üretirsin.")
    else:
        print("-> Maksimum revize hakkı doldu veya onay alındı, son hal işleniyor.")
        if "ONAYLANDI" in qa_response:
            article_body = qa_response.replace("ONAYLANDI", "").strip()
        elif "REVIZE_GEREKLI" in qa_response:
            article_body = qa_response.split("REVIZE_GEREKLI")[-1].strip()
        else:
            article_body = qa_response
        break

article_body = normalize_article_body(article_body)
article_body = limit_inline_image_placeholders(article_body, maximum=2)
article_body = remove_missing_local_images(article_body)
require_english_content(topic_data["title"], article_body)

# --- ADIM 4: Görsel İndirme (Garantili Retry Döngüsü) ---
main_visual_prompt = f"Professional technical engineering photograph of {topic_data['title']}, high detail, no text, no watermark"
main_image_filename = f"{topic_data['slug']}.jpg"
main_image_path = os.path.join("public/images", main_image_filename)
cover_image = f"/images/{main_image_filename}"

main_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(main_visual_prompt)}?width=1200&height=600&nologo=true&seed={random.randint(1, 10000)}"

main_image_downloaded = download_image_safely(main_url, main_image_path, max_retries=3)

# Alt görseller için de güvenli indirme
for idx, img_desc in enumerate(re.findall(r'\[IMAGE:\s*(.*?)\]', article_body), start=1):
    sub_img_filename = f"{topic_data['slug']}-part{idx}.jpg"
    sub_path = os.path.join("public/images", sub_img_filename)
    sub_url_path = f"/images/{sub_img_filename}"
    
    sub_prompt = f"Technical engineering photograph of {img_desc}, high quality, off-grid caravan or camping context, no text, no watermark"
    sub_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(sub_prompt)}?width=1000&height=500&nologo=true&seed={random.randint(1, 10000)}"
    
    if download_image_safely(sub_url, sub_path, max_retries=3):
        markdown_img_tag = f"\n\n![{img_desc}]({sub_url_path})\n\n"
        article_body = article_body.replace(f"[IMAGE: {img_desc}]", markdown_img_tag)
    else:
        print(f"⚠️ Alt görsel {idx} indirilemedi, etiket temizleniyor.")
        article_body = article_body.replace(f"[IMAGE: {img_desc}]", "")

# --- ADIM 5: Dosya Kaydı (En Güvenli Yöntem) ---
pub_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
normalized_tags = normalize_tags(topic_data.get("tags"), selected_category)
tags_formatted = "\n".join([f"  - {tag}" for tag in normalized_tags])

# Sadece gerçek kapak görseli başarıyla indiyse ogImage ekle, aksi halde alanı boş bırak
og_image_line = f'ogImage: "{cover_image}"' if main_image_downloaded else ''

post_content = f"""---
author: {CATEGORY_AUTHORS[selected_category]}
pubDatetime: {pub_datetime}
title: "{topic_data['title']}"
postSlug: "{topic_data['slug']}"
category: {selected_category}
featured: false
draft: false
tags:
{tags_formatted}
{og_image_line}
description: "Comprehensive technical guide for {topic_data['title']}."
---

{article_body}
"""

output_path = os.path.join(POSTS_DIR, f"{topic_data['slug']}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)
