import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { register as registerAPI } from '../api/auth';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [tab, setTab]         = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const { login }             = useAuth();
  const navigate              = useNavigate();

  // Login form
  const [loginData, setLoginData] = useState({ username: '', password: '' });

  // Register form
  const [regData, setRegData] = useState({
    username: '', email: '', first_name: '', last_name: '',
    password: '', password2: '', role: 'etudiant'
  });

  const handleLogin = async () => {
    if (!loginData.username || !loginData.password) {
      setError('Remplis tous les champs.'); return;
    }
    setLoading(true); setError('');
    try {
      const loggedUser = await login(loginData.username, loginData.password);
      // Redirige selon le rôle
      if (loggedUser.role === 'superviseur') {
        navigate('/superviseur');
      } else {
        navigate('/');
      }
    } catch (e) {
      setError(e.response?.data?.error || 'Identifiants incorrects.');
    } finally { setLoading(false); }
  };




  const handleRegister = async () => {
    if (!regData.username || !regData.password || !regData.password2) {
      setError('Remplis tous les champs obligatoires.'); return;
    }
    setLoading(true); setError('');
    try {
      await registerAPI(regData);
      const loggedUser = await login(regData.username, regData.password);
      if (loggedUser.role === 'superviseur') {
        navigate('/superviseur');
      } else {
        navigate('/');
      }
    } catch (e) {
      const errors = e.response?.data;
      if (errors) {
        setError(Object.values(errors).flat().join(' '));
      } else {
        setError("Erreur lors de l'inscription.");
      }
    } finally { setLoading(false); }
  };



  const inputStyle = {
    width: '100%', background: 'var(--surface)',
    border: '1px solid var(--border)', borderRadius: '10px',
    color: 'var(--text)', fontSize: '0.95rem', padding: '0.9rem 1.25rem',
    outline: 'none', fontFamily: 'DM Sans, sans-serif',
    marginBottom: '1rem',
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: '2rem',
    }}>
      <div style={{
        width: '100%', maxWidth: 440,
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: '20px', padding: '2.5rem',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, margin: '0 auto 1rem',
            background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
            borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '24px', fontWeight: 800, fontFamily: 'Syne',
          }}>P</div>
          <h1 style={{ fontFamily: 'Syne', fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Plateforme PPG
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            IA & Génération de Cours
          </p>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem' }}>
          {[
            { id: 'login', label: 'Connexion' },
            { id: 'register', label: 'Inscription' },
          ].map(({ id, label }) => (
            <button key={id} onClick={() => { setTab(id); setError(''); }} style={{
              flex: 1, padding: '10px',
              background: tab === id ? 'var(--accent)' : 'var(--surface2)',
              border: `1px solid ${tab === id ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: '10px', color: tab === id ? '#fff' : 'var(--text-muted)',
              fontFamily: 'Syne', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
            }}>{label}</button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)',
            borderRadius: '10px', padding: '0.75rem 1rem',
            color: '#ff6584', fontSize: '0.85rem', marginBottom: '1rem',
          }}>⚠ {error}</div>
        )}

        {/* Login Form */}
        {tab === 'login' && (
          <div>
            <input
              placeholder="Nom d'utilisateur"
              value={loginData.username}
              onChange={e => setLoginData({ ...loginData, username: e.target.value })}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={loginData.password}
              onChange={e => setLoginData({ ...loginData, password: e.target.value })}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <button onClick={handleLogin} disabled={loading} style={{
              width: '100%', padding: '1rem',
              background: 'linear-gradient(135deg, var(--accent), #8b7fff)',
              border: 'none', borderRadius: '10px',
              color: '#fff', fontFamily: 'Syne', fontWeight: 700,
              fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer',
            }}>
              {loading ? '⟳ Connexion...' : '→ Se connecter'}
            </button>
          </div>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
              <input placeholder="Prénom *" value={regData.first_name}
                onChange={e => setRegData({ ...regData, first_name: e.target.value })}
                style={inputStyle}
                onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                onBlur={e => e.target.style.borderColor = 'var(--border)'}
              />
              <input placeholder="Nom *" value={regData.last_name}
                onChange={e => setRegData({ ...regData, last_name: e.target.value })}
                style={inputStyle}
                onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                onBlur={e => e.target.style.borderColor = 'var(--border)'}
              />
            </div>
            <input placeholder="Nom d'utilisateur *" value={regData.username}
              onChange={e => setRegData({ ...regData, username: e.target.value })}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <input placeholder="Email" value={regData.email} type="email"
              onChange={e => setRegData({ ...regData, email: e.target.value })}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <select value={regData.role}
              onChange={e => setRegData({ ...regData, role: e.target.value })}
              style={{ ...inputStyle, cursor: 'pointer' }}
            >
              <option value="etudiant">👨‍🎓 Étudiant</option>
              <option value="superviseur">👨‍🏫 Superviseur</option>
            </select>
            <input type="password" placeholder="Mot de passe *" value={regData.password}
              onChange={e => setRegData({ ...regData, password: e.target.value })}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <input type="password" placeholder="Confirmer mot de passe *" value={regData.password2}
              onChange={e => setRegData({ ...regData, password2: e.target.value })}
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <button onClick={handleRegister} disabled={loading} style={{
              width: '100%', padding: '1rem',
              background: 'linear-gradient(135deg, var(--accent), #8b7fff)',
              border: 'none', borderRadius: '10px',
              color: '#fff', fontFamily: 'Syne', fontWeight: 700,
              fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer',
            }}>
              {loading ? '⟳ Inscription...' : '✦ Créer mon compte'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
