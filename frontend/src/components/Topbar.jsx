import React from 'react';
import { UploadCloud, CheckCircle2 } from 'lucide-react';

export default function Topbar({ activeTab, setActiveTab }) {
  const titles = {
    dashboard: 'Resume Screening Dashboard',
    analyzer: 'Resume Analyzer & Evaluation',
    candidates: 'Candidate Ranking Leaderboard',
  };

  return (
    <header className="topbar">
      <div className="topbar-title">
        <h2>{titles[activeTab] || 'Resume Screening System'}</h2>
      </div>

      <div className="topbar-actions">
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge badge-shortlisted" style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
            <CheckCircle2 size={13} /> Model Online
          </span>
        </div>

        {activeTab !== 'analyzer' && (
          <button className="btn btn-primary" onClick={() => setActiveTab('analyzer')}>
            <UploadCloud size={16} /> Upload Resume
          </button>
        )}
      </div>
    </header>
  );
}
