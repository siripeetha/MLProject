import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Briefcase, Plus, Trash2, MapPin, Calendar, Clock, X } from 'lucide-react';

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    job_role: '',
    description: '',
    required_skills: '',
    min_experience: 2,
    education: 'B.Tech / B.E. / MCA',
    location: 'Bangalore / Remote'
  });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/jobs');
      if (res.data.success) {
        setJobs(res.data.jobs);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        required_skills: formData.required_skills.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean)
      };
      const res = await axios.post('/api/jobs', payload);
      if (res.data.success) {
        setShowModal(false);
        setFormData({
          job_role: '',
          description: '',
          required_skills: '',
          min_experience: 2,
          education: 'B.Tech / B.E. / MCA',
          location: 'Bangalore / Remote'
        });
        fetchJobs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm(`Delete requisition ${jobId}?`)) return;
    try {
      await axios.delete(`/api/jobs/${jobId}`);
      fetchJobs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Technical Job Positions</h1>
          <p>Operational technical requisitions stored in MongoDB and mapped to Data Warehouse dimension tables.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} /> Create Requisition
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading jobs from MongoDB...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {jobs.map((job) => (
            <div key={job.job_id} className="chart-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span className="font-mono" style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 700 }}>
                    {job.job_id}
                  </span>
                  <button 
                    onClick={() => handleDeleteJob(job.job_id)}
                    style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '4px' }}
                    title="Delete Job"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '8px' }}>{job.job_role}</h3>
                
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: '1.4', marginBottom: '14px', minHeight: '58px' }}>
                  {job.description}
                </p>

                <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '16px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={13} color="#f59e0b" /> Min {job.min_experience} yrs
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} color="#06b6d4" /> {job.location || 'Remote'}
                  </span>
                </div>

                <div>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600 }}>MANDATORY SKILLS:</span>
                  <div className="tags-container" style={{ marginTop: '6px' }}>
                    {(job.required_skills || []).map((s) => (
                      <span key={s} className="skill-tag" style={{ backgroundColor: 'rgba(79, 70, 229, 0.15)', color: '#a5b4fc', borderColor: 'rgba(79, 70, 229, 0.3)' }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px', borderTop: '1px solid var(--border)', paddingTop: '12px', fontSize: '0.78rem', color: '#94a3b8' }}>
                Education: {job.education || 'Degree in Computer Science'}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-card" style={{ maxWidth: '600px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Job Position</h3>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateJob} style={{ padding: '24px' }}>
              <div className="form-group">
                <label className="form-label">Job Role Title</label>
                <input 
                  type="text" 
                  className="form-control" 
                  required
                  placeholder="e.g. Cloud DevOps Engineer"
                  value={formData.job_role}
                  onChange={(e) => setFormData({ ...formData, job_role: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Job Description</label>
                <textarea 
                  className="form-control" 
                  rows={3} 
                  required
                  placeholder="Describe core duties and engineering expectations..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Required Skills (comma-separated)</label>
                <input 
                  type="text" 
                  className="form-control" 
                  required
                  placeholder="e.g. aws, docker, kubernetes, terraform, python, git"
                  value={formData.required_skills}
                  onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Min Experience (Years)</label>
                  <input 
                    type="number" 
                    className="form-control" 
                    min={0}
                    max={15}
                    value={formData.min_experience}
                    onChange={(e) => setFormData({ ...formData, min_experience: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Location</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Position to MongoDB
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
