import { useState, useEffect } from 'react';
import { getSummaries, validateSummary } from '../api/ai';

const STATUS_STYLE = {
  pending:   { bg: 'rgba(255,193,7,0.1)',  border: 'rgba(255,193,7,0.3)',  color: '#ffc107', label: '⏳ En attente' },
  validated: { bg: 'rgba(67,233,123,0.1)', border: 'rgba(67,233,123,0.3)', color: '#43e97b', label: '✓ Validé' },
  rejected:  { bg: 'rgba(255,101,132,0.1)', border: 'rgba(255,101,132,0.3)', color: '#ff6584', label: '✕ Rejeté' },
};

export default function Superviseur() {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [actionId, setActionId]   = useState(null);

  const fetchSummaries = async () => {
    try {
      const res = await getSummaries();
      setSummaries(res.data);
    } catch {
      console.error('Erreur chargement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSummaries(); }, []);

  const handleAction = async (id, status) => {
    setActionId(id);
    try {
      await validateSummary(id, status);
      setSummaries(prev => prev.map(s => s.id === id ? { ...s, status } : s));
    } catch { console.error('Erreur validation'); }
    finally { setActionId(null); }
  };

  const stats = {
    total:     summaries.length,
    pending:   summaries.filter(s => s.status === 'pending').length,
    validated: summaries.filter(s => s.status === 'validated').length,
    rejected:  summaries.filter(s => s.status === 'rejected').length,
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '3rem 2rem' }}>

      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{
          display: 'inline-block',
          background: 'linear-gradient(135deg, rgba(255,101,132,0.15), rgba(108,99,255,0.1))',
          border: '1px solid rgba(255,101,132,0.3)',
          borderRadius: '100px',
          padding: '6px 16px',
          fontSize: '0.8rem',
          fontFamily: 'Syne',
          fontWeight: 600,
          color: 'var(--accent2)',
          letterSpacing: '0.05em',
          marginBottom: '1rem',
        }}>ESPACE SUPERVISEUR</div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
          Validation des <span style={{ background: 'linear-gradient(135deg, var(--accent2), var(--accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>résumés</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.75rem' }}>
          Valide ou rejette les résumés générés par l'IA.
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'Total', value: stats.total, color: 'var(--text)' },
          { label: 'En attente', value: stats.pending, color: '#ffc107' },
          { label: 'Validés', value: stats.validated, color: '#43e97b' },
          { label: 'Rejetés', value: stats.rejected, color: '#ff6584' },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '2rem', fontFamily: 'Syne', fontWeight: 800, color }}>{value}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Refresh */}
      <button onClick={fetchSummaries} style={{
        background: 'var(--surface2)', border: '1px solid var(--border)',
        borderRadius: '8px', color: 'var(--text-muted)',
        padding: '8px 16px', fontSize: '0.85rem', cursor: 'pointer',
        fontFamily: 'Syne', marginBottom: '1.5rem',
      }}>↻ Rafraîchir</button>

      {/* List */}
      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '4rem' }}>Chargement...</div>
      ) : summaries.length === 0 ? (
        <div style={{
          textAlign: 'center', color: 'var(--text-muted)', padding: '4rem',
          background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)',
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📭</div>
          <p>Aucun résumé pour l'instant.<br/>Va sur la page Générer pour créer le premier !</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {summaries.map(s => {
            const st = STATUS_STYLE[s.status];
            return (
              <div key={s.id} style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                padding: '1.5rem',
              }}>
                {/* Top row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem' }}>
                  <span style={{ fontFamily: 'Syne', fontWeight: 700, color: 'var(--text-muted)', fontSize: '0.85rem' }}>#{s.id}</span>
                  <span style={{
                    background: st.bg, border: `1px solid ${st.border}`,
                    color: st.color, borderRadius: '100px',
                    padding: '3px 12px', fontSize: '0.78rem', fontFamily: 'Syne', fontWeight: 600,
                  }}>{st.label}</span>
                  <span style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {new Date(s.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {/* Résumé */}
                <p style={{ fontSize: '0.92rem', lineHeight: 1.75, color: 'var(--text)', marginBottom: '1rem' }}>
                  {s.summary}
                </p>

                {/* Mots-clés */}
                {s.keywords?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '1.25rem' }}>
                    {s.keywords.map((kw, i) => (
                      <span key={i} style={{
                        background: 'rgba(108,99,255,0.1)', border: '1px solid rgba(108,99,255,0.2)',
                        color: '#a8a3ff', borderRadius: '100px',
                        padding: '3px 12px', fontSize: '0.78rem',
                      }}>{kw}</span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                {s.status === 'pending' && (
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => handleAction(s.id, 'validated')}
                      disabled={actionId === s.id}
                      style={{
                        flex: 1, padding: '10px',
                        background: 'rgba(67,233,123,0.1)', border: '1px solid rgba(67,233,123,0.3)',
                        borderRadius: '10px', color: '#43e97b',
                        fontFamily: 'Syne', fontWeight: 700, fontSize: '0.9rem',
                        cursor: 'pointer',
                      }}
                    >✓ Valider</button>
                    <button
                      onClick={() => handleAction(s.id, 'rejected')}
                      disabled={actionId === s.id}
                      style={{
                        flex: 1, padding: '10px',
                        background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)',
                        borderRadius: '10px', color: '#ff6584',
                        fontFamily: 'Syne', fontWeight: 700, fontSize: '0.9rem',
                        cursor: 'pointer',
                      }}
                    >✕ Rejeter</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
