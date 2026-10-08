import React from 'react';
import { 
  LayoutDashboard, 
  FileSearch, 
  Trophy,
  Database
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analyzer', label: 'Resume Analyzer', icon: FileSearch },
  { id: 'candidates', label: 'Candidate Ranking', icon: Trophy },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">RA</div>
        <div className="logo-text">
          <h1>ResumeScreen</h1>
          <span>AI Screening System</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981' }}>
            <span className="status-dot"></span>
            <span style={{ fontWeight: 600 }}>MongoDB Connected</span>
          </div>
          <div style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
            Trained Model: Random Forest
          </div>
        </div>
      </div>
    </aside>
  );
}
