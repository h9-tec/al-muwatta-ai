"""
Shafi'i Fiqh Scraper/Seeder.

Provides curated, predefined Shafi'i fiqh texts to bootstrap the knowledge base
before full scraping from primary sources is configured.
"""

from __future__ import annotations

from typing import Any


class ShafiiFiqhScraper:
    """Curated predefined texts for Shafi'i fiqh."""

    def get_predefined_texts(self) -> list[dict[str, Any]]:
        """Return a small curated set of foundational Shafi'i topics."""
        return [
            {
                "id": "shafii_pillars_1",
                "topic": "The Five Pillars in Shafi'i Fiqh",
                "madhab": "shafii",
                "category": "ibadah",
                "text": (
                    "# Five Pillars in Shafi'i Fiqh\n\n"
                    "Canonical structuring of pillars with emphasis on textual evidences\n"
                    "as treated in Al-Umm and Al-Majmu'."
                ),
                "source": "Shafi'i Fiqh Compilation",
                "references": ["Al-Umm", "Al-Majmu'", "Minhaj al-Talibin"],
            },
            {
                "id": "shafii_wudu_1",
                "topic": "Wudu (Ablution) in Shafi'i Fiqh",
                "madhab": "shafii",
                "category": "taharah",
                "text": (
                    "# Wudu in Shafi'i Fiqh\n\n"
                    "Obligations, sunnah acts, and nullifiers with clarifications\n"
                    "from Al-Majmu' and commentaries on Minhaj al-Talibin."
                ),
                "source": "Shafi'i Fiqh Compilation",
                "references": ["Al-Majmu'", "Minhaj al-Talibin"],
            },
            {
                "id": "shafii_prayer_1",
                "topic": "Prayer (Salah) Specific Rulings in Shafi'i Madhab",
                "madhab": "shafii",
                "category": "salah",
                "text": (
                    "# Prayer in Shafi'i Fiqh\n\n"
                    "Key procedural elements including takbir, hand placement, qunut,\n"
                    "and sujud al-sahw with relied-upon positions."
                ),
                "source": "Shafi'i Fiqh Compilation",
                "references": ["Al-Umm", "Al-Majmu'"],
            },
        ]
