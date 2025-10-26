"""
OCR Service using DeepSeek-OCR for extracting text from Islamic books.

This service allows users to upload book images/PDFs and extract text
to add to the Maliki fiqh knowledge base.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import base64
from loguru import logger
from PIL import Image
import io

# Note: DeepSeek-OCR requires transformers and torch
# For production, you would load the model here:
# from transformers import AutoModel, AutoTokenizer


class OCRService:
    """Service for OCR processing of Islamic book images."""

    def __init__(self, use_deepseek: bool = False) -> None:
        """
        Initialize OCR service.

        Args:
            use_deepseek: Whether to use DeepSeek-OCR (requires GPU)
        """
        self.use_deepseek = use_deepseek
        self.model = None
        self.tokenizer = None

        if use_deepseek:
            try:
                logger.info("Loading DeepSeek-OCR model (this requires GPU)...")
                # Uncomment when GPU is available:
                # from transformers import AutoModel, AutoTokenizer
                # self.tokenizer = AutoTokenizer.from_pretrained(
                #     'deepseek-ai/DeepSeek-OCR',
                #     trust_remote_code=True
                # )
                # self.model = AutoModel.from_pretrained(
                #     'deepseek-ai/DeepSeek-OCR',
                #     trust_remote_code=True,
                #     use_safetensors=True
                # ).eval()
                logger.warning("DeepSeek-OCR requires GPU - using fallback OCR")
            except Exception as e:
                logger.error(f"Failed to load DeepSeek-OCR: {e}")
                self.use_deepseek = False

    async def extract_text_from_image(
        self,
        image_path: str,
        language: str = "arabic",
    ) -> Optional[str]:
        """
        Extract text from an image using OCR.

        Args:
            image_path: Path to the image file
            language: Primary language (for OCR optimization)

        Returns:
            Extracted text or None if failed

        Example:
            >>> ocr = OCRService()
            >>> text = await ocr.extract_text_from_image("book_page.jpg", "arabic")
            >>> print(text)
        """
        try:
            # Open and validate image
            image = Image.open(image_path)
            logger.info(f"Processing image: {image_path} ({image.size})")

            if self.use_deepseek and self.model:
                # Use DeepSeek-OCR for high-quality extraction
                return await self._extract_with_deepseek(image)
            else:
                # Use fallback OCR (Tesseract or cloud OCR)
                return await self._extract_with_fallback(image, language)

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return None

    async def _extract_with_deepseek(self, image: Image.Image) -> Optional[str]:
        """
        Extract text using DeepSeek-OCR model.

        Args:
            image: PIL Image object

        Returns:
            Extracted markdown text
        """
        try:
            # DeepSeek-OCR usage (requires GPU)
            prompt = "<image>\n<|grounding|>Convert the document to markdown."

            # Save image temporarily
            temp_path = "/tmp/ocr_temp.jpg"
            image.save(temp_path)

            # Inference (placeholder - requires actual model)
            # result = self.model.infer(
            #     self.tokenizer,
            #     prompt=prompt,
            #     image_file=temp_path,
            #     base_size=1024,
            #     image_size=640,
            #     crop_mode=True,
            # )
            # return result

            logger.warning("DeepSeek-OCR model not loaded (GPU required)")
            return await self._extract_with_fallback(image, "arabic")

        except Exception as e:
            logger.error(f"DeepSeek-OCR extraction failed: {e}")
            return None

    async def _extract_with_fallback(
        self,
        image: Image.Image,
        language: str = "arabic",
    ) -> Optional[str]:
        """
        Fallback OCR using Tesseract or cloud service.

        Args:
            image: PIL Image object
            language: Language for OCR

        Returns:
            Extracted text
        """
        try:
            # Placeholder for fallback OCR
            # You can use:
            # 1. Tesseract OCR (pytesseract)
            # 2. Google Cloud Vision API
            # 3. Azure Computer Vision
            # 4. AWS Textract

            logger.info("Using fallback OCR (manual text extraction recommended)")
            
            return """
[OCR Placeholder]

To enable automatic OCR:
1. Install pytesseract: pip install pytesseract
2. Install Tesseract-OCR with Arabic support
3. Or use DeepSeek-OCR with GPU

For now, please manually paste the text from your book.
"""

        except Exception as e:
            logger.error(f"Fallback OCR failed: {e}")
            return None

    async def process_pdf(
        self,
        pdf_path: str,
        max_pages: int = 50,
    ) -> Dict[str, Any]:
        """
        Process a PDF file and extract text.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process

        Returns:
            Dictionary with extracted text per page
        """
        try:
            import pdfplumber

            logger.info(f"Processing PDF: {pdf_path}")
            extracted_pages = []

            with pdfplumber.open(pdf_path) as pdf:
                total_pages = min(len(pdf.pages), max_pages)

                for i, page in enumerate(pdf.pages[:total_pages]):
                    text = page.extract_text()
                    if text:
                        extracted_pages.append({
                            "page_number": i + 1,
                            "text": text,
                            "word_count": len(text.split()),
                        })

                logger.info(f"✅ Extracted text from {len(extracted_pages)} pages")

            return {
                "total_pages": len(extracted_pages),
                "pages": extracted_pages,
                "full_text": "\n\n".join([p["text"] for p in extracted_pages]),
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {"error": str(e), "pages": []}

