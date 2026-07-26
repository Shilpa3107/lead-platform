import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';
import PipelineStepper from '../components/PipelineStepper';

const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost'];

export default function LeadDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [lead, setLead] = useState(null);
  const [activity, setActivity] = useState([]);
  const [noteContent, setNoteContent] = useState('');
  const [error, setError] = useState('');
  const [users, setUsers] = useState([]);

  useEffect(() => {
    if (user?.role === 'admin') {
      api.get('/users').then((res) => setUsers(res.data));
    }
  }, [user]);

  useEffect(() => {
    loadLead();
    loadActivity();
  }, [id]);


  async function handleAssign(userId) {
    await api.patch(`/leads/${id}`, { assigned_to_id: userId || null });
    loadLead();
    loadActivity();
  }

  async function loadLead() {
    try {
      const response = await api.get(`/leads/${id}`);
      setLead(response.data);
    } catch (err) {
      setError('Lead not found or you do not have access to it');
    }
  }

  async function loadActivity() {
    try {
      const response = await api.get(`/leads/${id}/activity`);
      setActivity(response.data);
    } catch (err) {
      // non-critical, don't block the page for this
    }
  }

  async function handleStatusChange(newStatus) {
    await api.patch(`/leads/${id}`, { status: newStatus });
    loadLead();
    loadActivity();
  }

  async function handleAddNote(e) {
    e.preventDefault();
    if (!noteContent.trim()) return;
    await api.post(`/leads/${id}/notes`, { content: noteContent });
    setNoteContent('');
    loadActivity();
  }

  if (error) return <p className="error-text">{error}</p>;
  if (!lead) return <p>Loading...</p>;

  return (
    <div className="lead-detail-page">
      <h1>{lead.name}</h1>
      <p>{lead.company || 'No company listed'} · {lead.email || 'No email'}</p>
      
      <PipelineStepper status={lead.status} />
      
      <div className="detail-row">
        <label>Status:</label>
        <select value={lead.status} onChange={(e) => handleStatusChange(e.target.value)}>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {user?.role === 'admin' && (
        <div className="detail-row">
          <label>Assigned to:</label>
          <select value={lead.assigned_to_id || ''} onChange={(e) => handleAssign(e.target.value)}>
            <option value="">Unassigned</option>
            {users.filter(u => u.role === 'member').map((u) => (
              <option key={u.id} value={u.id}>{u.email}</option>
            ))}
          </select>
        </div>
      )}

      <form onSubmit={handleAddNote} className="note-form">
        <textarea
          placeholder="Add a note..."
          value={noteContent}
          onChange={(e) => setNoteContent(e.target.value)}
        />
        <button type="submit">Add note</button>
      </form>

      <h2>Activity</h2>
      <ul className="activity-list">
        {activity.map((entry) => (
          <li key={entry.id}>
            <strong>{entry.action}</strong> — {entry.details} <span className="timestamp">{new Date(entry.created_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}