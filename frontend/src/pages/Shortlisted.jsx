import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CheckCircle2, Mail, Phone, ExternalLink, Calendar, Award } from 'lucide-react';

export default function Shortlisted() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchShortlisted();
  }, []);

  const fetchShortlisted = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/shortlisted');
      if (res.data.success) {
        setCandidates(res.data.candidates);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Shortlisted Talent Pool</h1>
          <p>Pre-screened candidates achieving an Overall Match Score ≥ 80% with high technical qualification.</p>
        </div>
        <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#10b981', padding: '8px 16px', borderRadius: '20px', fontWeight: 700, fontSize: '0.9rem' }}>
          {candidates.length} Interview-Ready Candidates
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading shortlisted candidates...</div>
      ) : candidates.length === 0 ? (
        <div className="chart-card" style={{ textAlign: 'center', padding: '40px' }}>
          <CheckCircle2 size={48} color="#10b981" style={{ margin: '0 auto 12px' }} />
          <h3>No Shortlisted Candidates Yet</h3>
          <p style={{ color: '#94a3b8', marginTop: '6px' }}>Upload resumes in the Resume Analyzer to screen and shortlist candidates.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {candidates.map((c, idx) => (
            <div key={c.candidate_id} className="chart-card" style={{ border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 800 }}>#{idx + 1}</span>
                    <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>{c.candidate_name}</h3>
                  </div>
                  <span style={{ fontSize: '0.78rem', color: '#06b6d4', fontWeight: 600 }}>{c.job_role}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="badge badge-shortlisted" style={{ fontSize: '0.85rem' }}>
                    {c.overall_score}%
                  </span>
                </div>
              </div>

              <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Mail size={13} /> {c.email}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Phone size={13} /> {c.phone}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', padding: '10px', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '16px', textAlign: 'center' }}>
                <div>
                  <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>Skills</span>
                  <div style={{ fontWeight: 700, color: '#10b981' }}>{c.skill_match_score}%</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>Experience</span>
                  <div style={{ fontWeight: 700, color: '#fff' }}>{c.experience_years} yrs</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>Cosine Sim</span>
                  <div style={{ fontWeight: 700, color: '#06b6d4' }}>{c.cosine_similarity_score}%</div>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600 }}>VERIFIED CORE SKILLS:</span>
                <div className="tags-container" style={{ marginTop: '6px' }}>
                  {(c.matched_skills || []).slice(0, 4).map((s) => (
                    <span key={s} className="skill-tag matched">{s}</span>
                  ))}
                  {(c.matched_skills || []).length > 4 && (
                    <span className="skill-tag" style={{ color: '#06b6d4' }}>+{c.matched_skills.length - 4} more</span>
                  )}
                </div>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#a5b4fc' }}>Interview Status: Ready</span>
                <button 
                  className="btn btn-secondary" 
                  style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  onClick={() => alert(`Interview scheduled with ${c.candidate_name} for role ${c.job_role}!`)}
                >
                  <Calendar size={13} /> Schedule Interview
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
