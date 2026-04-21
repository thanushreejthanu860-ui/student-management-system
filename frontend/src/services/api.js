import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:5000/api' });

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const login = data => api.post('/login', data);
export const getDashboardStats = () => api.get('/dashboard-stats');
export const getStudents = params => api.get('/students', { params });
export const getStudent = id => api.get(`/student/${id}`);
export const addStudent = data => api.post('/students', data);
export const updateStudent = (id, data) => api.put(`/student/${id}`, data);
export const deleteStudent = id => api.delete(`/student/${id}`);
export const getResult = id => api.get(`/marks/result/${id}`);
export const getRanks = classId => api.get(`/marks/ranks/${classId}`);
export const getAttendance = id => api.get(`/attendance/${id}`);
export const getNotifications = () => api.get('/notifications');

export default api;
