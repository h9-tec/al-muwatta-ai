"""
Generic multi-madhab RAG (Retrieval Augmented Generation) service.

This service manages separate Qdrant collections per madhab (Maliki, Hanafi,
Shafi'i, Hanbali) while exposing a single API to search across one or more
schools and to build aggregated context for prompting.

Design goals:
- Single multilingual embedding model (384-dim) for comparability across collections
- Stable, deterministic merging across multiple collections
- Backward-compatible payload fields used throughout the app
"""

from __future__ import annotations

import unicodedata
import uuid
from collections.abc import Iterable
from typing import Any

from loguru import logger
from ..config import settings

# Optional heavy dependencies. Provide lightweight fallbacks for CI/tests.
try:  # pragma: no cover - import path
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.models import Distance, PointStruct, VectorParams  # type: ignore
except Exception:  # pragma: no cover - fallback used in minimal CI
    from types import SimpleNamespace
    from math import sqrt
    from collections import defaultdict

    class PointStruct(SimpleNamespace):  # type: ignore[no-redef]
        pass

    class VectorParams(SimpleNamespace):  # type: ignore[no-redef]
        pass

    class _CollectionInfo(SimpleNamespace):
        points_count: int = 0

    def _cosine(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        # Handle different lengths gracefully
        length = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(length))
        na = sqrt(sum(x * x for x in a[:length])) or 1.0
        nb = sqrt(sum(x * x for x in b[:length])) or 1.0
        return dot / (na * nb)

    class QdrantClient:  # type: ignore[no-redef]
        def __init__(self, path: str | None = None):
            self._collections: dict[str, list[PointStruct]] = defaultdict(list)

        def get_collection(self, collection_name: str) -> _CollectionInfo:
            return _CollectionInfo(points_count=len(self._collections.get(collection_name, [])))

        def create_collection(self, collection_name: str, vectors_config: VectorParams | None = None) -> None:
            self._collections.setdefault(collection_name, [])

        def upsert(self, collection_name: str, points: list[PointStruct]) -> None:
            self._collections.setdefault(collection_name, []).extend(points)

        def search(
            self,
            collection_name: str,
            query_vector: list[float],
            limit: int = 3,
            query_filter: dict | None = None,
            score_threshold: float = 0.0,
        ) -> list[SimpleNamespace]:
            items = self._collections.get(collection_name, [])
            results: list[SimpleNamespace] = []
            for p in items:
                payload = getattr(p, "payload", {})
                if query_filter:
                    try:
                        must = query_filter.get("must", [])
                        ok = True
                        for cond in must:
                            key = cond.get("key")
                            val = cond.get("match", {}).get("value")
                            if payload.get(key) != val:
                                ok = False
                                break
                        if not ok:
                            continue
                    except Exception:
                        pass
                score = _cosine(query_vector, getattr(p, "vector", []))
                if score >= score_threshold:
                    results.append(SimpleNamespace(id=p.id, payload=p.payload, score=score))
            # Highest score first
            results.sort(key=lambda r: (float(getattr(r, "score", 0.0) or 0.0), str(getattr(r, "id", ""))), reverse=True)
            return results[:limit]

    class Distance:  # type: ignore[no-redef]
        COSINE = "COSINE"

try:  # pragma: no cover
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - lightweight embedder
    class SentenceTransformer:  # type: ignore[no-redef]
        """Very small fallback embedder for CI: character 3-gram hashing.

        Produces deterministic vectors without heavy dependencies.
        """

        def __init__(self, _model_name: str) -> None:
            # Use a fixed dimensionality to keep stats stable
            self.embedding_dim: int = 256

        def encode(self, text: str, convert_to_numpy: bool = False) -> list[float]:
            text = (text or "").lower()
            dim = self.embedding_dim
            vec = [0.0] * dim
            for i in range(len(text) - 2):
                tri = text[i : i + 3]
                h = hash(tri) % dim
                vec[h] += 1.0
            # L2 normalize for cosine
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            return [x / norm for x in vec]

