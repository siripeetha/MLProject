import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BrainCircuit, 
  Award, 
  BarChart2, 
  Layers, 
  CheckCircle2, 
  HelpCircle, 
  Zap, 
  ChevronRight,
  TrendingUp,
  Cpu
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

export default function DataMining() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('models'); // 'models', 'features', 'clustering', 'nlp'

  useEffect(() => {
    fetchMiningData();
  }, []);

  const fetchMiningData = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/data-mining');
      if (res.data.success) {
        setData(res.data);
      }
    } catch (err) {
      console.error('Error fetching data mining info:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center', color: '#94a3b8' }}>
          <BrainCircuit size={48} className="spin-slow" style={{ color: '#4f46e5', marginBottom: '16px' }} />
          <h3>Loading Colab Data Mining Models & Evaluation...</h3>
        </div>
      </div>
    );
  }

  const models = data?.models_comparison || [];
  const features = data?.feature_importance || [];
  const clusters = data?.clustering || [];
  const cm = data?.confusion_matrix || { classes: [], matrix: [] };

  return (
    <div className="page-container">
      {/* Header Banner */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(6, 182, 212, 0.1))', borderColor: 'rgba(79, 70, 229, 0.4)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge badge-shortlisted" style={{ fontSize: '0.75rem' }}>COLAB TRAINED ARTIFACTS</span>
              <span className="badge" style={{ backgroundColor: 'rgba(79, 70, 229, 0.2)', color: '#818cf8', border: '1px solid #4f46e5' }}>3 CLASSIFIERS EVALUATED</span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
              Data Mining & Machine Learning Pipeline
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              Trained on 5,200 candidate profiles in Google Colab. Evaluated using Stratified 5-Fold Cross Validation. Multi-class prediction: Shortlisted, Review, and Rejected.
            </p>
          </div>
          <div style={{ background: 'rgba(19, 31, 61, 0.8)', padding: '16px 24px', borderRadius: '12px', border: '1px solid #2d4580', textAlign: 'center' }}>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Best Selected Model</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '4px' }}>
              <Award size={20} /> Random Forest
            </div>
            <div style={{ fontSize: '0.8rem', color: '#06b6d4', marginTop: '2px' }}>F1-Score: 99.81% (Colab Validated)</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', borderBottom: '1px solid #233768', paddingBottom: '12px' }}>
        <button 
          className={`btn ${activeTab === 'models' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('models')}
        >
          <Award size={16} /> Model Comparison & Matrix
        </button>
        <button 
          className={`btn ${activeTab === 'features' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('features')}
        >
          <BarChart2 size={16} /> Feature Importance
        </button>
        <button 
          className={`btn ${activeTab === 'clustering' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('clustering')}
        >
          <Layers size={16} /> Candidate Clustering (K-Means)
        </button>
        <button 
          className={`btn ${activeTab === 'nlp' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('nlp')}
        >
          <BrainCircuit size={16} /> Text Mining & TF-IDF
        </button>
      </div>

      {/* TAB 1: MODEL COMPARISON & CONFUSION MATRIX */}
      {activeTab === 'models' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '24px' }}>
            {/* Model Comparison Table */}
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Award size={18} style={{ color: '#f59e0b' }} /> Supervised Model Benchmarking
              </h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Algorithm</th>
                      <th>Accuracy</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1 Score</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((m, idx) => {
                      const isBest = m.Model.includes('Random Forest');
                      return (
                        <tr key={idx} style={{ backgroundColor: isBest ? 'rgba(16, 185, 129, 0.08)' : 'transparent' }}>
                          <td style={{ fontWeight: 600, color: isBest ? '#10b981' : '#f1f5f9' }}>
                            {m.Model}
                          </td>
                          <td>{(m.Accuracy * 100).toFixed(2)}%</td>
                          <td>{(m.Precision * 100).toFixed(2)}%</td>
                          <td>{(m.Recall * 100).toFixed(2)}%</td>
                          <td style={{ fontWeight: 700, color: isBest ? '#10b981' : '#94a3b8' }}>
                            {(m['F1 Score'] * 100).toFixed(2)}%
                          </td>
                          <td>
                            {isBest ? (
                              <span className="badge badge-shortlisted">DEPLOYED BEST</span>
                            ) : (
                              <span className="badge badge-review">EVALUATED</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div style={{ marginTop: '16px', padding: '12px 16px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px', border: '1px solid #233768', fontSize: '0.82rem', color: '#94a3b8' }}>
                <strong>Why Random Forest?</strong> Random Forest constructs 100 decorrelated decision trees using bagging (bootstrap aggregation). It avoids overfitting on correlated skill features and handles non-linear interactions between TF-IDF similarity and years of experience.
              </div>
            </div>

            {/* Model Metrics Chart */}
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>
                F1 Score & Accuracy Comparison
              </h3>
              <div style={{ height: '260px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={models} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#233768" />
                    <XAxis dataKey="Model" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" domain={[0.9, 1.0]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#131f3d', borderColor: '#2d4580', color: '#f1f5f9' }}
                      formatter={(val) => [`${(val * 100).toFixed(2)}%`]}
                    />
                    <Bar dataKey="Accuracy" fill="#4f46e5" name="Accuracy" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="F1 Score" fill="#10b981" name="F1 Score" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Confusion Matrix Section */}
          <div className="card">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp size={18} style={{ color: '#06b6d4' }} /> Multi-Class Confusion Matrix (Test Set Validation: N = 1,040)
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '20px' }}>
              Evaluates actual class versus predicted class across 3 decision thresholds: REJECTED, REVIEW, SHORTLISTED.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', alignItems: 'center' }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '12px', border: '1px solid #233768', background: 'rgba(0,0,0,0.2)' }}>Actual \ Predicted</th>
                      {cm.classes.map((cls, i) => (
                        <th key={i} style={{ padding: '12px', border: '1px solid #233768', color: '#06b6d4', fontWeight: 600 }}>
                          Pred: {cls}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {cm.classes.map((actualClass, rowIdx) => (
                      <tr key={rowIdx}>
                        <td style={{ padding: '12px', border: '1px solid #233768', fontWeight: 600, color: '#f1f5f9', textAlign: 'left', background: 'rgba(0,0,0,0.1)' }}>
                          Act: {actualClass}
                        </td>
                        {cm.matrix[rowIdx]?.map((val, colIdx) => {
                          const isDiagonal = rowIdx === colIdx;
                          return (
                            <td 
                              key={colIdx} 
                              style={{ 
                                padding: '16px', 
                                border: '1px solid #233768', 
                                backgroundColor: isDiagonal ? 'rgba(16, 185, 129, 0.2)' : val > 0 ? 'rgba(239, 68, 68, 0.1)' : 'transparent',
                                color: isDiagonal ? '#10b981' : val > 0 ? '#ef4444' : '#64748b',
                                fontWeight: isDiagonal ? 700 : 400,
                                fontSize: '1.1rem'
                              }}
                            >
                              {val}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
                  <div style={{ fontWeight: 600, color: '#10b981', marginBottom: '4px' }}>Diagonal (True Positives): 1,033 / 1,040</div>
                  <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>99.32% of candidates were classified into their exact true shortlist tier without misalignment.</div>
                </div>
                <div style={{ padding: '12px 16px', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px' }}>
                  <div style={{ fontWeight: 600, color: '#f59e0b', marginBottom: '4px' }}>Off-Diagonal Misclassifications: 7 (0.68%)</div>
                  <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>All misclassifications occurred strictly on the boundary between Review (59.8) and Shortlisted (60.1), preventing any severe false positives.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FEATURE IMPORTANCE */}
      {activeTab === 'features' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '24px' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart2 size={18} style={{ color: '#4f46e5' }} /> Random Forest Gini Feature Importance
              </h3>
              <div style={{ height: '320px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={features} layout="vertical" margin={{ top: 10, right: 30, left: 80, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#233768" />
                    <XAxis type="number" stroke="#94a3b8" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                    <YAxis dataKey="feature" type="category" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#131f3d', borderColor: '#2d4580', color: '#f1f5f9' }}
                      formatter={(val) => [`${(val * 100).toFixed(2)}%`, 'Weight / Importance']}
                    />
                    <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                      {features.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#10b981' : index === 1 ? '#06b6d4' : '#4f46e5'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>
                Feature Impact Analysis
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {features.map((f, i) => (
                  <div key={i} style={{ padding: '12px 14px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{f.feature}</span>
                      <span style={{ fontWeight: 700, color: '#06b6d4' }}>{(f.importance * 100).toFixed(1)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${f.importance * 100 * 2.5}%`, backgroundColor: i === 0 ? '#10b981' : '#4f46e5' }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: CANDIDATE CLUSTERING */}
      {activeTab === 'clustering' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card" style={{ borderLeft: '4px solid #06b6d4' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '6px' }}>
              Unsupervised Candidate Segmentation (K-Means Clustering, K=4)
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>
              Candidate vector space clustered along Skill Match %, Experience Years, and TF-IDF Cosine Similarity. The optimal K=4 was determined via the Elbow Method (Inertia SSE curve) and Silhouette Analysis in Google Colab.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
            {clusters.map((c) => (
              <div key={c.cluster} className="card" style={{ borderColor: c.cluster === 0 ? '#10b981' : '#233768' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span className="badge" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4' }}>
                    CLUSTER #{c.cluster}
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{c.pct}%</span>
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '4px' }}>
                  {c.archetype}
                </h4>
                <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '14px' }}>
                  {c.label}
                </div>
                <div style={{ padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768', fontSize: '0.82rem', color: '#cbd5e1' }}>
                  <strong style={{ color: '#06b6d4' }}>HR Strategy:</strong> {c.recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: NLP & TEXT MINING */}
      {activeTab === 'nlp' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card">
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={20} style={{ color: '#4f46e5' }} /> Resume Text Mining & Vector Space Architecture
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
              <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid #233768' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#06b6d4', marginBottom: '8px' }}>1. Preprocessing & Lemmatization</h4>
                <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#94a3b8', lineHeight: '1.6' }}>
                  <li>Regex pattern matching strips email, phone, and non-ASCII glyphs.</li>
                  <li>Lowercasing and NLTK English stopword filtering.</li>
                  <li>Skill dictionary synonym normalization (e.g. <code>k8s</code> → <code>kubernetes</code>, <code>react.js</code> → <code>react</code>).</li>
                </ul>
              </div>

              <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid #233768' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#4f46e5', marginBottom: '8px' }}>2. TF-IDF Vectorizer</h4>
                <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#94a3b8', lineHeight: '1.6' }}>
                  <li>Vocabulary: Top 5,000 sub-linear term frequencies.</li>
                  <li>N-gram range: Unigrams and Bigrams <code>(1, 2)</code> to capture compound tech stacks (e.g. "machine learning", "rest api").</li>
                  <li>L2 vector normalization to penalize lengthy, keyword-stuffed resumes.</li>
                </ul>
              </div>

              <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid #233768' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#10b981', marginBottom: '8px' }}>3. Cosine Similarity Metric</h4>
                <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#94a3b8', lineHeight: '1.6' }}>
                  <li>Measures the angular cosine distance between the Resume vector R and Job Description vector J.</li>
                  <li>Formula: <code>cos(θ) = (R · J) / (||R|| ||J||)</code>.</li>
                  <li>Independent of document length; focuses purely on contextual semantic overlap.</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
