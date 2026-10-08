import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Database, 
  Table, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Layers, 
  Share2, 
  FileSpreadsheet, 
  ArrowUpDown,
  CheckCircle2,
  Filter
} from 'lucide-react';

export default function DataWarehouse() {
  const [overview, setOverview] = useState(null);
  const [activeTableKey, setActiveTableKey] = useState('fact_candidate_analysis');
  const [tableData, setTableData] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingTable, setLoadingTable] = useState(false);
  
  // Table query params
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(15);
  const [sortCol, setSortCol] = useState('');
  const [sortDir, setSortDir] = useState('asc');

  useEffect(() => {
    fetchOverview();
  }, []);

  useEffect(() => {
    if (activeTableKey) {
      setPage(1);
      fetchTableData(activeTableKey, 1, search, sortCol, sortDir);
    }
  }, [activeTableKey]);

  const fetchOverview = async () => {
    try {
      setLoadingOverview(true);
      const res = await axios.get('/api/data-warehouse');
      if (res.data.success) {
        setOverview(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching warehouse overview:', err);
    } finally {
      setLoadingOverview(false);
    }
  };

  const fetchTableData = async (tableKey, p = page, s = search, sc = sortCol, sd = sortDir) => {
    try {
      setLoadingTable(true);
      const res = await axios.get(`/api/data-warehouse/table/${tableKey}`, {
        params: {
          page: p,
          limit,
          search: s,
          sort_col: sc,
          sort_dir: sd
        }
      });
      if (res.data.success) {
        setTableData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching table data:', err);
    } finally {
      setLoadingTable(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchTableData(activeTableKey, 1, search, sortCol, sortDir);
  };

  const handleSort = (column) => {
    const newDir = sortCol === column && sortDir === 'asc' ? 'desc' : 'asc';
    setSortCol(column);
    setSortDir(newDir);
    fetchTableData(activeTableKey, page, search, column, newDir);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    fetchTableData(activeTableKey, newPage, search, sortCol, sortDir);
  };

  const tablesList = [
    { key: 'fact_candidate_analysis', name: 'Fact: Candidate Analysis', type: 'FACT', tag: 'Central Fact' },
    { key: 'dim_candidate', name: 'Dim: Candidate', type: 'DIM', tag: 'Candidate Profile' },
    { key: 'dim_job', name: 'Dim: Job Role', type: 'DIM', tag: 'Job Requisition' },
    { key: 'dim_skill', name: 'Dim: Skill Match', type: 'DIM', tag: 'Skill Taxonomy' },
    { key: 'dim_date', name: 'Dim: Date Calendar', type: 'DIM', tag: 'Temporal Roll-up' },
    { key: 'dim_education', name: 'Dim: Education', type: 'DIM', tag: 'Degree Level' },
    { key: 'dim_experience', name: 'Dim: Experience', type: 'DIM', tag: 'Tenure Tier' },
  ];

  return (
    <div className="page-container">
      {/* Banner */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(79, 70, 229, 0.1))', borderColor: 'rgba(6, 182, 212, 0.3)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge" style={{ backgroundColor: 'rgba(6, 182, 212, 0.2)', color: '#06b6d4', border: '1px solid #06b6d4' }}>
                KIMBALL DIMENSIONAL MODEL
              </span>
              <span className="badge badge-shortlisted">STAR SCHEMA ARCHITECTURE</span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
              Data Warehouse & Star Schema Explorer
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              Enterprise data warehouse generated directly from Google Colab ETL. Built with 1 Fact table at candidate-application grain connected to 6 Dimension tables via surrogate foreign keys.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <div style={{ background: 'rgba(19, 31, 61, 0.8)', padding: '12px 20px', borderRadius: '10px', border: '1px solid #2d4580', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>Fact Records</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#06b6d4' }}>5,200</div>
            </div>
            <div style={{ background: 'rgba(19, 31, 61, 0.8)', padding: '12px 20px', borderRadius: '10px', border: '1px solid #2d4580', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>Dimensions</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#10b981' }}>6</div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Star Schema Diagram */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Share2 size={18} style={{ color: '#06b6d4' }} /> Star Schema Topology
        </h3>

        <div style={{ 
          background: 'rgba(11, 19, 41, 0.6)', 
          border: '1px solid #233768', 
          borderRadius: '12px', 
          padding: '24px', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          gap: '20px'
        }}>
          {/* Top Row Dimensions */}
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center', width: '100%' }}>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_CANDIDATE</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>candidate_key (PK)</div>
            </div>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_JOB</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>job_key (PK)</div>
            </div>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_SKILL</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>skill_key (PK)</div>
            </div>
          </div>

          {/* Central Fact */}
          <div style={{ 
            background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.25), rgba(6, 182, 212, 0.25))', 
            border: '2px solid #4f46e5', 
            borderRadius: '12px', 
            padding: '16px 32px', 
            textAlign: 'center',
            boxShadow: '0 0 20px rgba(79, 70, 229, 0.2)'
          }}>
            <div style={{ fontSize: '0.8rem', color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>Central Fact Table</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginTop: '4px' }}>FACT_CANDIDATE_ANALYSIS</div>
            <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '6px' }}>
              Foreign Keys: [candidate_key, job_key, skill_key, date_key, education_key, experience_key]<br/>
              Measures: overall_score, similarity_score, skill_match_score, shortlist_status
            </div>
          </div>

          {/* Bottom Row Dimensions */}
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center', width: '100%' }}>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_DATE</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>date_key (PK)</div>
            </div>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_EDUCATION</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>education_key (PK)</div>
            </div>
            <div style={{ background: '#131f3d', border: '1px solid #2d4580', borderRadius: '8px', padding: '10px 16px', textAlign: 'center', minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 600 }}>DIM_EXPERIENCE</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>experience_key (PK)</div>
            </div>
          </div>
        </div>
      </div>

      {/* Table Selector Pills */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '20px' }}>
        {tablesList.map((t) => {
          const isActive = activeTableKey === t.key;
          return (
            <button
              key={t.key}
              className={`btn ${isActive ? 'btn-primary' : 'btn-secondary'}`}
              style={{ whiteSpace: 'nowrap', fontSize: '0.82rem' }}
              onClick={() => setActiveTableKey(t.key)}
            >
              <Table size={14} />
              <span>{t.name}</span>
            </button>
          );
        })}
      </div>

      {/* Table Viewer Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff' }}>
              {tablesList.find((t) => t.key === activeTableKey)?.name}
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Displaying {tableData?.rows?.length || 0} of {tableData?.total || 0} total rows
            </span>
          </div>

          {/* Search bar */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
            <div className="search-box" style={{ maxWidth: '280px' }}>
              <Search size={16} className="search-icon" />
              <input 
                type="text" 
                placeholder="Search table values..." 
                value={search} 
                onChange={(e) => setSearch(e.target.value)} 
              />
            </div>
            <button type="submit" className="btn btn-secondary">Search</button>
          </form>
        </div>

        {/* Data Table */}
        {loadingTable ? (
          <div style={{ padding: '60px 0', textAlign: 'center', color: '#94a3b8' }}>
            Loading table records...
          </div>
        ) : (
          <>
            <div className="table-container" style={{ maxHeight: '550px', overflowY: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    {tableData?.columns?.map((col, idx) => (
                      <th 
                        key={idx} 
                        onClick={() => handleSort(col)}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span>{col}</span>
                          <ArrowUpDown size={12} style={{ color: sortCol === col ? '#06b6d4' : '#64748b' }} />
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData?.rows?.map((row, rIdx) => (
                    <tr key={rIdx}>
                      {tableData?.columns?.map((col, cIdx) => {
                        const val = row[col];
                        const isScore = col.includes('score');
                        const isStatus = col.includes('status');
                        return (
                          <td key={cIdx} style={{ fontSize: '0.82rem' }}>
                            {isStatus ? (
                              <span className={`badge badge-${val.toLowerCase()}`}>{val}</span>
                            ) : isScore && typeof val === 'number' ? (
                              <span style={{ fontWeight: 600, color: val >= 80 ? '#10b981' : val >= 60 ? '#f59e0b' : '#ef4444' }}>
                                {val.toFixed(1)}
                              </span>
                            ) : (
                              String(val ?? '')
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #233768' }}>
              <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                Page {tableData?.page || 1} of {tableData?.totalPages || 1}
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  className="btn btn-secondary" 
                  disabled={page <= 1}
                  onClick={() => handlePageChange(page - 1)}
                  style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                >
                  <ChevronLeft size={14} /> Prev
                </button>
                <button 
                  className="btn btn-secondary" 
                  disabled={page >= (tableData?.totalPages || 1)}
                  onClick={() => handlePageChange(page + 1)}
                  style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                >
                  Next <ChevronRight size={14} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
