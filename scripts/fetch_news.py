#!/usr/bin/env python3
"""Fetch India news from Google News RSS and generate business opportunity analysis."""

import json
import hashlib
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import html as html_module
import requests

import feedparser

# Categories and their Google News RSS search queries
CATEGORIES = {
    "health": "India health issues OR India healthcare problems OR India disease",
    "nutrition": "India nutrition OR India malnutrition OR India food safety",
    "education": "India education issues OR India schools OR India literacy",
    "technology": "India technology OR India digital OR India startup tech",
    "agriculture": "India agriculture problems OR India farming crisis OR India crop",
    "environment": "India pollution OR India climate change OR India waste management",
    "infrastructure": "India infrastructure OR India roads OR India smart city OR India housing",
    "finance": "India fintech OR India banking rural OR India financial inclusion OR India microfinance",
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
    "agriculture": [
        "Build a crop advisory platform using satellite imagery and weather data for smallholder farmers.",
        "Create a direct farm-to-consumer marketplace eliminating middlemen and ensuring fair prices.",
        "Develop soil health monitoring kits with mobile app integration for real-time recommendations.",
        "Launch a cold chain logistics network for perishable produce in underserved rural corridors.",
    ],
    "environment": [
        "Build a waste-to-energy platform connecting municipal waste generators with recycling facilities.",
        "Create a carbon credit marketplace for Indian SMEs and agricultural operations.",
        "Develop affordable air quality monitoring devices for schools and residential communities.",
        "Launch an e-waste recycling service with doorstep pickup for urban households and businesses.",
    ],
    "infrastructure": [
        "Create a smart parking and traffic management solution for tier-2 Indian cities.",
        "Build a platform connecting migrant construction workers with verified contractors and housing projects.",
        "Develop modular, affordable housing solutions using recycled materials for urban slum rehabilitation.",
        "Launch a last-mile delivery infrastructure for rural e-commerce using local transport networks.",
    ],
    "finance": [
        "Build a vernacular-language financial literacy app targeting rural women and SHG members.",
        "Create a micro-lending platform using alternative credit scoring (mobile usage, utility payments).",
        "Develop a unified dashboard for small merchants to manage UPI, credit, and inventory in one place.",
        "Launch a crop insurance tech platform simplifying claim filing for smallholder farmers.",
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
    "agriculture": [
        "Partner with ICAR and state agriculture universities for data validation. Pilot with progressive farmers in one district.",
        "Integrate with eNAM (National Agriculture Market) for price discovery. Use FPO networks for farmer onboarding.",
        "Collaborate with Soil Health Card scheme for baseline data. Offer freemium model with premium advisory tier.",
        "Apply for NABARD grants for cold chain infrastructure. Partner with Kisan Rails for long-distance transport.",
    ],
    "environment": [
        "Partner with municipal corporations under Swachh Bharat Mission. Use CSR funds from large corporates for initial setup.",
        "Leverage CCTS (Indian Carbon Trading Scheme) framework. Start with agriculture and renewable energy sectors.",
        "Collaborate with CPCB for data standards. Distribute through school networks and RWAs for community adoption.",
        "Register under Extended Producer Responsibility (EPR) framework. Partner with electronics brands for collection drives.",
    ],
    "infrastructure": [
        "Pilot with Smart Cities Mission cities. Integrate with existing ITMS infrastructure for faster adoption.",
        "Register on eShram portal for worker database. Partner with real estate developers and government housing schemes.",
        "Align with PMAY (Pradhan Mantri Awas Yojana) guidelines. Use local manufacturing to reduce costs by 40%.",
        "Partner with India Post and CSC (Common Service Centres) for rural reach. Use electric vehicles for last-mile delivery.",
    ],
    "finance": [
        "Partner with NABARD and regional rural banks for distribution. Align content with RBI financial literacy guidelines.",
        "Use India Stack (Account Aggregator + UPI) for underwriting. Partner with NBFCs for lending capital.",
        "Integrate with ONDC for e-commerce features. Offer in local languages with voice-first interface.",
        "Integrate with PMFBY (Pradhan Mantri Fasal Bima Yojana). Use satellite and weather data for automated claim assessment.",
    ],
}


def fetch_category_news(category: str, query: str, max_items: int = 15) -> list[dict]:
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


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def call_groq(title: str, summary: str, category: str, api_key: str) -> dict | None:
    """Call Groq API to generate contextual business opportunity and solution."""
    prompt = f"""You are an Indian startup business analyst. Analyze this news issue and provide a root cause analysis, a specific actionable business opportunity, and a practical solution relevant to the Indian market.

News Title: {title}
Summary: {summary}
Category: {category}

Respond ONLY with valid JSON (no markdown, no code blocks):
{{"root_cause": "A 2-3 sentence analysis of WHY this issue exists in India — systemic, structural, or policy reasons", "business_opportunity": "A specific 2-3 sentence business idea directly related to this news issue, with target audience and revenue model", "solution": "A practical 2-3 sentence implementation plan mentioning relevant Indian government schemes, partnerships, or ecosystem players", "market_potential": "high or medium or low based on urgency and market size"}}"""

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500,
            },
            timeout=15,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
        result = json.loads(content)
        # Validate required fields
        if all(k in result for k in ("business_opportunity", "solution", "market_potential", "root_cause")):
            if result["market_potential"] not in ("high", "medium", "low"):
                result["market_potential"] = "medium"
            return result
    except Exception as e:
        print(f"    Groq API error: {e}")
    return None


