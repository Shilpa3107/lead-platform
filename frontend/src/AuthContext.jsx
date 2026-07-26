import { createContext, useContext, useState } from 'react';
import api, { setAuthToken } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // { id, email, role }

  async function login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    const token = response.data.access_token;
    setAuthToken(token);
    // decode the role out of the JWT payload (base64, no verification needed client-side —
    // the server re-verifies on every request; this is purely for UI display)
    const payload = JSON.parse(atob(token.split('.')[1]));
    setUser({ id: payload.sub, role: payload.role, email });
  }

  function logout() {
    setAuthToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}