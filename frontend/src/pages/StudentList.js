import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Spinner from '../components/Spinner';
import { getStudents, deleteStudent } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { sortAlpha, initials } from '../utils/helpers';
import toast from 'react-hot-toast';
import StudentForm from '../components/StudentForm';

export default function StudentList() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [semFilter, setSemFilter] = useState('');
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    getStudents({ search })
      .then(r => {
        const sorted = sortAlpha(r.data.students || []);
        setAllStudents(sorted);
        setStudents(sorted);
      })
      .catch(() => toast.error('Failed to load students'))
      .finally(() => setLoading(false));
  }, [search]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    let filtered = allStudents;
    if (semFilter) filtered = filtered.filter(s => String(s.semester) === semFilter);
    if (classFilter) filtered = filtered.filter(s => s.class_name === classFilter);
    setStudents(filtered);
  }, [classFilter, semFilter, allStudents]);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this student?')) return;
    try {
      await deleteStudent(id);
      toast.success('Student deleted');
      load();
    } catch { toast.error('Delete failed'); }
  };

  const semesters = [...new Set(allStudents.map(s => s.semester))].sort((a,b) => a-b);
  const classes = [...new Set(
    allStudents
      .filter(s => !semFilter || String(s.semester) === semFilter)
      .map(s => s.class_name)
  )].sort();

  return (
    <Layout>
      <div className="page-header">
        <h2>Students</h2>
        {['admin', 'hod'].includes(user?.role) && (
          <button className="btn-primary" onClick={() => setShowForm(true)}>+ Add Student</button>
        )}
      </div>

      <div className="filters-bar">
        <input
          className="search-input"
          placeholder="Search by name or USN…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select className="filter-select" value={semFilter} onChange={e => { setSemFilter(e.target.value); setClassFilter(''); }}>
          <option value="">All Semesters</option>
          {semesters.map(s => <option key={s} value={s}>Semester {s}</option>)}
        </select>
        <select className="filter-select" value={classFilter} onChange={e => setClassFilter(e.target.value)}>
          <option value="">All Sections</option>
          {classes.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {loading ? <Spinner /> : (
        <div className="student-grid">
          {students.length === 0 && <p className="empty-msg">No students found.</p>}
          {students.map(s => (
            <div key={s.id} className="student-card" onClick={() => navigate(`/students/${s.id}`)}>
              <div className="student-avatar">{initials(s.name)}</div>
              <div className="student-info">
                <div className="student-name">{s.name}</div>
                <div className="student-meta">{s.usn}</div>
                <div className="student-meta">{s.class_name} · Sem {s.semester}</div>
                <div className="student-meta">{s.department}</div>
              </div>
              {user?.role === 'admin' && (
                <button className="delete-btn" onClick={e => handleDelete(e, s.id)}>🗑</button>
              )}
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <StudentForm onClose={() => setShowForm(false)} onSaved={() => { setShowForm(false); load(); }} />
      )}
    </Layout>
  );
}
