import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { generateSummary, generateFromPDF, requestVerification, getMySummaries } from '../api/ai';

export default function Etudiant() {
    const { user } = useAuth();
    const [tab, setTab]               = useState('text');
    const [text, setText]             = useState('');
    const [pdfFile, setPdfFile]       = useState(null);
    const [result, setResult]         = useState(null);
    const [loading, setLoading]       = useState(false);
    const [verifLoading, setVerifLoading] = useState(false);
    const [verifDone, setVerifDone]   = useState(false);
    const [error, setError]           = useState('');
    const [mySummaries, setMySummaries] = useState([]);
    const intervalRef = useRef(null);

    const isPremium = user?.is_premium || false;

    // Polling toutes les 30 secondes
    useEffect(() => {
        const fetchMySummaries = async () => {
            try {
                const res = await getMySummaries(user?.first_name || user?.username);
                setMySummaries(res.data);
            } catch {}
        };

        fetchMySummaries();
        intervalRef.current = setInterval(fetchMySummaries, 30000);
        return () => clearInterval(intervalRef.current);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

    const handleGenerate = async () => {
        if (tab === 'text' && !text.trim()) { setError("Entre un texte d'abord !"); return; }
        if (tab === 'pdf' && !pdfFile) { setError("Sélectionne un fichier PDF d'abord !"); return; }
        setLoading(true); setError(''); setResult(null); setVerifDone(false);
        try {
            let res;
            if (tab === 'text') {
                res = await generateSummary(text, user?.first_name || user?.username, isPremium);
            } else {
                res = await generateFromPDF(pdfFile, user?.first_name || user?.username, isPremium);
            }
            setResult(res.data);
            // Rafraîchit la liste après génération
            const updated = await getMySummaries(user?.first_name || user?.username);
            setMySummaries(updated.data);
        } catch (e) {
            setError(e.response?.data?.error || 'Erreur de connexion au serveur.');
        } finally { setLoading(false); }
    };

    const handleRequestVerification = async () => {
        setVerifLoading(true);
        try {
            await requestVerification(result.id);
            setVerifDone(true);
            // Rafraîchit la liste
            const updated = await getMySummaries(user?.first_name || user?.username);
            setMySummaries(updated.data);
        } catch (e) {
            setError(e.response?.data?.error || 'Erreur lors de la demande.');
        } finally { setVerifLoading(false); }
    };

    const hasNewResponse = mySummaries.some(
        s => s.verification?.status === 'correct' || s.verification?.status === 'incorrect'
    );

    return (
        <div style={{ maxWidth: 860, margin: '0 auto', padding: '3rem 2rem' }}>

            {/* Header */}
            <div style={{ marginBottom: '2.5rem' }}>
                <div style={{
                    display: 'inline-block',
                    background: 'linear-gradient(135deg, rgba(108,99,255,0.15), rgba(255,101,132,0.1))',
                    border: '1px solid rgba(108,99,255,0.3)',
                    borderRadius: '100px', padding: '6px 16px',
                    fontSize: '0.8rem', fontFamily: 'Syne', fontWeight: 600,
                    color: 'var(--accent)', letterSpacing: '0.05em', marginBottom: '1rem',
                }}>MODULE M2 — IA & GÉNÉRATION</div>
                <h1 style={{ fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.2 }}>
                    Bonjour {user?.first_name || user?.username} 👋<br />
                    <span style={{ background: 'linear-gradient(135deg, var(--accent), var(--accent2))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Génère ton résumé
          </span>
                </h1>
                <p style={{ color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                    Depuis un texte ou un fichier PDF — Mistral AI génère le résumé et les mots-clés.
                </p>
            </div>

            {/* Tabs texte / PDF */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '1.25rem' }}>
                {[{ id: 'text', label: '✏️ Texte' }, { id: 'pdf', label: '📄 PDF' }].map(({ id, label }) => (
                    <button key={id} onClick={() => { setTab(id); setResult(null); setError(''); }} style={{
                        padding: '10px 24px', borderRadius: '10px',
                        border: `1px solid ${tab === id ? 'var(--accent)' : 'var(--border)'}`,
                        background: tab === id ? 'var(--accent)' : 'var(--surface)',
                        color: tab === id ? '#fff' : 'var(--text-muted)',
                        fontFamily: 'Syne', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
                    }}>{label}</button>
                ))}
            </div>

            {/* Zone texte */}
            {tab === 'text' && (
                <div style={{ marginBottom: '1.25rem' }}>
          <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Colle ici le contenu de ton cours..."
              rows={9}
              style={{
                  width: '100%', background: 'var(--surface)',
                  border: '1px solid var(--border)', borderRadius: 'var(--radius)',
                  color: 'var(--text)', fontSize: '0.95rem', padding: '1.25rem',
                  resize: 'vertical', outline: 'none',
                  fontFamily: 'DM Sans, sans-serif', lineHeight: 1.7,
              }}
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
                    <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                        {text.length} caractères
                    </div>
                </div>
            )}

            {/* Zone PDF */}
            {tab === 'pdf' && (
                <div style={{ marginBottom: '1.25rem' }}>
                    <div
                        onClick={() => document.getElementById('pdf-input').click()}
                        style={{
                            background: 'var(--surface)', border: `2px dashed ${pdfFile ? 'var(--accent)' : 'var(--border)'}`,
                            borderRadius: 'var(--radius)', padding: '3rem 2rem',
                            textAlign: 'center', cursor: 'pointer',
                        }}
                    >
                        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📄</div>
                        {pdfFile ? (
                            <div>
                                <p style={{ color: 'var(--accent)', fontFamily: 'Syne', fontWeight: 600 }}>{pdfFile.name}</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
                                    {(pdfFile.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        ) : (
                            <div>
                                <p style={{ color: 'var(--text)', fontFamily: 'Syne', fontWeight: 600 }}>Clique pour sélectionner un PDF</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>Maximum 10 MB</p>
                            </div>
                        )}
                    </div>
                    <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }}
                           onChange={e => { setPdfFile(e.target.files[0]); setError(''); }} />
                    {pdfFile && (
                        <button onClick={() => setPdfFile(null)} style={{
                            marginTop: '8px', background: 'transparent', border: 'none',
                            color: 'var(--text-muted)', fontSize: '0.85rem', cursor: 'pointer',
                        }}>✕ Supprimer le fichier</button>
                    )}
                </div>
            )}

            {/* Error */}
            {error && (
                <div style={{
                    background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)',
                    borderRadius: '10px', padding: '1rem 1.25rem',
                    color: '#ff6584', fontSize: '0.9rem', marginBottom: '1rem',
                }}>⚠ {error}</div>
            )}

            {/* Bouton Générer */}
            <button onClick={handleGenerate} disabled={loading} style={{
                width: '100%', padding: '1rem',
                background: loading ? 'var(--surface2)' : 'linear-gradient(135deg, var(--accent), #8b7fff)',
                border: 'none', borderRadius: 'var(--radius)',
                color: '#fff', fontSize: '1rem', fontFamily: 'Syne', fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
            }}>
                {loading ? `⟳ Mistral traite ${tab === 'pdf' ? 'le PDF' : 'le texte'}... (1-2 min)` : `✦ Générer le résumé`}
            </button>

            {/* Résultat */}
            {result && (
                <div style={{ marginTop: '2.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

                    {result.file_name && (
                        <div style={{
                            background: 'rgba(108,99,255,0.08)', border: '1px solid rgba(108,99,255,0.2)',
                            borderRadius: '10px', padding: '0.75rem 1.25rem',
                            fontSize: '0.88rem', color: '#a8a3ff',
                        }}>📄 <strong>{result.file_name}</strong> — {result.text_length?.toLocaleString()} caractères extraits</div>
                    )}

                    {isPremium && (
                        <div style={{
                            background: 'linear-gradient(135deg, rgba(247,151,30,0.15), rgba(255,210,0,0.1))',
                            border: '1px solid rgba(255,210,0,0.3)', borderRadius: '10px',
                            padding: '0.75rem 1.25rem', color: '#ffd200',
                            fontSize: '0.9rem', fontFamily: 'Syne', fontWeight: 600,
                        }}>⭐ Compte Premium — Tu peux demander une vérification par le superviseur</div>
                    )}

                    {/* Résumé */}
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                            <span>📄</span>
                            <h3 style={{ fontFamily: 'Syne', fontSize: '1rem', fontWeight: 700 }}>Résumé généré</h3>
                            <span style={{
                                marginLeft: 'auto', background: 'rgba(67,233,123,0.15)', color: 'var(--accent3)',
                                border: '1px solid rgba(67,233,123,0.3)', borderRadius: '100px',
                                padding: '2px 12px', fontSize: '0.75rem', fontFamily: 'Syne', fontWeight: 600,
                            }}>EN ATTENTE</span>
                        </div>
                        <p style={{ color: 'var(--text)', lineHeight: 1.8, fontSize: '0.95rem' }}>{result.summary}</p>
                    </div>

                    {/* Mots-clés */}
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                            <span>🏷</span>
                            <h3 style={{ fontFamily: 'Syne', fontSize: '1rem', fontWeight: 700 }}>Mots-clés extraits</h3>
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {result.keywords.map((kw, i) => (
                                <span key={i} style={{
                                    background: 'rgba(108,99,255,0.12)', border: '1px solid rgba(108,99,255,0.25)',
                                    color: '#a8a3ff', borderRadius: '100px', padding: '5px 14px', fontSize: '0.85rem',
                                }}>{kw}</span>
                            ))}
                        </div>
                    </div>

                    {/* Bouton vérification Premium */}
                    {isPremium && (
                        verifDone ? (
                            <div style={{
                                background: 'rgba(67,233,123,0.1)', border: '1px solid rgba(67,233,123,0.3)',
                                borderRadius: 'var(--radius)', padding: '1rem 1.25rem',
                                color: '#43e97b', textAlign: 'center', fontFamily: 'Syne', fontWeight: 600,
                            }}>✅ Demande envoyée ! Le superviseur va vérifier ton résumé.</div>
                        ) : (
                            <button onClick={handleRequestVerification} disabled={verifLoading} style={{
                                width: '100%', padding: '1rem',
                                background: 'linear-gradient(135deg, #f7971e, #ffd200)',
                                border: 'none', borderRadius: 'var(--radius)',
                                color: '#000', fontSize: '1rem', fontFamily: 'Syne', fontWeight: 700,
                                cursor: verifLoading ? 'not-allowed' : 'pointer',
                            }}>
                                {verifLoading ? '⟳ Envoi...' : '⭐ Demander vérification par le superviseur'}
                            </button>
                        )
                    )}

                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                        Résumé #{result.id} sauvegardé
                    </p>
                </div>
            )}

            {/* ── Section Mes Résumés + Notifications ── */}
            {mySummaries.length > 0 && (
                <div style={{ marginTop: '3rem' }}>
                    <h2 style={{
                        fontFamily: 'Syne', fontSize: '1.3rem', fontWeight: 800,
                        marginBottom: '1.25rem', letterSpacing: '-0.02em',
                        display: 'flex', alignItems: 'center', gap: '10px',
                    }}>
                        📬 Mes résumés
                        {hasNewResponse && (
                            <span style={{
                                background: 'rgba(255,101,132,0.15)',
                                border: '1px solid rgba(255,101,132,0.3)',
                                borderRadius: '100px', padding: '2px 12px',
                                fontSize: '0.75rem', color: '#ff6584', fontWeight: 600,
                            }}>🔔 Nouvelle réponse !</span>
                        )}
                    </h2>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {mySummaries.map(s => (
                            <div key={s.id} style={{
                                background: 'var(--surface)', border: '1px solid var(--border)',
                                borderRadius: 'var(--radius)', padding: '1.5rem',
                            }}>
                                {/* Header résumé */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                                    <span style={{ fontFamily: 'Syne', fontWeight: 700, color: 'var(--text-muted)', fontSize: '0.85rem' }}>#{s.id}</span>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {s.source === 'pdf' ? `📄 ${s.file_name}` : '✏️ Texte'}
                  </span>
                                    <span style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {new Date(s.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                  </span>
                                </div>

                                {/* Aperçu résumé */}
                                <p style={{ fontSize: '0.9rem', lineHeight: 1.75, color: 'var(--text)', marginBottom: '1rem' }}>
                                    {s.summary}                                </p>

                                {/* Réponse du superviseur */}
                                {s.verification && (
                                    <div style={{
                                        background: s.verification.status === 'correct'
                                            ? 'rgba(67,233,123,0.08)'
                                            : s.verification.status === 'incorrect'
                                                ? 'rgba(255,101,132,0.08)'
                                                : 'rgba(255,193,7,0.08)',
                                        border: `1px solid ${
                                            s.verification.status === 'correct'
                                                ? 'rgba(67,233,123,0.3)'
                                                : s.verification.status === 'incorrect'
                                                    ? 'rgba(255,101,132,0.3)'
                                                    : 'rgba(255,193,7,0.3)'
                                        }`,
                                        borderRadius: '10px', padding: '1rem',
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: s.verification.supervisor_comment ? '0.75rem' : 0 }}>
                      <span style={{ fontSize: '1.1rem' }}>
                        {s.verification.status === 'correct' ? '✅' : s.verification.status === 'incorrect' ? '❌' : '⏳'}
                      </span>
                                            <span style={{
                                                fontFamily: 'Syne', fontWeight: 700, fontSize: '0.9rem',
                                                color: s.verification.status === 'correct' ? '#43e97b' : s.verification.status === 'incorrect' ? '#ff6584' : '#ffc107',
                                            }}>
                        {s.verification.status === 'correct'
                            ? 'Résumé correct !'
                            : s.verification.status === 'incorrect'
                                ? 'À corriger'
                                : 'En attente du superviseur...'}
                      </span>
                                        </div>
                                        {s.verification.supervisor_comment && (
                                            <p style={{ fontSize: '0.88rem', color: 'var(--text)', lineHeight: 1.6 }}>
                                                💬 {s.verification.supervisor_comment}
                                            </p>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </div>
    );
}