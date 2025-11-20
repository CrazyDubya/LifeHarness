import { useState } from 'react';
import { Link } from 'react-router-dom';
import { autobiographyApi } from '../services/api';
import type { Autobiography } from '../types';

export default function AutobiographyView() {
  const [autobiography, setAutobiography] = useState<Autobiography | null>(null);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    audience: 'self' as 'self' | 'trusted' | 'heirs' | 'public',
    tone: 'balanced' as 'light' | 'balanced' | 'deep',
    scopeType: 'full',
    yearFrom: '',
    yearTo: '',
  });

  const generateAutobiography = async () => {
    setLoading(true);
    try {
      const scope =
        config.scopeType === 'full'
          ? { type: 'full' }
          : {
              type: 'time_range',
              from: parseInt(config.yearFrom),
              to: parseInt(config.yearTo),
            };

      const result = await autobiographyApi.generate({
        audience: config.audience,
        date: new Date().toISOString(),
        include_placeholders: false,
        scope,
        tone: config.tone,
      });

      setAutobiography(result);
    } catch (err) {
      console.error('Failed to generate autobiography:', err);
      alert('Failed to generate autobiography. Make sure you have some life entries first.');
    } finally {
      setLoading(false);
    }
  };

  const downloadMarkdown = () => {
    if (!autobiography) return;

    const blob = new Blob([autobiography.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'my-autobiography.md';
    a.click();
    URL.revokeObjectURL(url);
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
          <h1>Generate Autobiography</h1>
          <p>Create a comprehensive autobiography from your life entries</p>
        </div>

        <div className="grid" style={{ gridTemplateColumns: '300px 1fr', gap: '20px' }}>
          <div className="card">
            <h3>Configuration</h3>

            <label>Audience</label>
            <select
              value={config.audience}
              onChange={(e) =>
                setConfig({ ...config, audience: e.target.value as any })
              }
            >
              <option value="self">Self Only</option>
              <option value="trusted">Trusted People</option>
              <option value="heirs">Heirs</option>
              <option value="public">Public</option>
            </select>

            <label>Tone</label>
            <select
              value={config.tone}
              onChange={(e) => setConfig({ ...config, tone: e.target.value as any })}
            >
              <option value="light">Light</option>
              <option value="balanced">Balanced</option>
              <option value="deep">Deep</option>
            </select>

            <label>Scope</label>
            <select
              value={config.scopeType}
              onChange={(e) => setConfig({ ...config, scopeType: e.target.value })}
            >
              <option value="full">Full Life</option>
              <option value="time_range">Time Range</option>
            </select>

            {config.scopeType === 'time_range' && (
              <>
                <label>From Year</label>
                <input
                  type="number"
                  value={config.yearFrom}
                  onChange={(e) => setConfig({ ...config, yearFrom: e.target.value })}
                  placeholder="1990"
                />

                <label>To Year</label>
                <input
                  type="number"
                  value={config.yearTo}
                  onChange={(e) => setConfig({ ...config, yearTo: e.target.value })}
                  placeholder="2020"
                />
              </>
            )}

            <button
              className="button"
              onClick={generateAutobiography}
              disabled={loading}
              style={{ marginTop: '16px' }}
            >
              {loading ? 'Generating...' : 'Generate'}
            </button>

            {autobiography && (
              <button
                className="button button-secondary"
                onClick={downloadMarkdown}
                style={{ marginTop: '8px' }}
              >
                Download Markdown
              </button>
            )}
          </div>

          <div className="card">
            {!autobiography && !loading && (
              <div style={{ textAlign: 'center', padding: '60px', color: '#888' }}>
                <p>Configure your autobiography and click Generate to begin</p>
              </div>
            )}

            {loading && (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p>Generating your autobiography...</p>
                <p style={{ color: '#888', marginTop: '8px' }}>
                  This may take a minute depending on how many entries you have.
                </p>
              </div>
            )}

            {autobiography && (
              <div>
                <div
                  style={{
                    marginBottom: '20px',
                    paddingBottom: '20px',
                    borderBottom: '1px solid #ddd',
                  }}
                >
                  <h2>Outline</h2>
                  {Array.isArray(autobiography.outline) &&
                    autobiography.outline.map((chapter: any, idx: number) => (
                      <div key={idx} style={{ marginBottom: '12px' }}>
                        <strong>
                          Chapter {chapter.chapter}: {chapter.title}
                        </strong>
                        {chapter.sections && Array.isArray(chapter.sections) && (
                          <ul style={{ marginLeft: '20px', marginTop: '4px' }}>
                            {chapter.sections.map((section: string, sidx: number) => (
                              <li key={sidx} style={{ fontSize: '14px', color: '#666' }}>
                                {section}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                </div>

                <div
                  style={{
                    background: '#f8f9fa',
                    padding: '20px',
                    borderRadius: '4px',
                    maxHeight: '600px',
                    overflow: 'auto',
                  }}
                >
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                    {autobiography.markdown}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
