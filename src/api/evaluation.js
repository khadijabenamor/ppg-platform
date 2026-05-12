import axios from 'axios';

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/evaluation',
  headers: { 'Content-Type': 'application/json' },
});

// ==================== QUIZ ====================

export const getQuizzes = () => API.get('/quizzes/', { headers: getAuthHeaders() });

export const getQuizDetail = (id) => API.get(`/quizzes/${id}/`, { headers: getAuthHeaders() });

export const createQuiz = (data) => API.post('/quizzes/', data, { headers: getAuthHeaders() });

export const createQuizWithAI = (data) => API.post('/quizzes/create-with-ai/', data, { headers: getAuthHeaders() });

export const generateQuizPreview = (course_content, count = 5) => 
  API.post('/quizzes/preview-questions/', { course_content, count }, { headers: getAuthHeaders() });

export const generateQuizQuestions = (quizId, course_content, count = 5) =>
  API.post(`/quizzes/${quizId}/generate-questions/`, { course_content, count }, { headers: getAuthHeaders() });

export const submitQuiz = (quizId, answers) =>
  API.post(`/quizzes/${quizId}/submit/`, { answers }, { headers: getAuthHeaders() });

export const deleteQuiz = (id) => API.delete(`/quizzes/${id}/`, { headers: getAuthHeaders() });

// ==================== FLASHCARDS ====================

export const getFlashcards = (course_id) => 
  course_id ? API.get(`/flashcards/?course_id=${course_id}`, { headers: getAuthHeaders() }) : API.get('/flashcards/', { headers: getAuthHeaders() });

export const getFlashcardDetail = (id) => API.get(`/flashcards/${id}/`, { headers: getAuthHeaders() });

export const createFlashcard = (data) => API.post('/flashcards/', data, { headers: getAuthHeaders() });

export const generateFlashcardsPreview = (course_content, count = 5) =>
  API.post('/flashcards/preview/', { course_content, count }, { headers: getAuthHeaders() });

export const generateFlashcards = (course_content, course_id, count = 5, tags = []) =>
  API.post('/flashcards/generate/', { course_content, course_id, count, tags }, { headers: getAuthHeaders() });

export const deleteFlashcard = (id) => API.delete(`/flashcards/${id}/`, { headers: getAuthHeaders() });

export const markFlashcardReviewed = (id) =>
  API.post(`/flashcards/${id}/mark-reviewed/`, {}, { headers: getAuthHeaders() });

// ==================== PROGRESS ====================

export const getProgress = () => API.get('/progress/', { headers: getAuthHeaders() });

export const getStatistics = () => API.get('/progress/statistics/', { headers: getAuthHeaders() });

export const getAttempts = () => API.get('/attempts/', { headers: getAuthHeaders() });