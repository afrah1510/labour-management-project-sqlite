-- =====================================
-- LABOUR MANAGEMENT SYSTEM (SQLite)
-- =====================================

PRAGMA foreign_keys = ON;

-- ========================
-- ADMIN TABLE
-- ========================
CREATE TABLE IF NOT EXISTS admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- ========================
-- LABOUR TABLE
-- ========================
CREATE TABLE IF NOT EXISTS labour (
    labour_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    contact TEXT,
    address TEXT,
    skill TEXT,
    join_date DATE DEFAULT (DATE('now'))
);

-- ========================
-- PROJECT TABLE
-- ========================
CREATE TABLE IF NOT EXISTS project (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'Ongoing'
);

-- ========================
-- ASSIGNMENT TABLE
-- ========================
CREATE TABLE IF NOT EXISTS assignment (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    labour_id INTEGER,
    project_id INTEGER,
    assigned_date DATE DEFAULT (DATE('now')),
    FOREIGN KEY (labour_id) REFERENCES labour(labour_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE
);

-- ========================
-- ATTENDANCE TABLE
-- ========================
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    labour_id INTEGER,
    date DATE,
    status TEXT CHECK(status IN ('Present', 'Absent')),
    FOREIGN KEY (labour_id) REFERENCES labour(labour_id) ON DELETE CASCADE
);

-- ========================
-- WAGES TABLE
-- ========================
CREATE TABLE IF NOT EXISTS wages (
    wage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    labour_id INTEGER,
    amount REAL,
    payment_date DATE DEFAULT (DATE('now')),
    FOREIGN KEY (labour_id) REFERENCES labour(labour_id) ON DELETE CASCADE
);