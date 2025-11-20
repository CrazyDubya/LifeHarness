import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { threadsApi, entriesApi, profileApi } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import type { Thread, CoverageCell, Profile } from '../types';
import CoverageHeatmap from '../components/CoverageHeatmap';

export default function Dashboard() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [coverage, setCoverage] = useState<CoverageCell[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [showNewThread, setShowNewThread] = useState(false);
  const [newThread, setNewThread] = useState({ title: '', root_prompt: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [threadsData, coverageData, profileData] = await Promise.all([
        threadsApi.list(),
        entriesApi.getCoverage(),
        profileApi.get(),
      ]);
      setThreads(threadsData);
      setCoverage(coverageData);
      setProfile(profileData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  };

  const createThread = async () => {
    if (!newThread.title || !newThread.root_prompt) return;

    try {
      const thread = await threadsApi.create(newThread);
      navigate(`/thread/${thread.id}`);
    } catch (err) {
      console.error('Failed to create thread:', err);
    }
  };

  return (
    <div>
      <nav className="nav">
        <div>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/entries">My Entries</Link>
          <Link to="/autobiography">Autobiography</Link>
        </div>
        <button onClick={logout} className="button button-secondary">
          Logout
        </button>
      </nav>

      <div className="container">
        <div className="card">
          <h1>Life Harness Dashboard</h1>
          <p>Welcome back! Continue documenting your life story.</p>
        </div>

        <div className="card">
          <h2>Coverage Heatmap</h2>
          <p style={{ marginBottom: '16px', color: '#666' }}>
            Visual representation of which life areas you've explored
          </p>
          <CoverageHeatmap data={coverage} />
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ margin: 0 }}>Your Threads</h2>
            <button className="button" onClick={() => setShowNewThread(true)}>
              New Thread
            </button>
          </div>

          {showNewThread && (
            <div style={{ marginBottom: '20px', padding: '16px', background: '#f8f9fa', borderRadius: '4px' }}>
              <h3>Create New Thread</h3>
              <label>Title</label>
              <input
                type="text"
                value={newThread.title}
                onChange={(e) => setNewThread({ ...newThread, title: e.target.value })}
                placeholder="e.g., My College Years"
              />
              <label>Root Prompt</label>
              <textarea
                value={newThread.root_prompt}
                onChange={(e) => setNewThread({ ...newThread, root_prompt: e.target.value })}
                rows={3}
                placeholder="Describe what this thread is about..."
              />
              <div style={{ display: 'flex', gap: '10px' }}>
                <button className="button" onClick={createThread}>
                  Create
                </button>
                <button className="button button-secondary" onClick={() => setShowNewThread(false)}>
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div className="grid grid-2">
            {threads.map((thread) => (
              <div
                key={thread.id}
                className="card"
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/thread/${thread.id}`)}
              >
                <h3>{thread.title}</h3>
                <p style={{ color: '#666', fontSize: '14px' }}>{thread.root_prompt}</p>
                <div style={{ marginTop: '12px', fontSize: '14px', color: '#888' }}>
                  <div>Questions asked: {thread.questions_asked}</div>
                  <div>Last active: {new Date(thread.last_activity_at).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>

          {threads.length === 0 && !showNewThread && (
            <p style={{ textAlign: 'center', color: '#888', padding: '40px' }}>
              No threads yet. Create your first thread to start documenting your life!
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
