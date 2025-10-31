"""
DSPy-Powered RAG Service for Maliki Fiqh

Implements optimized RAG workflows using DSPy framework with:
- ChainOfThought reasoning
- Automatic prompt optimization
- Multi-hop retrieval
- Citation generation
"""

import os
from collections.abc import Callable, Iterator
from typing import Any

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None  # type: ignore

from loguru import logger

from .rag_service import MalikiFiqhRAG


if DSPY_AVAILABLE:
    class FiqhQASignature(dspy.Signature):
        """Signature for Fiqh Question Answering with citations."""

        context: str = dspy.InputField(desc="Relevant Maliki fiqh texts from knowledge base")
        question: str = dspy.InputField(desc="User's fiqh question in Arabic or English")
        answer: str = dspy.OutputField(desc="Detailed answer with Islamic scholarship standards")
        citations: str = dspy.OutputField(desc="Source citations from provided context")


    class FiqhChainOfThought(dspy.Module):
        """ChainOfThought RAG for Fiqh questions."""

        def __init__(self, num_passages: int = 5) -> None:
        """
        Initialize ChainOfThought RAG module.

        Args:
            num_passages: Number of context passages to retrieve
        """
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(FiqhQASignature)

    def forward(self, question: str) -> dspy.Prediction:
        """
        Process question with retrieval and generation.

        Args:
            question: User's fiqh question

        Returns:
            Prediction with answer and citations
        """
        # Retrieve relevant context
        context_passages = self.retrieve(question).passages

        # Format context
        context = "\n\n".join(
            [f"[Source {i+1}]\n{passage}" for i, passage in enumerate(context_passages)]
        )

        # Generate answer with chain of thought
        prediction = self.generate_answer(context=context, question=question)

        return prediction


