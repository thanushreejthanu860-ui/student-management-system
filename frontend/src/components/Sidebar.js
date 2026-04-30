import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { initials } from '../utils/helpers';

const menus = {
  admin: [
    { to: '/dashboard', icon: '⊞', label: 'Dashboard' },
    { to: '/students', icon: '👥', label: 'Students' },
    { to: '/leaderboard', icon: '🏆', label: 'Leaderboard' },
    { to: '/admin', icon: '⚙️', label: 'Admin Panel' },
  ],
  hod: [
    { to: '/dashboard', icon: '⊞', label: 'Dashboard' },
    { to: '/students', icon: '👥', label: 'Students' },
    { to: '/leaderboard', icon: '🏆', label: 'Leaderboard' },
  ],
  faculty: [
    { to: '/dashboard', icon: '⊞', label: 'Dashboard' },
    { to: '/students', icon: '👥', label: 'My Students' },
  ],
};

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth();
  const items = menus[user?.role] || [];

  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar${open ? ' open' : ''}`}>
        <div className="sidebar-brand">
          <span className="brand-icon">🎓</span>
          <span className="brand-text">EduManage</span>
        </div>
        <div className="sidebar-user">
          <div className="avatar">{initials(user?.name)}</div>
          <div>
            <div className="user-name">{user?.name}</div>
            <div className={`role-badge role-${user?.role}`}>{user?.role}</div>
          </div>
        </div>
        <nav className="sidebar-nav">
          {items.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`} onClick={onClose}>
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <button className="logout-btn" onClick={logout}>
          <span>⏻</span> Logout
        </button>
      </aside>
    </>
  );
}
