from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

import fitz
import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
MIN_TEXT_CHARS = 25


class DocumentProcessingError(Exception):
    """Raised when a submitted document cannot be processed safely."""


def _clean_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _ocr_image(image: Image.Image) -> str:
    try:
        image = ImageOps.exif_transpose(image)
        image = ImageOps.grayscale(image)
        # Enlarge small images to improve OCR readability.
        if image.width < 1400:
            scale = min(2.0, 1400 / max(image.width, 1))
            image = image.resize((int(image.width * scale), int(image.height * scale)))
        return _clean_text(pytesseract.image_to_string(image, config="--psm 6"))
    except pytesseract.TesseractNotFoundError as exc:
        raise DocumentProcessingError(
            "OCR engine not found. Install Tesseract OCR and ensure tesseract.exe is on PATH."
        ) from exc
    except Exception as exc:
        raise DocumentProcessingError(f"OCR could not read this image: {exc}") from exc


def process_text(text: str) -> dict:
    cleaned = _clean_text(text or "")
    if not cleaned:
        raise DocumentProcessingError("Please enter clinical text or upload a document.")
    return {
        "input_type": "text",
        "extracted_text": cleaned,
        "extraction_method": "direct_text",
        "quality_warning": None if len(cleaned) >= MIN_TEXT_CHARS else
            "The supplied text is very short. Review it for completeness.",
    }


def process_upload(filename: str, content: bytes) -> dict:
    if not content:
        raise DocumentProcessingError("The uploaded file is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise DocumentProcessingError("File is too large. Maximum supported size is 10 MB.")

    extension = Path(filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(
            "Unsupported file type. Upload a PDF or an image (PNG, JPG, JPEG, TIFF, BMP, or WEBP)."
        )

    if extension == ".pdf":
        return _process_pdf(content)
    return _process_image(content)


def _process_pdf(content: bytes) -> dict:
    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise DocumentProcessingError("The PDF is corrupted or cannot be opened.") from exc

    page_texts: list[str] = []
    methods: set[str] = set()
    try:
        if document.is_encrypted:
            raise DocumentProcessingError("Password-protected PDFs are not supported.")
        if len(document) == 0:
            raise DocumentProcessingError("The PDF contains no pages.")
        if len(document) > 40:
            raise DocumentProcessingError("PDFs with more than 40 pages are not supported.")

        for page in document:
            text = _clean_text(page.get_text("text"))
            if len(text) >= MIN_TEXT_CHARS:
                page_texts.append(text)
                methods.add("pdf_text")
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(BytesIO(pix.tobytes("png")))
                ocr_text = _ocr_image(image)
                page_texts.append(ocr_text)
                methods.add("pdf_ocr")
    finally:
        document.close()

    combined = _clean_text("\\n\\n".join(t for t in page_texts if t))
    if not combined:
        raise DocumentProcessingError(
            "No readable text was found in this PDF. Try a clearer or text-based document."
        )

    return {
        "input_type": "pdf",
        "extracted_text": combined,
        "extraction_method": "+".join(sorted(methods)),
        "quality_warning": (
            "Little or no readable text was detected. OCR may have missed content; review the source."
            if len(combined) < MIN_TEXT_CHARS else None
        ),
    }


def _process_image(content: bytes) -> dict:
    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise DocumentProcessingError("The image is corrupted or unreadable.") from exc

    extracted = _ocr_image(image)
    if not extracted:
        raise DocumentProcessingError(
            "No readable text was detected. Try a sharper, well-lit image with the full document visible."
        )
    return {
        "input_type": "image",
        "extracted_text": extracted,
        "extraction_method": "tesseract_ocr",
        "quality_warning": (
            "Only a small amount of text was detected. Check the image and extracted text carefully."
            if len(extracted) < MIN_TEXT_CHARS else None
        ),
    }
