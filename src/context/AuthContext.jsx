import { createContext, useContext, useState, useEffect } from 'react';
import { login as loginAPI, logout as logoutAPI, profile as profileAPI } from '../api/auth';

const AuthContext = createContext(null);

// Stockage en mémoire (pas localStorage)
let storedToken = null;
let storedRefresh = null;

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(storedToken);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      if (token) {
        try {
          const res = await profileAPI(token);
          setUser(res.data);
        } catch {
          storedToken   = null;
          storedRefresh = null;
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  const login = async (username, password) => {
    const res = await loginAPI({ username, password });
    const { user, tokens } = res.data;
    storedToken   = tokens.access;
    storedRefresh = tokens.refresh;
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