import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav style={{
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      padding: '0 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '64px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: 36, height: 36,
          background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
          borderRadius: '10px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '16px', fontWeight: 800,
          fontFamily: 'Syne, sans-serif',
        }}>P</div>
        <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>
          PPG <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>· IA & Génération</span>
        </span>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        {[
          { path: '/', label: '✦ Générer' },
          { path: '/superviseur', label: '◈ Superviseur' },
        ].map(({ path, label }) => (
          <Link key={path} to={path} style={{
            textDecoration: 'none',
            padding: '8px 18px',
            borderRadius: '8px',
            fontSize: '0.875rem',
            fontWeight: 500,
            fontFamily: 'Syne',
            background: pathname === path ? 'var(--accent)' : 'transparent',
            color: pathname === path ? '#fff' : 'var(--text-muted)',
            border: `1px solid ${pathname === path ? 'var(--accent)' : 'var(--border)'}`,
            transition: 'all 0.2s',
          }}>{label}</Link>
        ))}
      </div>
    </nav>
  );
}
