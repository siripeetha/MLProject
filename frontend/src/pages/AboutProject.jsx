import React, { useState } from 'react';
import { 
  Info, 
  HelpCircle, 
  BookOpen, 
  Award, 
  CheckCircle2, 
  Layers, 
  Database, 
  Cpu, 
  Workflow, 
  ChevronDown, 
  ChevronUp,
  FileCode,
  BrainCircuit
} from 'lucide-react';

export default function AboutProject() {
  const [openFaq, setOpenFaq] = useState(null);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const vivaQuestions = [
    {
      q: '1. What was the core problem solved by this project?',
      a: 'Manual resume screening in high-volume enterprise recruitment is subjective, slow, and prone to cognitive bias. This project integrates Data Mining (NLP text preprocessing, TF-IDF vector space modeling, Cosine Similarity, and Random Forest classification) with an enterprise Data Warehouse (Kimball Star Schema) to provide automated, unbiased, multi-criteria candidate shortlisting and multidimensional OLAP recruitment intelligence.'
    },
    {
      q: '2. Why did Random Forest outperform Decision Trees and Logistic Regression?',
      a: 'Random Forest achieved 99.81% F1-score because it is an ensemble bagging method that builds 100 decorrelated decision trees. Individual decision trees suffered high variance and overfit on correlated tech skill combinations, while linear Logistic Regression struggled to capture non-linear boundary interactions (e.g. high experience compensating for a slight skill gap). Bagging effectively smoothed boundary variance.'
    },
    {
      q: '3. Why is TF-IDF + Cosine Similarity preferred over simple keyword counting?',
      a: 'Simple keyword counting rewards "keyword stuffing" where an unqualified applicant repeats tech terms 50 times. TF-IDF applies Term Frequency with sub-linear logarithmic dampening and penalizes pervasive generic terms via Inverse Document Frequency. Cosine Similarity calculates the angle between L2-normalized vectors (cos θ = (A · B) / (||A|| ||B||)), rendering the match score independent of resume document length.'
    },
    {
      q: '4. How was the Candidate Composite Score formulated?',
      a: 'We developed a multi-criteria weighted scoring formula: Overall Score = (Skill Match % × 0.35) + (Experience Match % × 0.25) + (TF-IDF Cosine Similarity × 100 × 0.20) + (Education Tier Score × 0.10) + (Project Quality Score × 0.05) + (Certification Score × 0.05). Thresholds: Score ≥ 80 → SHORTLISTED, 60–79 → REVIEW, < 60 → REJECTED.'
    },
    {
      q: '5. What is the Star Schema design used in the Data Warehouse?',
      a: 'The warehouse implements a Kimball Star Schema with a central Fact table (fact_candidate_analysis) at the atomic grain of one candidate application event. It connects via surrogate foreign keys to 6 Dimension tables: dim_candidate (demographics), dim_job (requisition details), dim_skill (skill taxonomy), dim_date (calendar hierarchy), dim_education (degree tiers), and dim_experience (tenure tiers).'
    },
    {
      q: '6. What OLAP operations are implemented and what business questions do they answer?',
      a: 'Four canonical OLAP operations are supported: (1) Roll-up: Aggregates monthly applicant volumes to quarterly and yearly executive totals; (2) Drill-down: Deconstructs high-level annual recruitment metrics into detailed monthly and job-role breakdowns; (3) Slice: Filters the data cube along a single dimension hyperplane (e.g., all applicants where Job Role = "Data Scientist"); (4) Dice: Extracts an arbitrary sub-cube across multiple dimensions simultaneously (e.g., Role = "Python Developer" AND Experience = "3-5 years" AND Score ≥ 70).'
    },
    {
      q: '7. How was Unsupervised K-Means Clustering utilized?',
      a: 'K-Means clustering (K=4, determined using the Elbow Method and Silhouette Analysis) segmented candidates into 4 actionable talent archetypes: Cluster 0 (Top-Tier Talent: High Skill / High Exp), Cluster 1 (High-Potential Freshers: High Skill / Low Exp), Cluster 2 (Career Pivots: Low Skill / High Exp), and Cluster 3 (Unqualified: Low Skill / Low Exp). This provides HR with automated interview routing strategies.'
    },
    {
      q: '8. How are uploaded PDF and DOCX resumes parsed in the website?',
      a: 'The Flask backend utilizes PyPDF2 and python-docx to extract text streams directly from memory buffers. Regular expressions extract candidate name, email, and phone numbers. The raw resume text is then fed through the exact NLP cleaner and TF-IDF pipeline serialized from Google Colab, computing feature scores and feeding them to the trained classifier.'
    }
  ];

  return (
    <div className="page-container">
      {/* Banner */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(6, 182, 212, 0.15))', borderColor: 'rgba(79, 70, 229, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span className="badge badge-shortlisted">ACADEMIC CAPSTONE PROJECT</span>
          <span className="badge" style={{ backgroundColor: 'rgba(79, 70, 229, 0.25)', color: '#818cf8', border: '1px solid #4f46e5' }}>
            DATA MINING & WAREHOUSING
          </span>
        </div>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', marginBottom: '8px' }}>
          Resume Shortlisting and Candidate Analytics System
        </h2>
        <p style={{ color: '#cbd5e1', fontSize: '0.92rem', maxWidth: '850px', lineHeight: '1.6' }}>
          A complete, end-to-end integrated recruitment intelligence solution bridging Google Colab Data Mining and Machine Learning workflows with a Kimball Star Schema Data Warehouse, modern Flask REST API, MongoDB document store, and React analytical dashboard.
        </p>
      </div>

      {/* Architecture Overview */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Workflow size={20} style={{ color: '#06b6d4' }} /> End-to-End System Architecture
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
            <div style={{ fontSize: '0.72rem', color: '#06b6d4', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Phase 1: Colab AI Lab</div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>Data Mining & Modeling</h4>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.5' }}>
              Dataset generation (5,200 rows), NLTK NLP preprocessing, TF-IDF vectorization, Cosine similarity, 3 classification models benchmarking, K-Means clustering, and pickle export.
            </p>
          </div>

          <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
            <div style={{ fontSize: '0.72rem', color: '#10b981', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Phase 1: Warehousing</div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>Kimball Star Schema</h4>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.5' }}>
              ETL dimension generation (Candidate, Job, Skill, Date, Education, Experience), 1 central Fact table, data quality validation audit, and materialization.
            </p>
          </div>

          <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
            <div style={{ fontSize: '0.72rem', color: '#818cf8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Phase 2: Backend</div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>Flask REST API & Services</h4>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.5' }}>
              PyPDF2 / Docx stream parsing, exact Colab pipeline execution, live MongoDB candidate persistence, warehouse table search/pagination, and OLAP cube engine.
            </p>
          </div>

          <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
            <div style={{ fontSize: '0.72rem', color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Phase 2: Frontend</div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>React Analytics Website</h4>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.5' }}>
              11 functional views: Resume upload, live scoring, candidate ranking, shortlisted talent, jobs, data mining dashboard, star schema explorer, ETL flowchart, and OLAP console.
            </p>
          </div>
        </div>
      </div>

      {/* Tech Stack Matrix */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileCode size={20} style={{ color: '#10b981' }} /> Technology Stack Matrix
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          <div style={{ padding: '14px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#06b6d4', fontWeight: 600, marginBottom: '6px' }}>Data Mining & Machine Learning</h4>
            <ul style={{ fontSize: '0.82rem', color: '#94a3b8', paddingLeft: '18px', lineHeight: '1.6' }}>
              <li><strong>Scikit-Learn:</strong> RandomForestClassifier, DecisionTreeClassifier, LogisticRegression, KMeans, TfidfVectorizer</li>
              <li><strong>NLTK:</strong> Stopwords, Word Tokenizer, PorterStemmer</li>
              <li><strong>Joblib:</strong> Serialization of pipelines and trained models</li>
            </ul>
          </div>

          <div style={{ padding: '14px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#818cf8', fontWeight: 600, marginBottom: '6px' }}>Data Warehouse & Storage</h4>
            <ul style={{ fontSize: '0.82rem', color: '#94a3b8', paddingLeft: '18px', lineHeight: '1.6' }}>
              <li><strong>Pandas:</strong> Fact & Dimension ETL, in-memory OLAP Cube</li>
              <li><strong>MongoDB:</strong> Document storage for candidate pool & job requisitions</li>
              <li><strong>Star Schema:</strong> 6 Dimensions + 1 Central Fact table</li>
            </ul>
          </div>

          <div style={{ padding: '14px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: 600, marginBottom: '6px' }}>Web Application & Visualization</h4>
            <ul style={{ fontSize: '0.82rem', color: '#94a3b8', paddingLeft: '18px', lineHeight: '1.6' }}>
              <li><strong>React 19 & Vite:</strong> Fast modular single-page interface</li>
              <li><strong>Flask & Flask-CORS:</strong> High-performance Python REST API</li>
              <li><strong>Recharts & Lucide:</strong> Dynamic analytics charts & modern iconography</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Viva Voce Guide Accordion */}
      <div className="card">
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={20} style={{ color: '#f59e0b' }} /> Project Viva Voce & Defense Q&A Guide
        </h3>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '20px' }}>
          Comprehensive academic explanations covering every foundational concept in Data Mining, Data Warehousing, and NLP used in this project.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {vivaQuestions.map((item, idx) => {
            const isOpen = openFaq === idx;
            return (
              <div 
                key={idx} 
                style={{ 
                  background: isOpen ? 'rgba(79, 70, 229, 0.12)' : 'rgba(19, 31, 61, 0.6)', 
                  border: isOpen ? '1px solid #4f46e5' : '1px solid #233768', 
                  borderRadius: '8px', 
                  overflow: 'hidden',
                  transition: 'all 0.2s ease'
                }}
              >
                <div 
                  onClick={() => toggleFaq(idx)}
                  style={{ 
                    padding: '14px 18px', 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: '0.92rem', color: isOpen ? '#a5b4fc' : '#f1f5f9' }}>
                    {item.q}
                  </span>
                  {isOpen ? <ChevronUp size={18} style={{ color: '#a5b4fc' }} /> : <ChevronDown size={18} style={{ color: '#64748b' }} />}
                </div>

                {isOpen && (
                  <div style={{ padding: '0 18px 16px 18px', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6', borderTop: '1px solid rgba(79, 70, 229, 0.2)', paddingTop: '12px' }}>
                    {item.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
