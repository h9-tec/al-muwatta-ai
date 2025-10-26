#!/usr/bin/env python3
"""
Comprehensive Maliki Fiqh Scraping and RAG Population

This script:
1. Scrapes ALL Maliki fiqh websites
2. Processes the content
3. Adds everything to Qdrant vector database
4. Creates a comprehensive knowledge base
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable

from loguru import logger

from src.services.rag_service import MalikiFiqhRAG
from src.services.fiqh_scraper import MalikiFiqhScraper

DATA_DIR = Path("data")
SCRAPED_FULL_PATH = DATA_DIR / "scraped_maliki_all.json"
MALIKI_FIQHQA_FULL = DATA_DIR / "maliki_fiqhqa_full.jsonl"
ARQAN_BLOG_PATH = DATA_DIR / "maliki_arqan_blog.jsonl"


async def load_manual_maliki_content() -> List[Dict[str, Any]]:
    """Load comprehensive manually curated Maliki content."""

    content = [
        {
            "topic": "The Five Pillars in Maliki Fiqh",
            "text": """[Content from original]""",
            "category": "ibadah",
        },
        {
            "topic": "Maliki Position on Tayammum (Dry Ablution)",
            "category": "taharah",
            "text": """
# Tayammum in Maliki Fiqh

## When Tayammum is Permitted
1. Absence of water (within reasonable distance)
2. Inability to use water (sickness, extreme cold)
3. Fear of harm from using water
4. Water needed for drinking/cooking

## How to Perform Tayammum
1. **Intention (niyyah)** - for purification
2. **Strike clean earth once** with both hands
3. **Wipe the face** completely
4. **Wipe both hands** to the wrists

## Maliki Specific Rulings
- ONE strike is sufficient (not two as in other madhabs)
- Wiping to wrists (not elbows)
- Can use any clean earth, sand, or dust
- Cannot use stone, metal, or wood alone
- Must search for water if unsure of its availability

## What Invalidates Tayammum
- Finding water (must perform wudu)
- Anything that breaks wudu also breaks tayammum
- Water becomes available

**Source**: Al-Risala, Mukhtasar Khalil
            """,
        },
        {
            "topic": "Maliki Rulings on Menstruation and Post-Natal Bleeding",
            "category": "taharah",
            "text": """
# Menstruation (Hayd) and Post-Natal Bleeding (Nifas) in Maliki Fiqh

## Minimum and Maximum Duration
**Menstruation (Hayd)**:
- Minimum: 1 day and night (24 hours)
- Maximum: 15 days
- Most common: 6 or 7 days

**Post-Natal Bleeding (Nifas)**:
- No minimum
- Maximum: 60 days (Maliki position)
- Most common: 40 days

## Prohibitions During Menstruation
1. Prayer (salah) - not performed, not made up
2. Fasting - not performed, must be made up
3. Sexual intercourse - prohibited
4. Touching the Quran - Maliki view: prohibited
5. Entering mosque - generally prohibited
6. Tawaf (circumambulation) - prohibited

## When Purity Returns
- After bleeding stops AND ghusl is performed
- White discharge (qassah) indicates purity

## Istihadah (Irregular Bleeding)
- Bleeding outside normal period
- Woman continues prayers and fasting
- Performs wudu for each prayer

**Source**: Al-Risala, Maliki Fiqh Manuals
            """,
        },
        {
            "topic": "Hand Placement in Maliki Prayer (Sadl vs Qabd)",
            "category": "salah",
            "text": """
# Hand Placement (Sadl vs Qabd) in Maliki Fiqh

## Core Ruling
- **Sadl** (letting the hands hang at the sides) is the relied-upon practice in the Maliki school during obligatory prayers.
- **Qabd** (folding the hands) is *permissible* but not preferred in the Maliki madhab.

## Evidence and Rationale
1. Imam Malik narrated that the Prophet ﷺ sometimes prayed with his hands by the sides, emphasising tranquility in the posture.
2. Reports from the people of Madinah highlight sadl as a continuous practice; Malikis prioritise their transmitted actions.
3. Folding the hands is accepted if a person follows another madhab or finds it helps them focus.

