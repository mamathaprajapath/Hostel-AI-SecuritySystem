-- AI-Enabled Unified Access and Intelligent Surveillance System for Hostelers
-- Database Schema for MySQL

CREATE DATABASE IF NOT EXISTS hostel_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hostel_db;

-- 1. Admins / Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'warden', -- warden, admin, security
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Residents (Hostelers) Table
CREATE TABLE IF NOT EXISTS residents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    room_no VARCHAR(20) NOT NULL,
    department VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    photo_path VARCHAR(255) DEFAULT NULL,
    face_enrolled TINYINT(1) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive
    current_state VARCHAR(20) DEFAULT 'INSIDE', -- INSIDE, OUTSIDE
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_current_state (current_state)
) ENGINE=InnoDB;

-- 3. Parents / Guardians Table
CREATE TABLE IF NOT EXISTS parents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hosteler_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL, -- Father, Mother, Guardian
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    whatsapp_number VARCHAR(20) DEFAULT NULL,
    notification_preference VARCHAR(20) DEFAULT 'both', -- email, whatsapp, both, none
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hosteler_id) REFERENCES residents(id) ON DELETE CASCADE,
    INDEX idx_parent_hosteler (hosteler_id)
) ENGINE=InnoDB;

-- 4. Resident Parent Relationship (For explicit multi-parent linkage if needed)
CREATE TABLE IF NOT EXISTS resident_parent_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id INT NOT NULL,
    parent_id INT NOT NULL,
    is_primary TINYINT(1) DEFAULT 1,
    FOREIGN KEY (resident_id) REFERENCES residents(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Face Profiles / Embeddings Table
CREATE TABLE IF NOT EXISTS face_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hosteler_id INT NOT NULL UNIQUE,
    embedding_data TEXT NOT NULL, -- JSON formatted embedding vector / histogram
    sample_count INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hosteler_id) REFERENCES residents(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Access Logs Table
CREATE TABLE IF NOT EXISTS access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hosteler_id INT NOT NULL,
    event_type VARCHAR(20) NOT NULL, -- ENTRY, EXIT
    event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    gate VARCHAR(50) DEFAULT 'Main Gate',
    confidence FLOAT DEFAULT 0.0,
    source VARCHAR(50) DEFAULT 'Camera 1',
    image_snapshot VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (hosteler_id) REFERENCES residents(id) ON DELETE CASCADE,
    INDEX idx_event_time (event_time),
    INDEX idx_access_hosteler (hosteler_id),
    INDEX idx_event_type (event_type)
) ENGINE=InnoDB;

-- 7. Outing / Home Requests Table
CREATE TABLE IF NOT EXISTS outing_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hosteler_id INT NOT NULL,
    request_type VARCHAR(20) DEFAULT 'OUTING', -- OUTING, HOME
    reason TEXT NOT NULL,
    destination VARCHAR(255) NOT NULL,
    departure_time DATETIME NOT NULL,
    expected_return DATETIME NOT NULL,
    actual_exit_time DATETIME DEFAULT NULL,
    actual_return_time DATETIME DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED, EXITED, RETURNED, EXPIRED
    remarks TEXT DEFAULT NULL,
    approved_by INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hosteler_id) REFERENCES residents(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_outing_status (status),
    INDEX idx_outing_hosteler (hosteler_id)
) ENGINE=InnoDB;

-- 8. Unknown Person Events Table
CREATE TABLE IF NOT EXISTS unknown_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gate VARCHAR(50) DEFAULT 'Main Gate',
    image_path VARCHAR(255) NOT NULL,
    review_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, REVIEWED, RESOLVED, DISMISSED
    reviewed_by INT DEFAULT NULL,
    remarks TEXT DEFAULT NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_unknown_status (review_status)
) ENGINE=InnoDB;

-- 9. Notification Records Table
CREATE TABLE IF NOT EXISTS notification_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hosteler_id INT DEFAULT NULL,
    event_type VARCHAR(50) NOT NULL, -- OUTING_APPROVED, OUTING_REJECTED, EXIT_DETECTED, RETURN_DETECTED
    channel VARCHAR(20) NOT NULL, -- EMAIL, WHATSAPP
    recipient VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'SENT', -- SENT, FAILED, PENDING
    error_message TEXT DEFAULT NULL,
    FOREIGN KEY (hosteler_id) REFERENCES residents(id) ON DELETE SET NULL,
    INDEX idx_notif_status (status)
) ENGINE=InnoDB;
