import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Dashboard() {
  const { user, logout } = useAuth();
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Logged in as {user?.email} ({user?.role})</p>
      <Link to="/leads">View leads</Link>
      <br />
      <button onClick={logout}>Log out</button>
    </div>
  );
}