class DSPyMalikiFiqhRAG:
    """DSPy-powered RAG service for Maliki fiqh."""

    def __init__(
        self,
        rag_service: MalikiFiqhRAG | None = None,
        model_name: str = "gemini/gemini-2.0-flash-exp",
        num_passages: int = 5,
    ) -> None:
        """
        Initialize DSPy RAG system.

        Args:
            rag_service: Existing Qdrant RAG service
            model_name: LiteLLM model identifier
            num_passages: Number of context passages to retrieve
        """
        self.rag = rag_service or MalikiFiqhRAG()
        self.num_passages = num_passages

        # Configure DSPy with Gemini via LiteLLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable required")

        logger.info(f"Configuring DSPy with model: {model_name}")

        # Set up LiteLLM-based language model
        self.lm = dspy.LM(
            model=model_name,
            api_key=api_key,
            temperature=0.7,
            max_tokens=2048,
        )

        dspy.settings.configure(lm=self.lm)

        # Initialize retrieval module using our Qdrant service
        self._setup_retrieval()

        # Initialize ChainOfThought module
        self.qa_module = FiqhChainOfThought(num_passages=num_passages)

        logger.info("✅ DSPy RAG system initialized")

    def _setup_retrieval(self) -> None:
        """Configure DSPy retrieval to use our existing Qdrant service."""

        class QdrantRetriever(dspy.Retrieve):
            """Custom retriever wrapping our MalikiFiqhRAG service."""

            def __init__(self, rag_service: MalikiFiqhRAG, k: int = 5):
                super().__init__(k=k)
                self.rag = rag_service

            def forward(self, query: str, k: int | None = None) -> list[str]:
                """
                Retrieve passages from Qdrant.

                Args:
                    query: Search query
                    k: Number of results (overrides default)

                Returns:
                    List of text passages
                """
                k = k or self.k
                results = self.rag.search(query, n_results=k, score_threshold=0.3)

                passages = []
                for result in results:
                    text = result.get("text", "")
                    metadata = result.get("metadata", {})

                    # Format with metadata for better context
                    formatted = f"""**{metadata.get('topic', 'Unknown')}**
Category: {metadata.get('category', 'general')}
Source: {metadata.get('source', 'Unknown')}

{text}"""
                    passages.append(formatted)

                return passages

        # Replace default retrieve with our Qdrant retriever
        dspy.settings.configure(rm=QdrantRetriever(self.rag, k=self.num_passages))

    def answer_question(
        self,
        question: str,
        return_context: bool = False,
    ) -> dict[str, Any]:
        """
        Answer a fiqh question using DSPy ChainOfThought.

        Args:
            question: User's question
            return_context: Whether to include retrieved context

        Returns:
            Dictionary with answer, citations, and optional context
        """
        try:
            logger.info(f"Processing question: {question[:100]}...")

            # Run ChainOfThought prediction
            prediction = self.qa_module(question=question)

            response = {
                "answer": prediction.answer,
                "citations": prediction.citations,
                "reasoning": getattr(prediction, "rationale", None),
            }

            if return_context:
                # Retrieve context for transparency
                context_results = self.rag.search(question, n_results=self.num_passages)
                response["context"] = context_results

            logger.info(f"✅ Generated answer with DSPy ({len(response['answer'])} chars)")
            return response

        except Exception as exc:
            logger.error(f"DSPy RAG error: {exc}")
            raise

    def stream_answer(
        self,
        question: str,
    ) -> Iterator[str]:
        """
        Stream answer generation (chunk-by-chunk).

        Args:
            question: User's question

        Yields:
            Answer chunks as they're generated
        """
        try:
            # Note: DSPy doesn't natively support streaming in ChainOfThought
            # Fall back to getting full answer then yielding in chunks
            prediction = self.qa_module(question=question)
            answer = prediction.answer

            # Yield in sentence-sized chunks for streaming effect
            sentences = answer.split(".")
            for sentence in sentences:
                if sentence.strip():
                    yield sentence.strip() + ". "

        except Exception as exc:
            logger.error(f"DSPy streaming error: {exc}")
            yield f"Error: {str(exc)}"

    def optimize_prompts(
        self,
        training_examples: list[dspy.Example],
        metric: Callable[..., float] | None = None,
    ) -> None:
        """
        Optimize prompts using DSPy's automatic optimization.

        Args:
            training_examples: List of Example(question=..., answer=...)
            metric: Evaluation metric function
        """
        try:
            logger.info(f"Optimizing with {len(training_examples)} examples...")

            # Use BootstrapFewShot optimizer
            from dspy.teleprompt import BootstrapFewShot

            optimizer = BootstrapFewShot(
                metric=metric or self._default_metric,
                max_bootstrapped_demos=4,
                max_labeled_demos=4,
            )

            # Compile the module
            self.qa_module = optimizer.compile(
                self.qa_module,
                trainset=training_examples,
            )

            logger.info("✅ Prompt optimization complete")

        except Exception as exc:
            logger.error(f"Optimization failed: {exc}")
            raise

    @staticmethod
    def _default_metric(example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
        """
        Default evaluation metric.

        Args:
            example: Ground truth example
            pred: Model prediction
            trace: Execution trace

        Returns:
            Score between 0 and 1
        """
        # Simple metric: check if answer is non-empty and citations present
        has_answer = len(pred.answer.strip()) > 20
        has_citations = len(pred.citations.strip()) > 5

        return 1.0 if (has_answer and has_citations) else 0.0


def create_training_examples() -> list[dspy.Example]:
    """
    Create training examples for prompt optimization.

    Returns:
        List of DSPy examples
    """
    examples = [
        dspy.Example(
            question="ما حكم رفع اليدين في الصلاة عند المالكية؟",
            answer="المالكية لا يرون رفع اليدين إلا عند تكبيرة الإحرام فقط، ولا يرفعونها عند الركوع ولا الرفع منه.",
        ).with_inputs("question"),
        dspy.Example(
            question="What is the ruling on combining prayers in Maliki madhab?",
            answer="Combining prayers (jam') is permitted in Maliki fiqh during travel, rain, illness, or other valid excuses. The combination can be either jam' taqdeem (praying both at the time of the first) or jam' ta'kheer (praying both at the time of the second).",
        ).with_inputs("question"),
        dspy.Example(
            question="كيف يكون السدل في الصلاة؟",
            answer="السدل هو إرسال اليدين وإسدالهما على الجنبين في الصلاة، وهو المعتمد في المذهب المالكي في الفرائض. والقبض جائز لكنه خلاف الأولى.",
        ).with_inputs("question"),
    ]

    return examples


# Singleton instance
_dspy_rag_instance: DSPyMalikiFiqhRAG | None = None


def get_dspy_rag() -> DSPyMalikiFiqhRAG:
    """
    Get or create singleton DSPy RAG instance.

    Returns:
        DSPyMalikiFiqhRAG instance

    Raises:
        ImportError: If dspy is not installed
    """
    global _dspy_rag_instance

    if not DSPY_AVAILABLE:
        raise ImportError(
            "dspy is not installed. Install it with: pip install dspy-ai"
        )

    if _dspy_rag_instance is None:
        _dspy_rag_instance = DSPyMalikiFiqhRAG()

    return _dspy_rag_instance
