import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav style={{
      background: 'var(--surface)', borderBottom: '1px solid var(--border)',
      padding: '0 2rem', display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', height: '64px',
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: 36, height: 36,
          background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
          borderRadius: '10px', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: '16px', fontWeight: 800, fontFamily: 'Syne',
        }}>P</div>
        <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>
          PPG <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>· IA & Génération</span>
        </span>
      </div>

      {/* Links */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        {user?.role === 'etudiant' && (
          <>
            <Link to="/" style={{
              textDecoration: 'none', padding: '8px 18px', borderRadius: '8px',
              fontSize: '0.875rem', fontFamily: 'Syne', fontWeight: 500,
              background: pathname === '/' ? 'var(--accent)' : 'transparent',
              color: pathname === '/' ? '#fff' : 'var(--text-muted)',
              border: `1px solid ${pathname === '/' ? 'var(--accent)' : 'var(--border)'}`,
            }}>✦ Générer</Link>
            <Link to="/evaluation" style={{
              textDecoration: 'none', padding: '8px 18px', borderRadius: '8px',
              fontSize: '0.875rem', fontFamily: 'Syne', fontWeight: 500,
              background: pathname === '/evaluation' ? 'var(--accent)' : 'transparent',
              color: pathname === '/evaluation' ? '#fff' : 'var(--text-muted)',
              border: `1px solid ${pathname === '/evaluation' ? 'var(--accent)' : 'var(--border)'}`,
            }}>📝 Quiz</Link>
          </>
        )}
        {user?.role === 'superviseur' && (
          <Link to="/superviseur" style={{
            textDecoration: 'none', padding: '8px 18px', borderRadius: '8px',
            fontSize: '0.875rem', fontFamily: 'Syne', fontWeight: 500,
            background: pathname === '/superviseur' ? 'var(--accent)' : 'transparent',
            color: pathname === '/superviseur' ? '#fff' : 'var(--text-muted)',
            border: `1px solid ${pathname === '/superviseur' ? 'var(--accent)' : 'var(--border)'}`,
          }}>◈ Superviseur</Link>
        )}

        {/* User info */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '8px' }}>
            <Link
  to="/profile"
  style={{
    textDecoration: 'none',
    padding: '8px 18px',
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontFamily: 'Syne',
    fontWeight: 500,
    background: pathname === '/profile' ? 'var(--accent)' : 'transparent',
    color: pathname === '/profile' ? '#fff' : 'var(--text-muted)',
    border: `1px solid ${
      pathname === '/profile'
        ? 'var(--accent)'
        : 'var(--border)'
    }`,
  }}
>
  👤 Profil
</Link>
            <div style={{
              background: user.is_premium
                ? 'linear-gradient(135deg, #f7971e, #ffd200)'
                : 'var(--surface2)',
              border: `1px solid ${user.is_premium ? '#ffd200' : 'var(--border)'}`,
              borderRadius: '100px', padding: '4px 12px',
              fontSize: '0.78rem', fontFamily: 'Syne', fontWeight: 600,
              color: user.is_premium ? '#000' : 'var(--text-muted)',
            }}>
              {user.is_premium ? '⭐ Premium' : '○ Free'}
            </div>
            <div style={{
              background: 'var(--surface2)', border: '1px solid var(--border)',
              borderRadius: '100px', padding: '4px 14px',
              fontSize: '0.85rem', color: 'var(--text)',
            }}>
              {user.first_name || user.username}
            </div>
            <button onClick={handleLogout} style={{
              background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)',
              borderRadius: '8px', padding: '6px 14px',
              color: '#ff6584', fontFamily: 'Syne', fontWeight: 600,
              fontSize: '0.82rem', cursor: 'pointer',
            }}>Déconnexion</button>
          </div>
        )}
      </div>
    </nav>
  );
}
