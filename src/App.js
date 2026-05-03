import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Etudiant from './pages/Etudiant';
import Superviseur from './pages/Superviseur';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Etudiant />} />
        <Route path="/superviseur" element={<Superviseur />} />
      </Routes>
    </BrowserRouter>
  );
}
