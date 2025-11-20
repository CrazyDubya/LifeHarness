import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileApi } from '../services/api';

export default function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    year_of_birth: '',
    country: '',
    primary_language: '',
    relationship_status: '',
    has_children: false,
    children_count: 0,
    main_role: '',
    field_or_industry: '',
    avoid_topics: [] as string[],
    intensity: 'balanced' as 'light' | 'balanced' | 'deep',
    life_snapshot: '',
  });

  const updateField = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async () => {
    try {
      await profileApi.upsert({
        ...formData,
        year_of_birth: formData.year_of_birth ? parseInt(formData.year_of_birth) : undefined,
      });
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to save profile:', err);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '50px' }}>
      <div className="card">
        <h1>Welcome to Life Harness</h1>
        <p style={{ marginBottom: '24px' }}>
          Let's set up your profile so we can personalize your experience.
        </p>

        {step === 1 && (
          <div>
            <h2>Basic Information</h2>
            <label>Year of Birth</label>
            <input
              type="number"
              value={formData.year_of_birth}
              onChange={(e) => updateField('year_of_birth', e.target.value)}
              placeholder="1990"
            />

            <label>Country</label>
            <input
              type="text"
              value={formData.country}
              onChange={(e) => updateField('country', e.target.value)}
              placeholder="United States"
            />

            <label>Primary Language</label>
            <input
              type="text"
              value={formData.primary_language}
              onChange={(e) => updateField('primary_language', e.target.value)}
              placeholder="English"
            />

            <label>Relationship Status</label>
            <select
              value={formData.relationship_status}
              onChange={(e) => updateField('relationship_status', e.target.value)}
            >
              <option value="">Select...</option>
              <option value="single">Single</option>
              <option value="partnered">Partnered</option>
              <option value="married">Married</option>
              <option value="divorced">Divorced</option>
              <option value="widowed">Widowed</option>
              <option value="complicated">It's complicated</option>
            </select>

            <label>
              <input
                type="checkbox"
                checked={formData.has_children}
                onChange={(e) => updateField('has_children', e.target.checked)}
                style={{ width: 'auto', marginRight: '8px' }}
              />
              I have children
            </label>

            {formData.has_children && (
              <>
                <label>Number of Children</label>
                <input
                  type="number"
                  value={formData.children_count}
                  onChange={(e) => updateField('children_count', parseInt(e.target.value))}
                  min="0"
                />
              </>
            )}

            <button className="button" onClick={() => setStep(2)}>
              Next
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2>Work & Preferences</h2>
            <label>Main Role</label>
            <select
              value={formData.main_role}
              onChange={(e) => updateField('main_role', e.target.value)}
            >
              <option value="">Select...</option>
              <option value="student">Student</option>
              <option value="employee">Employee</option>
              <option value="self_employed">Self-employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="retired">Retired</option>
              <option value="caregiver">Caregiver</option>
              <option value="other">Other</option>
            </select>

            <label>Field or Industry (optional)</label>
            <input
              type="text"
              value={formData.field_or_industry}
              onChange={(e) => updateField('field_or_industry', e.target.value)}
              placeholder="Technology, Healthcare, etc."
            />

            <label>Intensity</label>
            <select
              value={formData.intensity}
              onChange={(e) => updateField('intensity', e.target.value as any)}
            >
              <option value="light">Light - Casual questions</option>
              <option value="balanced">Balanced - Mix of depth and ease</option>
              <option value="deep">Deep - Thorough exploration</option>
            </select>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="button-secondary button" onClick={() => setStep(1)}>
                Back
              </button>
              <button className="button" onClick={() => setStep(3)}>
                Next
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2>Life Snapshot</h2>
            <p style={{ marginBottom: '16px' }}>
              Write a brief (5-10 lines) sketch of your life so far. This helps us understand
              your story and ask better questions.
            </p>
            <textarea
              value={formData.life_snapshot}
              onChange={(e) => updateField('life_snapshot', e.target.value)}
              rows={8}
              placeholder="I was born in... grew up in... studied... worked as... currently..."
            />

            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="button-secondary button" onClick={() => setStep(2)}>
                Back
              </button>
              <button className="button" onClick={handleSubmit}>
                Complete Setup
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
