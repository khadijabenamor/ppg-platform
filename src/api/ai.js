import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/ai',
  headers: { 'Content-Type': 'application/json' },
});

export const generateSummary = (text) =>
  API.post('/generate-summary/', { text });

export const getSummaries = () =>
  API.get('/summaries/');

export const validateSummary = (id, status) =>
  API.patch(`/summaries/${id}/validate/`, { status });
