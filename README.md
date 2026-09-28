# AI Clinical Document Reviewer

An AI-powered web application that analyzes clinical documents and generates structured review reports. The application supports clinical text, PDF documents, and PNG images using OCR (Optical Character Recognition).

## 🌐 Live Application

- **Frontend:** https://clinicalreview-ai.vercel.app/
- **Backend API:** https://clinicalreview-ai-backend-docker.onrender.com
- **API Documentation:** https://clinicalreview-ai-backend-docker.onrender.com/docs

---

## 🚀 Features

- Analyze clinical text directly.
- Upload PDF documents for analysis.
- Upload PNG images and extract text using OCR.
- Generate structured clinical review reports.
- View analysis history.
- Delete individual analysis records.
- Clear analysis history.
- Store analysis results persistently.
- Download reports as PDF.
- Handle invalid files and input errors.

---

## 🛠️ Technology Stack

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
- Tesseract OCR
- PyMuPDF
- Pillow

### Deployment
- Vercel for frontend hosting
- Render for backend hosting
- Docker for backend deployment

---

## 📂 Project Structure

```text
ai-clinical-document-reviewer/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── apt.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── index.html
│
├── sample_data/
│   ├── sample_clinical_note.txt
│   ├── sample_clinical_note.pdf
│   └── sample_clinical_image.png
│
├── screenshots/
│   ├── 01_homepage.png
│   ├── 02_text_analysis.png
│   ├── 03_analysis_report.png
│   ├── 04_pdf_upload.png
│   ├── 05_png_ocr.png
│   ├── 06_analysis_history.png
│   ├── 07_api_docs.png
│   └── 08_deployment.png
│
├── README.md
├── ARCHITECTURE.md
└── AI_ML_DESIGN.md
```

---

## ⚙️ Local Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or later
- Node.js and npm
- Git
- Tesseract OCR

### 1. Clone the Repository

```bash
git clone https://github.com/Anandcvv05/ai-clinical-document-reviewer.git
```

Navigate to the project directory:

```bash
cd ai-clinical-document-reviewer
```

### 2. Set Up the Backend

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

http://localhost:8000

API documentation:

http://localhost:8000/docs

### 3. Set Up the Frontend

Open a new terminal and navigate to the frontend folder:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at:

http://localhost:5173

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyses/review-text` | Analyze clinical text |
| POST | `/api/analyses/review-file` | Analyze uploaded documents |
| GET | `/api/analyses` | Retrieve analysis history |
| GET | `/api/analyses/{analysis_id}` | Retrieve a specific analysis |
| DELETE | `/api/analyses/{analysis_id}` | Delete an individual analysis |
| DELETE | `/api/analyses` | Clear all analysis history |

---

## 🧠 AI/ML Approach

The application uses rule-based analysis to identify relevant clinical information and generate structured review reports.

OCR is used to extract text from PNG images.

The application focuses on document processing, information extraction, and structured reporting.

**Note:** The current implementation uses rule-based analysis rather than a trained machine learning model.

---

## 📊 Sample Data

The `sample_data/` folder contains synthetic clinical documents for testing:

- Clinical text
- PDF clinical note
- PNG clinical image

These files are intended for demonstration and testing purposes only.

---

## 📸 Screenshots

The `screenshots/` folder contains screenshots demonstrating:

- Application homepage
- Clinical text analysis
- Generated analysis report
- PDF document analysis
- PNG OCR analysis
- Analysis history
- API documentation
- Deployed application

---

## 🔐 Privacy and Safety

- Use synthetic clinical data for testing and demonstration.
- Do not upload real patient information without appropriate authorization and safeguards.
- The application is intended for educational and demonstration purposes.
- Generated reports are not a substitute for professional medical judgment.

---

## 🚀 Deployment

The application is deployed using:

- **Frontend:** Vercel
- **Backend:** Render
- **Containerization:** Docker

### Live Links

- [Open Application](https://clinicalreview-ai.vercel.app/)
- [Backend API](https://clinicalreview-ai-backend-docker.onrender.com)
- [API Documentation](https://clinicalreview-ai-backend-docker.onrender.com/docs)

---

## 👨‍💻 Author

**CVV ANAND**

B.Tech in Artificial Intelligence and Machine Learning  
JAIN Deemed-to-be University, Bengaluru

---

## 📄 License

This project was developed for educational and demonstration purposes.