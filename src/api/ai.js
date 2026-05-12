import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/ai',
  headers: { 'Content-Type': 'application/json' },
});

export const generateSummary = (text, student_name, is_premium) =>
  API.post('/generate-summary/', { text, student_name, is_premium });

export const generateFromPDF = (pdfFile, student_name, is_premium) => {
  const formData = new FormData();
  formData.append('pdf', pdfFile);
  formData.append('student_name', student_name);
  formData.append('is_premium', is_premium.toString());
  return axios.post('http://127.0.0.1:8000/api/ai/generate-from-pdf/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getSummaries        = () => API.get('/summaries/');
export const validateSummary     = (id, status) => API.patch(`/summaries/${id}/validate/`, { status });
export const requestVerification = (id) => API.post(`/summaries/${id}/request-verification/`);
export const getVerifications    = () => API.get('/verifications/');
export const respondVerification = (id, status, supervisor_comment) =>
  API.patch(`/verification/${id}/respond/`, { status, supervisor_comment });
export const getMySummaries = (studentName) =>
    API.get(`/my-summaries/?student_name=${studentName}`);