from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Analysis
from app.services.document_processor import (
    DocumentProcessingError,
    MAX_FILE_BYTES,
    process_text,
    process_upload,
)
from app.services.clinical_analyzer import analyze_clinical_text

router = APIRouter()


class TextExtractionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


def _extract_text(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ("extracted_text", "text", "normalized_text", "content"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value
    raise DocumentProcessingError(
        "The document processor did not return text in a recognized field. "
        "Expected one of: extracted_text, text, normalized_text, content."
    )


def _save_analysis(db: Session, input_type: str, text: str):
    try:
        report = analyze_clinical_text(text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = Analysis(
        input_type=input_type,
        processing_status="completed",
        report_summary=report.get("report_summary", ""),
        report_json=report,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "input_type": row.input_type,
        "processing_status": row.processing_status,
        "created_at": row.created_at,
        "report_summary": row.report_summary,
        "report": report,
    }


@router.post("/extract-text")
async def extract_text_from_text(request: TextExtractionRequest):
    """Validate and normalize plain-text clinical notes."""
    try:
        return process_text(request.text)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/extract-file")
async def extract_text_from_file(file: UploadFile = File(...)):
    """Extract text from a PDF or supported image file."""
    try:
        content = await file.read(MAX_FILE_BYTES + 1)
        return process_upload(file.filename or "", content)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()


@router.post("/extract")
async def extract_document(
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
):
    """Single endpoint accepting either text or one uploaded document."""
    if bool((text or "").strip()) == bool(file):
        raise HTTPException(status_code=400, detail="Provide exactly one input: non-empty text OR one file.")
    try:
        if file is not None:
            content = await file.read(MAX_FILE_BYTES + 1)
            return process_upload(file.filename or "", content)
        return process_text(text or "")
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if file is not None:
            await file.close()


@router.post("/review-text", summary="Analyze text and save a structured clinical review")
def review_text(request: TextExtractionRequest, db: Session = Depends(get_db)):
    try:
        normalized = process_text(request.text)
        extracted = _extract_text(normalized)
        return _save_analysis(db, "text", extracted)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/review-file", summary="Analyze an uploaded PDF/image and save a structured clinical review")
async def review_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read(MAX_FILE_BYTES + 1)
        extracted = _extract_text(process_upload(file.filename or "", content))
        suffix = (file.filename or "").rsplit(".", 1)[-1].lower()
        input_type = "pdf" if suffix == "pdf" else "image"
        return _save_analysis(db, input_type, extracted)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()

@router.get("/{analysis_id}", summary="Get a saved clinical report")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve a complete saved clinical report by its ID."""

    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id)
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found."
        )

    return {
        "id": analysis.id,
        "input_type": analysis.input_type,
        "processing_status": analysis.processing_status,
        "created_at": analysis.created_at,
        "report_summary": analysis.report_summary,
        "report": analysis.report_json,
    }