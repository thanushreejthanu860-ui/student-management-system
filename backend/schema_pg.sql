-- ============================================
-- STUDENT PERFORMANCE MANAGEMENT SYSTEM
-- PostgreSQL Schema for Neon
-- ============================================

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hod_id INT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    department_id INT NOT NULL REFERENCES departments(id),
    academic_year VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    usn VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(15),
    class_id INT NOT NULL REFERENCES classes(id),
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    credits INT DEFAULT 4,
    max_marks INT DEFAULT 100,
    pass_marks INT DEFAULT 40,
    department_id INT NOT NULL REFERENCES departments(id),
    semester INT NOT NULL
);

CREATE TABLE IF NOT EXISTS faculty_assignments (
    id SERIAL PRIMARY KEY,
    faculty_id INT NOT NULL REFERENCES users(id),
    subject_id INT NOT NULL REFERENCES subjects(id),
    class_id INT NOT NULL REFERENCES classes(id),
    academic_year VARCHAR(10) NOT NULL,
    UNIQUE (faculty_id, subject_id, class_id, academic_year)
);

CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id),
    subject_id INT NOT NULL REFERENCES subjects(id),
    exam_type VARCHAR(20) NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    max_marks INT NOT NULL,
    uploaded_by INT NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, subject_id, exam_type)
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id),
    subject_id INT NOT NULL REFERENCES subjects(id),
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    marked_by INT NOT NULL REFERENCES users(id),
    UNIQUE (student_id, subject_id, date)
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INT,
    student_id INT REFERENCES students(id),
    message TEXT NOT NULL,
    type VARCHAR(30) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_affected VARCHAR(50),
    record_id INT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SEED DATA
-- ============================================

INSERT INTO roles (role_name) VALUES ('admin'), ('hod'), ('faculty')
ON CONFLICT (role_name) DO NOTHING;

-- Default admin password: admin123
INSERT INTO users (name, email, password, role_id)
VALUES ('Admin User', 'admin@college.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.IQOLI4i7yzmXi', 1)
ON CONFLICT (email) DO NOTHING;

-- Sample department
INSERT INTO departments (name) VALUES ('Computer Science')
ON CONFLICT DO NOTHING;

-- Sample class
INSERT INTO classes (class_name, semester, department_id, academic_year)
VALUES ('CS-A', 5, 1, '2024-25')
ON CONFLICT DO NOTHING;

-- Sample subjects
INSERT INTO subjects (subject_name, subject_code, credits, max_marks, pass_marks, department_id, semester) VALUES
('Data Structures', 'CS501', 4, 100, 40, 1, 5),
('Operating Systems', 'CS502', 4, 100, 40, 1, 5),
('Database Management', 'CS503', 4, 100, 40, 1, 5),
('Computer Networks', 'CS504', 4, 100, 40, 1, 5),
('Software Engineering', 'CS505', 4, 100, 40, 1, 5)
ON CONFLICT (subject_code) DO NOTHING;

-- Sample students
INSERT INTO students (name, usn, email, phone, class_id, gender) VALUES
('Alice Johnson', '1CS21CS001', 'alice@college.com', '9876543210', 1, 'Female'),
('Bob Smith', '1CS21CS002', 'bob@college.com', '9876543211', 1, 'Male'),
('Carol White', '1CS21CS003', 'carol@college.com', '9876543212', 1, 'Female'),
('David Brown', '1CS21CS004', 'david@college.com', '9876543213', 1, 'Male'),
('Eva Green', '1CS21CS005', 'eva@college.com', '9876543214', 1, 'Female')
ON CONFLICT (usn) DO NOTHING;

-- Sample marks for student 1
INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by) VALUES
(1, 1, 'semester', 85, 100, 1),
(1, 2, 'semester', 78, 100, 1),
(1, 3, 'semester', 92, 100, 1),
(1, 4, 'semester', 70, 100, 1),
(1, 5, 'semester', 88, 100, 1)
ON CONFLICT (student_id, subject_id, exam_type) DO NOTHING;

-- Sample marks for student 2
INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by) VALUES
(2, 1, 'semester', 72, 100, 1),
(2, 2, 'semester', 65, 100, 1),
(2, 3, 'semester', 80, 100, 1),
(2, 4, 'semester', 55, 100, 1),
(2, 5, 'semester', 75, 100, 1)
ON CONFLICT (student_id, subject_id, exam_type) DO NOTHING;
