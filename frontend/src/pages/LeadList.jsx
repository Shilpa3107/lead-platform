import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';

const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost'];

export default function LeadList() {
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const pageSize = 10;

  useEffect(() => {
    fetchLeads();
  }, [page, statusFilter]);

  async function fetchLeads() {
    setLoading(true);
    setError('');
    try {
      const params = { page, page_size: pageSize };
      if (statusFilter) params.status = statusFilter;
      const response = await api.get('/leads', { params });
      setLeads(response.data.items);
      setTotal(response.data.total);
    } catch (err) {
      setError('Failed to load leads');
    } finally {
      setLoading(false);
    }
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="lead-list-page">
      <div className="lead-list-header">
        <h1>Leads</h1>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && leads.length === 0 && <p>No leads found.</p>}

      <table className="lead-table">
        <thead>
          <tr>
            <th>Name</th><th>Company</th><th>Status</th><th>Assigned</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td><Link to={`/leads/${lead.id}`}>{lead.name}</Link></td>
              <td>{lead.company || '—'}</td>
              <td><span className={`status-badge status-${lead.status}`}>{lead.status}</span></td>
              <td>{lead.assigned_to_id ? 'Assigned' : 'Unassigned'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page} of {totalPages || 1}</span>
        <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}