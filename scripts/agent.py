import os
import re
import json
from datetime import datetime, timezone
import requests
from pydantic import BaseModel, Field

TOPICS_FILE = os.path.join("scripts", "topics.json")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class BlogPostSchema(BaseModel):
    title: str = Field(description="SEO-friendly title")
    slug: str = Field(description="URL slug")
    description: str = Field(description="Meta description")
    tags: list[str] = Field(description="Tags list")
    content: str = Field(description="Full markdown content (including raw HTML/JS if calculator)")

def get_next_topic():
    if not os.path.exists(TOPICS_FILE):
        return None
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)
    for topic in topics:
        if topic.get("status") == "pending":
            return topic
    return None

def mark_topic_done(topic_id):
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)
    for topic in topics:
        if topic.get("id") == topic_id:
            topic["status"] = "completed"
            break
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)

def generate_post(topic):
# Hem rehberler hem interaktif JS hesaplayıcılar için kararlı ve ekonomik DeepSeek-V3
    model_name = "deepseek/deepseek-chat"

    prompt = f"""
You are a senior technical writer and web developer.
Topic: {topic['title']}
Task details: {topic['prompt']}

If creating a calculator, use self-contained inline <style> and vanilla <script> elements inside standard HTML container so it renders and functions directly within Astro markdown.

Return response STRICTLY as valid JSON with keys:
- "title": string
- "slug": string
- "description": string
- "tags": list of strings
- "content": string (Markdown body)
No markdown json wrappers, pure JSON only.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Autonomous Blog Agent"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You output strictly valid JSON matching schema."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4 if topic.get("type") == "calculator" else 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    if not response.ok:
        print("API Hatası:", response.text)
        response.raise_for_status()

    raw = response.json()["choices"][0]["message"]["content"].strip()
    clean_json = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    data = json.loads(clean_json)
    return BlogPostSchema(**data)

def save_post(post: BlogPostSchema):
    target_dir = os.path.join("src", "content", "posts")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, f"{post.slug}.md")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    frontmatter = f"""---
author: AI Editorial
pubDatetime: {now_iso}
title: "{post.title}"
postSlug: "{post.slug}"
featured: true
draft: true
tags:
{chr(10).join([f'  - {tag}' for tag in post.tags])}
description: "{post.description}"
---

{post.content}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
    print(f"Yazı oluşturuldu: {filepath}")

if __name__ == "__main__":
    topic = get_next_topic()
    if not topic:
        print("İşlenecek yeni konu bulunamadı.")
    else:
        print(f"İşleniyor: {topic['title']} (Tip: {topic['type']})")
        post = generate_post(topic)
        save_post(post)
        mark_topic_done(topic["id"])
