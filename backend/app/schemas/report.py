from pydantic import BaseModel, Field
from typing import Any

class ClinicalReport(BaseModel):
    report_summary: str = ""
    patient_information: dict[str, Any] = Field(default_factory=dict)
    symptoms: list[Any] = Field(default_factory=list)
    diagnoses: list[Any] = Field(default_factory=list)
    medications: list[Any] = Field(default_factory=list)
    vitals: dict[str, Any] = Field(default_factory=dict)
    allergies: list[Any] = Field(default_factory=list)
    clinical_observations: list[Any] = Field(default_factory=list)
    clinical_concerns: list[Any] = Field(default_factory=list)
    missing_information: list[Any] = Field(default_factory=list)
    potential_inconsistencies: list[Any] = Field(default_factory=list)
    requires_review: list[Any] = Field(default_factory=list)
