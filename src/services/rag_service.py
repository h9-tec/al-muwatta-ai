"""
RAG (Retrieval Augmented Generation) Service for Maliki Fiqh using Qdrant.

This service implements vector search and retrieval for Islamic jurisprudence
using Qdrant and sentence transformers.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from loguru import logger
import uuid

from .fiqh_scraper import MalikiFiqhScraper


class MalikiFiqhRAG:
    """RAG system for Maliki fiqh knowledge base using Qdrant."""

    def __init__(
        self,
        persist_directory: str = "./qdrant_db",
        collection_name: str = "maliki_fiqh",
    ) -> None:
        """
        Initialize the RAG system with Qdrant.

        Args:
            persist_directory: Directory to persist Qdrant database
            collection_name: Name of the Qdrant collection
        """
        try:
            # Initialize Qdrant client (local mode)
            self.client = QdrantClient(path=persist_directory)

            # Initialize small multilingual embedding model
            logger.info("Loading multilingual embedding model...")
            # paraphrase-multilingual-MiniLM-L12-v2 - small, fast, supports 50+ languages including Arabic
            self.embedding_model = SentenceTransformer(
                'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            )
            self.embedding_dim = 384  # Dimension for this model
            logger.info("✅ Embedding model loaded (384 dimensions, multilingual)")

            self.collection_name = collection_name

            # Create collection if it doesn't exist
            try:
                self.client.get_collection(collection_name)
                logger.info(f"Collection '{collection_name}' already exists")
            except Exception:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"✅ Created collection: {collection_name}")

            logger.info(f"RAG system initialized with Qdrant")

        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise

    async def initialize_knowledge_base(self, force_reload: bool = False) -> None:
        """
        Initialize the knowledge base with Maliki fiqh texts.

        Args:
            force_reload: Whether to reload even if data exists
        """
        try:
            # Check if already populated
            collection_info = self.client.get_collection(self.collection_name)
            current_count = collection_info.points_count

            if current_count > 0 and not force_reload:
                logger.info(f"Knowledge base already has {current_count} documents")
                return

            logger.info("Initializing Maliki fiqh knowledge base...")

            # Get predefined texts
            scraper = MalikiFiqhScraper()
            fiqh_texts = scraper.get_predefined_maliki_texts()

            # Prepare points for Qdrant
            points = []

            for text_data in fiqh_texts:
                # Generate embedding
                embedding = self.embedding_model.encode(
                    text_data["text"],
                    convert_to_numpy=True,
                ).tolist()

                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": text_data["text"],
                        "topic": text_data["topic"],
                        "madhab": text_data["madhab"],
                        "category": text_data["category"],
                        "source": text_data["source"],
                        "references": ",".join(text_data.get("references", [])),
                    },
                )
                points.append(point)

                logger.info(f"✅ Processed: {text_data['topic']}")

            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(f"✅ Knowledge base initialized with {len(points)} documents")

        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 3,
        category_filter: Optional[str] = None,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search the Maliki fiqh knowledge base using semantic search.

        Args:
            query: Search query (Arabic or English)
            n_results: Number of results to return
            category_filter: Filter by category (e.g., 'salah', 'zakat')
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of relevant fiqh documents with scores

        Example:
            >>> rag = MalikiFiqhRAG()
            >>> results = rag.search("What is the ruling on raising hands in prayer?")
            >>> for result in results:
            ...     print(result['payload']['topic'])
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                query,
                convert_to_numpy=True,
            ).tolist()

            # Build filter
            query_filter = None
            if category_filter:
                query_filter = {
                    "must": [
                        {
                            "key": "category",
                            "match": {"value": category_filter}
                        }
                    ]
                }

            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "text": result.payload.get("text", ""),
                    "metadata": {
                        "topic": result.payload.get("topic", ""),
                        "category": result.payload.get("category", ""),
                        "source": result.payload.get("source", ""),
                        "references": result.payload.get("references", ""),
                    },
                    "score": result.score,
                    "id": result.id,
                })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    def get_relevant_context(
        self,
        query: str,
        max_context_length: int = 2000,
    ) -> str:
        """
        Get relevant context for RAG-enhanced generation.

        Args:
            query: User query
            max_context_length: Maximum characters of context

        Returns:
            Concatenated relevant context with citations
        """
        results = self.search(query, n_results=3, score_threshold=0.3)

        if not results:
            return ""

        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            text = result['text']
            metadata = result['metadata']
            score = result.get('score', 0)

            # Format with source citation
            formatted = f"""
---
**[Source {i}]** {metadata.get('topic', 'Unknown')}
**Category**: {metadata.get('category', 'General')} | **Relevance**: {score:.2f}
**References**: {metadata.get('references', 'Maliki Fiqh')}

{text.strip()}
---
"""

            if current_length + len(formatted) > max_context_length:
                break

            context_parts.append(formatted)
            current_length += len(formatted)

        return "\n".join(context_parts)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.

        Returns:
            Statistics about the knowledge base
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)

            return {
                "total_documents": collection_info.points_count,
                "collection_name": self.collection_name,
                "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
                "embedding_dimension": self.embedding_dim,
                "vector_database": "Qdrant",
                "status": "ready" if collection_info.points_count > 0 else "empty",
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"status": "error", "error": str(e)}

    def add_document(
        self,
        text: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Add a single document to the knowledge base.

        Args:
            text: Document text
            metadata: Document metadata

        Returns:
            True if successful
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(
                text,
                convert_to_numpy=True,
            ).tolist()

            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    **metadata,
                },
            )

            # Add to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.info(f"✅ Added document: {metadata.get('topic', 'Unknown')}")
            return True

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
