import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Nav() {
  const { user, logout } = useAuth();
  const location = useLocation();
  if (!user) return null;

  return (
    <nav className="top-nav">
      <Link to="/dashboard" className="brand">Lead Platform</Link>
      <div className="nav-links">
        <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link>
        <Link to="/leads" className={location.pathname.startsWith('/leads') ? 'active' : ''}>Leads</Link>
      </div>
      <div className="nav-right">
        <span>{user.email}</span>
        <span className="role-badge">{user.role}</span>
        <button onClick={logout}>Log out</button>
      </div>
    </nav>
  );
}