ROOT_CAUSE_TEMPLATES = {
    "health": "India's healthcare challenges stem from inadequate public health infrastructure, low government spending (around 2% of GDP), shortage of doctors in rural areas, and limited health insurance penetration among the population.",
    "nutrition": "Malnutrition persists due to poverty, lack of dietary diversity, poor sanitation, inadequate public distribution systems, and limited awareness about balanced nutrition among rural and urban poor populations.",
    "education": "Education gaps arise from underfunded public schools, teacher shortages and poor training, language barriers, urban-rural divide in access, and outdated curricula that don't align with market needs.",
    "technology": "India's digital divide is driven by uneven internet penetration, low digital literacy in rural areas, insufficient tech infrastructure in smaller cities, and regulatory complexity for startups.",
    "agriculture": "Farm distress is rooted in fragmented landholdings, dependence on monsoons, lack of cold chain infrastructure, exploitative middlemen, inadequate crop insurance, and poor access to credit and modern technology.",
    "environment": "Environmental degradation stems from rapid urbanization, weak enforcement of pollution laws, inadequate waste management infrastructure, industrial emissions, and over-reliance on fossil fuels.",
    "infrastructure": "Infrastructure gaps result from rapid urban migration outpacing city planning, bureaucratic delays in project execution, land acquisition challenges, insufficient municipal funding, and fragmented governance.",
    "finance": "Financial exclusion persists due to low financial literacy, limited banking access in rural areas, lack of formal credit history for the poor, complex regulatory requirements, and distrust of formal financial institutions.",
}


def enrich_with_templates(issue: dict, index: int) -> None:
    """Fallback: assign business ideas from templates."""
    cat = issue["category"]
    templates_opp = OPPORTUNITY_TEMPLATES.get(cat, OPPORTUNITY_TEMPLATES["technology"])
    templates_sol = SOLUTION_TEMPLATES.get(cat, SOLUTION_TEMPLATES["technology"])
    idx = index % len(templates_opp)

    issue["root_cause"] = ROOT_CAUSE_TEMPLATES.get(cat, ROOT_CAUSE_TEMPLATES["technology"])
    issue["business_opportunity"] = templates_opp[idx]
    issue["solution"] = templates_sol[idx]

    title_lower = issue["title"].lower()
    if any(w in title_lower for w in ["crisis", "urgent", "critical", "shortage", "death"]):
        issue["market_potential"] = "high"
    elif any(w in title_lower for w in ["new", "launch", "grow", "rise", "plan"]):
        issue["market_potential"] = "medium"
    else:
        issue["market_potential"] = "medium"


def enrich_with_ideas(issues: list[dict]) -> list[dict]:
    """Add business opportunity and solution using Groq LLM (with template fallback)."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    if api_key:
        print(f"  Using Groq API ({GROQ_MODEL}) for contextual analysis...")
        for i, issue in enumerate(issues):
            result = call_groq(issue["title"], issue["summary"], issue["category"], api_key)
            if result:
                issue["root_cause"] = result["root_cause"]
                issue["business_opportunity"] = result["business_opportunity"]
                issue["solution"] = result["solution"]
                issue["market_potential"] = result["market_potential"]
                print(f"    [{i+1}/{len(issues)}] {issue['title'][:50]}... OK")
            else:
                enrich_with_templates(issue, i)
                print(f"    [{i+1}/{len(issues)}] {issue['title'][:50]}... (template fallback)")
            time.sleep(3)  # Rate limit: stay within Groq free tier (30 req/min)
    else:
        print("  No GROQ_API_KEY found — using template fallback...")
        for i, issue in enumerate(issues):
            enrich_with_templates(issue, i)

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

    out_path = Path(__file__).parent.parent / "data" / "issues.json"
    out_path.parent.mkdir(exist_ok=True)

    # Merge with existing data (historical accumulation)
    existing_issues = []
    if out_path.exists():
        try:
            existing_data = json.loads(out_path.read_text(encoding="utf-8"))
            existing_issues = existing_data.get("issues", [])
            print(f"  Loaded {len(existing_issues)} existing issues")
        except Exception:
            pass

    # Merge: new issues take priority (by id), keep old ones that aren't duplicates
    new_ids = {issue["id"] for issue in all_issues}
    merged = list(all_issues)
    for old_issue in existing_issues:
        if old_issue["id"] not in new_ids:
            merged.append(old_issue)

    # Cap at 500 issues, keep newest first (sort by date descending, then trim)
    merged.sort(key=lambda x: x.get("date", ""), reverse=True)
    if len(merged) > 500:
        merged = merged[:500]
        print(f"  Capped to 500 issues (removed {len(merged) - 500} oldest)")

    print(f"  Total after merge: {len(merged)} issues ({len(all_issues)} new + {len(merged) - len(all_issues)} historical)")

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "issues": merged,
    }

    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(merged)} issues to {out_path}")


if __name__ == "__main__":
    main()
