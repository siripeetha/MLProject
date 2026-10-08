import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart3, 
  Layers, 
  Filter, 
  ArrowUpRight, 
  ArrowDownRight, 
  Scissors, 
  Box, 
  RefreshCw,
  Search,
  CheckCircle2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';

export default function OLAPAnalytics() {
  const [activeTab, setActiveTab] = useState('rollup'); // 'rollup', 'drilldown', 'slice', 'dice'
  
  // ROLL-UP State
  const [rollupLevel, setRollupLevel] = useState('quarter');
  const [rollupData, setRollupData] = useState([]);
  const [rollupLoading, setRollupLoading] = useState(false);

  // DRILL-DOWN State
  const [drillYear, setDrillYear] = useState('2025');
  const [drillQuarter, setDrillQuarter] = useState('Q1');
  const [drillData, setDrillData] = useState([]);
  const [drillLoading, setDrillLoading] = useState(false);

  // SLICE State
  const [sliceRole, setSliceRole] = useState('Data Scientist');
  const [sliceResult, setSliceResult] = useState(null);
  const [sliceLoading, setSliceLoading] = useState(false);

  // DICE State
  const [diceRole, setDiceRole] = useState('Python Developer');
  const [diceExp, setDiceExp] = useState('3-5 years');
  const [diceMinScore, setDiceMinScore] = useState(70);
  const [diceResult, setDiceResult] = useState(null);
  const [diceLoading, setDiceLoading] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchRollup(rollupLevel);
  }, []);

  const fetchRollup = async (level) => {
    try {
      setRollupLoading(true);
      const res = await axios.get('/api/olap/rollup', { params: { level } });
      if (res.data.success) {
        setRollupData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching rollup:', err);
    } finally {
      setRollupLoading(false);
    }
  };

  const fetchDrilldown = async (year, quarter) => {
    try {
      setDrillLoading(true);
      const res = await axios.get('/api/olap/drilldown', { params: { year, quarter } });
      if (res.data.success) {
        setDrillData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching drilldown:', err);
    } finally {
      setDrillLoading(false);
    }
  };

  const fetchSlice = async (role) => {
    try {
      setSliceLoading(true);
      const res = await axios.get('/api/olap/slice', { params: { dimension: 'job_role', value: role } });
      if (res.data.success) {
        setSliceResult(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching slice:', err);
    } finally {
      setSliceLoading(false);
    }
  };

  const fetchDice = async (role, exp, score) => {
    try {
      setDiceLoading(true);
      const res = await axios.get('/api/olap/dice', { 
        params: { job_role: role, experience_range: exp, min_score: score } 
      });
      if (res.data.success) {
        setDiceResult(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching dice:', err);
    } finally {
      setDiceLoading(false);
    }
  };

  const roles = [
    'Java Developer',
    'Python Developer',
    'Data Analyst',
    'Data Scientist',
    'Web Developer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Software Engineer',
    'Database Developer'
  ];

  return (
    <div className="page-container">
      {/* Banner */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(6, 182, 212, 0.15))', borderColor: 'rgba(79, 70, 229, 0.4)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge" style={{ backgroundColor: 'rgba(79, 70, 229, 0.25)', color: '#818cf8', border: '1px solid #4f46e5' }}>
                ONLINE ANALYTICAL PROCESSING
              </span>
              <span className="badge badge-shortlisted">MULTIDIMENSIONAL CUBE</span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
              OLAP Multi-Dimensional Analytics Console
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              Execute interactive Roll-up, Drill-down, Slice, and Dice operations against the materialized star schema data cube across temporal, educational, experience, and role dimensions.
            </p>
          </div>
        </div>
      </div>

      {/* Operation Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', borderBottom: '1px solid #233768', paddingBottom: '12px' }}>
        <button 
          className={`btn ${activeTab === 'rollup' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTab('rollup'); fetchRollup(rollupLevel); }}
        >
          <ArrowUpRight size={16} /> Roll-Up (Aggregation)
        </button>
        <button 
          className={`btn ${activeTab === 'drilldown' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTab('drilldown'); fetchDrilldown(drillYear, drillQuarter); }}
        >
          <ArrowDownRight size={16} /> Drill-Down (Decomposition)
        </button>
        <button 
          className={`btn ${activeTab === 'slice' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTab('slice'); fetchSlice(sliceRole); }}
        >
          <Scissors size={16} /> Slice (1D Filter)
        </button>
        <button 
          className={`btn ${activeTab === 'dice' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTab('dice'); fetchDice(diceRole, diceExp, diceMinScore); }}
        >
          <Box size={16} /> Dice (Multi-D Sub-cube)
        </button>
      </div>

      {/* 1. ROLL-UP */}
      {activeTab === 'rollup' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ArrowUpRight size={20} style={{ color: '#10b981' }} /> Roll-Up Operation
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                  Summarizes data by climbing up a concept hierarchy (e.g. Month → Quarter → Year or Job Role).
                </p>
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>Hierarchy Level:</span>
                <select 
                  className="form-select" 
                  value={rollupLevel} 
                  onChange={(e) => {
                    setRollupLevel(e.target.value);
                    fetchRollup(e.target.value);
                  }}
                  style={{ minWidth: '150px' }}
                >
                  <option value="year">Yearly Roll-Up</option>
                  <option value="quarter">Quarterly Roll-Up</option>
                  <option value="month">Monthly Roll-Up</option>
                  <option value="job_role">Job Role Roll-Up</option>
                </select>
              </div>
            </div>

            {/* Chart */}
            <div style={{ height: '300px', marginBottom: '24px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={rollupData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#233768" />
                  <XAxis 
                    dataKey={rollupLevel === 'job_role' ? 'job_role' : rollupLevel === 'year' ? 'year' : 'quarter'} 
                    stroke="#94a3b8" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }} 
                  />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#131f3d', borderColor: '#2d4580', color: '#f1f5f9' }} />
                  <Legend />
                  <Bar dataKey="shortlisted" fill="#10b981" name="Shortlisted" stackId="a" />
                  <Bar dataKey="review" fill="#f59e0b" name="Review" stackId="a" />
                  <Bar dataKey="rejected" fill="#ef4444" name="Rejected" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Aggregated Table */}
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    {rollupLevel === 'year' && <th>Year</th>}
                    {rollupLevel === 'quarter' && <><th>Year</th><th>Quarter</th></>}
                    {rollupLevel === 'month' && <><th>Year</th><th>Quarter</th><th>Month</th></>}
                    {rollupLevel === 'job_role' && <th>Job Role</th>}
                    <th>Total Applicants</th>
                    <th>Shortlisted</th>
                    <th>Review</th>
                    <th>Rejected</th>
                    <th>Shortlist Rate</th>
                    <th>Avg Score</th>
                  </tr>
                </thead>
                <tbody>
                  {rollupData.map((row, idx) => (
                    <tr key={idx}>
                      {rollupLevel === 'year' && <td style={{ fontWeight: 600 }}>{row.year}</td>}
                      {rollupLevel === 'quarter' && <><td>{row.year}</td><td style={{ fontWeight: 600, color: '#06b6d4' }}>{row.quarter}</td></>}
                      {rollupLevel === 'month' && <><td>{row.year}</td><td>{row.quarter}</td><td style={{ fontWeight: 600 }}>{row.month}</td></>}
                      {rollupLevel === 'job_role' && <td style={{ fontWeight: 600, color: '#fff' }}>{row.job_role}</td>}
                      <td style={{ fontWeight: 600 }}>{row.total_candidates}</td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>{row.shortlisted}</td>
                      <td style={{ color: '#f59e0b' }}>{row.review}</td>
                      <td style={{ color: '#ef4444' }}>{row.rejected}</td>
                      <td>
                        <span className="badge badge-shortlisted">{row.shortlist_rate}%</span>
                      </td>
                      <td style={{ fontWeight: 700, color: row.avg_overall_score >= 80 ? '#10b981' : '#f1f5f9' }}>
                        {row.avg_overall_score}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 2. DRILL-DOWN */}
      {activeTab === 'drilldown' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ArrowDownRight size={20} style={{ color: '#06b6d4' }} /> Drill-Down Operation
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                  Navigates from less detailed data to a more granular level of the dimensional cube.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <select 
                  className="form-select" 
                  value={drillYear} 
                  onChange={(e) => { setDrillYear(e.target.value); fetchDrilldown(e.target.value, drillQuarter); }}
                >
                  <option value="2025">Year 2025</option>
                  <option value="2024">Year 2024</option>
                </select>
                <select 
                  className="form-select" 
                  value={drillQuarter} 
                  onChange={(e) => { setDrillQuarter(e.target.value); fetchDrilldown(drillYear, e.target.value); }}
                >
                  <option value="Q1">Quarter 1</option>
                  <option value="Q2">Quarter 2</option>
                  <option value="Q3">Quarter 3</option>
                  <option value="Q4">Quarter 4</option>
                </select>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Job Role</th>
                    <th>Total Applicants</th>
                    <th>Shortlisted</th>
                    <th>Avg Overall Score</th>
                  </tr>
                </thead>
                <tbody>
                  {drillData.map((row, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600, color: '#06b6d4' }}>{row.month}</td>
                      <td style={{ fontWeight: 600, color: '#fff' }}>{row.job_role}</td>
                      <td>{row.total_candidates}</td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>{row.shortlisted}</td>
                      <td style={{ fontWeight: 700 }}>{row.avg_overall_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 3. SLICE */}
      {activeTab === 'slice' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Scissors size={20} style={{ color: '#f59e0b' }} /> Slice Operation
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                  Extracts a 2D sub-table by fixing one dimension (e.g. <code>Job Role = {sliceRole}</code>).
                </p>
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>Select Role Slice:</span>
                <select 
                  className="form-select" 
                  value={sliceRole} 
                  onChange={(e) => { setSliceRole(e.target.value); fetchSlice(e.target.value); }}
                >
                  {roles.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Slice KPI Summary Cards */}
            {sliceResult?.summary && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Total Slice Records</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>{sliceResult.summary.total_candidates}</div>
                </div>
                <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Shortlisted</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#10b981' }}>{sliceResult.summary.shortlisted_count}</div>
                </div>
                <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Avg Overall Score</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#06b6d4' }}>{sliceResult.summary.avg_overall_score}</div>
                </div>
                <div style={{ background: '#131f3d', padding: '16px', borderRadius: '10px', border: '1px solid #233768' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Avg Skill Match</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f59e0b' }}>{sliceResult.summary.avg_skill_match}</div>
                </div>
              </div>
            )}

            {/* Slice Sample Table */}
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate ID</th>
                    <th>Candidate Name</th>
                    <th>Job Role</th>
                    <th>Experience</th>
                    <th>Overall Score</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sliceResult?.records?.map((row, idx) => (
                    <tr key={idx}>
                      <td><code>{row.candidate_id}</code></td>
                      <td style={{ fontWeight: 600, color: '#fff' }}>{row.candidate_name}</td>
                      <td>{row.job_role}</td>
                      <td>{row.experience_range}</td>
                      <td style={{ fontWeight: 700, color: row.overall_score >= 80 ? '#10b981' : '#f1f5f9' }}>{row.overall_score}</td>
                      <td>
                        <span className={`badge badge-${row.shortlist_status.toLowerCase()}`}>
                          {row.shortlist_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 4. DICE */}
      {activeTab === 'dice' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card">
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Box size={20} style={{ color: '#a855f7' }} /> Dice Operation
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '20px' }}>
              Defines a sub-cube by applying multiple selection predicates across two or more dimensions simultaneously.
            </p>

            {/* Multi-attribute Filter Bar */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', background: 'rgba(11, 19, 41, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid #233768', marginBottom: '24px' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px', display: 'block' }}>Dimension: Job Role</label>
                <select 
                  className="form-select" 
                  value={diceRole} 
                  onChange={(e) => setDiceRole(e.target.value)}
                >
                  <option value="All">All Roles</option>
                  {roles.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px', display: 'block' }}>Dimension: Experience Range</label>
                <select 
                  className="form-select" 
                  value={diceExp} 
                  onChange={(e) => setDiceExp(e.target.value)}
                >
                  <option value="All">All Experience Ranges</option>
                  <option value="0-2 years">0-2 years (Entry)</option>
                  <option value="3-5 years">3-5 years (Mid)</option>
                  <option value="6-8 years">6-8 years (Senior)</option>
                  <option value="9+ years">9+ years (Lead/Principal)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px', display: 'block' }}>Measure: Min Overall Score ({diceMinScore})</label>
                <input 
                  type="range" 
                  min="0" 
                  max="95" 
                  step="5"
                  value={diceMinScore} 
                  onChange={(e) => setDiceMinScore(e.target.value)}
                  style={{ width: '100%', accentColor: '#4f46e5' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button 
                  className="btn btn-primary" 
                  style={{ width: '100%' }}
                  onClick={() => fetchDice(diceRole, diceExp, diceMinScore)}
                >
                  <Box size={16} /> Execute Sub-Cube Dice
                </button>
              </div>
            </div>

            {/* Results */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
                Matched Sub-Cube Records: <strong style={{ color: '#10b981' }}>{diceResult?.matched_count ?? 'Execute to search'}</strong>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate ID</th>
                    <th>Candidate Name</th>
                    <th>Job Role</th>
                    <th>Experience</th>
                    <th>Overall Score</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {diceResult?.records?.map((row, idx) => (
                    <tr key={idx}>
                      <td><code>{row.candidate_id}</code></td>
                      <td style={{ fontWeight: 600, color: '#fff' }}>{row.candidate_name}</td>
                      <td>{row.job_role}</td>
                      <td>{row.experience_range}</td>
                      <td style={{ fontWeight: 700, color: row.overall_score >= 80 ? '#10b981' : '#f1f5f9' }}>{row.overall_score}</td>
                      <td>
                        <span className={`badge badge-${row.shortlist_status.toLowerCase()}`}>
                          {row.shortlist_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
