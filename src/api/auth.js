import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth',
  headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => API.post('/register/', data);
export const login    = (data) => API.post('/login/', data);
export const logout   = (data) => API.post('/logout/', data);
export const profile  = (token) => API.get('/profile/', {
  headers: { Authorization: `Bearer ${token}` }
});
