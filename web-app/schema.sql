-- ============================================================
-- ASAG System Database Schema
-- Colors: #D4AF37 (Gold) | #1E3A8A (Deep Blue)
-- ============================================================

CREATE DATABASE IF NOT EXISTS asag_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE asag_db;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(150)  NOT NULL,
    email         VARCHAR(191)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          ENUM('admin','student') NOT NULL DEFAULT 'student',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- SUBJECTS / COURSES
-- ============================================================
CREATE TABLE subjects (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    code       VARCHAR(20)  NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO subjects (name, code) VALUES
  ('Networking Essentials',       'NET101'),
  ('Object Oriented Programming', 'OOP201'),
  ('Operating Systems',           'OS301');

-- ============================================================
-- TESTS / QUIZZES
-- ============================================================
CREATE TABLE tests (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    subject_id   INT UNSIGNED NOT NULL,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    time_limit   SMALLINT UNSIGNED NOT NULL DEFAULT 30
                 COMMENT 'Time limit in minutes. 0 = no limit.',
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    created_by   INT UNSIGNED NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- ============================================================
-- QUESTIONS
-- ============================================================
CREATE TABLE questions (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    test_id          INT UNSIGNED NOT NULL,
    question_text    TEXT         NOT NULL,
    question_type    ENUM('short_answer','multiple_choice') NOT NULL,
    reference_answer TEXT         NOT NULL
                     COMMENT 'Model answer used by ASAG API for grading',
    marks            DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    order_index      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- MCQ OPTIONS (only for multiple_choice questions)
-- ============================================================
CREATE TABLE question_options (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    question_id INT UNSIGNED NOT NULL,
    option_key  CHAR(1)      NOT NULL COMMENT 'A, B, C, D',
    option_text TEXT         NOT NULL,
    is_correct  TINYINT(1)   NOT NULL DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TEST ATTEMPTS (one row per student per test attempt)
-- ============================================================
CREATE TABLE test_attempts (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    test_id       INT UNSIGNED NOT NULL,
    student_id    INT UNSIGNED NOT NULL,
    started_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at  TIMESTAMP    NULL,
    time_taken    SMALLINT UNSIGNED NULL COMMENT 'Seconds taken',
    status        ENUM('in_progress','submitted','timed_out') NOT NULL DEFAULT 'in_progress',
    total_score   DECIMAL(6,2) NULL COMMENT 'Populated after grading',
    max_score     DECIMAL(6,2) NULL,
    percentage    DECIMAL(5,2) NULL,
    FOREIGN KEY (test_id)    REFERENCES tests(id)  ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- STUDENT ANSWERS (one row per question per attempt)
-- ============================================================
CREATE TABLE student_answers (
    id                   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    attempt_id           INT UNSIGNED NOT NULL,
    question_id          INT UNSIGNED NOT NULL,
    student_answer_text  TEXT         NOT NULL,
    -- Scores from ASAG API
    semantic_score       DECIMAL(5,4) NULL,
    terminology_score    DECIMAL(5,4) NULL,
    final_score          DECIMAL(5,4) NULL COMMENT 'Normalised 0-1',
    marks_awarded        DECIMAL(5,2) NULL COMMENT 'final_score * question marks',
    feedback             TEXT         NULL,
    graded_at            TIMESTAMP    NULL,
    FOREIGN KEY (attempt_id)   REFERENCES test_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id)  REFERENCES questions(id)     ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- STUDENT MARKS SUMMARY (denormalised for fast reporting)
-- ============================================================
CREATE TABLE student_marks (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    student_id     INT UNSIGNED NOT NULL,
    test_id        INT UNSIGNED NOT NULL,
    attempt_id     INT UNSIGNED NOT NULL,
    total_marks    DECIMAL(6,2) NOT NULL DEFAULT 0,
    max_marks      DECIMAL(6,2) NOT NULL DEFAULT 0,
    percentage     DECIMAL(5,2) NOT NULL DEFAULT 0,
    grade          CHAR(2)      NULL COMMENT 'A, B, C, D, F',
    submitted_at   TIMESTAMP    NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id)          ON DELETE CASCADE,
    FOREIGN KEY (test_id)    REFERENCES tests(id)          ON DELETE CASCADE,
    FOREIGN KEY (attempt_id) REFERENCES test_attempts(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_attempts_student  ON test_attempts (student_id);
CREATE INDEX idx_attempts_test     ON test_attempts (test_id);
CREATE INDEX idx_answers_attempt   ON student_answers (attempt_id);
CREATE INDEX idx_marks_student     ON student_marks (student_id);
CREATE INDEX idx_marks_test        ON student_marks (test_id);
CREATE INDEX idx_questions_test    ON questions (test_id);
