import { useState, useEffect } from 'react';
import { useDarkMode } from '../hooks/useDarkMode';
import { getNotifications } from '../services/api';

export default function Navbar({ onMenuClick }) {
  const [dark, toggleDark] = useDarkMode();
  const [notifs, setNotifs] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    getNotifications().then(r => setNotifs(r.data.notifications || [])).catch(() => {});
  }, []);

  return (
    <header className="navbar">
      <button className="menu-btn" onClick={onMenuClick}>☰</button>
      <h1 className="navbar-title">Student Management System</h1>
      <div className="navbar-actions">
        <div className="notif-wrap">
          <button className="icon-btn" onClick={() => setShowNotifs(s => !s)}>
            🔔 {notifs.length > 0 && <span className="notif-badge">{notifs.length}</span>}
          </button>
          {showNotifs && (
            <div className="notif-dropdown">
              {notifs.length === 0
                ? <p className="notif-empty">No new notifications</p>
                : notifs.slice(0, 8).map(n => (
                    <div key={n.id} className="notif-item">{n.message}</div>
                  ))}
            </div>
          )}
        </div>
        <button className="icon-btn" onClick={toggleDark} title="Toggle theme">
          {dark ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  );
}
