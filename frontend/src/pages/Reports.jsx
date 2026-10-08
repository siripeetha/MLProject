import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FileText, 
  Download, 
  Printer, 
  CheckCircle2, 
  BarChart2, 
  Users, 
  Award,
  Filter,
  FileSpreadsheet
} from 'lucide-react';

export default function Reports() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/reports');
      if (res.data.success) {
        setReportData(res.data);
      }
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = async (type) => {
    try {
      setExporting(true);
      const endpoint = type === 'shortlisted' ? '/api/shortlisted' : '/api/candidates?limit=500';
      const res = await axios.get(endpoint);
      
      const candidates = res.data.candidates || [];
      if (!candidates.length) {
        alert('No records available to export.');
        return;
      }

      const headers = ['Candidate ID', 'Name', 'Email', 'Job Role', 'Overall Score', 'Skill Match Score', 'Status', 'Skills'];
      const rows = candidates.map(c => [
        c.candidate_id || '',
        `"${c.candidate_name || ''}"`,
        c.email || '',
        `"${c.job_role || ''}"`,
        c.overall_score || 0,
        c.skill_match_score || 0,
        c.shortlist_status || '',
        `"${(c.skills || []).join('; ')}"`
      ]);

      const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `${type}_candidates_report_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Export error:', err);
      alert('Failed to generate export file.');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center', color: '#94a3b8' }}>
          <FileText size={48} className="spin-slow" style={{ color: '#4f46e5', marginBottom: '16px' }} />
          <h3>Compiling Recruitment & Warehouse Analytics Report...</h3>
        </div>
      </div>
    );
  }

  const summary = reportData?.summary || {};
  const byRole = reportData?.by_role || [];
  const topSkills = reportData?.top_skills || [];

  return (
    <div className="page-container">
      {/* Banner */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(16, 185, 129, 0.1))', borderColor: 'rgba(79, 70, 229, 0.3)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge badge-shortlisted">EXECUTIVE AUDIT READY</span>
              <span className="badge" style={{ backgroundColor: 'rgba(6, 182, 212, 0.2)', color: '#06b6d4' }}>CSV & PDF EXPORTABLE</span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
              Recruitment Analytics & Compliance Reports
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              Synthesized hiring funnel performance, skill demand analytics, and talent distribution metrics generated from MongoDB candidate store and Data Warehouse Fact repository.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              className="btn btn-secondary" 
              onClick={() => window.print()}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Printer size={16} /> Print / Save PDF
            </button>
            <button 
              className="btn btn-primary" 
              disabled={exporting}
              onClick={() => downloadCSV('shortlisted')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Download size={16} /> Export Shortlisted (CSV)
            </button>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-label">Total Evaluated Applicants</div>
          <div className="stat-value">{summary.total_candidates || 0}</div>
          <div className="stat-desc">Parsed through TF-IDF & ML Classifier</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Shortlisted Conversion Rate</div>
          <div className="stat-value" style={{ color: '#10b981' }}>{summary.shortlisted_rate}%</div>
          <div className="stat-desc">Candidates scoring ≥ 80 overall points</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Review Pool Rate</div>
          <div className="stat-value" style={{ color: '#f59e0b' }}>{summary.review_rate}%</div>
          <div className="stat-desc">Borderline candidates (60-79 points)</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Average Evaluation Score</div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>{summary.average_score}</div>
          <div className="stat-desc">Multi-criteria weighted mean</div>
        </div>
      </div>

      {/* Role-wise Breakdown Table */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={18} style={{ color: '#4f46e5' }} /> Talent Pool Breakdown by Job Requisition
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              Distribution of incoming talent pipeline by target job profile.
            </p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
            onClick={() => downloadCSV('all')}
          >
            <FileSpreadsheet size={14} style={{ marginRight: '6px' }} /> Export All Candidates (CSV)
          </button>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Job Role</th>
                <th>Total Candidates</th>
                <th>Share of Pipeline</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {byRole.map((r, idx) => {
                const total = summary.total_candidates || 1;
                const pct = ((r.count / total) * 100).toFixed(1);
                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{r._id || r.role}</td>
                    <td style={{ fontWeight: 700 }}>{r.count}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div className="progress-bar" style={{ width: '120px' }}>
                          <div className="progress-fill" style={{ width: `${pct}%`, backgroundColor: '#4f46e5' }}></div>
                        </div>
                        <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>{pct}%</span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-shortlisted">Active Sourcing</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Skills Demand */}
      <div className="card">
        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Award size={18} style={{ color: '#10b981' }} /> Most Frequently Identified Technical Competencies
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {topSkills.map((s, idx) => (
            <div key={idx} style={{ padding: '14px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid #233768' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600, color: '#06b6d4', textTransform: 'capitalize' }}>{s.skill}</span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{s.count} hits</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${Math.min(100, s.count * 2)}%`, backgroundColor: '#10b981' }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
