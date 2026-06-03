import { createContext, useContext, useState, useEffect } from 'react';
import { login as loginAPI, logout as logoutAPI, profile as profileAPI } from '../api/auth';

const AuthContext = createContext(null);

// Stockage en mémoire + localStorage pour compatibilité
let storedToken = localStorage.getItem('access_token');
let storedRefresh = localStorage.getItem('refresh_token');

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(storedToken);
  const [loading, setLoading] = useState(true);

  {/*useEffect(() => {
    if (storedToken) {
      setToken(storedToken);
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);*/}
  useEffect(() => {

  const loadUser = async () => {

    if (!storedToken) {
      setLoading(false);
      return;
    }

    try {

      const res = await profileAPI(storedToken);

      setUser(res.data);
      setToken(storedToken);

    } catch (err) {

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      storedToken = null;
      storedRefresh = null;

    } finally {

      setLoading(false);

    }
  };

  loadUser();

}, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem('access_token', token);
    }
  }, [token]);


  const login = async (username, password) => {
    const res = await loginAPI({ username, password });
    const { user, tokens } = res.data;
    storedToken   = tokens.access;
    storedRefresh = tokens.refresh;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    setUser(user);
    setToken(tokens.access);
    return user;
  };

  const logout = async () => {
    try {
      await logoutAPI({ refresh: storedRefresh });
    } catch {}
    storedToken   = null;
    storedRefresh = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setToken(null);
  };

  return (
      <AuthContext.Provider value={{ user, token, loading, login, logout }}>
        {children}
      </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);