import os
import ast
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

CONTENT_TRACKS = [
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Power & Solar", "subcategory": "Solar & Energy", "focus": "solar, charge controllers and energy budgets", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Power & Solar", "subcategory": "Batteries & Charging", "focus": "LiFePO4, BMS, DC-DC charging and inverters", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Water & Plumbing", "subcategory": "Freshwater & Wastewater", "focus": "freshwater tanks, pumps, filtration and wastewater", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "HVAC & Heating", "subcategory": "Climate Control", "focus": "air conditioning, insulation and thermal loads", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "HVAC & Heating", "subcategory": "Heating & Ventilation", "focus": "diesel heaters, ventilation and altitude effects", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Electrical & Wiring", "subcategory": "DC Wiring", "focus": "cable sizing, voltage drop, fuses and grounding", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Electrical & Wiring", "subcategory": "AC Shore Power", "focus": "shore power, load shedding, RCD/GFCI and transfer safety", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Smart RV & IoT", "subcategory": "Automation & Monitoring", "focus": "ESP32, MQTT, sensors and fail-safe automation", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Towing & Weight", "subcategory": "Payload & Stability", "focus": "payload, axle loads, nose weight and weighbridge checks", "author": "VanSpecs Technical Team"},
    {"scope": "caravan", "scope_name": "Caravan Systems", "category": "Towing & Weight", "subcategory": "Towing Safety", "focus": "towing limits, stability, brakes and loading", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Marine Power & Solar", "subcategory": "Solar & Energy", "focus": "marine solar, charge controllers and energy budgets", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Marine Power & Solar", "subcategory": "Batteries & Charging", "focus": "marine batteries, alternators, BMS and charging", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Freshwater & Bilge", "subcategory": "Water Systems", "focus": "freshwater, tanks and onboard water treatment", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Freshwater & Bilge", "subcategory": "Bilge & Pumps", "focus": "bilge pumps, alarms and flood protection", "author": "VanSpecs Technical Team", "calculator": "bilge-sizing"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Marine HVAC", "subcategory": "Climate Control", "focus": "marine air conditioning, heating and ventilation", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Wiring & Corrosion Protection", "subcategory": "Bonding & Corrosion", "focus": "galvanic corrosion, bonding and marine grounding", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Navigation & IoT", "subcategory": "Monitoring & Telemetry", "focus": "NMEA data, sensors, alarms and remote monitoring", "author": "VanSpecs Technical Team"},
    {"scope": "marine", "scope_name": "Marine & Boat Systems", "category": "Weight & Stability", "subcategory": "Stability & Trim", "focus": "load distribution, trim and stability calculations", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Off-Grid Power", "subcategory": "Solar & Energy", "focus": "tiny house energy budgets and solar sizing", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Off-Grid Power", "subcategory": "Batteries & Inverters", "focus": "battery storage, inverters and backup power", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Water & Wastewater", "subcategory": "Freshwater", "focus": "freshwater storage, pumps and filtration", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Water & Wastewater", "subcategory": "Wastewater & Treatment", "focus": "rainwater harvesting, cistern sizing, first-flush diversion and greywater treatment", "author": "VanSpecs Technical Team", "calculator": "rainwater-sizing"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Heating & Cooling", "subcategory": "Heating", "focus": "heating loads, insulation and ventilation", "author": "VanSpecs Technical Team", "calculator": "heat-loss"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Electrical Installation", "subcategory": "AC Distribution", "focus": "AC distribution, protection and local electrical requirements", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Automation & Monitoring", "subcategory": "Energy Monitoring", "focus": "smart energy monitoring and automation", "author": "VanSpecs Technical Team"},
    {"scope": "tiny-house", "scope_name": "Tiny House Systems", "category": "Structure & Weight", "subcategory": "Load Planning", "focus": "structural loads, transport and placement planning", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "Solar & Energy", "subcategory": "Energy Budgets", "focus": "portable and small-space energy budgeting", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "Battery Storage", "subcategory": "BMS & Protection", "focus": "battery safety, BMS limits and protection", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "Water Systems", "subcategory": "Pumps & Filtration", "focus": "pump sizing, filtration and tank autonomy", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "HVAC & Climate", "subcategory": "Cooling & Ventilation", "focus": "climate loads, ventilation and condensation control", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "Electrical Engineering", "subcategory": "Cable Sizing", "focus": "voltage drop, cable ampacity and protection", "author": "VanSpecs Technical Team"},
    {"scope": "shared", "scope_name": "Shared Systems", "category": "Automation & IoT", "subcategory": "Sensors", "focus": "sensors, telemetry and reliable control systems", "author": "VanSpecs Technical Team"},
]

CALCULATORS = {"solar-system", "battery-sizing", "cable-sizing", "inverter-sizing", "towing-safety", "heater-runtime", "gas-runtime", "ac-load", "pump-sizing", "weight-sizing", "water-sizing", "dc-dc-sizing", "bilge-sizing", "heat-loss", "rainwater-sizing"}

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
    # Never persist a provider SDK response/list representation as article Markdown.
    if body.startswith("[") and "'message'" in body and "'content'" in body:
        try:
            parsed = ast.literal_eval(body)
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                message = parsed[0].get("message", {})
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    body = message["content"].strip()
        except (SyntaxError, ValueError):
            pass
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

def normalize_tags(raw_tags, scope_name, category, subcategory):
    """Keep scope and taxonomy labels canonical while removing duplicate tags."""
    values = [scope_name, category, subcategory, "Off-Grid"] + (raw_tags or [])
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

def infer_track(content: str):
    scope_match = re.search(r"^scope:\s*([^\n]+)", content, re.MULTILINE)
    subcategory_match = re.search(r"^subcategory:\s*[\"']?([^\"'\n]+)", content, re.MULTILINE)
    category_match = re.search(r"^category:\s*[\"']?([^\"'\n]+)", content, re.MULTILINE)
    scope = scope_match.group(1).strip().strip("\"'") if scope_match else "caravan"
    subcategory = subcategory_match.group(1).strip() if subcategory_match else ""
    category = category_match.group(1).strip() if category_match else ""
    title = re.search(r"^title:\s*[\"']?(.*?)[\"']?$", content, re.MULTILINE)
    searchable = f"{category} {subcategory} {title.group(1) if title else ''}".casefold()

    if scope == "caravan":
        if "water" in searchable or "pump" in searchable or "plumbing" in searchable:
            category, subcategory = "Water & Plumbing", "Freshwater & Wastewater"
        elif "heater" in searchable or "hvac" in searchable or "thermal" in searchable:
            category, subcategory = "HVAC & Heating", "Heating & Ventilation"
        elif "towing" in searchable or "weight" in searchable or "distribution" in searchable:
            category, subcategory = "Towing & Weight", "Towing Safety"
        elif "smart" in searchable or "iot" in searchable or "mqtt" in searchable or "esp32" in searchable:
            category, subcategory = "Smart RV & IoT", "Automation & Monitoring"
        elif "shore" in searchable or "ac " in searchable:
            category, subcategory = "Electrical & Wiring", "AC Shore Power"
        elif "cable" in searchable or "voltage" in searchable or "ground" in searchable or "wiring" in searchable:
            category, subcategory = "Electrical & Wiring", "DC Wiring"
        else:
            category, subcategory = "Power & Solar", "Solar & Energy"

    for track in CONTENT_TRACKS:
        if track["scope"] == scope and track["category"] == category and track["subcategory"] == subcategory:
            return track
    return None

track_counts = {id(track): 0 for track in CONTENT_TRACKS}
for file_path in glob.glob(f"{POSTS_DIR}/*.md"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            track = infer_track(f.read())
        if track:
            track_counts[id(track)] += 1
    except Exception:
        continue

least_filled_count = min(track_counts.values())
selected_track = next(track for track in CONTENT_TRACKS if track_counts[id(track)] == least_filled_count)
selected_scope = selected_track["scope"]
selected_scope_name = selected_track["scope_name"]
selected_category = selected_track["category"]
selected_subcategory = selected_track["subcategory"]

# --- ADIM 1: Strateji, Tekrar Analizi ve Zengin Brief Üretimi (Gemini) ---
strategy_prompt = (
    f"Sen Kıdemli bir SEO ve İçerik Direktörüsün.\n"
    f"Content scope: {selected_scope_name}\n"
    f"Technical category: {selected_category}\n"
    f"Subcategory: {selected_subcategory}\n"
    f"Topic focus: {selected_track['focus']}\n\n"
    f"Relevant calculator hint: {selected_track.get('calculator', 'none')}\n\n"
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
    "  \"calculator\": null,\n"
    "  \"brief\": \"Bu makalede işlenecek teknik detaylar, formüller, karşılaştırma parametreleri ve adım adım hesaplama senaryosunun detaylı açıklaması.\"\n"
    "}"
)

print(f"-> [Adım 1] Gemini site analizi yapıyor ve stratejik brief hazırlıyor ({selected_category})...")
strategy_raw = call_gemini(strategy_prompt, json_mode=True)
strategy_raw = re.sub(r"^```json\s*", "", strategy_raw)
strategy_raw = re.sub(r"\s*```$", "", strategy_raw)
topic_data = json.loads(strategy_raw)

requested_calculator = topic_data.get("calculator")
if requested_calculator not in CALCULATORS:
    requested_calculator = None
if selected_track.get("calculator") and requested_calculator is None:
    requested_calculator = selected_track["calculator"]
if requested_calculator == "rainwater-sizing" and not re.search(r"rainwater|rain harvesting|cistern|stormwater", f"{topic_data.get('title', '')} {topic_data.get('brief', '')}", re.IGNORECASE):
    requested_calculator = None

print(f"-> Seçilen Konu: {topic_data['title']}")
print(f"-> Stratejik Brief: {topic_data['brief']}")

# --- ADIM 2: İçerik Üretimi ve 2 Haklı Revize Döngüsü (OpenRouter & Gemini QA) ---
content_prompt = (
    "IMPORTANT LANGUAGE RULE: The website is English-only. Write the title, article body, headings, tables, labels, image descriptions, and every sentence in clear professional English. Never write Turkish, even if this instruction or the brief contains Turkish text.\n\n"
    "Return only the article body. Do not return YAML frontmatter, a title line, or direct /images/*.jpg links; use the exact [IMAGE: English description] placeholder when an image is needed.\n\n"
    f"Content scope: {selected_scope_name}\n"
    f"Technical category: {selected_category}\n"
    f"Subcategory: {selected_subcategory}\n"
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
    "\n8. Never return a Python list, JSON object, SDK response, refusal metadata, escaped \\n sequences or provider log. Return readable Markdown only."
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
normalized_tags = normalize_tags(topic_data.get("tags"), selected_scope_name, selected_category, selected_subcategory)
tags_formatted = "\n".join([f"  - {tag}" for tag in normalized_tags])

# Sadece gerçek kapak görseli başarıyla indiyse ogImage ekle, aksi halde alanı boş bırak
og_image_line = f'ogImage: "{cover_image}"' if main_image_downloaded else ''

post_content = f"""---
author: {selected_track['author']}
pubDatetime: {pub_datetime}
title: "{topic_data['title']}"
postSlug: "{topic_data['slug']}"
scope: {selected_scope}
category: {selected_category}
subcategory: {selected_subcategory}
{"calculator: " + requested_calculator if requested_calculator else ""}
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
