"""
Hanafi Fiqh Scraper/Seeder.

Provides curated, predefined Hanafi fiqh texts to bootstrap the knowledge base
before full scraping from primary sources is configured.
"""

from __future__ import annotations

from typing import Any, Dict, List


class HanafiFiqhScraper:
    """Curated predefined texts for Hanafi fiqh."""

    def get_predefined_texts(self) -> List[Dict[str, Any]]:
        """Return a small curated set of foundational Hanafi topics.

        The intent is to seed the vector store; expand with proper scraping next.
        """
        return [
            {
                "id": "hanafi_pillars_1",
                "topic": "The Five Pillars in Hanafi Fiqh",
                "madhab": "hanafi",
                "category": "ibadah",
                "text": (
                    "# Five Pillars in Hanafi Fiqh\n\n"
                    "General Hanafi framing of obligations and recommended acts across\n"
                    "the pillars, with standard evidences from Quran and Sunnah.\n"
                    "This entry acts as a neutral seed; detailed rulings should be\n"
                    "sourced from primary Hanafi texts like Al-Hidaya and Bada'i."
                ),
                "source": "Hanafi Fiqh Compilation",
                "references": ["Al-Hidaya", "Bada'i al-Sana'i", "Radd al-Muhtar"],
            },
            {
                "id": "hanafi_wudu_1",
                "topic": "Wudu (Ablution) in Hanafi Fiqh",
                "madhab": "hanafi",
                "category": "taharah",
                "text": (
                    "# Wudu in Hanafi Fiqh\n\n"
                    "Obligations and recommended acts of wudu per the Hanafi school,\n"
                    "including canonical pillars, nullifiers, and notable positions\n"
                    "documented in the classical manuals."
                ),
                "source": "Hanafi Fiqh Compilation",
                "references": ["Al-Hidaya", "Bada'i al-Sana'i"],
            },
            {
                "id": "hanafi_prayer_1",
                "topic": "Prayer (Salah) Specific Rulings in Hanafi Madhab",
                "madhab": "hanafi",
                "category": "salah",
                "text": (
                    "# Prayer in Hanafi Fiqh\n\n"
                    "Overview of opening takbir, hand placement, qunut practices, and\n"
                    "sujud al-sahw rules per Hanafi manuals."
                ),
                "source": "Hanafi Fiqh Compilation",
                "references": ["Al-Hidaya", "Radd al-Muhtar"],
            },
        ]


