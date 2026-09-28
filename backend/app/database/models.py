import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base

# JSON works with SQLite for local development; PostgreSQL uses JSONB.
json_type = JSON().with_variant(JSONB, "postgresql")

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    report_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    report_json: Mapped[dict] = mapped_column(json_type, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