## When Qabd Is Allowed
- In **nafl (supererogatory)** prayers.
- When following an imam of another madhab to avoid disagreement.
- When a worshipper finds greater concentration or has a medical need.

## Practical Advice
- Maintain khushu' and serenity whichever posture is chosen.
- Avoid labelling the alternative invalid; both are recognised in classical texts such as *al-Mudawwana* and commentaries on *al-Risala*.

**Source**: Al-Mudawwana, Sharh Khalil, commentaries on Al-Risala
            """,
        },
        {
            "topic": "Friday Prayer (Jumu'ah) in Maliki Madhab",
            "category": "salah",
            "text": """
# Jumu'ah Prayer in Maliki Fiqh

## Conditions for Obligation
1. **Male** - not obligatory on women
2. **Free** (not a slave in classical rulings)
3. **Resident** (not traveler)
4. **Healthy** and able
5. **In a city/town** with established community

## Minimum Number
- **12 Muslim males** minimum for valid Jumu'ah (Maliki position)
- Must include the Imam

## Format of Jumu'ah
1. Two khutbahs (sermons) before prayer
2. Two rak'ahs prayer (instead of 4 for Dhuhr)

## Khutbah Requirements
**Obligations**:
- Praising Allah
- Sending salutations on Prophet ﷺ
- Admonition and reminder
- Reciting a verse from Quran

**Conditions**:
- Must be in Arabic (Maliki strict position)
- While standing (if able)
- Delivered before the prayer

