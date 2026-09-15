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
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
gemini_fallback_model = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")
gemini_max_retries = 3

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

CONTENT_TYPES = {
    "technical-guide": {"label": "technical guide", "target": 0.30},
    "calculator-support": {"label": "calculator/support", "target": 0.20},
    "troubleshooting": {"label": "troubleshooting", "target": 0.20},
    "comparison-decision": {"label": "comparison/decision", "target": 0.20},
    "complete-system-case-study": {"label": "complete system/case study", "target": 0.10},
}

ROLE_ORDER = ["pillar", "calculator", "decision", "troubleshooting", "sub-guide", "equipment-selection"]
CONTENT_PHASE = os.environ.get("CONTENT_PHASE", "foundation").strip().casefold()
ALLOW_SCOPE_FALLBACK = os.environ.get("ALLOW_SCOPE_FALLBACK", "false").strip().casefold() == "true"
PHASE_SCOPES = {
    "foundation": {"caravan"},
    "expansion": {"caravan", "marine", "tiny-house", "shared"},
}

if CONTENT_PHASE not in PHASE_SCOPES:
    raise ValueError(f"CONTENT_PHASE must be one of: {', '.join(PHASE_SCOPES)}")

def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return value

def is_semantic_duplicate(candidate, existing_titles):
    stopwords = {"a", "an", "and", "for", "how", "to", "the", "with", "in", "of", "on", "guide"}
    candidate_words = {word for word in re.findall(r"[a-z0-9]+", candidate.casefold()) if word not in stopwords}
    if len(candidate_words) < 4:
        return False
    for title in existing_titles:
        existing_words = {word for word in re.findall(r"[a-z0-9]+", title.casefold()) if word not in stopwords}
        overlap = len(candidate_words & existing_words) / max(1, len(candidate_words | existing_words))
        if overlap >= 0.72:
            return True
    return False

def parse_frontmatter(content):
    frontmatter = content.split("---", 2)[1] if content.startswith("---") else ""
    def field(name):
        match = re.search(rf"^{name}:\s*[\"']?([^\"'\n]+)", frontmatter, re.MULTILINE)
        return match.group(1).strip() if match else ""
    return {"title": field("title"), "slug": field("postSlug"), "scope": field("scope"),
            "category": field("category"), "subcategory": field("subcategory"),
            "calculator": field("calculator"), "content_type": field("contentType"),
            "cluster": field("topicCluster")}

def classify_content_type(post):
    if post.get("content_type") in CONTENT_TYPES:
        return post["content_type"]
    text = post["title"].casefold()
    if any(word in text for word in ("troubleshoot", "preventing", "eliminating", "rapid cycling", "tripping", "thermal throttling", "soot")):
        return "troubleshooting"
    if any(word in text for word in (" vs ", "versus", "choose", "comparison", "selection", "selecting")):
        return "comparison-decision"
    if any(word in text for word in ("complete system", "case study", "system design", "designing an " )):
        return "complete-system-case-study"
    if post.get("calculator"):
        return "calculator-support"
    return "technical-guide"

def cluster_key(post):
    return post.get("cluster") or " / ".join(filter(None, (post.get("scope"), post.get("category"), post.get("subcategory"))))

