import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/ai',
  headers: { 'Content-Type': 'application/json' },
});

export const generateSummary      = (text, student_name, is_premium) =>
  API.post('/generate-summary/', { text, student_name, is_premium });

export const getSummaries          = () => API.get('/summaries/');
export const validateSummary       = (id, status) => API.patch(`/summaries/${id}/validate/`, { status });
export const requestVerification   = (id) => API.post(`/summaries/${id}/request-verification/`);
export const getVerifications      = () => API.get('/verifications/');
export const respondVerification   = (id, status, supervisor_comment) =>
  API.patch(`/verification/${id}/respond/`, { status, supervisor_comment });
