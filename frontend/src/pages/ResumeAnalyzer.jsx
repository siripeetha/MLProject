import React, { useState } from 'react';
import axios from 'axios';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  ArrowRight,
  LayoutDashboard,
  Trophy,
  Tag
} from 'lucide-react';

const JOB_ROLES = [
  "Java Developer",
  "Python Developer",
  "Data Analyst",
  "Data Scientist",
  "Web Developer",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Software Engineer",
  "Database Developer"
];

const JOB_DESCRIPTIONS = {
  "Java Developer": "Looking for an experienced Java Developer proficient in Core Java, Spring Boot microservices, Hibernate, SQL databases, Git, Docker, and AWS cloud deployment. Responsible for building resilient enterprise backend services and RESTful APIs.",
  "Python Developer": "Seeking a Python Developer to build scalable backend systems, microservices, and automation pipelines using Python, SQL databases, Git, Docker, and AWS. Strong grasp of data structures and algorithms (DSA) required.",
  "Data Analyst": "Hiring a Data Analyst skilled in Python, SQL query optimization, data cleaning with Pandas and NumPy, and creating interactive BI dashboards using Tableau and Power BI. Experience translating data into business insights is essential.",
  "Data Scientist": "We are hiring a Data Scientist to develop statistical and predictive models using Python, Scikit-learn, Pandas, and NumPy, with advanced machine learning, deep learning architectures, and SQL data warehousing.",
  "Web Developer": "Seeking a Web Developer with solid expertise in modern web technologies including HTML, CSS, JavaScript, React for frontend interfaces, Node.js for backend runtime, and Git version control.",
  "Frontend Developer": "Looking for a Frontend Developer passionate about UI/UX to build high-performance web applications using JavaScript, React, HTML, CSS, Git, and GitHub. Experience with responsive layout design required.",
  "Backend Developer": "Hiring a Backend Developer to architect secure and scalable microservices using Python or Java, Spring Boot, PostgreSQL, SQL, Docker, and Git. Focused on high throughput and reliable database integration.",
  "Full Stack Developer": "Looking for a versatile Full Stack Developer experienced across the entire software stack: React and JavaScript on frontend, Node.js or Python backend, SQL database modeling, Docker containers, and Git.",
  "Software Engineer": "Seeking a Software Engineer with strong computer science fundamentals, data structures and algorithms (DSA), and proficiency in Java, Python, C++, SQL, and Git to develop mission-critical distributed software systems.",
  "Database Developer": "Hiring a Database Developer to design, optimize, and maintain relational and NoSQL databases using SQL, MySQL, PostgreSQL, MongoDB, with Python scripting and Git for schema migrations."
};

