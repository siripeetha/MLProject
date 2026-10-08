import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, 
  CheckCircle2, 
  XCircle, 
  Award, 
  UploadCloud, 
  BarChart3, 
  RefreshCw,
  AlertCircle,
  Check
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';

export default function Dashboard({ setActiveTab }) {
  const [metrics, setMetrics] = useState({
    total_candidates: 0,
    selected_candidates: 0,
    rejected_candidates: 0,
    average_score: 0.0,
    candidate_scores: []
  });
  const [loading, setLoading] = useState(false);
  const [refreshSuccess, setRefreshSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  useEffect(() => {
    fetchDashboardData(false);
  }, []);

  const fetchDashboardData = async (isManual = false) => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get('/api/dashboard', {
        headers: { 'Cache-Control': 'no-cache' }
      });
      if (res.data.success && res.data.data) {
        setMetrics(res.data.data);
        const timeStr = new Date().toLocaleTimeString();
        setLastRefreshed(timeStr);
        if (isManual) {
          setRefreshSuccess(true);
          setTimeout(() => setRefreshSuccess(false), 2000);
        }
      } else {
        setError('Server responded, but could not load dashboard metrics.');
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(
        'Backend server connection failed. Please ensure the Flask backend is running on port 5000 (run_backend.bat or python backend/app.py).'
      );
    } finally {
      setLoading(false);
    }
  };

  const total = metrics.total_candidates || 0;
  const selected = metrics.selected_candidates || 0;
  const rejected = metrics.rejected_candidates || 0;
  const avgScore = metrics.average_score || 0.0;
  
  // Guarantee alphabetical order by candidate_name for the Dashboard graph
  const candidateScores = (metrics.candidate_scores || [])
    .slice()
    .sort((a, b) => (a.candidate_name || '').localeCompare(b.candidate_name || ''));

  return (
    <div className="page-container">
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff' }}>
            Recruitment Screening Dashboard
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
            Live applicant analytics powered by Google Colab Data Mining and Machine Learning.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {lastRefreshed && (
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Last updated: {lastRefreshed}
            </span>
          )}

          <button 
            className="btn btn-secondary" 
            onClick={() => fetchDashboardData(true)} 
            disabled={loading}
            title="Fetch latest data from database"
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              backgroundColor: refreshSuccess ? 'rgba(16, 185, 129, 0.2)' : undefined,
              borderColor: refreshSuccess ? '#10b981' : undefined,
              color: refreshSuccess ? '#10b981' : undefined,
              transition: 'all 0.2s ease'
            }}
          >
            {refreshSuccess ? (
              <>
                <Check size={14} color="#10b981" /> Refreshed!
              </>
            ) : (
              <>
                <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
                <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
              </>
            )}
          </button>

          <button 
            className="btn btn-primary" 
            onClick={() => setActiveTab('analyzer')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <UploadCloud size={16} /> Analyze Resume
          </button>
        </div>
      </div>

      {/* Backend Connection Error Banner if down */}
      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid #ef4444',
          color: '#fca5a5',
          padding: '12px 18px',
          borderRadius: '8px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.88rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={20} color="#ef4444" style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
          <button 
            onClick={() => fetchDashboardData(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.78rem', marginLeft: '12px', whiteSpace: 'nowrap' }}
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="stats-grid" style={{ marginBottom: '28px' }}>
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Total Candidates</span>
            <Users size={20} style={{ color: '#4f46e5' }} />
          </div>
          <div className="stat-value">{total}</div>
          <div className="stat-desc">Analyzed from database</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Selected Candidates</span>
            <CheckCircle2 size={20} style={{ color: '#10b981' }} />
          </div>
          <div className="stat-value" style={{ color: '#10b981' }}>{selected}</div>
          <div className="stat-desc">Met selection threshold</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Rejected Candidates</span>
            <XCircle size={20} style={{ color: '#ef4444' }} />
          </div>
          <div className="stat-value" style={{ color: '#ef4444' }}>{rejected}</div>
          <div className="stat-desc">Did not meet criteria</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Average Score</span>
            <Award size={20} style={{ color: '#06b6d4' }} />
          </div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>
            {total > 0 ? avgScore : '0'}
          </div>
          <div className="stat-desc">Composite evaluation score</div>
        </div>
      </div>

      {/* Bar Graph Section */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={20} style={{ color: '#4f46e5' }} /> Candidate Scores
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              Scores sorted alphabetically by candidate name on the X-axis (0–100 scale).
            </p>
          </div>

          {candidateScores.length > 0 && (
            <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '3px', display: 'inline-block' }}></span>
                <span style={{ color: '#cbd5e1' }}>Selected</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#ef4444', borderRadius: '3px', display: 'inline-block' }}></span>
                <span style={{ color: '#cbd5e1' }}>Rejected</span>
              </div>
            </div>
          )}
        </div>

        {candidateScores.length === 0 ? (
          /* Empty State when no candidates in DB */
          <div style={{ 
            padding: '60px 20px', 
            textAlign: 'center', 
            background: 'rgba(11, 19, 41, 0.4)', 
            borderRadius: '10px', 
            border: '1px dashed #233768' 
          }}>
            <AlertCircle size={44} style={{ color: '#64748b', marginBottom: '12px' }} />
            <h4 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: 600, marginBottom: '6px' }}>
              No Candidate Data
            </h4>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', maxWidth: '420px', margin: '0 auto 20px auto' }}>
              No candidates have been analyzed yet. Upload a resume in the Resume Analyzer to calculate candidate scores and generate the graph.
            </p>
            <button 
              className="btn btn-primary" 
              onClick={() => setActiveTab('analyzer')}
            >
              <UploadCloud size={16} style={{ marginRight: '6px' }} /> Upload Your First Resume
            </button>
          </div>
        ) : (
          /* Live Recharts Bar Graph */
          <div style={{ height: '360px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={candidateScores} margin={{ top: 20, right: 30, left: 10, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#233768" vertical={false} />
                <XAxis 
                  dataKey="candidate_name" 
                  stroke="#94a3b8" 
                  tick={{ fill: '#cbd5e1', fontSize: 12, fontWeight: 500 }}
                  angle={-15}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis 
                  domain={[0, 100]} 
                  stroke="#94a3b8" 
                  tick={{ fill: '#94a3b8', fontSize: 12 }} 
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#131f3d', 
                    borderColor: '#2d4580', 
                    borderRadius: '8px', 
                    color: '#f1f5f9',
                    boxShadow: '0 4px 14px rgba(0,0,0,0.4)'
                  }}
                  formatter={(value, name, item) => [
                    `${value} / 100 (Status: ${item.payload.status})`, 
                    'Candidate Score'
                  ]}
                />
                <Bar dataKey="score" radius={[6, 6, 0, 0]} barSize={42}>
                  {candidateScores.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.status === 'Selected' ? '#10b981' : '#ef4444'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Candidate Scores Table View */}
      {candidateScores.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>
            Candidate Scores Overview
          </h3>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Candidate Name</th>
                  <th>Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {candidateScores.map((c, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{c.candidate_name}</td>
                    <td style={{ fontWeight: 700, color: c.score >= 75 ? '#10b981' : '#f1f5f9' }}>
                      {c.score} / 100
                    </td>
                    <td>
                      <span className={`badge ${c.status === 'Selected' ? 'badge-shortlisted' : 'badge-rejected'}`}>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
