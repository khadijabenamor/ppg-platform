import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import * as evalAPI from '../api/evaluation';

export default function Evaluation() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('quizzes');
    const [quizzes, setQuizzes] = useState([]);
    const [flashcards, setFlashcards] = useState([]);
    const [progress, setProgress] = useState(null);
    const [newQuiz, setNewQuiz] = useState({ title: '', course_id: '', course_content: '', difficulty: 'medium', questions_count: 5 });
    const [newFlashcard, setNewFlashcard] = useState({ course_id: '', course_content: '', flashcards_count: 5, tags: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedQuiz, setSelectedQuiz] = useState(null);
    const [quizMode, setQuizMode] = useState(null);
    const [userAnswers, setUserAnswers] = useState({});
    const [quizResult, setQuizResult] = useState(null);
    const [flippedCards, setFlippedCards] = useState({});

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        try {
            const [q, f, p] = await Promise.all([
                evalAPI.getQuizzes(),
                evalAPI.getFlashcards(),
                evalAPI.getProgress()
            ]);
            setQuizzes(q.data);
            setFlashcards(f.data);
            setProgress(p.data);
        } catch (e) { console.error(e); }
    };

    const createQuiz = async () => {
        if (!newQuiz.title || !newQuiz.course_id || !newQuiz.course_content) {
            setError('Veuillez remplir tous les champs'); return;
        }
        setLoading(true); setError('');
        try {
            await evalAPI.createQuizWithAI({ ...newQuiz, count: newQuiz.questions_count });
            loadData();
            setNewQuiz({ title: '', course_id: '', course_content: '', difficulty: 'medium', questions_count: 5 });
        } catch (e) { setError(e.response?.data?.errors?.[0] || 'Erreur'); }
        setLoading(false);
    };

    const createFlashcard = async () => {
        if (!newFlashcard.course_id || !newFlashcard.course_content) {
            setError('Veuillez remplir tous les champs'); return;
        }
        setLoading(true); setError('');
        try {
            const tags = newFlashcard.tags ? newFlashcard.tags.split(',').map(t => t.trim()).filter(t => t) : [];
            await evalAPI.generateFlashcards(newFlashcard.course_content, newFlashcard.course_id, newFlashcard.flashcards_count, tags);
            loadData();
            setNewFlashcard({ course_id: '', course_content: '', flashcards_count: 5, tags: '' });
        } catch (e) { setError(e.response?.data?.errors?.[0] || 'Erreur'); }
        setLoading(false);
    };

    const delQuiz = async (id) => { try { await evalAPI.deleteQuiz(id); loadData(); } catch {} };
    const delFlashcard = async (id) => { try { await evalAPI.deleteFlashcard(id); loadData(); } catch {} };

    const flipFlashcard = (id) => setFlippedCards(prev => ({ ...prev, [id]: !prev[id] }));
    
    const markFlashcardReviewed = async (id) => {
        try {
            await evalAPI.markFlashcardReviewed(id);
            loadData();
        } catch (e) { console.error(e); }
    };

    const startQuiz = (quiz) => { setSelectedQuiz(quiz); setQuizMode('answer'); setUserAnswers({}); setQuizResult(null); };
    const submitQuiz = async () => {
        try {
            const answers = Object.entries(userAnswers).map(([question_id, answerIndex]) => {
                const question = selectedQuiz.questions.find(q => q.id === parseInt(question_id));
                const answerText = question?.options?.[answerIndex] || "";
                let answerLetter = "";
                const letterMatch = answerText.match(/^([A-D])\)?\.?\s*/i);
                if (letterMatch) {
                    answerLetter = letterMatch[1].toUpperCase();
                } else {
                    const allOptions = question?.options || [];
                    const optionIndex = allOptions.findIndex(opt => opt === answerText);
                    if (optionIndex >= 0) {
                        answerLetter = String.fromCharCode(65 + optionIndex);
                    }
                }
                return {
                    question_id: parseInt(question_id),
                    answer: answerLetter
                };
            });
            const res = await evalAPI.submitQuiz(selectedQuiz.id, answers);
            setQuizResult(res.data);
            setQuizMode('result');
            loadData();
        } catch (e) { setError('Erreur lors de la soumission: ' + (e.response?.data?.error || e.message)); }
    };

    const difficultyStyle = (diff) => {
        const styles = { 
            easy: { background: 'rgba(34,197,94,0.2)', color: '#22c55e' }, 
            medium: { background: 'rgba(234,179,8,0.2)', color: '#eab308' }, 
            hard: { background: 'rgba(239,68,68,0.2)', color: '#ef4444' } 
        };
        return styles[diff] || {};
    };

    return (
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem' }}>
            <header style={{ marginBottom: '2rem' }}>
                <div style={{
                    display: 'inline-block',
                    background: 'linear-gradient(135deg, rgba(108,99,255,0.15), rgba(255,101,132,0.1))',
                    border: '1px solid rgba(108,99,255,0.3)',
                    borderRadius: '100px', padding: '6px 16px',
                    fontSize: '0.8rem', fontFamily: 'Syne', fontWeight: 600,
                    color: 'var(--accent)', letterSpacing: '0.05em', marginBottom: '1rem',
                }}>MODULE M3 — AUTO-ÉVALUATION</div>
                <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
                    Quiz & Flashcards
                </h1>
                <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Teste tes connaissances avec des quiz et des flashcards générés par IA
                </p>
            </header>

            {error && <div style={{ background: 'rgba(255,101,132,0.1)', border: '1px solid rgba(255,101,132,0.3)', borderRadius: '10px', padding: '0.75rem', color: '#ff6584', marginBottom: '1rem' }}>{error}</div>}

            <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
                {[
                    { id: 'quizzes', label: '📝 Quizzes' },
                    { id: 'flashcards', label: '🗃️ Flashcards' },
                    { id: 'progress', label: '📊 Progression' }
                ].map(t => (
                    <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
                        padding: '12px 24px',
                        background: 'transparent',
                        border: 'none',
                        borderBottom: `2px solid ${activeTab === t.id ? 'var(--accent)' : 'transparent'}`,
                        color: activeTab === t.id ? 'var(--accent)' : 'var(--text-muted)',
                        fontFamily: 'Syne', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
                    }}>{t.label}</button>
                ))}
            </div>

            {activeTab === 'quizzes' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--surface)', border: '2px solid rgba(108,99,255,0.3)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                            <span style={{ fontSize: '1.5rem' }}>🤖</span>
                            <h3 style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: '1.1rem' }}>Générer un Quiz avec l'IA</h3>
                        </div>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Entrez le contenu du cours pour générer automatiquement des questions</p>
                        <div style={{ display: 'grid', gap: '0.75rem' }}>
                            <input value={newQuiz.title} onChange={e => setNewQuiz({...newQuiz, title: e.target.value})} placeholder="Titre du quiz" style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }} />
                            <input value={newQuiz.course_id} onChange={e => setNewQuiz({...newQuiz, course_id: e.target.value})} placeholder="ID du cours (ex: python101)" style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }} />
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                            <select value={newQuiz.difficulty} onChange={e => setNewQuiz({...newQuiz, difficulty: e.target.value})} style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }}>
                                <option value="easy">Facile</option>
                                <option value="medium">Moyen</option>
                                <option value="hard">Difficile</option>
                            </select>
                            <input 
                                type="number" 
                                value={newQuiz.questions_count} 
                                onChange={e => setNewQuiz({...newQuiz, questions_count: parseInt(e.target.value) || 5})}
                                min={1}
                                max={50}
                                placeholder="Nombre de questions"
                                style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }}
                            />
                            </div>
                            <textarea value={newQuiz.course_content} onChange={e => setNewQuiz({...newQuiz, course_content: e.target.value})} placeholder="Collez le contenu du cours ici..." rows={4} style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans', resize: 'vertical' }} />
                            <button onClick={createQuiz} disabled={loading} style={{ background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px 24px', fontFamily: 'Syne', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}>
                                {loading ? 'Génération en cours...' : 'Générer le Quiz avec l\'IA'}
                            </button>
                        </div>
                    </div>

                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <h3 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>Mes Quizzes ({quizzes.length})</h3>
                        {quizzes.length === 0 && <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Aucun quiz créé</p>}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {quizzes.map(q => (
                                <div key={q.id} style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>{q.title}</h4>
                                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{q.description || 'Quiz généré par IA'}</p>
                                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                                                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', ...difficultyStyle(q.difficulty) }}>{q.difficulty}</span>
                                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{q.course_id}</span>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button onClick={() => startQuiz(q)} style={{ color: 'var(--accent)', fontSize: '0.85rem', background: 'transparent', border: 'none', cursor: 'pointer' }}>Commencer</button>
                                            <button onClick={() => delQuiz(q.id)} style={{ color: '#ff6584', fontSize: '0.85rem', background: 'transparent', border: 'none', cursor: 'pointer' }}>Supprimer</button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {selectedQuiz && quizMode && (
                        <div style={{ background: 'var(--surface)', border: '2px solid var(--accent)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                            <h3 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>{selectedQuiz.title}</h3>
                            {quizMode === 'answer' && selectedQuiz.questions?.map((q, i) => (
                                <div key={i} style={{ marginBottom: '1.25rem' }}>
                                    <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{i + 1}. {q.question_text}</p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                        {q.options?.map((opt, j) => (
                                            <label key={j} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <input type="radio" name={`q${q.id}`} checked={userAnswers[q.id] === j} onChange={() => setUserAnswers({ ...userAnswers, [q.id]: j })} />
                                                <span>{opt}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            ))}
                            {quizMode === 'answer' && <button onClick={submitQuiz} style={{ background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px 24px', fontFamily: 'Syne', fontWeight: 600, cursor: 'pointer' }}>Soumettre</button>}
                            {quizMode === 'result' && quizResult && (
                                <div>
                                    <div style={{ 
                                        background: quizResult.percentage >= 50 
                                            ? 'linear-gradient(135deg, rgba(67,233,123,0.2), rgba(34,197,94,0.1))' 
                                            : 'linear-gradient(135deg, rgba(255,101,132,0.2), rgba(239,68,68,0.1))',
                                        border: `2px solid ${quizResult.percentage >= 50 ? 'rgba(67,233,123,0.5)' : 'rgba(255,101,132,0.5)'}`,
                                        borderRadius: '12px', padding: '1.5rem', textAlign: 'center', marginBottom: '1.5rem' 
                                    }}>
                                        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Score Final</p>
                                        <p style={{ 
                                            fontSize: '3rem', fontWeight: 800, 
                                            color: quizResult.percentage >= 50 ? '#43e97b' : '#ff6584',
                                            lineHeight: 1
                                        }}>
                                            {quizResult.percentage.toFixed(0)}%
                                        </p>
                                        <p style={{ fontSize: '1rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                            {quizResult.score} / {quizResult.total_points} réponses correctes
                                        </p>
                                    </div>
                                    <h4 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>Détails des réponses:</h4>
                                    {Object.values(quizResult.graded_answers || quizResult.answers || {}).map((r, i) => (
                                        <div key={i} style={{ 
                                            marginBottom: '0.75rem', 
                                            padding: '0.75rem',
                                            background: r.is_correct ? 'rgba(67,233,123,0.1)' : 'rgba(255,101,132,0.1)',
                                            borderRadius: '8px',
                                            borderLeft: `3px solid ${r.is_correct ? '#43e97b' : '#ff6584'}`
                                        }}>
                                            <p style={{ marginBottom: '0.25rem', color: 'var(--text)' }}>
                                                <span style={{ fontWeight: 600 }}>{i + 1}.</span> {r.question_text?.substring(0, 80) || 'Question'}...
                                            </p>
                                            <p style={{ fontSize: '0.85rem', color: r.is_correct ? '#43e97b' : '#ff6584' }}>
                                                {r.is_correct ? '✓ Correct' : `✕ Votre réponse: ${r.user_answer}`}
                                            </p>
                                            {!r.is_correct && (
                                                <p style={{ fontSize: '0.8rem', color: 'var(--accent3)', marginTop: '0.25rem' }}>
                                                    → Réponse correcte: {r.correct_answer}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                    <button onClick={() => { setQuizMode(null); setSelectedQuiz(null); setQuizResult(null); }} style={{ marginTop: '1rem', background: 'var(--accent)', border: 'none', borderRadius: '8px', padding: '12px 24px', fontFamily: 'Syne', fontWeight: 600, cursor: 'pointer', color: '#fff' }}>Fermer</button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'flashcards' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--surface)', border: '2px solid rgba(108,99,255,0.3)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                            <span style={{ fontSize: '1.5rem' }}>🤖</span>
                            <h3 style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: '1.1rem' }}>Générer avec l'IA</h3>
                        </div>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Entrez le contenu du cours pour générer automatiquement des flashcards</p>
                        <div style={{ display: 'grid', gap: '0.75rem' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                            <input value={newFlashcard.course_id} onChange={e => setNewFlashcard({...newFlashcard, course_id: e.target.value})} placeholder="ID du cours (ex: python101)" style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }} />
                            <input 
                                type="number" 
                                value={newFlashcard.flashcards_count} 
                                onChange={e => setNewFlashcard({...newFlashcard, flashcards_count: parseInt(e.target.value) || 5})}
                                min={1}
                                max={50}
                                placeholder="Nombre de flashcards"
                                style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }}
                            />
                            </div>
                            <input value={newFlashcard.tags} onChange={e => setNewFlashcard({...newFlashcard, tags: e.target.value})} placeholder="Tags (séparés par virgules, ex: python, basics, fonctions)" style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans' }} />
                            <textarea value={newFlashcard.course_content} onChange={e => setNewFlashcard({...newFlashcard, course_content: e.target.value})} placeholder="Collez le contenu du cours ici..." rows={4} style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', color: 'var(--text)', fontFamily: 'DM Sans', resize: 'vertical' }} />
                            <button onClick={createFlashcard} disabled={loading} style={{ background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px 24px', fontFamily: 'Syne', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}>
                                {loading ? 'Génération en cours...' : 'Générer des Flashcards'}
                            </button>
                        </div>
                    </div>

                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <h3 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>Mes Flashcards ({flashcards.length})</h3>
                        {flashcards.length === 0 && <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Aucune flashcard créée</p>}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                            {flashcards.map(fc => (
                                <div 
                                    key={fc.id} 
                                    onClick={() => flipFlashcard(fc.id)}
                                    style={{ 
                                        background: 'var(--bg)', 
                                        border: `2px solid ${fc.is_reviewed ? 'rgba(67,233,123,0.5)' : 'var(--border)'}`, 
                                        borderRadius: '12px', 
                                        padding: '1.5rem',
                                        cursor: 'pointer',
                                        minHeight: '150px',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        justifyContent: 'center',
                                        transition: 'all 0.3s ease',
                                        position: 'relative'
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                        <span style={{ fontSize: '0.7rem', color: 'var(--accent)', fontWeight: 600 }}>
                                            {flippedCards[fc.id] ? 'RÉPONSE' : 'QUESTION'}
                                        </span>
                                        <button onClick={(e) => { e.stopPropagation(); delFlashcard(fc.id); }} style={{ background: 'transparent', border: 'none', color: '#ff6584', cursor: 'pointer', padding: 0 }}>✕</button>
                                    </div>
                                    <p style={{ fontWeight: 600, fontSize: '1.1rem', textAlign: 'center' }}>
                                        {flippedCards[fc.id] ? fc.answer : fc.question}
                                    </p>
                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '0.5rem' }}>
                                        {flippedCards[fc.id] ? 'Cliquez pour voir la question' : 'Cliquez pour voir la réponse'}
                                    </p>
                                    <div style={{ display: 'flex', gap: '6px', marginTop: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                                        {!fc.is_reviewed && (
                                            <button 
                                                onClick={(e) => { e.stopPropagation(); markFlashcardReviewed(fc.id); }}
                                                style={{ 
                                                    background: 'rgba(67,233,123,0.2)', 
                                                    border: '1px solid rgba(67,233,123,0.4)', 
                                                    borderRadius: '100px', 
                                                    padding: '4px 12px', 
                                                    fontSize: '0.75rem',
                                                    color: 'var(--accent3)',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                ✓ Marquer révisé
                                            </button>
                                        )}
                                        {fc.is_reviewed && (
                                            <span style={{ background: 'rgba(67,233,123,0.2)', color: 'var(--accent3)', borderRadius: '100px', padding: '4px 12px', fontSize: '0.75rem' }}>
                                                ✓ Révisé
                                            </span>
                                        )}
                                        {fc.is_ai_generated && (
                                            <span style={{ background: 'rgba(108,99,255,0.15)', color: '#a8a3ff', borderRadius: '100px', padding: '2px 10px', fontSize: '0.7rem' }}>IA</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'progress' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <h3 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>Statistiques Globales</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                            <div style={{ background: 'rgba(108,99,255,0.15)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                                <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent)' }}>{progress?.quizzes_completed || 0}</p>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Quizzes Complétés</p>
                            </div>
                            <div style={{ background: 'rgba(67,233,123,0.15)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                                <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent3)' }}>{progress?.average_score || 0}%</p>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Score Moyen</p>
                            </div>
                            <div style={{ background: 'rgba(255,193,7,0.15)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                                <p style={{ fontSize: '2rem', fontWeight: 700, color: '#ffc107' }}>{progress?.streak || 0}</p>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Jours Consécutifs</p>
                            </div>
                            <div style={{ background: 'rgba(255,101,132,0.15)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                                <p style={{ fontSize: '2rem', fontWeight: 700, color: '#ff6584' }}>{progress?.flashcards_reviewed || 0}</p>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Flashcards Révisées</p>
                            </div>
                        </div>
                    </div>

                    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem' }}>
                        <h3 style={{ fontFamily: 'Syne', fontWeight: 700, marginBottom: '1rem' }}>Historique des Tentatives</h3>
                        {(!progress?.attempts || progress.attempts.length === 0) && <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Aucun historique</p>}
                        {progress?.attempts?.map((attempt, i) => (
                            <div key={i} style={{ borderBottom: '1px solid var(--border)', padding: '0.75rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <p style={{ fontWeight: 600 }}>{attempt.quiz_title}</p>
                                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{new Date(attempt.attempted_at).toLocaleDateString('fr-FR')}</p>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 700, color: attempt.score >= 60 ? 'var(--accent3)' : '#ff6584' }}>{attempt.score}%</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}