import { useState, useEffect } from 'react';
import { getSummaries, validateSummary, getVerifications, respondVerification } from '../api/ai';

const STATUS_STYLE = {
  pending:   { bg: 'rgba(255,193,7,0.1)',  border: 'rgba(255,193,7,0.3)',  color: '#ffc107', label: '⏳ En attente' },
  validated: { bg: 'rgba(67,233,123,0.1)', border: 'rgba(67,233,123,0.3)', color: '#43e97b', label: '✓ Validé' },
  rejected:  { bg: 'rgba(255,101,132,0.1)', border: 'rgba(255,101,132,0.3)', color: '#ff6584', label: '✕ Rejeté' },
};

const VERIF_STYLE = {
  pending:   { bg: 'rgba(255,193,7,0.1)',  border: 'rgba(255,193,7,0.3)',  color: '#ffc107', label: '⏳ En attente' },
  correct:   { bg: 'rgba(67,233,123,0.1)', border: 'rgba(67,233,123,0.3)', color: '#43e97b', label: '✅ Correct' },
  incorrect: { bg: 'rgba(255,101,132,0.1)', border: 'rgba(255,101,132,0.3)', color: '#ff6584', label: '❌ À corriger' },
};

export default function Superviseur() {
  const [tab, setTab]               = useState('resumes');
  const [summaries, setSummaries]   = useState([]);
  const [verifs, setVerifs]         = useState([]);
  const [loading, setLoading]       = useState(true);
  const [actionId, setActionId]     = useState(null);
  const [comments, setComments]     = useState({});

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [s, v] = await Promise.all([getSummaries(), getVerifications()]);
      setSummaries(s.data);
      setVerifs(v.data);
    } catch { console.error('Erreur chargement'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleValidate = async (id, status) => {
    setActionId(id);
    try {
      await validateSummary(id, status);
      setSummaries(prev => prev.map(s => s.id === id ? { ...s, status } : s));
    } finally { setActionId(null); }
  };

  const handleRespond = async (id, status) => {
    const comment = comments[id] || '';
    if (status === 'incorrect' && !comment.trim()) {
      alert('Un commentaire est obligatoire si le résumé est incorrect !');
      return;
    }
    setActionId(id);
    try {
      await respondVerification(id, status, comment);
      setVerifs(prev => prev.map(v => v.id === id ? { ...v, status, supervisor_comment: comment } : v));
    } finally { setActionId(null); }
  };

  const stats = {
    resumes:       summaries.length,
    pending:       summaries.filter(s => s.status === 'pending').length,
    validated:     summaries.filter(s => s.status === 'validated').length,
    verifications: verifs.filter(v => v.status === 'pending').length,
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '3rem 2rem' }}>

      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{
          display: 'inline-block',
          background: 'linear-gradient(135deg, rgba(255,101,132,0.15), rgba(108,99,255,0.1))',
          border: '1px solid rgba(255,101,132,0.3)',
          borderRadius: '100px', padding: '6px 16px',
          fontSize: '0.8rem', fontFamily: 'Syne', fontWeight: 600,
          color: 'var(--accent2)', letterSpacing: '0.05em', marginBottom: '1rem',
        }}>ESPACE SUPERVISEUR</div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
          Tableau de <span style={{ background: 'linear-gradient(135deg, var(--accent2), var(--accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>bord</span>
        </h1>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'Résumés total', value: stats.resumes,       color: 'var(--text)' },
          { label: 'En attente',    value: stats.pending,       color: '#ffc107' },
          { label: 'Validés',       value: stats.validated,     color: '#43e97b' },
          { label: '⭐ Vérif. premium', value: stats.verifications, color: '#ffd200' },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius)', padding: '1.25rem', textAlign: 'center',
          }}>
            <div style={{ fontSize: '2rem', fontFamily: 'Syne', fontWeight: 800, color }}>{value}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem' }}>
        {[
          { id: 'resumes', label: '📄 Résumés' },
          { id: 'verifications', label: '⭐ Vérifications Premium' },
        ].map(({ id, label }) => (
          <button key={id} onClick={() => setTab(id)} style={{
            padding: '10px 20px', borderRadius: '10px',
            border: `1px solid ${tab === id ? 'var(--accent)' : 'var(--border)'}`,
            background: tab === id ? 'var(--accent)' : 'var(--surface)',
            color: tab === id ? '#fff' : 'var(--text-muted)',
            fontFamily: 'Syne', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
          }}>{label}</button>
        ))}
        <button onClick={fetchAll} style={{
          marginLeft: 'auto', padding: '10px 16px',
          background: 'var(--surface2)', border: '1px solid var(--border)',
          borderRadius: '10px', color: 'var(--text-muted)',
          fontFamily: 'Syne', fontSize: '0.85rem', cursor: 'pointer',
        }}>↻ Rafraîchir</button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '4rem' }}>Chargement...</div>
      ) : (
        <>
          {/* Tab Résumés */}
          {tab === 'resumes' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {summaries.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '4rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                  <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📭</div>
                  <p>Aucun résumé pour l'instant.</p>
                </div>
              ) : summaries.map(s => {
                const st = STATUS_STYLE[s.status];
                return (
                  <div key={s.id} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', flexWrap: 'wrap' }}>
                      <span style={{ fontFamily: 'Syne', fontWeight: 700, color: 'var(--text-muted)', fontSize: '0.85rem' }}>#{s.id}</span>
                      <span style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: '0.85rem', color: 'var(--text)' }}>{s.student_name}</span>
                      {s.is_premium && <span style={{ background: 'rgba(255,210,0,0.15)', color: '#ffd200', border: '1px solid rgba(255,210,0,0.3)', borderRadius: '100px', padding: '2px 10px', fontSize: '0.75rem', fontFamily: 'Syne', fontWeight: 600 }}>⭐ Premium</span>}
                      <span style={{ background: st.bg, border: `1px solid ${st.border}`, color: st.color, borderRadius: '100px', padding: '3px 12px', fontSize: '0.78rem', fontFamily: 'Syne', fontWeight: 600 }}>{st.label}</span>
                      <span style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {new Date(s.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.92rem', lineHeight: 1.75, marginBottom: '1rem' }}>{s.summary}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '1.25rem' }}>
                      {s.keywords?.map((kw, i) => (
                        <span key={i} style={{ background: 'rgba(108,99,255,0.1)', border: '1px solid rgba(108,99,255,0.2)', color: '#a8a3ff', borderRadius: '100px', padding: '3px 12px', fontSize: '0.78rem' }}>{kw}</span>
                      ))}
                    </div>
                    {s.status === 'pending' && (
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={() => handleValidate(s.id, 'validated')} disabled={actionId === s.id} style={{ flex: 1, padding: '10px', background: 'rgba(67,233,123,0.1)', border: '1px solid rgba(67,233,123,0.3)', borderRadius: '10px', color: '#43e97b', fontFamily: 'Syne', fontWeight: 700, cursor: 'pointer' }}>✓ Valider</button>
                        <button onClick={() => handleValidate(s.id, 'rejected')} disabled={actionId === s.id} style={{ flex: 1, padding: '10px', background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)', borderRadius: '10px', color: '#ff6584', fontFamily: 'Syne', fontWeight: 700, cursor: 'pointer' }}>✕ Rejeter</button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Tab Vérifications Premium */}
          {tab === 'verifications' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {verifs.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '4rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                  <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⭐</div>
                  <p>Aucune demande de vérification Premium pour l'instant.</p>
                </div>
              ) : verifs.map(v => {
                const st = VERIF_STYLE[v.status];
                return (
                  <div key={v.id} style={{ background: 'var(--surface)', border: '1px solid rgba(255,210,0,0.2)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', flexWrap: 'wrap' }}>
                      <span style={{ fontFamily: 'Syne', fontWeight: 700, color: '#ffd200' }}>⭐ Demande #{v.id}</span>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>par {v.summary.student_name}</span>
                      <span style={{ background: st.bg, border: `1px solid ${st.border}`, color: st.color, borderRadius: '100px', padding: '3px 12px', fontSize: '0.78rem', fontFamily: 'Syne', fontWeight: 600 }}>{st.label}</span>
                      <span style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {new Date(v.requested_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <div style={{ background: 'var(--surface2)', borderRadius: '10px', padding: '1rem', marginBottom: '1rem' }}>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'Syne', marginBottom: '0.5rem' }}>RÉSUMÉ À VÉRIFIER</p>
                      <p style={{ fontSize: '0.92rem', lineHeight: 1.75 }}>{v.summary.summary}</p>
                    </div>

                    {v.status === 'pending' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <textarea
                          placeholder="Commentaire du superviseur (obligatoire si incorrect)..."
                          value={comments[v.id] || ''}
                          onChange={e => setComments(prev => ({ ...prev, [v.id]: e.target.value }))}
                          rows={3}
                          style={{
                            width: '100%', background: 'var(--surface2)',
                            border: '1px solid var(--border)', borderRadius: '10px',
                            color: 'var(--text)', padding: '0.75rem 1rem',
                            fontFamily: 'DM Sans', fontSize: '0.9rem', resize: 'vertical', outline: 'none',
                          }}
                        />
                        <div style={{ display: 'flex', gap: '10px' }}>
                          <button onClick={() => handleRespond(v.id, 'correct')} disabled={actionId === v.id} style={{ flex: 1, padding: '10px', background: 'rgba(67,233,123,0.1)', border: '1px solid rgba(67,233,123,0.3)', borderRadius: '10px', color: '#43e97b', fontFamily: 'Syne', fontWeight: 700, cursor: 'pointer' }}>✅ Correct</button>
                          <button onClick={() => handleRespond(v.id, 'incorrect')} disabled={actionId === v.id} style={{ flex: 1, padding: '10px', background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)', borderRadius: '10px', color: '#ff6584', fontFamily: 'Syne', fontWeight: 700, cursor: 'pointer' }}>❌ À corriger</button>
                        </div>
                      </div>
                    )}

                    {v.status !== 'pending' && v.supervisor_comment && (
                      <div style={{ background: 'rgba(108,99,255,0.08)', border: '1px solid rgba(108,99,255,0.2)', borderRadius: '10px', padding: '0.75rem 1rem', marginTop: '0.5rem' }}>
                        <p style={{ fontSize: '0.8rem', fontFamily: 'Syne', color: 'var(--text-muted)', marginBottom: '4px' }}>COMMENTAIRE SUPERVISEUR</p>
                        <p style={{ fontSize: '0.9rem' }}>{v.supervisor_comment}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
