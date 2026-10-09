
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
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

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
      if (!response.ok) throw new Error(data.detail || "Analysis failed.");
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  const analysis = result?.analysis;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Headphones size={23} /></div>
          <div><h2>CallSense AI</h2><span>QUALITY INTELLIGENCE</span></div>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active"><Activity size={18} />Call analysis</div>
        <div className="sidebar-bottom"><div className="status-dot" /><span>AI analysis workspace</span></div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div><div className="eyebrow">CALL CENTER INTELLIGENCE</div><h1>Call Analysis</h1></div>
          <div className="live-status"><span className="status-dot" />Backend integration</div>
        </header>

        <section className="welcome">
          <div>
            <span className="eyebrow light">AI-POWERED QUALITY REVIEW</span>
            <h2>Understand every customer conversation.</h2>
            <p>Upload a call recording to generate a transcript and AI-powered insights.</p>
          </div>
          <div className="welcome-icon"><Headphones size={48} /></div>
        </section>

        <section className="upload-card">
          <div className="section-heading">
            <div className="heading-icon"><Upload size={19} /></div>
            <div><h3>Analyze a call</h3><p>Supported formats: WAV, MP3, M4A and OGG</p></div>
          </div>
          <form onSubmit={analyzeCall}>
            <label className="drop-zone">
              <input type="file" accept=".wav,.mp3,.m4a,.ogg,audio/*"
                onChange={(event) => {
                  setFile(event.target.files?.[0] || null);
                  setError("");
                  setResult(null);
                }} />
              <div className="upload-icon"><FileAudio size={27} /></div>
              <strong>{file ? file.name : "Choose a call recording"}</strong>
              <span>{file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : "Click here to browse files on your computer"}</span>
            </label>
            <button className="analyze-button" type="submit" disabled={loading}>
              {loading ? <><LoaderCircle className="spin" size={18} />Analyzing call...</> : <><Activity size={18} />Analyze call</>}
            </button>
          </form>
          {error && <div className="error-message"><AlertCircle size={18} />{error}</div>}
        </section>

        {loading && <div className="loading-note">Transcribing the recording and generating AI insights. This may take a little while.</div>}

        {result && analysis && (
          <section className="results-section">
            <div className="results-title">
              <div><div className="eyebrow">ANALYSIS REPORT</div><h2>Call insights</h2><p>Results for {result.filename}</p></div>
              <div className="success-badge"><CheckCircle2 size={16} />Analysis complete</div>
            </div>
            <div className="insight-grid">
              <article className="insight-card summary-card">
                <div className="card-icon purple"><MessageSquareText size={20} /></div>
                <div className="eyebrow">CALL SUMMARY</div><p>{analysis.summary}</p>
              </article>
              <article className="insight-card">
                <div className="card-icon orange"><Activity size={20} /></div>
                <div className="eyebrow">CUSTOMER SENTIMENT</div>
                <div className={`sentiment ${analysis.sentiment?.toLowerCase()}`}>{analysis.sentiment}</div>
              </article>
              <article className="insight-card">
                <div className="card-icon blue"><Target size={20} /></div>
                <div className="eyebrow">CUSTOMER INTENT</div><p>{analysis.customer_intent}</p>
              </article>
              <article className="insight-card">
                <div className="card-icon green"><ListChecks size={20} /></div>
                <div className="eyebrow">KEY ISSUES</div>
                {analysis.key_issues?.length ? <ul>{analysis.key_issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul> : <p>No key issues identified.</p>}
              </article>
            </div>
            <article className="transcript-card">
              <div className="section-heading">
                <div className="heading-icon"><MessageSquareText size={19} /></div>
                <div><h3>Full transcript</h3><p>Text generated from the call recording</p></div>
              </div>
              <p className="transcript-text">{result.transcript}</p>
            </article>
          </section>
        )}
        <footer>CallSense AI · AI-assisted call quality analysis</footer>
      </main>
    </div>
  );
}

export default App;
