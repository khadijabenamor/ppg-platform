import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Etudiant from './pages/Etudiant';
import Superviseur from './pages/Superviseur';
import Evaluation from './pages/Evaluation';
import Admin from './pages/Admin';
import Profile from './pages/Profile';

function PrivateRoute({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ color: 'var(--text)', textAlign: 'center', padding: '4rem' }}>Chargement...</div>;
  if (!user) return <Navigate to="/login" />;
  if (role && user.role !== role) return <Navigate to="/" />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();
  return (
      <>
        {user && <Navbar />}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <PrivateRoute role="etudiant">
              <Etudiant />
            </PrivateRoute>
          } />
          <Route path="/evaluation" element={
            <PrivateRoute role="etudiant">
              <Evaluation />
            </PrivateRoute>
          } />
          <Route path="/superviseur" element={
            <PrivateRoute role="superviseur">
              <Superviseur />
            </PrivateRoute>
          } />
          <Route path="/admin" element={
            <PrivateRoute role="admin">
               <Admin />
            </PrivateRoute>
          } />
          <Route path="/profile" element={
            <PrivateRoute>
               <Profile />
          </PrivateRoute>
} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </>
  );
}

export default function App() {
  return (
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
  );
}