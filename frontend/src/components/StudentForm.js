import { useState } from 'react';
import { addStudent } from '../services/api';
import toast from 'react-hot-toast';

export default function StudentForm({ onClose, onSaved }) {
  const [form, setForm] = useState({ name: '', usn: '', email: '', phone: '', class_id: '', gender: '', date_of_birth: '', address: '' });
  const [loading, setLoading] = useState(false);

  const set = f => e => setForm(p => ({ ...p, [f]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.name || !form.usn || !form.class_id) {
      toast.error('Name, USN and Class ID are required'); return;
    }
    setLoading(true);
    try {
      await addStudent({ ...form, class_id: Number(form.class_id) });
      toast.success('Student added!');
      onSaved();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to add student');
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Student</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label>Full Name *</label>
              <input placeholder="John Doe" value={form.name} onChange={set('name')} />
            </div>
            <div className="form-group">
              <label>USN *</label>
              <input placeholder="1XX21CS001" value={form.usn} onChange={set('usn')} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email</label>
              <input type="email" placeholder="student@college.com" value={form.email} onChange={set('email')} />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input placeholder="9876543210" value={form.phone} onChange={set('phone')} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Class ID *</label>
              <input type="number" placeholder="1" value={form.class_id} onChange={set('class_id')} />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select value={form.gender} onChange={set('gender')}>
                <option value="">Select</option>
                <option>Male</option><option>Female</option><option>Other</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Date of Birth</label>
              <input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} />
            </div>
            <div className="form-group">
              <label>Address</label>
              <input placeholder="City, State" value={form.address} onChange={set('address')} />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving…' : 'Add Student'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
