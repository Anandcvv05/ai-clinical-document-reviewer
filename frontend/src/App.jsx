import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const SAMPLE_TEXT =
  "Patient presents with headache and nausea.\n" +
  "Temperature 37.5°C. Blood pressure 116/78 mmHg.\n" +
  "Heart rate 82 bpm.";

function App() {
  const [inputMode, setInputMode] = useState("text");
  const [clinicalText, setClinicalText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [clearingAll, setClearingAll] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load saved analyses
  async function loadHistory() {
    try {
      const response = await fetch(`${API_URL}/api/analyses`);

      if (!response.ok) {
        throw new Error("Unable to load analysis history.");
      }

      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    }
  }

  // Open a saved report
  async function handleHistoryClick(analysisId) {
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/analyses/${analysisId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load the saved report."
        );
      }

      setReport(data);

      setTimeout(() => {
        document
          .querySelector(".report-panel")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Delete one saved analysis from history
  async function handleDeleteAnalysis(analysisId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this analysis? This action cannot be undone."
    );

    if (!confirmed) return;

    setDeletingId(analysisId);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/analyses/${analysisId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to delete this analysis."
        );
      }

      // Remove the deleted item from the visible history.
      setHistory((previousHistory) =>
        previousHistory.filter((item) => item.id !== analysisId)
      );

      // Clear the report if the deleted analysis is currently open.
      if (String(report?.id) === String(analysisId)) {
        setReport(null);
      }
    } catch (err) {
      setError(err.message || "Unable to delete analysis.");
    } finally {
      setDeletingId(null);
    }
  }

  // Delete all saved analyses from history
  async function handleClearAllHistory() {
    if (history.length === 0 || clearingAll) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete all ${history.length} saved analyses? This action cannot be undone.`
    );

    if (!confirmed) return;

    setClearingAll(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/analyses`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to clear analysis history.");
      }

      setHistory([]);
      setReport(null);
    } catch (err) {
      setError(err.message || "Unable to clear analysis history.");
    } finally {
      setClearingAll(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  // Analyze clinical text or uploaded file
  async function handleAnalyze(event) {
    event.preventDefault();

    setError("");
    setReport(null);

    if (inputMode === "text" && !clinicalText.trim()) {
      setError("Please enter clinical text.");
      return;
    }

    if (inputMode === "file" && !selectedFile) {
      setError("Please select a document.");
      return;
    }

    setLoading(true);

    try {
      let response;

      if (inputMode === "text") {
        response = await fetch(
          `${API_URL}/api/analyses/review-text`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              text: clinicalText,
            }),
          }
        );
      } else {
        const formData = new FormData();
        formData.append("file", selectedFile);

        response = await fetch(
          `${API_URL}/api/analyses/review-file`,
          {
            method: "POST",
            body: formData,
          }
        );
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Clinical analysis failed."
        );
      }

      setReport(data);
      await loadHistory();

      setTimeout(() => {
        document
          .querySelector(".report-panel")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the backend. Check whether the server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  // Load example text into the input box
  function loadExample() {
    setInputMode("text");
    setClinicalText(SAMPLE_TEXT);
    setSelectedFile(null);
    setError("");
  }

  // Format field names for display
  function formatLabel(value) {
    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  // Render values inside report sections
  function renderValue(value) {
    if (value === null || value === undefined || value === "") {
      return <span className="muted-value">Not provided</span>;
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="muted-value">Not provided</span>;
      }

      return (
        <ul className="report-list">
          {value.map((item, index) => (
            <li key={index}>
              {typeof item === "object"
                ? JSON.stringify(item)
                : String(item)}
            </li>
          ))}
        </ul>
      );
    }

    if (typeof value === "object") {
      return (
        <div className="report-grid">
          {Object.entries(value).map(([key, item]) => (
            <div className="report-item" key={key}>
              <span className="item-label">
                {formatLabel(key)}
              </span>
              <strong>{renderValue(item)}</strong>
            </div>
          ))}
        </div>
      );
    }

    return <span>{String(value)}</span>;
  }

  // Render a report section
  function renderSection(title, content, className = "") {
    if (
      content === null ||
      content === undefined ||
      (Array.isArray(content) && content.length === 0)
    ) {
      return null;
    }

    return (
      <section className={`report-section ${className}`}>
        <div className="section-heading">
          <h3>{title}</h3>
        </div>

        <div className="section-content">
          {renderValue(content)}
        </div>
      </section>
    );
  }

  const reportData = report?.report || {};

  return (
    <div className="app">
      {/* Header */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">✚</div>

          <div>
            <h1>ClinicalReview AI</h1>
            <p>Clinical Document Reviewer</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          AI Review System
        </div>
      </header>

      {/* Main dashboard */}
      <main className="main-container">
        <div className="dashboard-grid">

          {/* LEFT COLUMN: INPUT */}
          <aside className="left-column">
            <section className="panel input-panel">
              <div className="panel-heading">
                <div className="heading-icon blue-icon">
                  ▤
                </div>

                <div>
                  <h2>Analyze Clinical Document</h2>
                  <p>
                    Upload a file or enter clinical text to get
                    an AI-powered structured review.
                  </p>
                </div>
              </div>

              {/* Input tabs */}
              <div className="tabs">
                <button
                  className={
                    inputMode === "text"
                      ? "tab active"
                      : "tab"
                  }
                  onClick={() => {
                    setInputMode("text");
                    setError("");
                  }}
                  type="button"
                >
                  Text Input
                </button>

                <button
                  className={
                    inputMode === "file"
                      ? "tab active"
                      : "tab"
                  }
                  onClick={() => {
                    setInputMode("file");
                    setError("");
                  }}
                  type="button"
                >
                  File Upload
                </button>
              </div>

              <form onSubmit={handleAnalyze}>
                {inputMode === "text" ? (
                  <div className="form-group">
                    <label htmlFor="clinicalText">
                      Clinical Notes / Report Text
                    </label>

                    <textarea
                      id="clinicalText"
                      value={clinicalText}
                      onChange={(event) =>
                        setClinicalText(event.target.value)
                      }
                      placeholder="Paste clinical notes, symptoms, or report text here..."
                      rows={12}
                    />
                  </div>
                ) : (
                  <div className="form-group">
                    <label htmlFor="clinicalFile">
                      Upload Clinical Document
                    </label>

                    <div className="upload-box">
                      <div className="upload-icon">↑</div>

                      <h3>Choose a document</h3>

                      <p>
                        PDF, PNG, JPG, JPEG, TIFF, BMP, WEBP
                      </p>

                      <input
                        id="clinicalFile"
                        type="file"
                        accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp"
                        onChange={(event) =>
                          setSelectedFile(
                            event.target.files?.[0] || null
                          )
                        }
                      />

                      {selectedFile && (
                        <p className="selected-file">
                          Selected: {selectedFile.name}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    {error}
                  </div>
                )}

                <button
                  className="primary-button"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? (
                    "Analyzing..."
                  ) : (
                    <>
                      <span>⌕</span>
                      Analyze Document
                    </>
                  )}
                </button>
              </form>
            </section>

            {/* Example input card */}
            <section className="panel example-panel">
              <div className="panel-heading">
                <div className="heading-icon yellow-icon">
                  ✦
                </div>

                <div>
                  <h2>Example Input</h2>
                  <p>
                    Try a sample to see how it works:
                  </p>
                </div>
              </div>

              <div className="example-text">
                Patient presents with headache and nausea.
                <br />
                Temperature 37.5°C. Blood pressure 116/78 mmHg.
                <br />
                Heart rate 82 bpm.
              </div>

              <button
                className="load-example-button"
                type="button"
                onClick={loadExample}
              >
                ▤ &nbsp; Load Example
              </button>
            </section>
          </aside>

          {/* CENTER COLUMN: REPORT */}
          <section className="panel report-panel">
            <div className="report-header">
              <div className="report-title">
                <div className="heading-icon blue-icon">
                  ▤
                </div>

                <div>
                  <h2>Clinical Report</h2>
                  <p>
                    AI-generated structured analysis based on
                    the provided document.
                  </p>
                </div>
              </div>

              {report && (
  <div className="report-actions">
    <button
      className="download-button"
      type="button"
      onClick={() => window.print()}
    >
      ↓ Download Report
    </button>

    <div className="report-status">
      <span className="status-dot"></span>
      Analysis Completed
    </div>
  </div>
)}
            </div>

            {report ? (
              <div className="report-content">
                <div className="report-meta">
                  <span>
                    Report ID: {report.id ?? "—"}
                  </span>

                  <span>
                    {report.created_at
                      ? new Date(
                          report.created_at
                        ).toLocaleString()
                      : ""}
                  </span>
                </div>

                {/* Summary */}
                {reportData.report_summary && (
                  <div className="summary-card">
                    <span className="item-label">
                      REPORT SUMMARY
                    </span>

                    <p>{reportData.report_summary}</p>
                  </div>
                )}

                {/* Patient information */}
                {renderSection(
                  "♙  Patient Information",
                  reportData.patient_information,
                  "patient-section"
                )}

                {/* Symptoms */}
                {renderSection(
                  "☷  Reported Symptoms",
                  reportData.symptoms,
                  "symptoms-section"
                )}

                {/* Vital signs */}
                {renderSection(
                  "♥  Vital Signs",
                  reportData.vitals,
                  "vitals-section"
                )}

                {/* Diagnoses */}
                {renderSection(
                  "✚  Diagnoses",
                  reportData.diagnoses,
                  "diagnoses-section"
                )}

                {/* Medications */}
                {renderSection(
                  "▤  Medications",
                  reportData.medications,
                  "medications-section"
                )}

                {/* Allergies */}
                {renderSection(
                  "⚠  Allergies",
                  reportData.allergies,
                  "allergies-section"
                )}

                {/* Clinical observations */}
                {renderSection(
                  "☷  Clinical Observations",
                  reportData.clinical_observations,
                  "observations-section"
                )}

                {/* Clinical concerns */}
                {renderSection(
                  "⚠  Clinical Concerns",
                  reportData.clinical_concerns,
                  "concerns-section"
                )}

                {/* Missing information */}
                {renderSection(
                  "?  Missing Information",
                  reportData.missing_information,
                  "missing-section"
                )}

                {/* Inconsistencies */}
                {renderSection(
                  "⚠  Potential Inconsistencies",
                  reportData.potential_inconsistencies,
                  "inconsistencies-section"
                )}

                {/* Requires review */}
                {renderSection(
                  "✓  Requires Review",
                  reportData.requires_review,
                  "review-section"
                )}

                

                <div className="disclaimer">
                  <strong>Important:</strong> This automated
                  report is for documentation support only.
                  It is not a medical diagnosis. Verify all
                  extracted information against the original
                  source.
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">▤</div>

                <h3>No report generated yet</h3>

                <p>
                  Submit a clinical note or upload a document
                  to view its structured report.
                </p>
              </div>
            )}
          </section>

          {/* RIGHT COLUMN: HISTORY */}
          <aside className="panel history-panel">
            <div className="panel-heading history-heading">
              <div>
                <h2>Analysis History</h2>
                <p>
                  Previously processed clinical documents.
                </p>
              </div>

              <button
                className="refresh-button"
                onClick={loadHistory}
                type="button"
                title="Refresh history"
              >
                ↻
              </button>
            </div>

            <div className="history-count">
              <span>
                {history.length}{" "}
                {history.length === 1 ? "analysis" : "analyses"}
              </span>

              <button
                className="delete-button clear-history-button"
                type="button"
                onClick={handleClearAllHistory}
                disabled={history.length === 0 || clearingAll}
              >
                {clearingAll ? "Clearing..." : "🗑 Clear All History"}
              </button>
            </div>

            {history.length === 0 ? (
              <div className="history-empty">
                <div className="empty-icon">▤</div>
                <p>No previous analyses found.</p>
              </div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div
                    className={`history-item ${
                      report?.id === item.id ? "selected" : ""
                    }`}
                    key={item.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => handleHistoryClick(item.id)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        handleHistoryClick(item.id);
                      }
                    }}
                  >
                    <div className="history-icon">▤</div>

                    <div className="history-details">
                      <strong>
                        {item.input_type?.toUpperCase() ||
                          "DOCUMENT"}{" "}
                        Analysis
                      </strong>

                      <p>
                        {item.report_summary ||
                          "Clinical document analysis"}
                      </p>

                      <span>
                        {item.created_at
                          ? new Date(
                              item.created_at
                            ).toLocaleString()
                          : ""}
                      </span>

                      <button
                        className="delete-button"
                        type="button"
                        disabled={deletingId === item.id}
                        onClick={(event) => {
                          event.stopPropagation();
                          handleDeleteAnalysis(item.id);
                        }}
                      >
                        {deletingId === item.id
                          ? "Deleting..."
                          : "🗑 Delete"}
                      </button>
                    </div>

                    <span className="history-arrow">›</span>
                  </div>
                ))}
              </div>
            )}
          </aside>
        </div>

        <footer className="footer">
          <p>
            ClinicalReview AI · Synthetic data only ·
            Automated documentation support
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;