export default function ResumeAnalyzer({ setActiveTab }) {
  const [selectedRole, setSelectedRole] = useState("Python Developer");
  const [jobDescription, setJobDescription] = useState(JOB_DESCRIPTIONS["Python Developer"]);
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    setJobDescription(JOB_DESCRIPTIONS[role] || "");
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !resumeText.trim()) {
      setError("Please select a resume file (PDF/DOCX/TXT) or paste resume text.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    if (file) {
      formData.append("file", file);
    }
    formData.append("resume_text", resumeText);
    formData.append("job_role", selectedRole);
    formData.append("job_description", jobDescription);

    try {
      const res = await axios.post("/api/analyze-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      if (res.data.success) {
        setResult(res.data.candidate);
      } else {
        setError(res.data.error || "Analysis failed.");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Error analyzing resume. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff' }}>
          Resume Analyzer & Candidate Evaluation
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
          Upload a resume PDF to run extraction, TF-IDF cosine matching, and our trained machine learning classification model.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '24px' }}>
        {/* Upload Form Card */}
        <div className="card">
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>
            Resume Ingestion & Target Role
          </h3>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Target Job Role</label>
              <select 
                className="form-select" 
                value={selectedRole} 
                onChange={(e) => handleRoleChange(e.target.value)}
              >
                {JOB_ROLES.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Job Description & Requirements</label>
              <textarea 
                className="form-textarea" 
                rows={3} 
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Enter job requirements..."
              />
            </div>

            <div className="form-group">
              <label className="form-label">Upload Resume PDF / Document</label>
              <div 
                style={{
                  border: '2px dashed #2d4580',
                  borderRadius: '12px',
                  padding: '28px 16px',
                  textAlign: 'center',
                  backgroundColor: 'rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  position: 'relative'
                }}
              >
                <input 
                  type="file" 
                  accept=".pdf,.docx,.doc,.txt" 
                  onChange={handleFileChange}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    opacity: 0,
                    cursor: 'pointer'
                  }}
                />
                <UploadCloud size={40} color="#06b6d4" style={{ margin: '0 auto 8px' }} />
                <p style={{ fontWeight: 600, color: '#fff', fontSize: '0.95rem' }}>
                  {file ? file.name : "Click to browse or drop resume PDF here"}
                </p>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  Accepts PDF, DOCX, TXT files
                </span>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Or Paste Resume Text (Optional)</label>
              <textarea 
                className="form-textarea" 
                rows={3}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste candidate resume plain text..."
              />
            </div>

            {error && (
              <div style={{ color: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '0.88rem' }}>
                {error}
              </div>
            )}

            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '1rem' }}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Sparkles size={18} className="spin-slow" /> Analyzing Candidate Resume...
                </>
              ) : (
                <>
                  <Sparkles size={18} /> Analyze Resume
                </>
              )}
            </button>
          </form>
        </div>

        {/* Real-Time Scorecard Result Card */}
        {result && (
          <div className="card" style={{ borderColor: result.status === 'Selected' ? '#10b981' : '#ef4444' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', borderBottom: '1px solid #233768', paddingBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#06b6d4', textTransform: 'uppercase', fontWeight: 700 }}>
                  Analysis Outcome
                </span>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                  {result.candidate_name || result.candidateName}
                </h3>
                <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                  {result.job_role} • {result.email || 'Candidate Contact Recorded'}
                </span>
              </div>

              <div>
                <span 
                  className={`badge ${result.status === 'Selected' ? 'badge-shortlisted' : 'badge-rejected'}`}
                  style={{ fontSize: '1rem', padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  {result.status === 'Selected' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                  {result.status}
                </span>
              </div>
            </div>

            {/* Resume Score Card */}
            <div style={{ 
              backgroundColor: 'rgba(0, 0, 0, 0.25)', 
              borderRadius: '10px', 
              padding: '16px 20px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              marginBottom: '20px',
              border: '1px solid #233768'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Resume Score</span>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, color: result.status === 'Selected' ? '#10b981' : '#ef4444' }}>
                  {result.score || result.overall_score} / 100
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Saved File:</span>
                <div style={{ color: '#06b6d4', fontWeight: 600, fontSize: '0.85rem' }}>
                  {result.resume_filename || result.resumeFileName || 'resume.pdf'}
                </div>
                <span style={{ fontSize: '0.75rem', color: '#10b981', display: 'block', marginTop: '4px' }}>
                  ✓ Permanently Stored in DB
                </span>
              </div>
            </div>

            {/* Recommendation Box */}
            <div style={{ 
              backgroundColor: result.status === 'Selected' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
              borderLeft: `4px solid ${result.status === 'Selected' ? '#10b981' : '#ef4444'}`, 
              padding: '12px 16px', 
              borderRadius: '4px',
              marginBottom: '20px'
            }}>
              <span style={{ fontSize: '0.78rem', color: result.status === 'Selected' ? '#10b981' : '#f87171', fontWeight: 700 }}>
                SELECTION RECOMMENDATION:
              </span>
              <p style={{ fontSize: '0.88rem', color: '#f1f5f9', marginTop: '4px' }}>
                {result.recommendation}
              </p>
            </div>

            {/* Skills Breakdown */}
            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#10b981', display: 'block', marginBottom: '8px' }}>
                Relevant / Matched Skills ({(result.matched_skills || []).length}):
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(result.matched_skills && result.matched_skills.length > 0) ? (
                  result.matched_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-shortlisted" style={{ fontSize: '0.8rem' }}>
                      {s}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>None matched</span>
                )}
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f87171', display: 'block', marginBottom: '8px' }}>
                Missing Requisite Skills ({(result.missing_skills || []).length}):
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(result.missing_skills && result.missing_skills.length > 0) ? (
                  result.missing_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-rejected" style={{ fontSize: '0.8rem' }}>
                      {s}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8rem', color: '#10b981' }}>All required skills present!</span>
                )}
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#06b6d4', display: 'block', marginBottom: '8px' }}>
                All Skills Detected on Resume ({(result.skills || []).length}):
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(result.skills && result.skills.length > 0) ? (
                  result.skills.map((s, idx) => (
                    <span key={idx} className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.06)', color: '#e2e8f0', fontSize: '0.78rem' }}>
                      {s}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>No technical skills detected</span>
                )}
              </div>
            </div>

            {/* Quick Navigation Buttons */}
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button 
                className="btn btn-primary" 
                onClick={() => setActiveTab('dashboard')}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <LayoutDashboard size={16} /> View on Dashboard
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => setActiveTab('candidates')}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <Trophy size={16} /> View Candidate Ranking
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => { setResult(null); setFile(null); setResumeText(''); }}
              >
                Analyze Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
