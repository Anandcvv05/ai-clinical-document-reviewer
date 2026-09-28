# ClinicalReview AI – AI/ML Design Documentation

## 1. Overview

ClinicalReview AI is a web-based clinical document review application that processes clinical text, PDF documents, and images to generate structured clinical reports.

The current implementation uses a **rule-based clinical analysis approach** rather than a trained machine learning model or an external AI service.

The system extracts and processes clinical information, identifies relevant details using predefined rules, and generates a structured report.

The application is intended for educational and demonstration purposes only.

---

## 2. AI/ML Approach

### 2.1 Analysis Method

The application uses rule-based analysis to identify clinical information from the submitted document.

The analysis relies on predefined patterns and rules to identify relevant medical information.

### 2.2 Model or Service Used

- **Approach:** Rule-based clinical information analysis
- **Machine Learning Model:** No trained ML model is currently integrated.
- **External AI Service:** No external AI service is currently integrated.

This approach was selected to provide a simple, understandable, and locally executable analysis pipeline.

---

## 3. Document Processing Pipeline

The application follows these processing stages:

### Stage 1: Input Collection

The user can submit clinical information through:

- Direct text input
- PDF document upload
- Image upload

The frontend sends the input to the FastAPI backend through the appropriate API endpoint.

### Stage 2: Input Validation

The backend validates the submitted input.

Validation includes checking for empty text, unsupported file types, and unreadable or corrupted documents.

Invalid inputs are rejected with appropriate error messages.

### Stage 3: Text Extraction

The document-processing layer extracts text from supported document formats.

The extracted text is passed to the preprocessing stage.

The exact extraction method depends on the submitted file format and the implemented processing functions.

### Stage 4: Text Preprocessing

The extracted text is cleaned before analysis.

Preprocessing helps standardize the input and prepare it for rule-based information extraction.

### Stage 5: Clinical Information Extraction

The analyzer uses predefined patterns and rules to identify relevant clinical information.

Examples of information that may be identified include:

- Patient details
- Symptoms
- Vital signs
- Medications
- Allergies
- Other relevant clinical information present in the document

The extracted information is used to construct the report.

### Stage 6: Structured Report Generation

The backend organizes the extracted information into a structured clinical report.

The report is returned to the frontend for display.

### Stage 7: Data Persistence

The completed analysis is stored in the SQLite database through SQLAlchemy.

The saved report can later be retrieved through the Analysis History feature.

---

## 4. Information Extraction and Data Flow

The information extraction workflow is:

1. Receive clinical text or an uploaded document.
2. Validate the input.
3. Extract text from the document.
4. Clean and preprocess the extracted text.
5. Apply predefined clinical analysis rules.
6. Organize the extracted information into a structured report.
7. Store the completed analysis in the database.
8. Return the report to the frontend.

The frontend is responsible for displaying the report and providing access to saved analyses.

The core processing logic is handled by the backend.

---

## 5. Structured Output

The application generates a structured clinical report rather than displaying only the original document text.

The report organizes relevant information into sections.

The structured report is used for:

- Displaying the analysis summary
- Presenting detailed clinical information
- Saving completed analyses
- Retrieving previously generated reports
- Supporting PDF report downloads

The report reflects the information identified by the current rule-based analyzer.

---

## 6. Handling Missing or Uncertain Information

Clinical documents may contain incomplete or unclear information.

The current implementation relies on the information extracted from the submitted document and the rules defined in the analyzer.

Important limitations include:

- Missing information may not be identified or interpreted correctly.
- Unclear or ambiguous clinical statements may not be understood accurately.
- The rule-based analyzer does not independently verify the truth of the extracted information.
- The system should not assume that an unmentioned clinical detail is absent.

A future version could explicitly label missing information as "Not provided" and distinguish uncertain information from confirmed findings.

---

## 7. Reducing Incorrect or Unsupported Information

The current system uses predefined rules and patterns instead of generating unrestricted responses through a generative AI model.

This limits the scope of the analysis to the information and patterns supported by the implemented rules.

However, rule-based processing does not guarantee that every extracted result is correct.

Potential weaknesses include:

- Incorrect matches caused by similar words or phrases
- Failure to recognize unfamiliar medical terminology
- Incorrect interpretation of negation or context
- Incomplete extraction from poorly formatted documents
- Failure to identify relationships between clinical findings

The generated report should therefore be treated as an automated extraction result, not a medically validated conclusion.

---

## 8. Error Handling

The application includes validation and error handling for common input failures.

Examples include:

| Failure Scenario | Expected Handling |
|---|---|
| Empty clinical text | Display a validation message |
| Unsupported file type | Reject the file and display an error |
| Corrupted PDF | Display an error indicating that the file cannot be opened |
| Unreadable document | Report the processing failure |
| Invalid input | Return an appropriate error response |

Additional improvements could include more detailed error logging and more comprehensive handling of unexpected processing failures.

---

## 9. Technical Decisions

### 9.1 Rule-Based Analysis

A rule-based approach was selected for the current implementation because it is straightforward to implement and does not require model training or external AI services.

**Trade-off:** The approach is easier to understand and execute, but it has limited flexibility compared with advanced clinical NLP or machine learning systems.

### 9.2 Backend Framework

FastAPI was selected to provide a dedicated backend service.

It handles API requests, input validation, document processing, analysis, and database interactions.

### 9.3 Frontend Framework

React with Vite was selected to build an interactive user interface.

It supports report display, document submission, and analysis history.

### 9.4 Database

SQLite was selected for persistent storage because it is lightweight and suitable for a local demonstration application.

SQLAlchemy provides database interaction through an ORM.

### 9.5 Frontend and Backend Separation

The frontend and backend are separated so that the user interface communicates with the backend through APIs.

This keeps the core processing logic outside the frontend and makes the application easier to maintain.

---

## 10. Limitations

The current implementation has the following limitations:

1. It uses rule-based analysis rather than a trained clinical ML model.
2. It may not recognize all medical terminology or clinical expressions.
3. It may fail to interpret complex clinical context.
4. Its accuracy depends on the quality of document extraction and predefined rules.
5. It has not been clinically validated.
6. It must not be used as a substitute for professional medical judgment.

All clinical information used for demonstration and testing should be synthetic.

---

## 11. Future Improvements

Possible improvements include:

- Integrating a clinical NLP model for more advanced information extraction.
- Improving recognition of medical terminology and clinical relationships.
- Adding explicit handling of missing and uncertain information.
- Improving extraction from scanned and low-quality documents.
- Adding validation for structured report output.
- Introducing automated evaluation using synthetic clinical test cases.
- Improving error logging and processing reliability.
- Evaluating the system against a carefully prepared synthetic dataset.

Any future model integration should be evaluated for accuracy, reliability, and safety before being used in clinical settings.

---

## 12. Conclusion

ClinicalReview AI demonstrates a document-processing and rule-based clinical information extraction workflow.

The application combines document processing, a FastAPI backend, a React frontend, structured report generation, and SQLite persistence.

Although the current system does not use a trained machine learning model, it provides a foundation for future development of more advanced clinical document analysis capabilities.

The application is intended for educational and demonstration purposes only.