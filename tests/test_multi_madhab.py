"""Tests for multi-madhab RAG functionality.

Tests FiqhRAG with multiple collections, search merging, and context aggregation.
"""

from __future__ import annotations

import pytest

from src.services.fiqh_rag_service import (
    MADHAB_KEYS,
    FiqhRAG,
    collection_for_madhab,
    normalize_madhab_name,
)


class TestMadhabNormalization:
    """Test madhab name normalization."""

    def test_normalize_english_names(self):
        assert normalize_madhab_name("maliki") == "maliki"
        assert normalize_madhab_name("Maliki") == "maliki"
        assert normalize_madhab_name("MALIKI") == "maliki"
        assert normalize_madhab_name("hanafi") == "hanafi"
        assert normalize_madhab_name("shafii") == "shafii"
        assert normalize_madhab_name("shafi'i") == "shafii"
        assert normalize_madhab_name("hanbali") == "hanbali"

    def test_normalize_arabic_names(self):
        assert normalize_madhab_name("مالكي") == "maliki"
        assert normalize_madhab_name("المالكي") == "maliki"
        assert normalize_madhab_name("حنفي") == "hanafi"
        assert normalize_madhab_name("الحنفي") == "hanafi"
        assert normalize_madhab_name("شافعي") == "shafii"
        assert normalize_madhab_name("الشافعي") == "shafii"
        assert normalize_madhab_name("حنبلي") == "hanbali"
        assert normalize_madhab_name("الحنبلي") == "hanbali"

    def test_normalize_invalid_names(self):
        assert normalize_madhab_name("invalid") is None
        assert normalize_madhab_name("") is None
        assert normalize_madhab_name("   ") is None


class TestCollectionMapping:
    """Test collection name generation."""

    def test_collection_for_madhab(self):
        assert collection_for_madhab("maliki") == "maliki_fiqh"
        assert collection_for_madhab("hanafi") == "hanafi_fiqh"
        assert collection_for_madhab("shafii") == "shafii_fiqh"
        assert collection_for_madhab("hanbali") == "hanbali_fiqh"

    def test_collection_for_invalid_madhab(self):
        with pytest.raises(ValueError):
            collection_for_madhab("invalid")


