import { useState } from 'react';
import { generateSummary } from '../api/ai';

export default function Etudiant() {
  const [text, setText]       = useState('');
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const handleGenerate = async () => {
    if (!text.trim()) { setError("Entre un texte d'abord !"); return; }
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await generateSummary(text);
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Erreur de connexion au serveur.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '3rem 2rem' }}>

      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{
          display: 'inline-block',
          background: 'linear-gradient(135deg, rgba(108,99,255,0.15), rgba(255,101,132,0.1))',
          border: '1px solid rgba(108,99,255,0.3)',
          borderRadius: '100px',
          padding: '6px 16px',
          fontSize: '0.8rem',
          fontFamily: 'Syne',
          fontWeight: 600,
          color: 'var(--accent)',
          letterSpacing: '0.05em',
          marginBottom: '1rem',
        }}>MODULE M2 — IA & GÉNÉRATION</div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.2 }}>
          Génère ton résumé<br />
          <span style={{ background: 'linear-gradient(135deg, var(--accent), var(--accent2))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            automatiquement
          </span>
        </h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.75rem', fontSize: '1rem' }}>
          Colle ton cours ci-dessous — Mistral AI génère le résumé et extrait les mots-clés.
        </p>
      </div>

      {/* Textarea */}
      <div style={{ marginBottom: '1.25rem' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
          TEXTE DU COURS
        </label>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Colle ici le contenu de ton cours..."
          rows={9}
          style={{
            width: '100%',
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            color: 'var(--text)',
            fontSize: '0.95rem',
            padding: '1.25rem',
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'DM Sans, sans-serif',
            lineHeight: 1.7,
            transition: 'border-color 0.2s',
          }}
          onFocus={e => e.target.style.borderColor = 'var(--accent)'}
          onBlur={e => e.target.style.borderColor = 'var(--border)'}
        />
        <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
          {text.length} caractères
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)',
          borderRadius: '10px', padding: '1rem 1.25rem',
          color: '#ff6584', fontSize: '0.9rem', marginBottom: '1rem',
        }}>⚠ {error}</div>
      )}

      {/* Button */}
      <button
        onClick={handleGenerate}
        disabled={loading}
        style={{
          width: '100%',
          padding: '1rem',
          background: loading ? 'var(--surface2)' : 'linear-gradient(135deg, var(--accent), #8b7fff)',
          border: 'none',
          borderRadius: 'var(--radius)',
          color: '#fff',
          fontSize: '1rem',
          fontFamily: 'Syne',
          fontWeight: 700,
          cursor: loading ? 'not-allowed' : 'pointer',
          letterSpacing: '0.02em',
          transition: 'opacity 0.2s',
        }}
      >
        {loading ? '⟳  Mistral réfléchit... (1-2 min)' : '✦  Générer le résumé'}
      </button>

      {/* Result */}
      {result && (
        <div style={{ marginTop: '2.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Résumé */}
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '1.75rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
              <span style={{ fontSize: '1.1rem' }}>📄</span>
              <h3 style={{ fontFamily: 'Syne', fontSize: '1rem', fontWeight: 700 }}>Résumé généré</h3>
              <span style={{
                marginLeft: 'auto',
                background: 'rgba(67,233,123,0.15)',
                color: 'var(--accent3)',
                border: '1px solid rgba(67,233,123,0.3)',
                borderRadius: '100px',
                padding: '2px 12px',
                fontSize: '0.75rem',
                fontFamily: 'Syne',
                fontWeight: 600,
              }}>EN ATTENTE</span>
            </div>
            <p style={{ color: 'var(--text)', lineHeight: 1.8, fontSize: '0.95rem' }}>
              {result.summary}
            </p>
          </div>

          {/* Mots-clés */}
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '1.75rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
              <span style={{ fontSize: '1.1rem' }}>🏷</span>
              <h3 style={{ fontFamily: 'Syne', fontSize: '1rem', fontWeight: 700 }}>Mots-clés extraits</h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {result.keywords.map((kw, i) => (
                <span key={i} style={{
                  background: 'rgba(108,99,255,0.12)',
                  border: '1px solid rgba(108,99,255,0.25)',
                  color: '#a8a3ff',
                  borderRadius: '100px',
                  padding: '5px 14px',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                }}>{kw}</span>
              ))}
            </div>
          </div>

          {/* ID */}
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
            Résumé #{result.id} sauvegardé · visible dans l'espace superviseur
          </p>
        </div>
      )}
    </div>
  );
}
