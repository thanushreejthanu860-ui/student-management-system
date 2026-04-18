import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';
import Layout from '../components/Layout';
import Spinner from '../components/Spinner';
import { getStudent, getResult, getAttendance } from '../services/api';
import { fmt, badge, initials } from '../utils/helpers';
import toast from 'react-hot-toast';

export default function StudentProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [result, setResult] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStudent(id), getResult(id).catch(() => null), getAttendance(id).catch(() => null)])
      .then(([s, r, a]) => {
        setData(s.data);
        setResult(r?.data || null);
        setAttendance(a?.data?.attendance || []);
      })
      .catch(() => toast.error('Failed to load student'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Layout><Spinner /></Layout>;
  if (!data) return <Layout><p className="empty-msg">Student not found.</p></Layout>;

  const { student } = data;
  const barData = result?.subjects?.map(s => ({
    name: s.code,
    obtained: s.obtained,
    max: s.max,
    pct: s.percentage,
  })) || [];

  const avgAttendance = attendance.length
    ? (attendance.reduce((s, a) => s + Number(a.percentage), 0) / attendance.length).toFixed(1)
    : '—';

  return (
    <Layout>
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

      <div className="profile-header">
        <div className="profile-avatar">{initials(student.name)}</div>
        <div className="profile-info">
          <h2>{student.name}</h2>
          <p className="student-meta">{student.usn} · {student.class_name} · Sem {student.semester}</p>
          <p className="student-meta">{student.department}</p>
          <div className="profile-tags">
            {student.gender && <span className="tag">{student.gender}</span>}
            {student.email && <span className="tag">{student.email}</span>}
            {student.phone && <span className="tag">📞 {student.phone}</span>}
          </div>
        </div>
        {result && (
          <div className={`result-badge ${result.result === 'Pass' ? 'pass' : 'fail'}`}>
            {result.result}
          </div>
        )}
      </div>

      <div className="stats-grid">
        <div className="stat-card" style={{ '--card-color': '#6366f1' }}>
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-value">{result ? fmt(result.overall_percentage) + '%' : '—'}</div>
            <div className="stat-label">Overall %</div>
          </div>
        </div>
        <div className="stat-card" style={{ '--card-color': '#10b981' }}>
          <div className="stat-icon">📅</div>
          <div className="stat-info">
            <div className="stat-value">{avgAttendance !== '—' ? avgAttendance + '%' : '—'}</div>
            <div className="stat-label">Avg Attendance</div>
          </div>
        </div>
        <div className="stat-card" style={{ '--card-color': '#f59e0b' }}>
          <div className="stat-icon">📚</div>
          <div className="stat-info">
            <div className="stat-value">{result?.subjects?.length ?? '—'}</div>
            <div className="stat-label">Subjects</div>
          </div>
        </div>
      </div>

      {barData.length > 0 && (
        <div className="chart-card">
          <h3>Subject-wise Marks</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={barData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(v, n) => [v, n === 'obtained' ? 'Marks' : n]} />
              <Bar dataKey="obtained" radius={[4, 4, 0, 0]}>
                {barData.map((d, i) => (
                  <Cell key={i} fill={d.pct >= 40 ? '#6366f1' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="tables-grid">
        {result?.subjects?.length > 0 && (
          <div className="table-card">
            <h3>Marks Summary</h3>
            <table className="data-table">
              <thead>
                <tr><th>Subject</th><th>Code</th><th>Obtained</th><th>Max</th><th>%</th><th>Status</th></tr>
              </thead>
              <tbody>
                {result.subjects.map((s, i) => (
                  <tr key={i}>
                    <td>{s.subject}</td>
                    <td>{s.code}</td>
                    <td>{s.obtained}</td>
                    <td>{s.max}</td>
                    <td>{fmt(s.percentage)}%</td>
                    <td><span className={`badge ${badge(s.status)}`}>{s.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {attendance.length > 0 && (
          <div className="table-card">
            <h3>Attendance</h3>
            <table className="data-table">
              <thead>
                <tr><th>Subject</th><th>Present</th><th>Total</th><th>%</th><th>Status</th></tr>
              </thead>
              <tbody>
                {attendance.map((a, i) => (
                  <tr key={i}>
                    <td>{a.subject_name}</td>
                    <td>{a.present_count}</td>
                    <td>{a.total_classes}</td>
                    <td>{fmt(a.percentage)}%</td>
                    <td><span className={`badge ${badge(a.attendance_status)}`}>{a.attendance_status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