class TestFiqhRAG:
    """Test FiqhRAG multi-collection operations."""

    def test_initialization(self, tmp_path):
        """Test that FiqhRAG initializes and creates all collections."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        stats = rag.get_statistics()
        assert "collections" in stats
        assert len(stats["collections"]) == 4

        for key in MADHAB_KEYS:
            assert key in stats["collections"]
            assert stats["collections"][key]["collection_name"] == f"{key}_fiqh"
            assert stats["collections"][key]["status"] in ["empty", "ready"]

    def test_add_document_to_correct_collection(self, tmp_path):
        """Test that documents are added to the correct madhab collection."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        # Add a Maliki document
        success = rag.add_document(
            text="Test Maliki fiqh text about wudu.",
            metadata={
                "madhab": "maliki",
                "topic": "Wudu in Maliki School",
                "category": "taharah",
                "source": "Test",
            },
        )
        assert success is True

        # Verify it's in the collection
        stats = rag.get_statistics()
        assert stats["collections"]["maliki"]["points"] == 1
        assert stats["collections"]["hanafi"]["points"] == 0

    def test_add_document_with_arabic_madhab(self, tmp_path):
        """Test adding documents with Arabic madhab names."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        success = rag.add_document(
            text="Test text in Arabic madhab.",
            metadata={
                "madhab": "حنفي",
                "topic": "Test Topic",
                "category": "general",
                "source": "Test",
            },
        )
        assert success is True

        stats = rag.get_statistics()
        assert stats["collections"]["hanafi"]["points"] == 1

    def test_search_single_madhab(self, tmp_path):
        """Test searching within a single madhab collection."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        # Add documents to different collections
        rag.add_document(
            text="Maliki ruling on hand placement during prayer is sadl (arms at sides).",
            metadata={"madhab": "maliki", "topic": "Prayer", "category": "salah", "source": "Test"},
        )
        rag.add_document(
            text="Hanafi ruling on hand placement during prayer is qabd (folded on chest).",
            metadata={"madhab": "hanafi", "topic": "Prayer", "category": "salah", "source": "Test"},
        )

        # Search only Maliki
        results = rag.search("hand placement in prayer", n_results=5, madhabs=["maliki"])

        assert len(results) <= 5
        for r in results:
            assert r["metadata"]["madhab"] == "maliki"

    def test_search_multiple_madhabs(self, tmp_path):
        """Test searching across multiple madhab collections."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        # Add documents to multiple collections
        for madhab_name in ["maliki", "hanafi", "shafii"]:
            rag.add_document(
                text=f"{madhab_name.capitalize()} position on fasting rules.",
                metadata={
                    "madhab": madhab_name,
                    "topic": "Fasting",
                    "category": "sawm",
                    "source": "Test",
                },
            )

        # Search across all three
        results = rag.search("fasting", n_results=10, madhabs=["maliki", "hanafi", "shafii"])

        # Should get results from multiple schools
        madhabs_in_results = {r["metadata"]["madhab"] for r in results}
        assert len(madhabs_in_results) >= 2  # At least two schools

    def test_search_defaults_to_all_madhabs(self, tmp_path):
        """Test that search defaults to all four madhabs when none specified."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        for madhab_name in MADHAB_KEYS:
            rag.add_document(
                text=f"{madhab_name.capitalize()} position on zakat.",
                metadata={
                    "madhab": madhab_name,
                    "topic": "Zakat",
                    "category": "zakat",
                    "source": "Test",
                },
            )

        # Search without specifying madhabs (should search all)
        results = rag.search("zakat", n_results=10)

        # Should potentially get results from multiple schools
        assert len(results) > 0

    def test_get_relevant_context_single_madhab(self, tmp_path):
        """Test context generation for single madhab."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        rag.add_document(
            text="Detailed Shafi'i ruling on purification and cleanliness.",
            metadata={
                "madhab": "shafii",
                "topic": "Purification",
                "category": "taharah",
                "source": "Test Source",
                "references": "Al-Majmu'",
            },
        )

        context = rag.get_relevant_context("purification", madhabs=["shafii"])
        assert "Purification" in context
        assert "shafii" in context.lower()

    def test_get_relevant_context_multi_madhab(self, tmp_path):
        """Test context generation across multiple madhabs."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        for madhab_name in ["maliki", "hanbali"]:
            rag.add_document(
                text=f"{madhab_name.capitalize()} view on combining prayers during travel.",
                metadata={
                    "madhab": madhab_name,
                    "topic": "Combining Prayers",
                    "category": "salah",
                    "source": "Test",
                    "references": "Classical Manual",
                },
            )

        context = rag.get_relevant_context("combining prayers", madhabs=["maliki", "hanbali"])

        # Should contain references to both schools
        assert context != ""
        # Context should be reasonably formatted
        assert "**[Source" in context


class TestMultiMadhabIntegration:
    """Integration tests for multi-madhab workflows."""

    def test_add_and_search_workflow(self, tmp_path):
        """Test complete add and search workflow across schools."""
        rag = FiqhRAG(persist_directory=str(tmp_path / "test_qdrant"))

        # Add sample documents for each school
        test_docs = [
            ("maliki", "Maliki position on wiping over socks is permissible."),
            ("hanafi", "Hanafi position on wiping over socks is permissible with conditions."),
            ("shafii", "Shafi'i position on wiping over socks has specific conditions."),
            ("hanbali", "Hanbali position on wiping over socks is similar to Hanafi."),
        ]

        for madhab, text in test_docs:
            success = rag.add_document(
                text=text,
                metadata={
                    "madhab": madhab,
                    "topic": f"{madhab.capitalize()} Wiping Socks",
                    "category": "taharah",
                    "source": "Test Manual",
                },
            )
            assert success is True

        # Search across all schools
        all_results = rag.search("wiping socks", n_results=10)
        assert len(all_results) == 4

        # Search only Maliki and Hanafi
        filtered_results = rag.search("wiping socks", n_results=10, madhabs=["maliki", "hanafi"])
        madhabs_found = {r["metadata"]["madhab"] for r in filtered_results}
        assert madhabs_found <= {"maliki", "hanafi"}  # Only these two or subset