def get_content_inventory():
    inventory = []
    for file_path in sorted(glob.glob(f"{POSTS_DIR}/*.md")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            post = parse_frontmatter(raw_content)
            inferred_track = infer_track(raw_content)
            if inferred_track:
                post["scope"] = inferred_track["scope"]
                post["category"] = inferred_track["category"]
                post["subcategory"] = inferred_track["subcategory"]
            post["file"] = os.path.basename(file_path)
            post["content_type"] = classify_content_type(post)
            post["cluster"] = cluster_key(post)
            inventory.append(post)
        except (OSError, UnicodeError):
            continue
    return inventory

def build_topic_plan(inventory, phase=None):
    """Create a deterministic cluster/role gap plan before asking a model for wording."""
    phase = phase or CONTENT_PHASE
    clusters = {}
    for post in inventory:
        clusters.setdefault(post["cluster"], []).append(post)
    plans = []
    active_tracks = [track for track in CONTENT_TRACKS if track["scope"] in PHASE_SCOPES[phase]]
    for track in active_tracks:
        key = " / ".join((track["scope"], track["category"], track["subcategory"]))
        posts = clusters.get(key, [])
        calculator = track.get("calculator")
        roles = {
            "pillar": ("complete-system-case-study", f"Complete {track['focus']} system design for {track['scope_name']}"),
            "calculator": ("calculator-support", f"How to size {track['focus']} with a practical calculator"),
            "decision": ("comparison-decision", f"How to choose {track['focus']} equipment for an off-grid system"),
            "troubleshooting": ("troubleshooting", f"Troubleshooting common {track['focus']} failures"),
            "sub-guide": ("technical-guide", f"Technical guide to {track['focus']} installation and verification"),
            "equipment-selection": ("comparison-decision", f"Equipment selection checklist for {track['focus']}"),
        }
        for role in ROLE_ORDER:
            content_type, seed_title = roles[role]
            role_terms = {"pillar": ("complete", "system", "case study"), "calculator": ("calculator", "size"),
                          "decision": (" vs ", "choose", "comparison", "select"), "troubleshooting": ("troubleshoot", "prevent", "eliminat", "failure"),
                          "sub-guide": ("guide", "wiring", "installation", "designing"), "equipment-selection": ("selection", "select", "choose")}[role]
            covered = any(any(term in post["title"].casefold() for term in role_terms) for post in posts)
            if role == "calculator" and calculator and calculator in {post["calculator"] for post in posts}:
                covered = True
            if not covered:
                plans.append({"track": track, "cluster": key, "role": role, "content_type": content_type,
                              "seed_title": seed_title, "calculator": calculator if role == "calculator" else None,
                              "existing_titles": [post["title"] for post in posts]})
    type_counts = {content_type: sum(post["content_type"] == content_type for post in inventory) for content_type in CONTENT_TYPES}
    total = max(len(inventory), 1)
    for plan in plans:
        current_share = type_counts[plan["content_type"]] / total
        plan["cluster_count"] = len(clusters.get(plan["cluster"], []))
        plan["role_index"] = ROLE_ORDER.index(plan["role"])
        plan["priority"] = CONTENT_TYPES[plan["content_type"]]["target"] - current_share
    # Önce en az beslenen alt kategori, sonra o kategorinin sıradaki rolü seçilir.
    # Böylece günlük yayınlar tek bir kategoriye yığılmadan dengeli ilerler.
    return sorted(plans, key=lambda plan: (plan["cluster_count"], plan["role_index"], -plan["priority"], plan["cluster"])), type_counts

def _gemini_retry_delay(error: Exception, attempt: int) -> float:
    """Honor Google's retryDelay when available, with a bounded exponential fallback."""
    match = re.search(r"retryDelay['\"]?\s*[:=]\s*['\"]([0-9]+(?:\.[0-9]+)?)s", str(error))
    delay = float(match.group(1)) if match else min(8 * (2 ** (attempt - 1)), 60)
    return min(delay, 60)

def call_gemini(prompt: str, json_mode: bool = False) -> str:
    config_kwargs = {}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
        
    models = [gemini_model]
    if gemini_fallback_model and gemini_fallback_model != gemini_model:
        models.append(gemini_fallback_model)

    for model_index, model in enumerate(models):
        for attempt in range(1, gemini_max_retries + 1):
            try:
                response = gemini_client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs)
                )
                if model != gemini_model:
                    print(f"-> Gemini fallback aktif: {model}")
                return response.text.strip()
            except Exception as error:
                status_code = getattr(error, "status_code", None)
                error_text = str(error)
                is_model_not_found = status_code == 404 or "NOT_FOUND" in error_text
                is_retryable_model_error = (
                    status_code in {404, 429, 500, 503}
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "UNAVAILABLE" in error_text
                    or "NOT_FOUND" in error_text
                    or "429" in error_text
                )
                is_daily_quota = "quota_exceeded" in error_text.casefold() or "daily quota" in error_text.casefold()
                if not is_retryable_model_error:
                    raise
                if model_index < len(models) - 1:
                    reason = "model bulunamadı" if is_model_not_found else "kota/geçici servis yoğunluğu"
                    print(f"⚠️ {model} ({reason}) kullanılamıyor; {gemini_fallback_model} ile devam edilecek.")
                    break
                if is_model_not_found:
                    raise RuntimeError(
                        "Gemini primary and fallback model IDs are unavailable for this API project."
                    ) from error
                if is_daily_quota:
                    raise RuntimeError(
                        "Gemini daily quota is exhausted on both primary and fallback models; the next scheduled run will retry."
                    ) from error
                if attempt == gemini_max_retries:
                    raise RuntimeError(
                        "Gemini primary and fallback models are unavailable after retrying quota/service errors."
                    ) from error
                delay = _gemini_retry_delay(error, attempt)
                print(f"⚠️ Gemini fallback geçici hata. {delay:g} saniye sonra tekrar denenecek ({attempt}/{gemini_max_retries - 1}).")
                time.sleep(delay)

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

