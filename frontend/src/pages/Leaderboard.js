import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Spinner from '../components/Spinner';
import { getRanks } from '../services/api';
import { fmt, initials } from '../utils/helpers';
import toast from 'react-hot-toast';

const medals = ['🥇', '🥈', '🥉'];

export default function Leaderboard() {
  const navigate = useNavigate();
  const [classId, setClassId] = useState('1');
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!classId) return;
    setLoading(true);
    getRanks(classId)
      .then(r => setRankings(r.data.rankings || []))
      .catch(() => toast.error('Failed to load rankings'))
      .finally(() => setLoading(false));
  }, [classId]);

  return (
    <Layout>
      <div className="page-header">
        <h2>🏆 Leaderboard</h2>
        <div className="filters-bar" style={{ margin: 0 }}>
          <input
            type="number"
            className="search-input"
            style={{ width: 120 }}
            placeholder="Class ID"
            value={classId}
            onChange={e => setClassId(e.target.value)}
            min="1"
          />
        </div>
      </div>

      {loading ? <Spinner /> : (
        <div className="leaderboard">
          {rankings.length === 0 && <p className="empty-msg">No data for this class.</p>}
          {rankings.map((s, i) => (
            <div
              key={s.id}
              className={`rank-card${i < 3 ? ' top-rank' : ''}`}
              onClick={() => navigate(`/students/${s.id}`)}
            >
              <div className="rank-num">{medals[i] || `#${s.rank}`}</div>
              <div className="student-avatar sm">{initials(s.name)}</div>
              <div className="rank-info">
                <div className="student-name">{s.name}</div>
                <div className="student-meta">{s.usn}</div>
              </div>
              <div className="rank-pct">{fmt(s.percentage)}%</div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
