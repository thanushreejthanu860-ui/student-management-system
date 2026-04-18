import { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import Spinner from '../components/Spinner';
import { getDashboardStats } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#3b82f6'];

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(r => setStats(r.data))
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Layout><Spinner /></Layout>;

  const passFailData = [
    { name: 'Pass', value: stats?.total_students - stats?.students_at_risk || 0 },
    { name: 'At Risk', value: stats?.students_at_risk || 0 },
  ];

  const trendData = [
    { month: 'Jan', avg: 72 }, { month: 'Feb', avg: 75 }, { month: 'Mar', avg: 70 },
    { month: 'Apr', avg: 78 }, { month: 'May', avg: 82 }, { month: 'Jun', avg: 80 },
  ];

  return (
    <Layout>
      <div className="page-header">
        <h2>Welcome back, {user?.name} 👋</h2>
        <span className={`role-badge role-${user?.role}`}>{user?.role}</span>
      </div>

      <div className="stats-grid">
        <StatCard icon="👥" label="Total Students" value={stats?.total_students} color="#6366f1" />
        <StatCard icon="👨‍🏫" label="Faculty" value={stats?.total_faculty} color="#10b981" />
        <StatCard icon="📚" label="Subjects" value={stats?.total_subjects} color="#f59e0b" />
        <StatCard icon="🏫" label="Classes" value={stats?.total_classes} color="#3b82f6" />
        <StatCard icon="⚠️" label="At Risk (Attendance)" value={stats?.students_at_risk} color="#ef4444" />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Pass / At-Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={passFailData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {passFailData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Performance Trend</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[60, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="avg" stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card chart-full">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            {(stats?.recent_activity || []).map((a, i) => (
              <div key={i} className="activity-item">
                <span className="activity-dot" />
                <span className="activity-action">{a.action.replace(/_/g, ' ')}</span>
                <span className="activity-user">by {a.name}</span>
                <span className="activity-time">{new Date(a.created_at).toLocaleString()}</span>
              </div>
            ))}
            {!stats?.recent_activity?.length && <p className="empty-msg">No recent activity</p>}
          </div>
        </div>
      </div>
    </Layout>
  );
}