MADHAB_KEYS: tuple[str, ...] = ("maliki", "hanafi", "shafii", "hanbali")


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics/marks for normalization in embeddings.

    This function is intentionally light; we keep the original text in payload
    for display while optionally using normalized text in embeddings if needed.
    """
    if not text:
        return text
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_madhab_name(name: str) -> str | None:
    """Normalize various inputs (English/Arabic/Case) to canonical madhab key.

    Accepted inputs include English and Arabic names:
      - "maliki", "مالكي" → "maliki"
      - "hanafi", "حنفي" → "hanafi"
      - "shafii", "shafi'i", "شافعي" → "shafii"
      - "hanbali", "حنبلي" → "hanbali"
    """
    if not name:
        return None
    n = name.strip().lower()
    # English variants
    if n in {"maliki", "maliky"}:
        return "maliki"
    if n in {"hanafi", "hanafy"}:
        return "hanafi"
    if n in {"shafii", "shafi", "shafi'i", "shafei", "shafe'i"}:
        return "shafii"
    if n in {"hanbali", "hanbaly"}:
        return "hanbali"
    # Arabic variants
    if n in {"مالكي", "المالكي"}:
        return "maliki"
    if n in {"حنفي", "الحنفي"}:
        return "hanafi"
    if n in {"شافعي", "الشافعي"}:
        return "shafii"
    if n in {"حنبلي", "الحنبلي"}:
        return "hanbali"
    return None


def collection_for_madhab(madhab_key: str) -> str:
    """Map canonical madhab key to its Qdrant collection name."""
    if madhab_key not in MADHAB_KEYS:
        raise ValueError(f"Unsupported madhab key: {madhab_key}")
    return f"{madhab_key}_fiqh"


class FiqhRAG:
    """Generic multi-collection RAG over the four Sunni madhabs.

    Methods are synchronous where I/O is CPU-bound or qdrant-client is sync.
    """

    def __init__(
        self,
        persist_directory: str = "./qdrant_db",
        embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        create_all_collections: bool = True,
    ) -> None:
        """Initialize Qdrant client and embedding model.

        Args:
            persist_directory: Local Qdrant path
            embedding_model_name: Sentence-Transformers model name
            create_all_collections: Ensure all four collections exist
        """
        try:
            # Prefer external Qdrant server if configured
            if getattr(settings, "qdrant_url", None):
                logger.info(f"Connecting to Qdrant server at {settings.qdrant_url}")
                self.client = QdrantClient(url=settings.qdrant_url)
            else:
                logger.info(f"Using embedded Qdrant at path {persist_directory}")
                self.client = QdrantClient(path=persist_directory)

            logger.info("Loading multilingual embedding model for FiqhRAG...")
            self.embedding_model = SentenceTransformer(embedding_model_name)
            # Use model-provided dimension if available; default to 384
            self.embedding_dim = getattr(self.embedding_model, "embedding_dim", 384)

            if create_all_collections:
                for key in MADHAB_KEYS:
                    self._ensure_collection(collection_for_madhab(key))

            logger.info("✅ FiqhRAG ready (collections ensured, embeddings loaded)")
        except Exception as exc:
            logger.error(f"Failed to initialize FiqhRAG: {exc}")
            raise

    # ---------------------------
    # Collection/Schema utilities
    # ---------------------------
    def _ensure_collection(self, collection_name: str) -> None:
        try:
            self.client.get_collection(collection_name)
            logger.debug(f"Collection '{collection_name}' exists")
        except Exception:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
            logger.info(f"✅ Created collection: {collection_name}")

    # ---------------------------
    # Ingestion
    # ---------------------------
    def add_document(self, text: str, metadata: dict[str, Any]) -> bool:
        """Add a document to the appropriate madhab collection.

        Required metadata keys: 'madhab'. Optional (recommended):
        'topic', 'category', 'source', 'references', 'book_title', 'author',
        'page', 'chunk_index'.
        """
        try:
            madhab_raw = metadata.get("madhab")
            madhab_key = normalize_madhab_name(str(madhab_raw)) if madhab_raw else None
            if not madhab_key:
                raise ValueError("metadata['madhab'] must be one of maliki/hanafi/shafii/hanbali")

            collection_name = collection_for_madhab(madhab_key)
            self._ensure_collection(collection_name)

            # Embed (using original text; diacritics removal optional)
            vector = self.embedding_model.encode(text, convert_to_numpy=True).tolist()

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": text,
                    **metadata,
                    "madhab": madhab_key,  # canonicalize
                },
            )

            self.client.upsert(collection_name=collection_name, points=[point])
            logger.info(
                f"✅ Added document to {collection_name}: {metadata.get('topic', 'Unknown')}"
            )
            return True
        except Exception as exc:
            logger.error(f"Error adding document: {exc}")
            return False

    # ---------------------------
    # Search
    # ---------------------------
    def search(
        self,
        query: str,
        n_results: int = 3,
        madhabs: Iterable[str] | None = None,
        category_filter: str | None = None,
        score_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Search across one or more madhab collections and merge results.

        Args:
            query: Search text (Arabic/English)
            n_results: Total results to return globally
            madhabs: Iterable of school names; default: all four
            category_filter: Optional category payload filter
            score_threshold: Minimum similarity score (0..1)
        """
        try:
            if not query.strip():
                return []

            # Normalize selected madhabs (default all)
            selected = [normalize_madhab_name(m) for m in (madhabs or MADHAB_KEYS)]
            selected = [m for m in selected if m]
            if not selected:
                selected = list(MADHAB_KEYS)

            # Single query embedding reused across collections
            q_vec = self.embedding_model.encode(query, convert_to_numpy=True).tolist()

            # Optional filter
            query_filter = None
            if category_filter:
                query_filter = {"must": [{"key": "category", "match": {"value": category_filter}}]}

            per_collection_results: list[tuple[str, Any]] = []
            for key in selected:
                cname = collection_for_madhab(key)
                try:
                    results = self.client.search(
                        collection_name=cname,
                        query_vector=q_vec,
                        limit=n_results,  # fetch up to n per collection, merge later
                        query_filter=query_filter,
                        score_threshold=score_threshold,
                    )
                    for r in results:
                        per_collection_results.append((key, r))
                except Exception as exc:
                    logger.warning(f"Search failed for {cname}: {exc}")
                    continue

            # Merge globally by score desc; stable tiebreak by (madhab, id)
            merged: list[dict[str, Any]] = []
            per_collection_results.sort(
                key=lambda t: (
                    float(getattr(t[1], "score", 0.0) or 0.0),
                    t[0],
                    str(getattr(t[1], "id", "")),
                ),
                reverse=True,
            )

            for key, r in per_collection_results[:n_results]:
                payload = r.payload or {}
                merged.append(
                    {
                        "text": payload.get("text", ""),
                        "metadata": {
                            "topic": payload.get("topic", ""),
                            "category": payload.get("category", ""),
                            "source": payload.get("source", ""),
                            "references": payload.get("references", ""),
                            "madhab": key,
                            "book_title": payload.get("book_title", ""),
                            "author": payload.get("author", ""),
                            "page": payload.get("page"),
                            "chunk_index": payload.get("chunk_index"),
                        },
                        "score": float(getattr(r, "score", 0.0) or 0.0),
                        "id": str(getattr(r, "id", "")),
                    }
                )

            logger.info(
                "Merged {} results across {} collections for query: {}...",
                len(merged),
                len(selected),
                query[:60],
            )
            return merged
        except Exception as exc:
            logger.error(f"Error during multi-collection search: {exc}")
            return []

    def get_relevant_context(
        self,
        query: str,
        max_context_length: int = 2000,
        madhabs: Iterable[str] | None = None,
    ) -> str:
        """Build formatted, citation-ready context across selected madhabs."""
        results = self.search(query, n_results=5, madhabs=madhabs, score_threshold=0.3)
        if not results:
            return ""

        parts: list[str] = []
        total_len = 0
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            formatted = (
                f"---\n"
                f"**[Source {i}]** {meta.get('topic', 'Unknown')}\n"
                f"**Madhab**: {meta.get('madhab', '')} | **Category**: {meta.get('category', 'General')} | "
                f"**Relevance**: {r.get('score', 0.0):.2f}\n"
                f"**References**: {meta.get('references', '')}\n\n"
                f"{(r.get('text') or '').strip()}\n"
                f"---\n"
            )
            if total_len + len(formatted) > max_context_length:
                break
            parts.append(formatted)
            total_len += len(formatted)

        return "\n".join(parts)

    # ---------------------------
    # Monitoring/Stats
    # ---------------------------
    def get_statistics(self) -> dict[str, Any]:
        """Return per-collection document counts and model metadata."""
        stats: dict[str, Any] = {
            "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
            "embedding_dimension": self.embedding_dim,
            "vector_database": "Qdrant",
            "collections": {},
        }
        for key in MADHAB_KEYS:
            cname = collection_for_madhab(key)
            try:
                info = self.client.get_collection(cname)
                stats["collections"][key] = {
                    "collection_name": cname,
                    "points": info.points_count,
                    "status": "ready" if info.points_count > 0 else "empty",
                }
            except Exception as exc:
                logger.warning(f"Failed to read stats for {cname}: {exc}")
                stats["collections"][key] = {
                    "collection_name": cname,
                    "points": 0,
                    "status": "unavailable",
                }
        return stats


# Singleton convenience (optional)
_fiqh_rag_singleton: FiqhRAG | None = None


def get_fiqh_rag() -> FiqhRAG:
    global _fiqh_rag_singleton
    if _fiqh_rag_singleton is None:
        _fiqh_rag_singleton = FiqhRAG()
    return _fiqh_rag_singleton
