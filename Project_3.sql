CREATE DATABASE course_system;

USE course_system;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('student', 'instructor') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from users;

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    duration INT,  -- in hours/days
    instructor_id INT,
    
    FOREIGN KEY (instructor_id) REFERENCES users(user_id)
    ON DELETE SET NULL
);

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    enrollment_date TIMESTAMP DEFAULT current_timestamp,
    
    FOREIGN KEY (student_id) REFERENCES users(user_id)
    ON DELETE CASCADE,
    
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
    ON DELETE CASCADE,
    
    UNIQUE (student_id, course_id)
);

select * from enrollments;
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    title VARCHAR(100),
    description TEXT,
    max_marks INT,
    due_date DATE,
    
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
    ON DELETE CASCADE
);
CREATE TABLE submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT,
    student_id INT,
    submission_date DATE,
    marks_obtained INT,
    
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id)
    ON DELETE CASCADE,
    
    FOREIGN KEY (student_id) REFERENCES users(user_id)
    ON DELETE CASCADE
);
CREATE TABLE performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    total_marks INT,
    percentage DECIMAL(5,2),
    grade CHAR(2),
    
    FOREIGN KEY (student_id) REFERENCES users(user_id)
    ON DELETE CASCADE,
    
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
    ON DELETE CASCADE,
    
    UNIQUE (student_id, course_id)
);

INSERT INTO users (name, email, password, role) VALUES
('Aman Thakur', 'aman@gmail.com', '123', 'student'),
('Sneha Patil', 'sneha@gmail.com', '123', 'student'),
('Rahul Sharma', 'rahul@gmail.com', '123', 'student'),
('Dr. Mehta', 'mehta@gmail.com', '123', 'instructor'),
('Prof. Iyer', 'iyer@gmail.com', '123', 'instructor');

INSERT INTO courses (course_name, description, duration, instructor_id) VALUES
('Python Programming', 'Learn Python from basics', 30, 4),
('Data Science', 'Data analysis and ML basics', 45, 4),
('Web Development', 'HTML, CSS, JS', 40, 5),
('SQL Mastery', 'Database and queries', 25, 5),
('Machine Learning', 'ML algorithms', 50, 4);

INSERT INTO enrollments (student_id, course_id) VALUES
(1, 1),
(1, 2),
(2, 3),
(2, 4),
(3, 5);

INSERT INTO assignments (course_id, title, description, max_marks, due_date) VALUES
(1, 'Python Basics', 'Variables and loops', 100, '2026-04-01'),
(2, 'Data Analysis', 'Pandas task', 100, '2026-04-05'),
(3, 'Website Design', 'Create homepage', 100, '2026-04-10'),
(4, 'SQL Queries', 'Write joins', 100, '2026-04-12'),
(5, 'ML Model', 'Build prediction model', 100, '2026-04-15');

INSERT INTO submissions (assignment_id, student_id, submission_date, marks_obtained) VALUES
(1, 1, '2026-03-30', 85),
(2, 1, '2026-04-04', 90),
(3, 2, '2026-04-09', 78),
(4, 2, '2026-04-11', 88),
(5, 3, '2026-04-14', 92);

INSERT INTO performance (student_id, course_id, total_marks, percentage, grade) VALUES
(1, 1, 85, 85.00, 'A'),
(1, 2, 90, 90.00, 'A'),
(2, 3, 78, 78.00, 'B'),
(2, 4, 88, 88.00, 'A'),
(3, 5, 92, 92.00, 'A');

select * from enrollments;

ALTER TABLE performance
MODIFY percentage DECIMAL(5,2) DEFAULT 0;

SELECT u.name, c.course_name
FROM enrollments e
JOIN users u ON e.student_id = u.user_id
JOIN courses c ON e.course_id = c.course_id;
