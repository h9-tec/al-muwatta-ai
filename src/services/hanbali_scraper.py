"""
Hanbali Fiqh Scraper/Seeder.

Provides curated, predefined Hanbali fiqh texts to bootstrap the knowledge base
before full scraping from primary sources is configured.
"""

from __future__ import annotations

from typing import Any, Dict, List


class HanbaliFiqhScraper:
    """Curated predefined texts for Hanbali fiqh."""

    def get_predefined_texts(self) -> List[Dict[str, Any]]:
        """Return a small curated set of foundational Hanbali topics."""
        return [
            {
                "id": "hanbali_pillars_1",
                "topic": "The Five Pillars in Hanbali Fiqh",
                "madhab": "hanbali",
                "category": "ibadah",
                "text": (
                    "# Five Pillars in Hanbali Fiqh\n\n"
                    "High-level coverage referencing Al-Mughni and Al-Insaf as relied-\n"
                    "upon sources; detailed rulings to be expanded with full ingestion."
                ),
                "source": "Hanbali Fiqh Compilation",
                "references": ["Al-Mughni", "Al-Insaf", "Zad al-Mustaqni'"]
            },
            {
                "id": "hanbali_wudu_1",
                "topic": "Wudu (Ablution) in Hanbali Fiqh",
                "madhab": "hanbali",
                "category": "taharah",
                "text": (
                    "# Wudu in Hanbali Fiqh\n\n"
                    "Core obligations and recommended acts as treated by the Hanbali\n"
                    "jurists; includes standard nullifiers and notable positions."
                ),
                "source": "Hanbali Fiqh Compilation",
                "references": ["Zad al-Mustaqni'", "Al-Mughni"],
            },
            {
                "id": "hanbali_prayer_1",
                "topic": "Prayer (Salah) Specific Rulings in Hanbali Madhab",
                "madhab": "hanbali",
                "category": "salah",
                "text": (
                    "# Prayer in Hanbali Fiqh\n\n"
                    "Overview of procedural rulings (takbir, qunut, sujud al-sahw)\n"
                    "with references to relied-upon Hanbali manuals."
                ),
                "source": "Hanbali Fiqh Compilation",
                "references": ["Al-Insaf", "Zad al-Mustaqni'"]
            },
        ]


