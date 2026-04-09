-- Assignment Deadline Optimizer Initial Data
-- This script populates the database with sample data

-- Insert sample courses
INSERT INTO courses (name, code, description, instructor, semester, credits, color)
VALUES
    ('Introduction to Computer Science', 'CS101', 'Fundamentals of programming and computer science', 'Dr. Smith', 'Fall 2024', 4, '#3B82F6'),
    ('Calculus I', 'MATH201', 'Differential and integral calculus', 'Prof. Johnson', 'Fall 2024', 3, '#EF4444'),
    ('Physics Laboratory', 'PHYS301', 'Experimental physics and lab reports', 'Dr. Williams', 'Fall 2024', 4, '#10B981'),
    ('Data Structures and Algorithms', 'CS201', 'Advanced data structures and algorithm analysis', 'Prof. Brown', 'Fall 2024', 3, '#8B5CF6'),
    ('Technical Writing', 'ENG102', 'Professional and technical communication', 'Dr. Davis', 'Fall 2024', 3, '#F59E0B')
ON CONFLICT (code) DO NOTHING;

-- Insert sample assignments
INSERT INTO assignments (course_id, title, description, assignment_type, weight, estimated_hours, priority, status)
VALUES
    -- CS101 assignments
    (1, 'Python Basics Lab', 'Complete exercises on variables, loops, and functions', 'lab', 10, 3, 'medium', 'not_started'),
    (1, 'Midterm Project', 'Build a simple application using all concepts learned', 'project', 25, 15, 'high', 'not_started'),
    (1, 'Algorithm Quiz', 'Online quiz on basic algorithm complexity', 'exam', 15, 2, 'urgent', 'not_started'),

    -- MATH201 assignments
    (2, 'Derivatives Homework', 'Problems 1-30 from Chapter 3', 'homework', 10, 5, 'high', 'in_progress'),
    (2, 'Integration Lab', 'Complete integration exercises', 'lab', 15, 4, 'medium', 'not_started'),
    (2, 'Midterm Exam', 'Comprehensive exam on chapters 1-5', 'exam', 30, 8, 'urgent', 'not_started'),

    -- PHYS301 assignments
    (3, 'Mechanics Lab Report', 'Write full report on pendulum experiment', 'lab', 20, 6, 'high', 'not_started'),
    (3, 'Error Analysis Assignment', 'Statistical analysis of measurement errors', 'homework', 10, 3, 'medium', 'not_started'),
    (3, 'Final Project Proposal', 'Submit proposal for final experiment', 'project', 15, 2, 'low', 'not_started'),

    -- CS201 assignments
    (4, 'Tree Implementation', 'Implement binary search tree with operations', 'lab', 15, 8, 'high', 'not_started'),
    (4, 'Sorting Algorithms Comparison', 'Benchmark and analyze sorting algorithms', 'project', 20, 12, 'medium', 'not_started'),
    (4, 'Graph Theory Quiz', 'Quiz on graph traversal and shortest paths', 'exam', 15, 3, 'urgent', 'not_started'),

    -- ENG102 assignments
    (5, 'Research Paper Draft', 'First draft of 10-page research paper', 'homework', 20, 10, 'high', 'not_started'),
    (5, 'Presentation', '15-minute technical presentation', 'project', 25, 5, 'medium', 'not_started'),
    (5, 'Peer Review Assignment', 'Review 3 classmate papers', 'homework', 10, 2, 'low', 'not_started')
WHERE EXISTS (SELECT 1 FROM courses WHERE code = 'CS101');

-- Insert sample deadlines
INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 1, '2024-11-15 23:59:00+00', true, 'Submit via Moodle'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 1);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 2, '2024-11-20 23:59:00+00', true, 'Group project, 2-3 students'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 2);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 3, '2024-11-14 14:00:00+00', true, 'Online quiz, 60 minutes'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 3);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 4, '2024-11-14 23:59:00+00', true, 'Show all work'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 4);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 5, '2024-11-18 23:59:00+00', true, 'Use LaTeX template'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 5);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 6, '2024-11-15 10:00:00+00', true, 'In-class exam'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 6);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 7, '2024-11-16 23:59:00+00', true, 'Follow lab report template'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 7);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 8, '2024-11-17 23:59:00+00', true, 'Include all calculations'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 8);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 9, '2024-11-22 23:59:00+00', true, '1-2 page proposal'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 9);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 10, '2024-11-19 23:59:00+00', true, 'Include unit tests'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 10);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 11, '2024-11-25 23:59:00+00', true, 'Include complexity analysis'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 11);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 12, '2024-11-15 16:00:00+00', true, 'Online quiz, 45 minutes'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 12);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 13, '2024-11-21 23:59:00+00', true, 'APA format required'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 13);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 14, '2024-11-23 14:00:00+00', true, 'Book room in advance'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 14);

INSERT INTO deadlines (assignment_id, due_date, is_final, notes)
SELECT 15, '2024-11-24 23:59:00+00', true, 'Use provided rubric'
WHERE NOT EXISTS (SELECT 1 FROM deadlines WHERE assignment_id = 15);
