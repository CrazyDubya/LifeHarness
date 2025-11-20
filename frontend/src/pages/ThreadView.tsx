import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { threadsApi } from '../services/api';
import type { Thread, Question, Answer } from '../types';

export default function ThreadView() {
  const { threadId } = useParams<{ threadId: string }>();
  const navigate = useNavigate();
  const [thread, setThread] = useState<Thread | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState<Answer>({ question_id: '', choice_id: '', free_text: '' });
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (threadId) {
      loadThread();
    }
  }, [threadId]);

  const loadThread = async () => {
    if (!threadId) return;

    try {
      const threadData = await threadsApi.get(threadId);
      setThread(threadData);

      // Get first/next question
      await nextStep();
    } catch (err) {
      console.error('Failed to load thread:', err);
    }
  };

  const nextStep = async (lastAnswer?: Answer) => {
    if (!threadId) return;

    setLoading(true);
    try {
      const response = await threadsApi.step(threadId, {
        last_answer: lastAnswer,
        control: 'continue',
      });

      if (response.done) {
        setDone(true);
        setCurrentQuestion(null);
      } else if (response.question) {
        setCurrentQuestion(response.question);
        setAnswer({
          question_id: response.question.id,
          choice_id: '',
          free_text: '',
        });
      }
    } catch (err) {
      console.error('Failed to get next question:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!currentQuestion) return;

    // Validate answer
    if (currentQuestion.type === 'multiple_choice' && !answer.choice_id && !answer.free_text) {
      alert('Please select an option or provide text');
      return;
    }

    if (currentQuestion.type === 'short_answer' && !answer.free_text) {
      alert('Please provide an answer');
      return;
    }

    await nextStep(answer);
  };

  const handleStop = async () => {
    if (!threadId) return;

    await threadsApi.step(threadId, { control: 'stop' });
    navigate('/dashboard');
  };

  if (!thread) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div>
      <nav className="nav">
        <div>
          <Link to="/dashboard">Dashboard</Link>
        </div>
      </nav>

      <div className="container" style={{ maxWidth: '800px' }}>
        <div className="card">
          <h1>{thread.title}</h1>
          <p style={{ color: '#666' }}>{thread.root_prompt}</p>
          <div style={{ marginTop: '12px', fontSize: '14px', color: '#888' }}>
            Questions answered: {thread.questions_asked}
          </div>
        </div>

        {done && (
          <div className="card">
            <h2>Session Complete</h2>
            <p>You've chosen to stop for now. You can continue this thread anytime!</p>
            <button className="button" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </button>
          </div>
        )}

        {!done && currentQuestion && (
          <div className="card">
            <form onSubmit={handleSubmit}>
              <h2 style={{ marginBottom: '20px' }}>{currentQuestion.text}</h2>

              {currentQuestion.type === 'multiple_choice' && currentQuestion.options && (
                <div style={{ marginBottom: '20px' }}>
                  {currentQuestion.options.map((option) => (
                    <label
                      key={option.id}
                      style={{
                        display: 'block',
                        padding: '12px',
                        marginBottom: '8px',
                        border: '2px solid #ddd',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        backgroundColor:
                          answer.choice_id === option.id ? '#e3f2fd' : 'white',
                      }}
                    >
                      <input
                        type="radio"
                        name="choice"
                        value={option.id}
                        checked={answer.choice_id === option.id}
                        onChange={(e) =>
                          setAnswer({ ...answer, choice_id: e.target.value })
                        }
                        style={{ marginRight: '8px' }}
                      />
                      {option.text}
                    </label>
                  ))}

                  {answer.choice_id === 'OTHER' && (
                    <div style={{ marginTop: '16px' }}>
                      <label>Please explain:</label>
                      <textarea
                        value={answer.free_text || ''}
                        onChange={(e) =>
                          setAnswer({ ...answer, free_text: e.target.value })
                        }
                        rows={4}
                        placeholder="Share your thoughts..."
                      />
                    </div>
                  )}

                  {answer.choice_id && answer.choice_id !== 'OTHER' && (
                    <div style={{ marginTop: '16px' }}>
                      <label>Want to elaborate? (optional)</label>
                      <textarea
                        value={answer.free_text || ''}
                        onChange={(e) =>
                          setAnswer({ ...answer, free_text: e.target.value })
                        }
                        rows={3}
                        placeholder="Add more details if you'd like..."
                      />
                    </div>
                  )}
                </div>
              )}

              {currentQuestion.type === 'short_answer' && (
                <div style={{ marginBottom: '20px' }}>
                  <textarea
                    value={answer.free_text || ''}
                    onChange={(e) =>
                      setAnswer({ ...answer, free_text: e.target.value })
                    }
                    rows={8}
                    placeholder="Write your response..."
                    style={{ fontSize: '16px' }}
                  />
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="button" disabled={loading}>
                  {loading ? 'Processing...' : 'Continue'}
                </button>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={handleStop}
                  disabled={loading}
                >
                  Stop for Today
                </button>
              </div>
            </form>
          </div>
        )}

        {loading && (
          <div className="card" style={{ textAlign: 'center' }}>
            <p>Generating next question...</p>
          </div>
        )}
      </div>
    </div>
  );
}
