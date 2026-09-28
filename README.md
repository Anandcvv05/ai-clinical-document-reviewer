# ClinicalReview AI – AI Clinical Document Reviewer

## 1. Project Overview

ClinicalReview AI is a web-based application designed to analyze clinical documents and generate structured clinical reports.

The application accepts clinical text, PDF documents, and images. It extracts clinical information, identifies relevant medical details, and presents the results in a structured report.

The application also maintains a history of previous analyses and allows users to download reports as PDFs.

**Important:** This application is intended for educational and demonstration purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## 2. Features

- Clinical text analysis
- PDF document upload and analysis
- Image upload and analysis
- Structured clinical report generation
- Analysis history with saved reports
- View previously generated reports
- Delete individual analyses
- Clear all analysis history
- Download reports as PDF
- Input validation and error handling
- REST API documentation using Swagger UI
- Persistent storage using SQLite

---

## 3. Technology Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

### Document Processing
- Text extraction and preprocessing
- Rule-based clinical information analysis
- PDF and image processing

---

## 4. Project Structure

```text
ai-clinical-document-reviewer/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── history.py
│   │   └── document_processor.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   └── ...
│
└── README.md