## If Jumu'ah is Missed
- Pray Dhuhr (4 rak'ahs) instead
- No specific makeup for Jumu'ah itself

## Maliki Unique Positions
- Ghusl before Jumu'ah is sunna muakkadah
- Should not travel on Friday after Fajr if it means missing Jumu'ah
- Khutbah must be in Arabic

**Source**: Al-Mudawwana, Al-Risala
            """,
        },
        {
            "topic": "Funeral Prayer (Salat al-Janazah) in Maliki Fiqh",
            "category": "salah",
            "text": """
# Funeral Prayer in Maliki Madhab

## Status
- **Fard Kifayah** (communal obligation)
- If some Muslims perform it, obligation lifted from others

## How to Perform
1. **Four takbirat** (saying Allahu Akbar)
2. **After 1st takbir**: Recite Al-Fatiha
3. **After 2nd takbir**: Send salutations on Prophet ﷺ
4. **After 3rd takbir**: Supplicate for the deceased
5. **After 4th takbir**: Give salam once to the right

## Maliki Specific Rulings
- Only ONE salam (to the right)
- Al-Fatiha is recited after first takbir
- No hands raising except for first takbir
- Performed standing only (no ruku or sujud)

## Supplications
**For adult Muslim**:
"Allahumma ighfir lahu warhamhu..."
(O Allah, forgive him and have mercy on him...)

**For child**:
Different supplications asking Allah to make child intercession for parents

## Where to Pray
- In open space preferred
- Can be in mosque (Maliki permits)
- Should not be in graveyard

**Source**: Al-Risala, Maliki Fiqh Manuals
            """,
        },
        {
            "topic": "Eid Prayers in Maliki Madhab",
            "category": "salah",
            "text": """
# Eid Prayers (Salat al-Eidayn) in Maliki Fiqh

## Status
- **Sunna Muakkadah** (confirmed sunnah)
- Highly recommended, some scholars say wajib

## Two Eids
1. **Eid al-Fitr** - After Ramadan
2. **Eid al-Adha** - 10th of Dhul Hijjah

## Format
**Two rak'ahs with extra takbirat**:

**First Rak'ah**:
- 7 takbirat (including opening takbir)
- Recite Al-Fatiha and Surah

**Second Rak'ah**:
- 5 takbirat (after rising from sajdah)
- Recite Al-Fatiha and Surah

## Khutbah
- Given AFTER the prayer (not before)
- Two khutbahs like Jumu'ah
- Listening is recommended but not obligatory

## Recommended Actions
- Ghusl before Eid prayer
- Wear best clothes
- Use perfume
- Go to prayer by one route, return by another
- Break fast before Eid al-Fitr prayer
- Delay eating until after Eid al-Adha prayer

## Takbirat
From Maghrib of last Ramadan day until Eid prayer starts (Eid al-Fitr)

**Source**: Al-Mudawwana, Mukhtasar Khalil
            """,
        },
        {
            "topic": "Sacrificial Animal (Udhiyah) in Maliki Fiqh",
            "category": "hajj",
            "text": """
# Udhiyah (Sacrificial Animal) in Maliki Madhab

## Status
**Sunna Muakkadah** - highly recommended
Some Maliki scholars consider it wajib for those who can afford it

## Timing
- **Days**: 10th, 11th, 12th of Dhul Hijjah
- **Time**: After Eid prayer until sunset of 12th

## Eligible Animals
1. **Sheep/Goat**: 1 animal per person
2. **Cow**: 1/7 share per person
3. **Camel**: 1/7 share per person

## Age Requirements (Maliki Position)
- **Sheep**: 1 year old
- **Goat**: 1 year old
- **Cow**: 2 years old
- **Camel**: 5 years old

## Conditions
- Must be free from defects
- Not blind, lame, sick, or emaciated
- Should be healthy and well-fed

## Distribution
**Maliki recommendation**:
- 1/3 for family
- 1/3 for relatives and friends
- 1/3 for the poor

Can eat from one's own sacrifice (Maliki permits)

## What to Avoid
- Cutting nails and hair from 1st of Dhul Hijjah if planning to sacrifice
- This is recommended, not obligatory (Maliki view)

**Source**: Al-Mudawwana, Maliki Fiqh References
            """,
        },
        {
            "topic": "Business Transactions (Muamalat) in Maliki Fiqh",
            "category": "muamalat",
            "text": """
# Business Transactions in Maliki Madhab

## General Principles
- **Mutual consent** is essential
- **Transparency** in transactions
- **No gharar** (excessive uncertainty)
- **No riba** (usury/interest)

## Valid Sale (Bay') Requirements
1. **Offer and acceptance** (ijab wa qabul)
2. **Subject matter** must be lawful and known
3. **Price** must be specified
4. **Parties** must be competent
5. **Delivery** must be possible

## Forbidden Transactions
- **Riba** (interest) in all forms
- **Gharar** (excessive uncertainty)
- **Selling what you don't own** (bay' al-ma'dum)
- **Two sales in one** (bayʿatayn fi bayʿa)

## Salam (Forward Sale)
Permitted with conditions:
- Full payment in advance
- Precise description of goods
- Specified delivery date
- Goods must be typically available

## Murabaha (Cost-Plus Financing)
- Seller discloses cost
- Adds known profit margin
- Widely used in Islamic banking

## Maliki Position on Modern Issues
- **Insurance**: Scholars differ, many consider it gharar
- **Stocks**: Permissible if company dealings are halal
- **Credit cards**: Interest-bearing ones prohibited

**Source**: Al-Mudawwana, Maliki Fiqh Economics
            """,
        },
    ]

    scraper = MalikiFiqhScraper()
    original_content = scraper.get_predefined_maliki_texts()

    return original_content + content


def _load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _normalize_external_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    text = doc.get("text") or doc.get("markdown") or ""
    metadata = {
        "topic": doc.get("title", "Maliki Fiqh Resource"),
        "madhab": "Maliki",
        "category": doc.get("category") or doc.get("tags", ["general"])[0] if doc.get("tags") else "general",
        "source": doc.get("source", "External Maliki Source"),
        "references": doc.get("references", doc.get("url", "")),
        "language": doc.get("language", "English"),
        "url": doc.get("url"),
        "tags": doc.get("tags", []),
    }
    return {"text": text, "metadata": metadata}


async def ingest_documents(rag: MalikiFiqhRAG, documents: Iterable[Dict[str, Any]]) -> int:
    added = 0
    for doc in documents:
        normalized = _normalize_external_doc(doc)
        if not normalized["text"]:
            continue
        success = rag.add_document(text=normalized["text"], metadata=normalized["metadata"])
        if success:
            added += 1
            logger.info(f"✅ Added external doc: {normalized['metadata']['topic']}")
    return added


async def main():
    print("\n" + "=" * 70)
    print("🕷️  COMPREHENSIVE MALIKI FIQH SCRAPING & RAG POPULATION")
    print("=" * 70 + "\n")

    DATA_DIR.mkdir(exist_ok=True)

    print("📚 Step 1: Loading curated Maliki fiqh content...")
    manual_content = await load_manual_maliki_content()
    print(f"✅ Loaded {len(manual_content)} curated documents\n")

    print("🔧 Step 2: Initializing Qdrant RAG system...")
    rag = MalikiFiqhRAG()
    print("✅ RAG system ready\n")

    print("📖 Step 3: Adding manual curated content...")
    manual_added = 0
    for doc in manual_content:
        try:
            success = rag.add_document(
                text=doc["text"],
                metadata={
                    "topic": doc["topic"],
                    "madhab": "Maliki",
                    "category": doc.get("category", "general"),
                    "source": doc.get("source", "Maliki Fiqh Compilation"),
                    "references": ",".join(doc.get("references", ["Al-Risala"])),
                },
            )
            if success:
                manual_added += 1
                logger.info(f"✅ Added manual doc: {doc['topic']}")
        except Exception as exc:
            logger.error(f"Failed to add {doc['topic']}: {exc}")
    print(f"\n✅ Added {manual_added} manual documents\n")

    print("📥 Step 4: Loading scraped datasets (if available)...")
    external_docs = []

    if SCRAPED_FULL_PATH.exists():
        with SCRAPED_FULL_PATH.open("r", encoding="utf-8") as stream:
            try:
                external_docs.extend(json.load(stream))
                print(f"   • Loaded {len(external_docs)} items from {SCRAPED_FULL_PATH.name}")
            except json.JSONDecodeError:
                print(f"   • Failed to parse {SCRAPED_FULL_PATH.name}")

    arqan_docs = list(_load_jsonl(ARQAN_BLOG_PATH))
    if arqan_docs:
        external_docs.extend(arqan_docs)
        print(f"   • Loaded {len(arqan_docs)} items from {ARQAN_BLOG_PATH.name}")

    fiqhqa_full_docs = list(_load_jsonl(MALIKI_FIQHQA_FULL))
    if fiqhqa_full_docs:
        external_docs.extend(fiqhqa_full_docs)
        print(f"   • Loaded {len(fiqhqa_full_docs)} items from {MALIKI_FIQHQA_FULL.name}")

    if external_docs:
        print("📦 Step 5: Ingesting external scraped content...")
        external_added = await ingest_documents(rag, external_docs)
        print(f"   ✅ Added {external_added} external documents")
    else:
        print("   • No external scraped data found.")

    print("\n📊 Step 6: Knowledge base statistics...")
    stats = rag.get_statistics()
    print(f"\n{'=' * 70}")
    print("✨ MALIKI FIQH KNOWLEDGE BASE READY!")
    print("=" * 70)
    print(f"\n📊 Statistics:")
    print(f"   • Total Documents: {stats['total_documents']}")
    print(f"   • Collection: {stats['collection_name']}")
    print(f"   • Vector DB: {stats['vector_database']}")
    print(f"   • Embedding Model: {stats['embedding_model']}")
    print(f"   • Dimensions: {stats['embedding_dimension']}")
    print(f"   • Status: {stats['status'].upper()}")

    print("\n🔍 Step 7: Sample semantic search...")
    for query in [
        "How do I perform prayer in Maliki madhab?",
        "ما حكم الجمع بين الصلاتين؟",
        "What breaks wudu in Maliki fiqh?",
        "Learn Maliki fiqh foundations",
    ]:
        results = rag.search(query, n_results=1)
        if results:
            print(f"   ✅ '{query[:40]}...' → {results[0]['metadata']['topic']}")

    print(f"\n{'=' * 70}")
    print("🚀 RESTART backend to use the enhanced knowledge base!")
    print("   Suggested: pkill -f 'uvicorn' && uvicorn src.main:app --reload")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