def reject_remote_image_references(body: str) -> None:
    """Enforce the repository rule that generated article images are local assets."""
    remote_image = re.compile(r"!\[[^\]]*\]\(https?://|<img\b[^>]*\bsrc=[\"']https?://", re.IGNORECASE)
    if remote_image.search(body):
        raise RuntimeError("Generated content contains a remote image URL; only /images/* assets are allowed.")

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
    """Keep topical tags useful; scope and category already have dedicated taxonomy fields."""
    values = raw_tags or []
    tags = []
    seen = set()
    for value in values:
        tag = str(value).strip()
        key = tag.casefold()
        if tag and key not in seen:
            tags.append(tag)
            seen.add(key)
    return tags[:8]

def get_existing_posts_summary(inventory):
    summary = "\n".join(
        f"- {post['title']} | type={post['content_type']} | cluster={post['cluster']} | calculator={post['calculator'] or 'none'} | file={post['file']}"
        for post in inventory
    ) or "No existing posts."
    return summary[:6000]

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

content_inventory = get_content_inventory()
topic_plans, type_counts = build_topic_plan(content_inventory)
selected_phase = CONTENT_PHASE
if not topic_plans and ALLOW_SCOPE_FALLBACK and CONTENT_PHASE == "foundation":
    selected_phase = "expansion"
    topic_plans, type_counts = build_topic_plan(content_inventory, selected_phase)
    print("-> Foundation topic gaps are exhausted; controlled scope fallback enabled.")
if not topic_plans:
    raise RuntimeError("No uncovered topic-cluster role remains; review the cluster blueprints before generating more content.")
selected_plan = topic_plans[0]
selected_track = selected_plan["track"]
selected_scope = selected_track["scope"]
selected_scope_name = selected_track["scope_name"]
selected_category = selected_track["category"]
selected_subcategory = selected_track["subcategory"]
selected_content_type = selected_plan["content_type"]
selected_cluster = selected_plan["cluster"]
existing_posts_context = get_existing_posts_summary(content_inventory)
print(f"-> Content inventory: {len(content_inventory)} posts; type counts: {type_counts}")
print(f"-> Content phase: {selected_phase}; active scopes: {', '.join(sorted(PHASE_SCOPES[selected_phase]))}")
print(f"-> Gap plan: {selected_cluster} / {selected_plan['role']} / {selected_content_type}")

