"""
File Upload Router for adding books to knowledge base.

This router handles image and PDF uploads for OCR processing and
adding to the Maliki fiqh RAG system.
"""

from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from loguru import logger
from pathlib import Path
import shutil

from ..services.ocr_service import OCRService
from ..services.rag_service import MalikiFiqhRAG

router = APIRouter(prefix="/api/v1/upload", tags=["Upload & OCR"])

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/book-image", summary="Upload book image for OCR")
async def upload_book_image(
    file: UploadFile = File(..., description="Book image (JPG, PNG)"),
    title: str = Form(..., description="Book/section title"),
    category: str = Form("general", description="Category (salah, zakat, etc.)"),
    add_to_knowledge_base: bool = Form(True, description="Add to RAG"),
) -> Dict[str, Any]:
    """
    Upload a book image, extract text using OCR, and optionally add to knowledge base.

    Args:
        file: Image file (JPG, PNG, JPEG)
        title: Title of the book or section
        category: Fiqh category
        add_to_knowledge_base: Whether to add extracted text to RAG

    Returns:
        Extracted text and processing status
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only image files are supported (JPG, PNG)"
            )

        # Save uploaded file
        file_path = UPLOAD_DIR / f"{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"📄 Uploaded file saved: {file.filename}")

        # Extract text using OCR
        ocr_service = OCRService(use_deepseek=False)  # Set to True if GPU available
        extracted_text = await ocr_service.extract_text_from_image(
            str(file_path),
            language="arabic",
        )

        if not extracted_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract text from image"
            )

        # Add to knowledge base if requested
        added_to_rag = False
        if add_to_knowledge_base:
            try:
                rag = MalikiFiqhRAG()
                success = rag.add_document(
                    text=extracted_text,
                    metadata={
                        "topic": title,
                        "madhab": "Maliki",
                        "category": category,
                        "source": f"User upload: {file.filename}",
                        "references": "User contributed",
                    },
                )
                added_to_rag = success
                logger.info(f"✅ Added to knowledge base: {title}")
            except Exception as e:
                logger.error(f"Failed to add to RAG: {e}")

        return {
            "status": "success",
            "filename": file.filename,
            "title": title,
            "extracted_text": extracted_text,
            "text_length": len(extracted_text),
            "word_count": len(extracted_text.split()),
            "added_to_knowledge_base": added_to_rag,
            "message": "Text extracted successfully! " + (
                "Added to knowledge base." if added_to_rag else "Not added to knowledge base."
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book-pdf", summary="Upload PDF book for extraction")
async def upload_book_pdf(
    file: UploadFile = File(..., description="PDF file"),
    title: str = Form(..., description="Book title"),
    category: str = Form("general", description="Category"),
    max_pages: int = Form(50, description="Maximum pages to process"),
    add_to_knowledge_base: bool = Form(True),
) -> Dict[str, Any]:
    """
    Upload a PDF book, extract text, and optionally add to knowledge base.

    Args:
        file: PDF file
        title: Book title
        category: Fiqh category
        max_pages: Maximum pages to process
        add_to_knowledge_base: Whether to add to RAG

    Returns:
        Extracted text and processing status
    """
    try:
        # Validate file type
        if not file.content_type == 'application/pdf':
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )

        # Save uploaded file
        file_path = UPLOAD_DIR / f"{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"📚 PDF uploaded: {file.filename}")

        # Extract text from PDF
        ocr_service = OCRService()
        pdf_data = await ocr_service.process_pdf(str(file_path), max_pages=max_pages)

        if pdf_data.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process PDF: {pdf_data['error']}"
            )

        full_text = pdf_data.get("full_text", "")

        # Add to knowledge base
        added_to_rag = False
        if add_to_knowledge_base and full_text:
            try:
                rag = MalikiFiqhRAG()
                success = rag.add_document(
                    text=full_text,
                    metadata={
                        "topic": title,
                        "madhab": "Maliki",
                        "category": category,
                        "source": f"User PDF: {file.filename}",
                        "references": "User contributed",
                        "page_count": pdf_data.get("total_pages", 0),
                    },
                )
                added_to_rag = success
                logger.info(f"✅ Added PDF to knowledge base: {title}")
            except Exception as e:
                logger.error(f"Failed to add to RAG: {e}")

        return {
            "status": "success",
            "filename": file.filename,
            "title": title,
            "total_pages": pdf_data.get("total_pages", 0),
            "text_length": len(full_text),
            "word_count": len(full_text.split()),
            "added_to_knowledge_base": added_to_rag,
            "preview": full_text[:500] + "..." if full_text else "",
            "message": f"Extracted {pdf_data.get('total_pages', 0)} pages! " + (
                "Added to knowledge base." if added_to_rag else ""
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-directly", summary="Add text directly to knowledge base")
async def add_text_directly(
    title: str = Form(..., description="Topic title"),
    text: str = Form(..., description="Islamic text content"),
    category: str = Form("general", description="Category"),
    source: str = Form("User input", description="Source/reference"),
) -> Dict[str, Any]:
    """
    Add Islamic text directly to the knowledge base without file upload.

    Args:
        title: Topic title
        text: Text content
        category: Category
        source: Source reference

    Returns:
        Processing status
    """
    try:
        if len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 50 characters"
            )

        # Add to knowledge base
        rag = MalikiFiqhRAG()
        success = rag.add_document(
            text=text,
            metadata={
                "topic": title,
                "madhab": "Maliki",
                "category": category,
                "source": source,
                "references": source,
            },
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to add to knowledge base"
            )

        return {
            "status": "success",
            "title": title,
            "text_length": len(text),
            "word_count": len(text.split()),
            "added_to_knowledge_base": True,
            "message": "Text added to knowledge base successfully!",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/stats", summary="Get knowledge base statistics")
async def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Get statistics about the Maliki fiqh knowledge base.

    Returns:
        Knowledge base statistics
    """
    try:
        rag = MalikiFiqhRAG()
        stats = rag.get_statistics()

        return {
            "status": "success",
            **stats,
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/search", summary="Search knowledge base")
async def search_knowledge_base(
    query: str = Form(..., description="Search query"),
    n_results: int = Form(3, description="Number of results"),
    category: str = Form(None, description="Filter by category"),
) -> Dict[str, Any]:
    """
    Search the Maliki fiqh knowledge base.

    Args:
        query: Search query
        n_results: Number of results
        category: Optional category filter

    Returns:
        Search results
    """
    try:
        rag = MalikiFiqhRAG()
        results = rag.search(
            query=query,
            n_results=n_results,
            category_filter=category,
        )

        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

