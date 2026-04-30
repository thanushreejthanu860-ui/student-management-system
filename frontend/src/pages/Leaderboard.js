import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Spinner from '../components/Spinner';
import { getRanks } from '../services/api';
import api from '../services/api';
import { fmt, initials } from '../utils/helpers';
import toast from 'react-hot-toast';

const medals = ['🥇', '🥈', '🥉'];

export default function Leaderboard() {
  const navigate = useNavigate();
  const [classes, setClasses] = useState([]);
  const [classId, setClassId] = useState('');
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/admin/classes')
      .then(r => {
        const cls = r.data.classes || [];
        setClasses(cls);
        setClassId('all');
      })
      .catch(() => toast.error('Failed to load classes'));
  }, []);

  useEffect(() => {
    if (!classId) return;
    setLoading(true);
    const req = classId === 'all' ? api.get('/marks/ranks/all') : getRanks(classId);
    req
      .then(r => setRankings(r.data.rankings || []))
      .catch(() => toast.error('Failed to load rankings'))
      .finally(() => setLoading(false));
  }, [classId]);

  const semesters = [...new Set(classes.map(c => c.semester))].sort((a, b) => a - b);

  return (
    <Layout>
      <div className="page-header">
        <h2>🏆 Leaderboard</h2>
        <select
          className="filter-select"
          value={classId}
          onChange={e => setClassId(e.target.value)}
        >
          <option value="all">All Students</option>
          {semesters.map(sem => (
            <optgroup key={sem} label={`Semester ${sem}`}>
              {classes.filter(c => c.semester === sem).map(c => (
                <option key={c.id} value={c.id}>{c.class_name} — Sem {c.semester}</option>
              ))}
            </optgroup>
          ))}
        </select>
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
                <div className="student-meta">{s.usn}{s.class_name ? ` · ${s.class_name} Sem ${s.semester}` : ''}</div>
              </div>
              <div className="rank-pct">{fmt(s.percentage)}%</div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
