import os
import re
import json
from datetime import datetime, timezone
import requests
from pydantic import BaseModel, Field

# --- Doğrulama Şeması (Pydantic) ---
class BlogPostSchema(BaseModel):
    title: str = Field(description="İçeriğin SEO uyumlu İngilizce başlığı")
    slug: str = Field(description="URL için küçük harf ve tireli slug")
    description: str = Field(description="1-2 cümlelik meta açıklama")
    tags: list[str] = Field(description="İlgili etiketler listesi")
    content: str = Field(description="Markdown formatında zengin içerik veya hesaplayıcı kodu")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# İhtiyaca göre model kademelendirmesi
# Rutin içerik: deepseek/deepseek-chat
# JS Hesaplayıcı/Karmaşık: anthropic/claude-3.5-sonnet
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"

PROMPT = """
You are an expert technical content writer and developer.
Generate an engaging, highly useful English blog post about "Top Essential Caravan Equipment & Weight Distribution Tips".
If applicable, include a lightweight, vanilla HTML/JavaScript calculator snippet embedded directly in the markdown.

Return the response STRICTLY as a valid JSON object with the following keys:
- "title": string
- "slug": string (e.g. caravan-weight-distribution-guide)
- "description": string (short SEO description)
- "tags": list of strings (e.g. ["caravan", "travel", "calculator"])
- "content": string (detailed Markdown body, use subheadings, bold text, and clean formatting)
Do not wrap JSON in markdown blockquotes, just return pure JSON.
"""

def generate_post():
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Autonomous Blog Agent"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You output strictly valid JSON matching the requested schema."},
            {"role": "user", "content": PROMPT}
        ],
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    raw_content = response.json()["choices"][0]["message"]["content"].strip()

    # Markdown json bloğu varsa temizle
    clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_content, flags=re.MULTILINE).strip()
    data = json.loads(clean_json)
    
    # Pydantic ile şema doğrulaması
    validated = BlogPostSchema(**data)
    return validated

def save_to_astro(post: BlogPostSchema):
    # AstroPaper blog klasörü
    target_dir = os.path.join("src", "content", "blog")
    os.makedirs(target_dir, exist_ok=True)
    
    filename = f"{post.slug}.md"
    filepath = os.path.join(target_dir, filename)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Human-in-the-Loop: draft her zaman True olarak kaydedilir
    frontmatter = f"""---
author: AI Editorial
pubDatetime: {now_iso}
title: "{post.title}"
postSlug: "{post.slug}"
featured: false
draft: true
tags:
{chr(10).join([f'  - {tag}' for tag in post.tags])}
description: "{post.description}"
---

{post.content}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
    print(f"Başarıyla taslak oluşturuldu: {filepath}")

if __name__ == "__main__":
    post = generate_post()
    save_to_astro(post)
