import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Trophy, 
  Search, 
  Eye, 
  Trash2, 
  UploadCloud, 
  CheckCircle2, 
  XCircle, 
  FileText,
  Calendar,
  X,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

export default function Candidates({ setActiveTab }) {
  const [candidates, setCandidates] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  useEffect(() => {
    fetchCandidates();
  }, [search, statusFilter]);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/candidates', {
        params: {
          search,
          status: statusFilter,
          sort_by: 'score',
          sort_order: 'desc',
          limit: 100
        }
      });
      if (res.data.success) {
        setCandidates(res.data.candidates || []);
        setTotal(res.data.total || 0);
      }
    } catch (err) {
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (candId, name) => {
    if (!window.confirm(`Delete candidate "${name}" from database?`)) return;
    try {
      await axios.delete(`/api/candidates/${candId}`);
      fetchCandidates();
      if (selectedCandidate && selectedCandidate.candidate_id === candId) {
        setSelectedCandidate(null);
      }
    } catch (err) {
      console.error(err);
      alert('Error deleting candidate.');
    }
  };

  return (
    <div className="page-container">
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff' }}>
            Candidate Ranking
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
            Live applicant leaderboard sorted primarily by resume score in descending order.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', color: '#06b6d4', fontWeight: 600 }}>
            Total Analyzed: {total}
          </span>
          <button 
            className="btn btn-secondary" 
            onClick={() => fetchCandidates(true)} 
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
            <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
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

      {/* Filter and Search Bar */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', alignItems: 'center' }}>
          <div className="search-box">
            <Search size={16} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search by candidate name or skill..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div>
            <select 
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="All">All Statuses</option>
              <option value="Selected">Selected Only</option>
              <option value="Rejected">Rejected Only</option>
            </select>
          </div>

          {(search || statusFilter !== 'All') && (
            <button 
              className="btn btn-secondary" 
              onClick={() => { setSearch(''); setStatusFilter('All'); }}
              style={{ width: 'fit-content' }}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Leaderboard Table or Empty State */}
      <div className="card">
        {loading ? (
          <div style={{ padding: '60px 20px', textAlign: 'center', color: '#94a3b8' }}>
            Loading candidates from database...
          </div>
        ) : candidates.length === 0 ? (
          /* Exact Initial Empty State */
          <div style={{ 
            padding: '70px 20px', 
            textAlign: 'center', 
            background: 'rgba(11, 19, 41, 0.4)', 
            borderRadius: '10px' 
          }}>
            <AlertCircle size={44} style={{ color: '#64748b', marginBottom: '12px' }} />
            <h4 style={{ color: '#f1f5f9', fontSize: '1.15rem', fontWeight: 600, marginBottom: '6px' }}>
              No candidates analyzed yet.
            </h4>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', maxWidth: '420px', margin: '0 auto 20px auto' }}>
              When resumes are uploaded and processed in the Resume Analyzer, candidates will automatically appear here ranked by their score.
            </p>
            <button 
              className="btn btn-primary" 
              onClick={() => setActiveTab('analyzer')}
            >
              <UploadCloud size={16} style={{ marginRight: '6px' }} /> Upload Resume
            </button>
          </div>
        ) : (
          /* Populated Dynamic Ranking Table */
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '70px' }}>Rank</th>
                  <th>Candidate Name</th>
                  <th>Score</th>
                  <th>Status</th>
                  <th>Resume</th>
                  <th>Date</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((c) => (
                  <tr key={c.candidate_id}>
                    {/* Rank */}
                    <td>
                      <span 
                        style={{ 
                          fontWeight: 800, 
                          fontFamily: 'var(--font-mono)', 
                          fontSize: '1rem',
                          color: c.rank === 1 ? '#fbbf24' : c.rank === 2 ? '#94a3b8' : c.rank === 3 ? '#cd7f32' : '#64748b',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        {c.rank === 1 && <Trophy size={14} color="#fbbf24" />}
                        #{c.rank}
                      </span>
                    </td>

                    {/* Candidate Name */}
                    <td>
                      <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.95rem' }}>
                        {c.candidate_name || c.candidateName}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        {c.job_role || 'General Role'} {c.email ? `• ${c.email}` : ''}
                      </div>
                    </td>

                    {/* Score */}
                    <td>
                      <span 
                        style={{ 
                          fontWeight: 700, 
                          fontSize: '1.05rem', 
                          fontFamily: 'var(--font-mono)',
                          color: c.status === 'Selected' ? '#10b981' : '#f1f5f9' 
                        }}
                      >
                        {c.score}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}> / 100</span>
                    </td>

                    {/* Status */}
                    <td>
                      <span className={`badge ${c.status === 'Selected' ? 'badge-shortlisted' : 'badge-rejected'}`}>
                        {c.status === 'Selected' ? <CheckCircle2 size={12} style={{ marginRight: '4px' }} /> : <XCircle size={12} style={{ marginRight: '4px' }} />}
                        {c.status}
                      </span>
                    </td>

                    {/* Resume File */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#cbd5e1', fontSize: '0.82rem' }}>
                        <FileText size={14} color="#06b6d4" />
                        <span>{c.resume_filename || c.resumeFileName || 'resume.pdf'}</span>
                      </div>
                    </td>

                    {/* Date */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#94a3b8', fontSize: '0.8rem' }}>
                        <Calendar size={13} />
                        <span>{c.date || c.created_at || 'Just now'}</span>
                      </div>
                    </td>

                    {/* Actions */}
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '8px' }}>
                        <button 
                          className="btn btn-secondary" 
                          style={{ padding: '6px 10px', fontSize: '0.78rem' }}
                          onClick={() => setSelectedCandidate(c)}
                        >
                          <Eye size={14} /> View
                        </button>
                        <button 
                          className="btn btn-danger" 
                          style={{ padding: '6px 8px' }}
                          title="Delete candidate"
                          onClick={() => handleDelete(c.candidate_id, c.candidate_name)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', borderBottom: '1px solid #233768', paddingBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#06b6d4', textTransform: 'uppercase', fontWeight: 700 }}>
                  Candidate #{selectedCandidate.rank}
                </span>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                  {selectedCandidate.candidate_name || selectedCandidate.candidateName}
                </h3>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                  {selectedCandidate.job_role} • {selectedCandidate.email}
                </span>
              </div>
              <button 
                onClick={() => setSelectedCandidate(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Score & Status Banner */}
            <div style={{ 
              background: selectedCandidate.status === 'Selected' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
              border: `1px solid ${selectedCandidate.status === 'Selected' ? '#10b981' : '#ef4444'}`,
              borderRadius: '10px',
              padding: '16px 20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Candidate Score</span>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: selectedCandidate.status === 'Selected' ? '#10b981' : '#ef4444' }}>
                  {selectedCandidate.score} / 100
                </div>
              </div>
              <span className={`badge ${selectedCandidate.status === 'Selected' ? 'badge-shortlisted' : 'badge-rejected'}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
                {selectedCandidate.status}
              </span>
            </div>

            {/* Recommendation */}
            <div style={{ marginBottom: '20px', background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid #233768' }}>
              <span style={{ fontSize: '0.78rem', color: '#06b6d4', fontWeight: 700, textTransform: 'uppercase' }}>Recommendation:</span>
              <p style={{ fontSize: '0.88rem', color: '#f1f5f9', marginTop: '4px' }}>
                {selectedCandidate.recommendation || 'Evaluated via model pipeline.'}
              </p>
            </div>

            {/* Skills */}
            <div style={{ marginBottom: '20px' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '8px' }}>
                Extracted Skills ({(selectedCandidate.skills || []).length}):
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(selectedCandidate.skills || []).map((s, idx) => (
                  <span key={idx} className="badge badge-shortlisted" style={{ fontSize: '0.78rem' }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>

            {/* File & Date metadata */}
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8', borderTop: '1px solid #233768', paddingTop: '14px' }}>
              <span>File: {selectedCandidate.resume_filename || 'resume.pdf'}</span>
              <span>Date: {selectedCandidate.date || selectedCandidate.created_at}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
