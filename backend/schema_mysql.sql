CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hod_id INT,
    FOREIGN KEY (hod_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    department_id INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    usn VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(15),
    class_id INT NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    credits INT DEFAULT 4,
    max_marks INT DEFAULT 100,
    pass_marks INT DEFAULT 40,
    department_id INT NOT NULL,
    semester INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS faculty_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    subject_id INT NOT NULL,
    class_id INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    UNIQUE KEY uq_assignment (faculty_id, subject_id, class_id, academic_year),
    FOREIGN KEY (faculty_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    exam_type VARCHAR(20) NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    max_marks INT NOT NULL,
    uploaded_by INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_marks (student_id, subject_id, exam_type),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    marked_by INT NOT NULL,
    UNIQUE KEY uq_attendance (student_id, subject_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (marked_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    student_id INT,
    message TEXT NOT NULL,
    type VARCHAR(30) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    table_affected VARCHAR(50),
    record_id INT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT IGNORE INTO roles (role_name) VALUES ('admin'), ('hod'), ('faculty');

INSERT IGNORE INTO users (name, email, password, role_id)
VALUES ('Admin User', 'admin@college.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.IQOLI4i7yzmXi', 1);

INSERT IGNORE INTO departments (name) VALUES ('Computer Science');

INSERT IGNORE INTO classes (class_name, semester, department_id, academic_year)
VALUES ('CS-A', 5, 1, '2024-25');

INSERT IGNORE INTO subjects (subject_name, subject_code, credits, max_marks, pass_marks, department_id, semester) VALUES
('Data Structures', 'CS501', 4, 100, 40, 1, 5),
('Operating Systems', 'CS502', 4, 100, 40, 1, 5),
('Database Management', 'CS503', 4, 100, 40, 1, 5),
('Computer Networks', 'CS504', 4, 100, 40, 1, 5),
('Software Engineering', 'CS505', 4, 100, 40, 1, 5);

INSERT IGNORE INTO students (name, usn, email, phone, class_id, gender) VALUES
('Alice Johnson', '1CS21CS001', 'alice@college.com', '9876543210', 1, 'Female'),
('Bob Smith', '1CS21CS002', 'bob@college.com', '9876543211', 1, 'Male'),
('Carol White', '1CS21CS003', 'carol@college.com', '9876543212', 1, 'Female'),
('David Brown', '1CS21CS004', 'david@college.com', '9876543213', 1, 'Male'),
('Eva Green', '1CS21CS005', 'eva@college.com', '9876543214', 1, 'Female');

INSERT IGNORE INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by) VALUES
(1, 1, 'semester', 85, 100, 1),
(1, 2, 'semester', 78, 100, 1),
(1, 3, 'semester', 92, 100, 1),
(1, 4, 'semester', 70, 100, 1),
(1, 5, 'semester', 88, 100, 1),
(2, 1, 'semester', 72, 100, 1),
(2, 2, 'semester', 65, 100, 1),
(2, 3, 'semester', 80, 100, 1),
(2, 4, 'semester', 55, 100, 1),
(2, 5, 'semester', 75, 100, 1);
