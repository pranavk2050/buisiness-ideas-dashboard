#!/usr/bin/env python3
"""Fetch India news from Google News RSS and generate business opportunity analysis."""

import json
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import html as html_module

import feedparser

# Categories and their Google News RSS search queries
CATEGORIES = {
    "health": "India health issues OR India healthcare problems OR India disease",
    "nutrition": "India nutrition OR India malnutrition OR India food safety",
    "education": "India education issues OR India schools OR India literacy",
    "technology": "India technology OR India digital OR India startup tech",
}

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from text."""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = html_module.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

# Template-based business ideas (placeholder until OpenAI integration)
OPPORTUNITY_TEMPLATES = {
    "health": [
        "Develop an affordable telemedicine platform targeting rural India, connecting patients with specialists via low-bandwidth video.",
        "Create a health insurance micro-product for low-income families with simple claim processes via mobile apps.",
        "Build an AI-powered diagnostic tool that works offline on low-cost smartphones for community health workers.",
    ],
    "nutrition": [
        "Launch a fortified food product line targeting nutritional gaps identified in this region.",
        "Create a supply chain platform connecting local farmers directly to school mid-day meal programs.",
        "Develop affordable nutrition monitoring wearables or apps for pregnant women and children.",
    ],
    "education": [
        "Build an offline-first e-learning platform with vernacular language support for rural students.",
        "Create a vocational training marketplace connecting skilled trainers with youth in tier-2/3 cities.",
        "Develop AI tutoring assistants that adapt to regional curricula and local languages.",
    ],
    "technology": [
        "Build digital infrastructure solutions for small businesses to adopt e-commerce in underserved regions.",
        "Create cybersecurity tools tailored for Indian SMEs that handle compliance with local data protection laws.",
        "Develop low-cost IoT solutions for agriculture, enabling precision farming for smallholder farmers.",
    ],
}

SOLUTION_TEMPLATES = {
    "health": [
        "Partner with PHCs (Primary Health Centres) and ASHA workers for last-mile delivery. Use government health data APIs for targeting.",
        "Integrate with Ayushman Bharat scheme for subsidized access. Build trust via local language support and community health camps.",
        "Leverage India Stack (Aadhaar, UPI) for identity verification and payments. Pilot in one state before scaling.",
    ],
    "nutrition": [
        "Collaborate with ICDS (Integrated Child Development Services) and anganwadi centres for distribution and awareness.",
        "Use FPOs (Farmer Producer Organizations) for sourcing. Apply for FSSAI grants for fortification research.",
        "Partner with SHGs (Self-Help Groups) for community-level monitoring and data collection.",
    ],
    "education": [
        "Align with NEP 2020 guidelines. Partner with state education departments for pilot programs in government schools.",
        "Use NSDC (National Skill Development Corporation) framework for certification. Partner with local industries for placement.",
        "Leverage DIKSHA platform integration. Start with subjects with highest failure rates in board exams.",
    ],
    "technology": [
        "Target MSME clusters identified by the Ministry. Offer freemium model with UPI-based payments.",
        "Align with DPDP Act requirements. Offer compliance-as-a-service for businesses handling citizen data.",
        "Partner with KVKs (Krishi Vigyan Kendras) for farmer onboarding. Use satellite + drone data for insights.",
    ],
}


def fetch_category_news(category: str, query: str, max_items: int = 5) -> list[dict]:
    """Fetch news items from Google News RSS for a category."""
    url = GOOGLE_NEWS_RSS.format(query=query.replace(" ", "+"))
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:max_items]:
        title = re.sub(r"\s*-\s*[^-]+$", "", entry.get("title", ""))  # strip source suffix
        item_id = hashlib.md5(title.encode()).hexdigest()[:12]

        pub_date = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
        else:
            pub_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        raw_summary = strip_html(entry.get("summary", ""))
        summary = raw_summary if raw_summary and raw_summary != title.strip() else title.strip()

        items.append({
            "id": item_id,
            "title": title.strip(),
            "summary": summary[:200],
            "category": category,
            "source": "Google News",
            "date": pub_date,
        })

    return items


def deduplicate(issues: list[dict]) -> list[dict]:
    """Remove duplicate issues by title similarity."""
    seen_titles = set()
    unique = []
    for issue in issues:
        key = issue["title"].lower()[:60]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(issue)
    return unique


def enrich_with_ideas(issues: list[dict]) -> list[dict]:
    """Add business opportunity and solution using templates.

    When an OpenAI API key is available, this function can be updated to call
    the API for more contextual analysis:

        import openai
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(...)
    """
    openai_key = os.environ.get("OPENAI_API_KEY")

    for i, issue in enumerate(issues):
        cat = issue["category"]
        templates_opp = OPPORTUNITY_TEMPLATES.get(cat, OPPORTUNITY_TEMPLATES["technology"])
        templates_sol = SOLUTION_TEMPLATES.get(cat, SOLUTION_TEMPLATES["technology"])
        idx = i % len(templates_opp)

        issue["business_opportunity"] = templates_opp[idx]
        issue["solution"] = templates_sol[idx]

        # Simple market potential heuristic
        title_lower = issue["title"].lower()
        if any(w in title_lower for w in ["crisis", "urgent", "critical", "shortage", "death"]):
            issue["market_potential"] = "high"
        elif any(w in title_lower for w in ["new", "launch", "grow", "rise", "plan"]):
            issue["market_potential"] = "medium"
        else:
            issue["market_potential"] = "medium"

    return issues


def main():
    print("Fetching India news across categories...")
    all_issues = []

    for category, query in CATEGORIES.items():
        print(f"  Fetching {category}...")
        try:
            items = fetch_category_news(category, query)
            all_issues.extend(items)
            print(f"    Got {len(items)} items")
        except Exception as e:
            print(f"    Error fetching {category}: {e}")

    all_issues = deduplicate(all_issues)
    all_issues = enrich_with_ideas(all_issues)

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "issues": all_issues,
    }

    out_path = Path(__file__).parent.parent / "data" / "issues.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(all_issues)} issues to {out_path}")


if __name__ == "__main__":
    main()
