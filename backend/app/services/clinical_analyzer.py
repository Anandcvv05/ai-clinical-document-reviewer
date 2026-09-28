import re
from typing import Any

from app.schemas.report import ClinicalReport


def _clean(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip(" \t\r\n:;,.-")


def _field(text: str, labels: list[str]) -> str | None:
    """
    Extract a labeled field until the next recognized label or line ending.
    Works when fields are on separate lines or separated by semicolons.
    """
    all_labels = [
        "patient name", "patient", "name", "age", "visit date", "date of visit",
        "date", "chief complaint", "symptoms", "diagnosis", "diagnoses",
        "clinical condition", "medications", "medication", "medication list",
        "prescriptions", "allergies", "allergy", "temperature", "temp",
        "blood pressure", "bp", "heart rate", "pulse", "hr",
        "oxygen saturation", "spo2", "o2 sat", "clinical observations",
        "observations", "assessment", "plan",
    ]
    label_pattern = "|".join(
        re.escape(label) for label in sorted(set(all_labels), key=len, reverse=True)
    )
    wanted = "|".join(re.escape(label) for label in sorted(labels, key=len, reverse=True))
    pattern = rf"(?i)(?:^|[\n;|])\s*(?:{wanted})\s*:\s*(.*?)(?=\s*(?:[\n;|]\s*|(?:{label_pattern})\s*:)|$)"
    match = re.search(pattern, text)
    if match:
        return _clean(match.group(1))
    # Also support a field following other inline text, e.g. "Vitals: Temperature: ..."
    pattern = rf"(?i)\b(?:{wanted})\s*:\s*(.*?)(?=\s*(?:[\n;|]\s*|(?:{label_pattern})\s*:)|$)"
    match = re.search(pattern, text)
    return _clean(match.group(1)) if match else None


def _is_missing(value: str | None) -> bool:
    if not value:
        return True
    normalized = re.sub(r"[^a-z ]", "", value.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized in {
        "none", "none documented", "not specified", "not documented",
        "no", "n a", "na", "unknown", "nil", "not available",
    }


def analyze_clinical_text(text: str) -> dict[str, Any]:
    """Conservative rule-based structuring of synthetic clinical notes."""
    source = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    source = re.sub(r"[ \t]+", " ", source).strip()
    if not source:
        raise ValueError("No clinical text was provided for analysis.")

    patient: dict[str, Any] = {}
    name = _field(source, ["patient name", "patient", "name"])
    age_raw = _field(source, ["age"])
    visit_date = _field(source, ["visit date", "date of visit", "date"])
    if name and not _is_missing(name):
        patient["name"] = name
    age_match = re.search(r"\b(\d{1,3})\b", age_raw or "")
    if age_match:
        patient["age"] = int(age_match.group(1))
    if visit_date and not _is_missing(visit_date):
        patient["visit_date"] = visit_date

    symptom_text = _field(source, ["symptoms", "chief complaint"])
    symptoms: list[str] = []
    if symptom_text and not _is_missing(symptom_text):
        # Remove common duration tail; preserve symptom phrases.
        symptom_text = re.sub(
            r"\bfor\s+\d+\s*(?:hours?|days?|weeks?|months?)\b.*$",
            "", symptom_text, flags=re.IGNORECASE
        )
        symptoms = [
            _clean(item) for item in re.split(r",|;|\band\b", symptom_text, flags=re.IGNORECASE)
            if _clean(item) and not _is_missing(_clean(item))
        ]
    else:
        known = [
            "shortness of breath", "chest pain", "abdominal pain",
            "headache", "fatigue", "fever", "cough", "nausea",
            "vomiting", "dizziness",
        ]
        lower = source.lower()
        symptoms = [item for item in known if item in lower]

    diagnosis_raw = _field(source, ["diagnosis", "diagnoses", "clinical condition"])
    diagnoses = [] if _is_missing(diagnosis_raw) else [diagnosis_raw]

    medication_raw = _field(source, ["medications", "medication", "medication list", "prescriptions"])
    medications = [] if _is_missing(medication_raw) else [medication_raw]

    allergy_raw = _field(source, ["allergies", "allergy"])
    allergies = [] if _is_missing(allergy_raw) else [allergy_raw]

    vitals: dict[str, Any] = {}
        # Extract vital signs from both separate lines and combined sentences.
    vitals: dict[str, Any] = {}

    # Temperature
    temp_match = re.search(
        r"\b(?:temperature|temp)\s*:?\s*(\d{2,3}(?:\.\d+)?)\s*(?:°\s*)?([CF])?\b",
        source,
        re.IGNORECASE,
    )
    if temp_match:
        unit = f" °{temp_match.group(2).upper()}" if temp_match.group(2) else " °C"
        vitals["temperature"] = temp_match.group(1) + unit

    # Blood pressure
    bp_match = re.search(
        r"\b(?:blood pressure|bp)\s*:?\s*(\d{2,3}\s*/\s*\d{2,3})",
        source,
        re.IGNORECASE,
    )
    if bp_match:
        vitals["blood_pressure"] = (
            re.sub(r"\s+", "", bp_match.group(1)) + " mmHg"
        )

    # Heart rate
    hr_match = re.search(
        r"\b(?:heart rate|pulse|hr)\s*:?\s*(\d{2,3})\b",
        source,
        re.IGNORECASE,
    )
    if hr_match:
        vitals["heart_rate"] = hr_match.group(1) + " bpm"

    # Oxygen saturation
    spo2_match = re.search(
        r"\b(?:oxygen saturation|spo2|o2 sat)\s*:?\s*(\d{2,3})\s*%?",
        source,
        re.IGNORECASE,
    )
    if spo2_match:
        vitals["oxygen_saturation"] = spo2_match.group(1) + "%"

    observations = []
    for label in ("clinical observations", "observations", "assessment", "plan"):
        value = _field(source, [label])
        if value and not _is_missing(value):
            observations.append(f"{label.title()}: {value}")

    missing = []
    if "age" not in patient:
        missing.append("Patient age not documented.")
    if not diagnoses:
        missing.append("Diagnosis or clinical condition not specified.")
    if not medications:
        missing.append("Medication information not documented.")
    if not allergy_raw or _is_missing(allergy_raw):
        missing.append("Allergy information not documented.")
    if not vitals:
        missing.append("Vital signs not documented.")

    review_items = [
        "This is an automated text-structuring result; verify all extracted information against the source note."
    ]
    if not patient:
        review_items.append("Patient information could not be identified.")
    if not symptoms:
        review_items.append("Symptoms were not confidently identified.")
    if any(token in source.lower() for token in ("unclear", "illegible", "unable to read", "uncertain")):
        review_items.append("The source contains wording indicating uncertainty or unreadable information.")

    summary_parts = []
    if symptoms:
        summary_parts.append("Reported symptoms: " + ", ".join(symptoms) + ".")
    if diagnoses:
        summary_parts.append("Diagnosis recorded: " + "; ".join(diagnoses) + ".")
    if vitals:
        summary_parts.append(
            "Recorded vital signs: " + "; ".join(
                f"{key.replace('_', ' ').title()}: {value}" for key, value in vitals.items()
            ) + "."
        )
    if missing:
        summary_parts.append("Missing information: " + " ".join(missing))
    if not summary_parts:
        summary_parts.append("Clinical details were received, but few structured fields could be confidently extracted.")

    report = ClinicalReport(
        report_summary=" ".join(summary_parts),
        patient_information=patient,
        symptoms=symptoms,
        diagnoses=diagnoses,
        medications=medications,
        vitals=vitals,
        allergies=allergies,
        clinical_observations=observations,
        clinical_concerns=[],
        missing_information=missing,
        potential_inconsistencies=[],
        requires_review=review_items,
    )
    return report.model_dump() if hasattr(report, "model_dump") else report.dict()
