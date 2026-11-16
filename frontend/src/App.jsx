
import { useState } from "react";

import {
  Headphones,
  Upload,
  FileAudio,
  LoaderCircle,
  CheckCircle2,
  AlertCircle,
  Activity,
  MessageSquareText,
  Target,
  ListChecks,
  UserRound,
  Headset,
  Award,
  TrendingUp,
  ThumbsUp,
  Lightbulb,
  ClipboardCheck,
} from "lucide-react";

import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


function formatTimestamp(seconds) {
  const totalSeconds = Math.max(0, Math.floor(Number(seconds) || 0));
  const minutes = Math.floor(totalSeconds / 60);
  const remainingSeconds = totalSeconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(
    remainingSeconds
  ).padStart(2, "0")}`;
}


function speakerAlignment(role) {
  if (role === "Agent") return "left";
  if (role === "Customer") return "right";
  return "neutral";
}


function getScoreColor(score) {
  if (score >= 80) return "#16a34a";
  if (score >= 60) return "#d97706";
  return "#dc2626";
}


function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function analyzeCall(event) {
    event.preventDefault();

    if (!file) {
      setError("Please select an audio file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setResult(data);

    } catch (err) {
      setError(err.message || "Could not connect to the backend.");

    } finally {
      setLoading(false);
    }
  }


  const analysis = result?.analysis;

  const conversation = Array.isArray(result?.conversation)
    ? result.conversation
    : [];

  const performance = analysis?.agent_performance;

  const criteriaLabels = {
    greeting: "Greeting",
    communication: "Communication",
    customer_understanding: "Customer Understanding",
    professionalism: "Professionalism",
    resolution: "Resolution",
  };


  return (
    <div className="app-shell">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <Headphones size={23} />
          </div>

          <div>
            <h2>CallSense AI</h2>
            <span>QUALITY INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <div className="nav-item active">
          <Activity size={18} />
          Call analysis
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>AI analysis workspace</span>
        </div>

      </aside>


      {/* Main Content */}
      <main className="main-content">

        {/* Header */}
        <header className="topbar">

          <div>
            <div className="eyebrow">CALL CENTER INTELLIGENCE</div>
            <h1>Call Analysis</h1>
          </div>

          <div className="live-status">
            <span className="status-dot" />
            Backend integration
          </div>

        </header>


        {/* Welcome Section */}
        <section className="welcome">

          <div>
            <span className="eyebrow light">
              AI-POWERED QUALITY REVIEW
            </span>

            <h2>Understand every customer conversation.</h2>

            <p>
              Upload a call recording to generate a transcript and
              AI-powered insights.
            </p>
          </div>

          <div className="welcome-icon">
            <Headphones size={48} />
          </div>

        </section>


        {/* Upload Section */}
        <section className="upload-card">

          <div className="section-heading">

            <div className="heading-icon">
              <Upload size={19} />
            </div>

            <div>
              <h3>Analyze a call</h3>
              <p>Supported formats: WAV, MP3, M4A and OGG</p>
            </div>

          </div>


          <form onSubmit={analyzeCall}>

            <label className="drop-zone">

              <input
                type="file"
                accept=".wav,.mp3,.m4a,.ogg,audio/*"
                onChange={(event) => {
                  setFile(event.target.files?.[0] || null);
                  setError("");
                  setResult(null);
                }}
              />

              <div className="upload-icon">
                <FileAudio size={27} />
              </div>

              <strong>
                {file ? file.name : "Choose a call recording"}
              </strong>

              <span>
                {file
                  ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
                  : "Click here to browse files on your computer"}
              </span>

            </label>


            <button
              className="analyze-button"
              type="submit"
              disabled={loading}
            >

              {loading ? (
                <>
                  <LoaderCircle className="spin" size={18} />
                  Analyzing call...
                </>
              ) : (
                <>
                  <Activity size={18} />
                  Analyze call
                </>
              )}

            </button>

          </form>


          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              {error}
            </div>
          )}

        </section>


        {/* Loading Message */}
        {loading && (
          <div className="loading-note">
            Transcribing the recording and generating AI insights.
            This may take a little while.
          </div>
        )}


        {/* Results Section */}
        {result && analysis && (

          <section className="results-section">

            <div className="results-title">

              <div>
                <div className="eyebrow">ANALYSIS REPORT</div>
                <h2>Call insights</h2>
                <p>Results for {result.filename}</p>
              </div>

              <div className="success-badge">
                <CheckCircle2 size={16} />
                Analysis complete
              </div>

            </div>


            {/* Call Insights */}
            <div className="insight-grid">

              <article className="insight-card summary-card">

                <div className="card-icon purple">
                  <MessageSquareText size={20} />
                </div>

                <div className="eyebrow">CALL SUMMARY</div>

                <p>{analysis.summary}</p>

              </article>


              <article className="insight-card">

                <div className="card-icon orange">
                  <Activity size={20} />
                </div>

                <div className="eyebrow">CUSTOMER SENTIMENT</div>

                <div
                  className={`sentiment ${analysis.sentiment?.toLowerCase()}`}
                >
                  {analysis.sentiment}
                </div>

              </article>


              <article className="insight-card">

                <div className="card-icon blue">
                  <Target size={20} />
                </div>

                <div className="eyebrow">CUSTOMER INTENT</div>

                <p>{analysis.customer_intent}</p>

              </article>


              <article className="insight-card">

                <div className="card-icon green">
                  <ListChecks size={20} />
                </div>

                <div className="eyebrow">KEY ISSUES</div>

                {analysis.key_issues?.length ? (
                  <ul>
                    {analysis.key_issues.map((issue, index) => (
                      <li key={index}>{issue}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No key issues identified.</p>
                )}

              </article>

            </div>


            {/* Agent Performance Evaluation */}
            {performance && (

              <article className="performance-card">

                <div className="section-heading">

                  <div className="heading-icon">
                    <Award size={20} />
                  </div>

                  <div>
                    <h3>Agent Performance Evaluation</h3>
                    <p>
                      AI-powered evaluation of agent performance
                    </p>
                  </div>

                </div>


                {/* Overall Score */}
                <div className="performance-overview">

                  <div className="performance-score">

                    <div className="eyebrow">
                      OVERALL PERFORMANCE SCORE
                    </div>

                    <div className="score-value">
                      {performance.overall_score !== null &&
                      performance.overall_score !== undefined
                        ? `${performance.overall_score}/100`
                        : "Not evaluated"}
                    </div>

                    <p>
                      Based on evaluable performance criteria
                    </p>

                  </div>


                  {performance.overall_score !== null &&
                    performance.overall_score !== undefined && (

                    <div
                      className="score-ring"
                      style={{
                        background: `conic-gradient(
                          ${getScoreColor(performance.overall_score)}
                          ${performance.overall_score}%,
                          #e8edf3 ${performance.overall_score}%
                        )`,
                      }}
                    >
                      <div className="score-ring-inner">
                        <strong>{performance.overall_score}%</strong>
                      </div>
                    </div>

                  )}

                </div>


                {/* Individual Criteria */}
                <div className="criteria-section">

                  <h4>
                    <ClipboardCheck size={17} />
                    Performance Criteria
                  </h4>

                  <div className="criteria-grid">

                    {Object.entries(criteriaLabels).map(
                      ([key, label]) => {

                        const score = performance.criteria?.[key];

                        const isEvaluated =
                          typeof score === "number";

                        return (

                          <div className="criterion-item" key={key}>

                            <div className="criterion-header">

                              <span>{label}</span>

                              <strong>
                                {isEvaluated
                                  ? `${score}/100`
                                  : "Not evaluated"}
                              </strong>

                            </div>

                            <div className="criterion-track">

                              {isEvaluated && (
                                <div
                                  className="criterion-fill"
                                  style={{
                                    width: `${score}%`,
                                    backgroundColor: getScoreColor(score),
                                  }}
                                />
                              )}

                            </div>

                          </div>

                        );

                      }
                    )}

                  </div>

                </div>


                {/* Strengths and Improvements */}
                <div className="performance-lists">

                  <div className="performance-list-card strengths-card">

                    <h4>
                      <ThumbsUp size={18} />
                      Strengths
                    </h4>

                    {performance.strengths?.length ? (
                      <ul>
                        {performance.strengths.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>No strengths identified.</p>
                    )}

                  </div>


                  <div className="performance-list-card improvements-card">

                    <h4>
                      <Lightbulb size={18} />
                      Areas for Improvement
                    </h4>

                    {performance.improvements?.length ? (
                      <ul>
                        {performance.improvements.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>No improvements suggested.</p>
                    )}

                  </div>

                </div>


                {/* Overall Feedback */}
                <div className="feedback-card">

                  <h4>
                    <TrendingUp size={18} />
                    Overall Feedback
                  </h4>

                  <p>
                    {performance.feedback ||
                      "No additional feedback available."}
                  </p>

                </div>

              </article>

            )}


            {/* Conversation */}
            <article className="transcript-card">

              <div className="section-heading">

                <div className="heading-icon">
                  <MessageSquareText size={19} />
                </div>

                <div>
                  <h3>Conversation</h3>

                  <p>
                    Agent and customer conversation with timestamps
                  </p>
                </div>

              </div>


              {conversation.length ? (

                <div className="conversation">

                  {conversation.map((segment, index) => {

                    const role = segment.speaker_role || "Unknown";
                    const alignment = speakerAlignment(role);

                    return (

                      <div
                        key={`${segment.start}-${segment.end}-${index}`}
                        className={`conversation-segment align-${alignment}`}
                      >

                        <div className="conversation-meta">

                          <span className="conversation-speaker">

                            {role === "Agent" ? (
                              <>
                                <Headset size={13} />
                                Agent
                              </>
                            ) : role === "Customer" ? (
                              <>
                                <UserRound size={13} />
                                Customer
                              </>
                            ) : (
                              role
                            )}

                          </span>


                          <span className="conversation-time">
                            {formatTimestamp(segment.start)} –{" "}
                            {formatTimestamp(segment.end)}
                          </span>

                        </div>


                        <p className="conversation-text">
                          {segment.text}
                        </p>

                      </div>

                    );

                  })}

                </div>

              ) : (

                <p className="transcript-text">
                  No conversation segments were returned.
                </p>

              )}

            </article>

          </section>

        )}


        {/* Footer */}
        <footer>
          CallSense AI · AI-assisted call quality analysis
        </footer>

      </main>

    </div>
  );
}


export default App;