# --- ADIM 1: Strateji, Tekrar Analizi ve Zengin Brief Üretimi (Gemini) ---
strategy_prompt = (
    f"Sen Kıdemli bir SEO ve İçerik Direktörüsün.\n"
    f"Content scope: {selected_scope_name}\n"
    f"Technical category: {selected_category}\n"
    f"Subcategory: {selected_subcategory}\n"
    f"Topic focus: {selected_track['focus']}\n\n"
    f"Cluster role: {selected_plan['role']}\n"
    f"Required content type: {selected_content_type}\n"
    f"Relevant calculator hint: {selected_plan.get('calculator') or 'none'}\n"
    f"Gap seed (do not copy literally): {selected_plan['seed_title']}\n\n"
    f"Publishing phase: {selected_phase}. Do not select a topic outside the active scopes.\n"
    f"Sitede Daha Önce Yayınlanmış Yazılar:\n{existing_posts_context}\n\n"
    "GÖREV:\n"
    "1. Use the inventory and gap plan to select a genuinely uncovered topic. Never repeat or lightly rephrase an existing title. Reject semantic duplicates and choose one narrow, answerable user problem. Do not combine more than one major engineering system in the same article.\n"
    "2. Seçtiğin konunun kullanıcıya sağlayacağı ekstra faydayı stratejik olarak kurgula.\n"
    "3. Search intent, primary query, secondary queries, title promise and a concise meta description oluştur.\n"
    "4. Yazıyı yazacak olan mühendis yazar (OpenRouter) için uygulanabilir ama kısa bir içerik brief'i hazırla. Brief 1600 karakteri geçmesin; en fazla 4 ana teknik bölüm, gerekli kaynak türleri ve açık güvenlik sınırları içersin.\n"
    "5. AC, şebeke, gaz, towing veya yapısal güvenlik içeren konularda evrensel bağlantı/uygulama talimatı verme. Üretici dokümanı ve yetkili kontrol gerektiren noktaları açıkça belirt; kaynak yoksa sayısal değeri varsayım olarak etiketle.\n\n"
    "ÇIKTI FORMATI (Saf JSON):\n"
    "{\n"
    "  \"title\": \"İngilizce SEO Uyumlu Başlık\",\n"
    "  \"slug\": \"url-slug\",\n"
    "  \"tags\": [\"tag1\", \"tag2\"],\n"
    "  \"content_type\": \"technical-guide|calculator-support|troubleshooting|comparison-decision|complete-system-case-study\",\n"
    "  \"topic_cluster\": \"scope / category / subcategory\",\n"
    "  \"calculator\": null,\n"
    "  \"primary_query\": \"specific English search query\",\n"
    "  \"secondary_queries\": [\"related query 1\", \"related query 2\"],\n"
    "  \"meta_description\": \"A clear 140-160 character description for search results.\",\n"
    "  \"related_posts\": [\"exact existing post title\"],\n"
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

if topic_data.get("content_type") not in CONTENT_TYPES:
    topic_data["content_type"] = selected_content_type
topic_data["topic_cluster"] = selected_cluster
existing_titles = [post["title"].casefold() for post in content_inventory]
candidate_title = str(topic_data.get("title", "")).strip()
candidate_slug = slugify(str(topic_data.get("slug") or candidate_title))
existing_slugs = {post["slug"].casefold() for post in content_inventory if post["slug"]}
if (not candidate_title or is_semantic_duplicate(candidate_title, existing_titles)
        or candidate_slug in existing_slugs):
    raise RuntimeError("Planner returned an existing or semantically duplicate topic; no post was written.")
topic_data["slug"] = candidate_slug
related_posts = [post for post in content_inventory if post["cluster"] == selected_cluster]
if len(related_posts) < 3:
    related_posts.extend(
        post for post in content_inventory
        if post not in related_posts
        and post.get("scope") == selected_scope
        and post.get("category") == selected_category
    )
related_posts = related_posts[:5]
CALCULATOR_ROUTES = {
    "solar-system": "solar-calculator", "battery-sizing": "battery-calculator", "cable-sizing": "cable-calculator",
    "inverter-sizing": "inverter-calculator", "towing-safety": "towing-calculator", "heater-runtime": "heater-calculator",
    "gas-runtime": "gas-calculator", "ac-load": "ac-load-calculator", "pump-sizing": "pump-calculator",
    "weight-sizing": "weight-calculator", "water-sizing": "water-calculator", "dc-dc-sizing": "dc-dc-calculator",
    "bilge-sizing": "bilge-calculator", "heat-loss": "heat-loss-calculator", "rainwater-sizing": "rainwater-calculator",
}
related_calculator_route = f"/tools/{CALCULATOR_ROUTES[requested_calculator]}" if requested_calculator in CALCULATOR_ROUTES else "none"
scope_route = f"/scopes/{selected_scope}-systems/"
related_links = "\n".join(f"- [{post['title']}](/posts/{post['slug']})" for post in related_posts)
related_links += f"\n- [Explore {selected_scope_name}]({scope_route})\n- [Browse engineering calculators](/tools/)"

print(f"-> Seçilen Konu: {topic_data['title']}")
print(f"-> Stratejik Brief: {topic_data['brief']}")

# --- ADIM 2: İçerik Üretimi ve 2 Haklı Revize Döngüsü (OpenRouter & Gemini QA) ---
content_prompt = (
    "IMPORTANT LANGUAGE RULE: The website is English-only. Write the title, article body, headings, tables, labels, image descriptions, and every sentence in clear professional English. Never write Turkish, even if this instruction or the brief contains Turkish text.\n\n"
    "Return only the article body. Do not return YAML frontmatter, a title line, or direct /images/*.jpg links; use the exact [IMAGE: English description] placeholder when an image is needed.\n\n"
    f"Content scope: {selected_scope_name}\n"
    f"Technical category: {selected_category}\n"
    f"Subcategory: {selected_subcategory}\n"
    f"Required content type: {selected_content_type}\n"
    f"Topic cluster: {selected_cluster}\n"
    f"Konu Başlığı: \"{topic_data['title']}\"\n\n"
    f"TEKNİK BİRİEF / YÖNLENDİRME:\n{topic_data['brief']}\n\n"
    f"Primary search query: {topic_data.get('primary_query') or 'choose a specific long-tail query'}\n"
    f"Secondary queries: {', '.join(topic_data.get('secondary_queries') or []) or 'choose two closely related queries'}\n"
    f"Existing related guide links (use only when relevant):\n{related_links}\n"
    f"Related calculator route: {related_calculator_route}\n\n"
    "GÖREV:\n"
    "Yukarıdaki stratejik brief'e sadık kalarak, en az 1200 kelime, son derece derinlemesine ve profesyonel bir teknik rehber yaz.\n\n"
    "KESİN KURALLAR:\n"
    "1. HTML veya LaTeX ($...$) KULLANMA. Formülleri düz metin yaz (Örn: Voltage Drop = ...).\n"
    "2. İçerikte en az 2 adet detaylı Markdown Veri/Karşılaştırma Tablosu bulunsun.\n"
    "3. Somut sayısal hesaplama adımları ekle.\n"
    "4. Every calculation must state inputs, units, formula, assumptions, and result. Never invent manufacturer specifications; mark unknown values as assumptions.\n"
    "5. End with a concise Sources and Assumptions section using direct official manufacturer, standards or government URLs when available. State clearly when a value is illustrative or model-specific.\n"
    "6. Görsel yerleri için tam olarak şu formatı kullan: [IMAGE: Kısa ingilizce görsel açıklaması]. En fazla 2 görsel işareti kullan.\n"
    "7. Sadece makale gövdesini yaz; `# Başlık` kullanma, çünkü sayfa şablonu başlığı zaten H1 olarak basıyor. Giriş paragrafı veya `##` başlığıyla başla.\n"
    "8. Generated images must never be linked remotely. Use only the provided [IMAGE: English description] placeholders; the pipeline stores them under public/images.\n"
    "9. Tags must be short, English, topic-specific labels only. Do not repeat scope, category or subcategory values as tags.\n"
    "10. Add 2-5 natural internal links to the supplied related guides, scope page, tools page and calculator route when relevant. Use descriptive English anchor text, never a raw URL list. Link only to existing paths.\n"
    "11. Match the required content type: pillar/system content must connect the full system; calculator/support must explain inputs and interpretation; troubleshooting must use symptoms, tests and safe fixes; comparison/decision must end with a clear choice matrix; technical guides must focus on one implementation topic.\n"
    "12. State safety boundaries for electrical, gas, towing, structural and marine work. Do not present illustrative values as universal specifications.\n"
    "13. Optimize for people-first search usefulness: answer the primary query early, use descriptive headings, avoid keyword stuffing, and include a practical next step.\n"
    "14. Never return a Python list, JSON object, SDK response, refusal metadata, escaped \\n sequences or provider log. Return readable Markdown only."
)

print("-> [Adım 2] OpenRouter makaleyi kaleme alıyor...")
article_body = call_openrouter(content_prompt, system_instruction="Uzun, teknik ve profesyonel Markdown makaleleri yazarsın.")

max_revisions = 1
qa_approved = False
for revision_count in range(max_revisions + 1):
    qa_prompt = (
        "- The website is English-only. If any Turkish sentence, heading, table text, or Turkish language markers appear, return REVIZE_GEREKLI and require a complete English rewrite.\n"
        "Aşağıdaki makaleyi SEO uygunluğu, teknik doğruluk, kelime uzunluğu, tablo varlığı ve kurallara uyum açısından denetle. Yalnızca kritik bir güvenlik/faktüel hata, İngilizce kuralı, belirgin format ihlali veya görevin temel amacının kaçırılması varsa REVIZE_GEREKLI döndür; küçük üslup eksikleri ve isteğe bağlı ayrıntılar için onay ver.\n"
        "KURALLAR:\n"
        "- HTML etiketleri veya LaTeX ($...$) var mı? Varsa tamamen düz metne çevir.\n"
        "- Markdown tabloları ve başlık hiyerarşisi tam mı? İlk satırda H1 (`# Başlık`) var mı? Varsa kaldır.\n\n"
        "Eğer makale eksiksizse ve kurallara uyuyorsa, başa 'ONAYLANDI' yaz ve hemen ardından düzeltilmiş nihai makaleyi ver.\n"
        "Eğer eksikler veya kural ihlalleri varsa, başa 'REVIZE_GEREKLI' yaz ve nelerin düzeltilmesi gerektiğini OpenRouter için detaylıca açıkla.\n\n"
        f"{article_body}"
    )

    print(f"-> [Adım 3] Gemini kalite kontrol ve SEO denetimi yapıyor (Deneme {revision_count + 1}/{max_revisions + 1})...")
    qa_response = call_gemini(qa_prompt)
    print(f"-> QA sonucu: {qa_response[:900].replace(chr(10), ' ')}")

    if qa_response.startswith("ONAYLANDI"):
        print("-> ✅ İçerik Gemini kalite kontrolünden başarıyla geçti.")
        article_body = qa_response.replace("ONAYLANDI", "").strip()
        qa_approved = True
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
        print("-> ❌ Maksimum revize hakkı doldu; içerik yayınlanmayacak.")
        if "ONAYLANDI" in qa_response:
            article_body = qa_response.replace("ONAYLANDI", "").strip()
            qa_approved = True
        # REVIZE_GEREKLI responses contain QA feedback, not article content.
        break

if not qa_approved:
    raise RuntimeError(
        "Gemini quality gate did not approve the article after the maximum revision attempts; no post was written."
    )

article_body = normalize_article_body(article_body)
article_body = limit_inline_image_placeholders(article_body, maximum=2)
article_body = remove_missing_local_images(article_body)
reject_remote_image_references(article_body)
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
related_guides_formatted = "\n".join(f'  - "{post["slug"]}"' for post in related_posts) or "  []"

# Sadece gerçek kapak görseli başarıyla indiyse ogImage ekle, aksi halde alanı boş bırak
og_image_line = f'ogImage: "{cover_image}"' if main_image_downloaded else ''
description = str(topic_data.get("meta_description") or f"A practical technical guide to {topic_data['title']}.").replace('"', "'").strip()
if len(description) > 160:
    description = description[:157].rsplit(" ", 1)[0] + "..."

post_content = f"""---
author: {selected_track['author']}
pubDatetime: {pub_datetime}
title: "{topic_data['title']}"
postSlug: "{topic_data['slug']}"
scope: {selected_scope}
category: {selected_category}
subcategory: {selected_subcategory}
contentType: {topic_data['content_type']}
topicCluster: "{selected_cluster}"
{"calculator: " + requested_calculator if requested_calculator else ""}
relatedGuides:
{related_guides_formatted}
featured: false
draft: false
tags:
{tags_formatted}
{og_image_line}
description: "{description}"
lastReviewed: {pub_datetime}
---

{article_body}
"""

output_path = os.path.join(POSTS_DIR, f"{topic_data['slug']}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(post_content)
