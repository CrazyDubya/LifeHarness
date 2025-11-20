import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { entriesApi } from '../services/api';
import type { LifeEntry } from '../types';

export default function Entries() {
  const [entries, setEntries] = useState<LifeEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<LifeEntry | null>(null);
  const [filter, setFilter] = useState({ time_bucket: '', topic_bucket: '' });

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    try {
      const data = await entriesApi.list(
        filter.time_bucket || filter.topic_bucket ? filter : undefined
      );
      setEntries(data);
    } catch (err) {
      console.error('Failed to load entries:', err);
    }
  };

  const updateSeal = async (entryId: string, updates: any) => {
    try {
      await entriesApi.updateSeal(entryId, updates);
      await loadEntries();
      setSelectedEntry(null);
    } catch (err) {
      console.error('Failed to update seal:', err);
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
      </nav>

      <div className="container">
        <div className="card">
          <h1>Life Entries</h1>
          <p>All your documented memories and experiences</p>
        </div>

        <div className="grid" style={{ gridTemplateColumns: '300px 1fr', gap: '20px' }}>
          <div>
            <div className="card">
              <h3>Filters</h3>
              <label>Time Period</label>
              <select
                value={filter.time_bucket}
                onChange={(e) => setFilter({ ...filter, time_bucket: e.target.value })}
              >
                <option value="">All</option>
                <option value="pre10">Pre-10</option>
                <option value="10s">10s</option>
                <option value="20s">20s</option>
                <option value="30s">30s</option>
                <option value="40s">40s</option>
                <option value="50plus">50+</option>
              </select>

              <button className="button" onClick={loadEntries} style={{ marginTop: '8px' }}>
                Apply Filters
              </button>
            </div>
          </div>

          <div>
            {entries.map((entry) => (
              <div
                key={entry.id}
                className="card"
                style={{
                  cursor: 'pointer',
                  borderLeft: selectedEntry?.id === entry.id ? '4px solid #007bff' : 'none',
                }}
                onClick={() => setSelectedEntry(entry)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <h3>{entry.headline}</h3>
                    <div style={{ fontSize: '14px', color: '#888', marginBottom: '8px' }}>
                      {entry.timeframe_label} • {entry.time_bucket}
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {entry.visibility}
                  </div>
                </div>
                <p style={{ color: '#666', marginTop: '8px' }}>{entry.distilled}</p>
                {entry.tags && entry.tags.length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    {entry.tags.map((tag) => (
                      <span
                        key={tag}
                        style={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          marginRight: '4px',
                          background: '#e3f2fd',
                          borderRadius: '4px',
                          fontSize: '12px',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {entries.length === 0 && (
              <div className="card">
                <p style={{ textAlign: 'center', color: '#888' }}>
                  No entries yet. Start a thread to create your first entry!
                </p>
              </div>
            )}
          </div>
        </div>

        {selectedEntry && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
            onClick={() => setSelectedEntry(null)}
          >
            <div
              className="card"
              style={{ maxWidth: '600px', maxHeight: '80vh', overflow: 'auto' }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2>{selectedEntry.headline}</h2>
              <div style={{ marginBottom: '16px', fontSize: '14px', color: '#888' }}>
                {selectedEntry.timeframe_label}
              </div>

              <h3>Full Text</h3>
              <p style={{ whiteSpace: 'pre-wrap' }}>{selectedEntry.raw_text}</p>

              <h3 style={{ marginTop: '20px' }}>Visibility Settings</h3>
              <label>Visibility Level</label>
              <select
                value={selectedEntry.visibility}
                onChange={(e) =>
                  updateSeal(selectedEntry.id, { visibility: e.target.value })
                }
              >
                <option value="self">Self Only</option>
                <option value="trusted">Trusted People</option>
                <option value="heirs">Heirs</option>
                <option value="public">Public</option>
              </select>

              <button
                className="button button-secondary"
                onClick={() => setSelectedEntry(null)}
                style={{ marginTop: '16px' }}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
