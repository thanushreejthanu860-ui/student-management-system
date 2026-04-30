import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Spinner from '../components/Spinner';
import StudentForm from '../components/StudentForm';
import toast from 'react-hot-toast';
import api from '../services/api';
import { initials, sortAlpha } from '../utils/helpers';

const TABS = [
  { key: 'students', label: '👥 Students' },
  { key: 'assign',   label: '📋 Assign Faculty/HOD' },
  { key: 'users',    label: '👤 Manage Users' },
  { key: 'upload',   label: '📤 Upload Students' },
];

export default function AdminPanel() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('students');

  // Students
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [studentsLoading, setStudentsLoading] = useState(true);

  // Assign
  const [users, setUsers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [assignForm, setAssignForm] = useState({ faculty_id: '', subject_id: '', class_id: '', academic_year: '2024-25' });

  // Users
  const [userForm, setUserForm] = useState({ name: '', email: '', password: '', role: 'faculty' });
  const [userLoading, setUserLoading] = useState(false);

  // Upload
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const loadStudents = useCallback(() => {
    setStudentsLoading(true);
    api.get('/students', { params: { search } })
      .then(r => setStudents(sortAlpha(r.data.students || [])))
      .catch(() => toast.error('Failed to load students'))
      .finally(() => setStudentsLoading(false));
  }, [search]);

  const loadAssignData = useCallback(() => {
    Promise.all([
      api.get('/admin/users'),
      api.get('/admin/subjects'),
      api.get('/admin/classes'),
      api.get('/admin/assignments'),
    ]).then(([u, s, c, a]) => {
      setUsers(u.data.users);
      setSubjects(s.data.subjects);
      setClasses(c.data.classes);
      setAssignments(a.data.assignments);
    }).catch(() => toast.error('Failed to load assignment data'));
  }, []);

  useEffect(() => { loadStudents(); }, [loadStudents]);
  useEffect(() => { if (tab === 'assign' || tab === 'users') loadAssignData(); }, [tab, loadAssignData]);

  // Student delete
  const handleDeleteStudent = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this student?')) return;
    try {
      await api.delete(`/student/${id}`);
      toast.success('Student deleted');
      loadStudents();
    } catch { toast.error('Delete failed'); }
  };

  // Assign
  const handleAssign = async (e) => {
    e.preventDefault();
    try {
      await api.post('/assign-faculty', assignForm);
      toast.success('Assigned successfully');
      setAssignForm({ faculty_id: '', subject_id: '', class_id: '', academic_year: '2024-25' });
      loadAssignData();
    } catch (err) { toast.error(err.response?.data?.error || 'Assignment failed'); }
  };

  const handleDeleteAssignment = async (id) => {
    if (!window.confirm('Remove this assignment?')) return;
    try {
      await api.delete(`/admin/assignments/${id}`);
      toast.success('Assignment removed');
      loadAssignData();
    } catch { toast.error('Failed to remove'); }
  };

  // Create user
  const handleCreateUser = async (e) => {
    e.preventDefault();
    setUserLoading(true);
    try {
      await api.post('/admin/users', userForm);
      toast.success(`${userForm.role} created successfully`);
      setUserForm({ name: '', email: '', password: '', role: 'faculty' });
      loadAssignData();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed to create user'); }
    finally { setUserLoading(false); }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm('Deactivate this user?')) return;
    try {
      await api.delete(`/admin/users/${id}`);
      toast.success('User deactivated');
      loadAssignData();
    } catch { toast.error('Failed to deactivate'); }
  };

  // Upload
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) { toast.error('Please select a file'); return; }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'students');
    setUploading(true);
    try {
      const res = await api.post('/upload-excel', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success(`Uploaded ${res.data.result.inserted} students`);
      if (res.data.result.errors?.length) toast.error(`${res.data.result.errors.length} rows had errors`);
      setFile(null);
      loadStudents();
    } catch (err) { toast.error(err.response?.data?.error || 'Upload failed'); }
    finally { setUploading(false); }
  };

  return (
    <Layout>
      <div className="page-header">
        <h2>Admin Panel</h2>
      </div>

      <div className="tabs">
        {TABS.map(t => (
          <button key={t.key} className={`tab-btn ${tab === t.key ? 'active' : ''}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── STUDENTS TAB ── */}
      {tab === 'students' && (
        <div className="tab-content">
          <div className="page-header" style={{ marginBottom: 16 }}>
            <input className="search-input" placeholder="Search by name or USN…" value={search} onChange={e => setSearch(e.target.value)} style={{ maxWidth: 320 }} />
            <button className="btn-primary" onClick={() => setShowForm(true)}>+ Add Student</button>
          </div>
          {studentsLoading ? <Spinner /> : (
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
                  <button className="delete-btn" onClick={e => handleDeleteStudent(e, s.id)}>🗑</button>
                </div>
              ))}
            </div>
          )}
          {showForm && <StudentForm onClose={() => setShowForm(false)} onSaved={() => { setShowForm(false); loadStudents(); }} />}
        </div>
      )}

      {/* ── ASSIGN TAB ── */}
      {tab === 'assign' && (
        <div className="tab-content">
          <div className="admin-grid">
            <div className="admin-card">
              <h3>Assign Faculty / HOD to Subject</h3>
              <form onSubmit={handleAssign}>
                <div className="form-group">
                  <label>Faculty / HOD</label>
                  <select value={assignForm.faculty_id} onChange={e => setAssignForm({ ...assignForm, faculty_id: e.target.value })} required>
                    <option value="">Select person</option>
                    {users.filter(u => u.is_active && u.role === 'hod').length > 0 && (
                      <optgroup label="HOD">
                        {users.filter(u => u.is_active && u.role === 'hod').map(u => (
                          <option key={u.id} value={u.id}>{u.name}</option>
                        ))}
                      </optgroup>
                    )}
                    {users.filter(u => u.is_active && u.role === 'faculty').length > 0 && (
                      <optgroup label="Faculty">
                        {users.filter(u => u.is_active && u.role === 'faculty').map(u => (
                          <option key={u.id} value={u.id}>{u.name}</option>
                        ))}
                      </optgroup>
                    )}
                  </select>
                </div>
                <div className="form-group">
                  <label>Subject</label>
                  <select value={assignForm.subject_id} onChange={e => setAssignForm({ ...assignForm, subject_id: e.target.value })} required>
                    <option value="">Select subject</option>
                    {subjects.map(s => <option key={s.id} value={s.id}>{s.subject_name} ({s.subject_code})</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Class</label>
                  <select value={assignForm.class_id} onChange={e => setAssignForm({ ...assignForm, class_id: e.target.value })} required>
                    <option value="">Select class</option>
                    {classes.map(c => <option key={c.id} value={c.id}>{c.class_name} — Sem {c.semester}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Academic Year</label>
                  <input value={assignForm.academic_year} onChange={e => setAssignForm({ ...assignForm, academic_year: e.target.value })} required />
                </div>
                <button type="submit" className="btn-primary">Assign</button>
              </form>
            </div>

            <div className="admin-card">
              <h3>Current Assignments</h3>
              <div className="assignments-list">
                {assignments.map(a => (
                  <div key={a.id} className="assignment-item">
                    <div>
                      <strong>{a.faculty_name}</strong> <span className={`role-badge role-${a.role}`}>{a.role}</span>
                      <div className="assignment-meta">{a.subject_name} ({a.subject_code}) · {a.class_name} · {a.academic_year}</div>
                    </div>
                    <button className="delete-btn" onClick={() => handleDeleteAssignment(a.id)}>🗑️</button>
                  </div>
                ))}
                {!assignments.length && <p className="empty-msg">No assignments yet</p>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── USERS TAB ── */}
      {tab === 'users' && (
        <div className="tab-content">
          <div className="admin-grid">
            <div className="admin-card">
              <h3>Create HOD / Faculty Account</h3>
              <form onSubmit={handleCreateUser}>
                <div className="form-group">
                  <label>Full Name</label>
                  <input placeholder="Dr. John Smith" value={userForm.name} onChange={e => setUserForm({ ...userForm, name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" placeholder="faculty@college.com" value={userForm.email} onChange={e => setUserForm({ ...userForm, email: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Password</label>
                  <input type="password" placeholder="••••••••" value={userForm.password} onChange={e => setUserForm({ ...userForm, password: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Role</label>
                  <select value={userForm.role} onChange={e => setUserForm({ ...userForm, role: e.target.value })}>
                    <option value="faculty">Faculty</option>
                    <option value="hod">HOD</option>
                  </select>
                </div>
                <button type="submit" className="btn-primary" disabled={userLoading}>
                  {userLoading ? 'Creating...' : 'Create Account'}
                </button>
              </form>
            </div>

            <div className="admin-card">
              <h3>Faculty & HOD Accounts</h3>
              <div className="assignments-list">
                {users.filter(u => u.is_active).map(u => (
                  <div key={u.id} className="assignment-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div className="student-avatar sm">{initials(u.name)}</div>
                      <div>
                        <strong>{u.name}</strong> <span className={`role-badge role-${u.role}`}>{u.role}</span>
                        <div className="assignment-meta">{u.email}</div>
                      </div>
                    </div>
                    <button className="delete-btn" onClick={() => handleDeleteUser(u.id)}>🗑️</button>
                  </div>
                ))}
                {!users.filter(u => u.is_active).length && <p className="empty-msg">No users yet</p>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── UPLOAD TAB ── */}
      {tab === 'upload' && (
        <div className="tab-content">
          <div className="upload-card">
            <h3>Upload Students from Excel</h3>
            <p className="upload-hint">
              Excel columns required: <strong>name, usn, email, phone, class_id, gender</strong><br />
              Use class_id numbers (e.g. 1 for CS-A). Existing USNs will be updated.
            </p>
            <form onSubmit={handleUpload}>
              <div className="file-input-wrap">
                <input type="file" accept=".xlsx,.xls" onChange={e => setFile(e.target.files[0])} className="file-input" />
                {file && <span className="file-name">📄 {file.name}</span>}
              </div>
              <button type="submit" className="btn-primary" disabled={uploading}>
                {uploading ? 'Uploading...' : '⬆ Upload Students'}
              </button>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
