import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';

import Dashboard from './pages/Dashboard';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import Candidates from './pages/Candidates';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} />;
      case 'analyzer':
        return <ResumeAnalyzer setActiveTab={setActiveTab} />;
      case 'candidates':
        return <Candidates setActiveTab={setActiveTab} />;
      default:
        return <Dashboard setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-wrapper">
        <Topbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="content-area">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}
