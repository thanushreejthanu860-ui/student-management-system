import { createContext, useContext, useState, useCallback } from 'react';
import { login as loginApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const stored = localStorage.getItem('user');
  const [user, setUser] = useState(stored ? JSON.parse(stored) : null);

  const login = useCallback(async (email, password) => {
    const { data } = await loginApi({ email, password });
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
