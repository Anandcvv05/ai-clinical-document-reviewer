from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.connection import get_db
from app.database.models import Analysis

router = APIRouter()

@router.get("")
def list_analyses(db: Session = Depends(get_db)):
    rows = db.query(Analysis).order_by(desc(Analysis.created_at)).all()
    return [
        {
            "id": row.id,
            "input_type": row.input_type,
            "processing_status": row.processing_status,
            "created_at": row.created_at,
            "report_summary": row.report_summary,
        }
        for row in rows
    ]

@router.get("/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    row = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": row.id,
        "input_type": row.input_type,
        "processing_status": row.processing_status,
        "created_at": row.created_at,
        "report_summary": row.report_summary,
        "report": row.report_json,
        "error_message": row.error_message,
    }
@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """Delete one analysis from history."""

    row = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    db.delete(row)
    db.commit()

    return {
        "message": "Analysis deleted successfully",
        "id": analysis_id,
    }
@router.delete("")
def delete_all_analyses(db: Session = Depends(get_db)):
    """Delete all analyses from history."""

    deleted_count = db.query(Analysis).delete(
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "All analyses deleted successfully",
        "deleted_count": deleted_count,
    }