import type { CoverageCell } from '../types';

const TIME_BUCKETS = ['pre10', '10s', '20s', '30s', '40s', '50plus'];
const TOPIC_BUCKETS = [
  'family_of_origin',
  'friendships',
  'romantic_love',
  'children',
  'work_career',
  'money_status',
  'health_body',
  'creativity_play',
  'beliefs_values',
  'crises_turning_points',
];

const TOPIC_LABELS: Record<string, string> = {
  family_of_origin: 'Family',
  friendships: 'Friends',
  romantic_love: 'Love',
  children: 'Children',
  work_career: 'Career',
  money_status: 'Money',
  health_body: 'Health',
  creativity_play: 'Creativity',
  beliefs_values: 'Beliefs',
  crises_turning_points: 'Turning Points',
};

interface Props {
  data: CoverageCell[];
}

export default function CoverageHeatmap({ data }: Props) {
  const getScore = (time: string, topic: string): number => {
    const cell = data.find((c) => c.time_bucket === time && c.topic_bucket === topic);
    return cell?.score || 0;
  };

  const getColor = (score: number): string => {
    if (score === 0) return '#f5f5f5';
    if (score < 20) return '#e3f2fd';
    if (score < 40) return '#90caf9';
    if (score < 60) return '#42a5f5';
    if (score < 80) return '#1e88e5';
    return '#1565c0';
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
              Topic / Age
            </th>
            {TIME_BUCKETS.map((time) => (
              <th
                key={time}
                style={{
                  padding: '8px',
                  textAlign: 'center',
                  borderBottom: '2px solid #ddd',
                  fontSize: '14px',
                }}
              >
                {time}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {TOPIC_BUCKETS.map((topic) => (
            <tr key={topic}>
              <td
                style={{
                  padding: '8px',
                  borderBottom: '1px solid #eee',
                  fontSize: '14px',
                  fontWeight: 500,
                }}
              >
                {TOPIC_LABELS[topic]}
              </td>
              {TIME_BUCKETS.map((time) => {
                const score = getScore(time, topic);
                return (
                  <td
                    key={`${time}-${topic}`}
                    style={{
                      padding: '8px',
                      textAlign: 'center',
                      borderBottom: '1px solid #eee',
                      backgroundColor: getColor(score),
                      fontSize: '12px',
                      fontWeight: score > 0 ? 'bold' : 'normal',
                    }}
                  >
                    {score > 0 ? score : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: '16px', fontSize: '12px', color: '#666' }}>
        <strong>Legend:</strong> Darker blue = more coverage. Scores range from 0-100.
      </div>
    </div>
  );
}
