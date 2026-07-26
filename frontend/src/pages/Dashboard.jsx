import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';

const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost'];

export default function Dashboard() {
  const { user } = useAuth();
  const [counts, setCounts] = useState(null);
  const [unassigned, setUnassigned] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCounts();
  }, []);

  async function loadCounts() {
    setLoading(true);
    try {
      const results = {};
      for (const status of STATUSES) {
        const res = await api.get('/leads', { params: { page: 1, page_size: 1, status } });
        results[status] = res.data.total;
      }
      setCounts(results);

      if (user?.role === 'admin') {
        const all = await api.get('/leads', { params: { page: 1, page_size: 1 } });
        const assignedTotal = STATUSES.reduce((sum, s) => sum + (results[s] || 0), 0);
        // simplest accurate way: fetch all leads once and count client-side for unassigned
        const fullList = await api.get('/leads', { params: { page: 1, page_size: 100 } });
        setUnassigned(fullList.data.items.filter((l) => !l.assigned_to_id).length);
      }
    } finally {
      setLoading(false);
    }
  }

  const total = counts ? STATUSES.reduce((sum, s) => sum + counts[s], 0) : 0;

  return (
    <div className="dashboard-page">
      <h1>{user?.role === 'admin' ? 'Pipeline overview' : 'Your leads'}</h1>
      {loading && <p>Loading...</p>}

      {!loading && counts && (
        <div className="stat-cards">
          <div className="stat-card">
            <span className="stat-number">{total}</span>
            <span className="stat-label">{user?.role === 'admin' ? 'total leads' : 'assigned to you'}</span>
          </div>
          {STATUSES.map((s) => (
            <div className="stat-card" key={s}>
              <span className={`stat-number status-text-${s}`}>{counts[s]}</span>
              <span className="stat-label">{s}</span>
            </div>
          ))}
          {user?.role === 'admin' && unassigned !== null && (
            <div className="stat-card stat-card-alert">
              <span className="stat-number">{unassigned}</span>
              <span className="stat-label">unassigned</span>
            </div>
          )}
        </div>
      )}

      <Link to="/leads" className="dashboard-card">
        <h3>View leads</h3>
        <p>
          {user?.role === 'admin'
            ? 'See every lead in the pipeline, assign reps, and track progress.'
            : 'See the leads assigned to you and keep them moving.'}
        </p>
      </Link>
    </div>
  );
}