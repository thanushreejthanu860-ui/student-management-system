# Student Performance Management System - Backend API

## Tech Stack
- **Framework:** Flask (Python)
- **Database:** MySQL
- **Auth:** JWT (Flask-JWT-Extended)
- **Excel:** Pandas + OpenPyXL
- **PDF:** ReportLab

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL
```bash
mysql -u root -p < schema.sql
```

### 3. Configure environment
Edit `.env` file:
```
DB_PASSWORD=your_mysql_password
JWT_SECRET_KEY=your-secret-key
```

### 4. Run server
```bash
python app.py
```
Server runs at: `http://localhost:5000`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Login (Admin/HOD/Faculty) |
| POST | `/api/register` | Create user (Admin only) |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students` | List all students |
| GET | `/api/student/{id}` | Get student details + marks + attendance |
| POST | `/api/students` | Add student |
| PUT | `/api/student/{id}` | Update student |
| DELETE | `/api/student/{id}` | Delete student |

### Marks & Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/marks` | Add/update marks |
| GET | `/api/marks/result/{student_id}` | Get result + percentage + pass/fail |
| GET | `/api/marks/ranks/{class_id}` | Get class rankings |
| POST | `/api/attendance` | Mark attendance |
| GET | `/api/attendance/{student_id}` | Get attendance summary |

### Reports & Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-excel` | Upload Excel (students/marks/attendance) |
| GET | `/api/export-excel?class_id=1` | Export class data to Excel |
| GET | `/api/report-card/{student_id}` | Download PDF report card |
| POST | `/api/assign-faculty` | Assign faculty to subject/class |
| GET | `/api/dashboard-stats` | Admin dashboard statistics |
| GET | `/api/notifications` | Get unread notifications |

---

## Request Examples

### Login
```json
POST /api/login
{
  "email": "admin@college.com",
  "password": "admin123"
}
```

### Add Marks
```json
POST /api/marks
Authorization: Bearer <token>
{
  "student_id": 1,
  "subject_id": 2,
  "exam_type": "IA1",
  "marks_obtained": 45,
  "max_marks": 50
}
```

### Mark Attendance
```json
POST /api/attendance
Authorization: Bearer <token>
{
  "subject_id": 1,
  "date": "2024-01-15",
  "records": [
    {"student_id": 1, "status": "present"},
    {"student_id": 2, "status": "absent"}
  ]
}
```

### Upload Excel
```
POST /api/upload-excel
Authorization: Bearer <token>
Form-data: file=marks.xlsx, type=marks
```
Excel columns for marks: `usn, subject_code, exam_type, marks_obtained, max_marks`

---

## Default Admin Login
- Email: `admin@college.com`
- Password: `admin123`

---

## Role Permissions
| Feature | Admin | HOD | Faculty |
|---------|-------|-----|---------|
| Add/Delete Students | ✅ | ✅ | ❌ |
| Upload Marks | ✅ | ✅ | ✅ |
| Mark Attendance | ✅ | ✅ | ✅ |
| Assign Faculty | ✅ | ✅ | ❌ |
| Dashboard Stats | ✅ | ✅ | ❌ |
| View Students | ✅ | ✅ | Own classes only |
