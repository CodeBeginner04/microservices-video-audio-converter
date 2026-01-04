-- ========================================
-- MySQL Database Setup for Auth Server
-- ========================================

-- Create dedicated database user with secure password
-- NOTE: Change 'YourSecurePassword123!' to a strong password
CREATE USER IF NOT EXISTS 'auth_user'@'localhost' 
IDENTIFIED WITH mysql_native_password BY 'YourSecurePassword123!';

-- Create the authentication database
CREATE DATABASE IF NOT EXISTS auth;

-- Grant necessary privileges to auth_user
-- Using specific privileges instead of ALL for better security
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.* TO 'auth_user'@'localhost';

-- Apply privilege changes
FLUSH PRIVILEGES;

-- Switch to the auth database
USE auth;

-- ========================================
-- Create Users Table
-- ========================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Stores hashed passwords
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- Insert Test User (Optional)
-- ========================================
-- WARNING: This is a PLAIN TEXT password - DO NOT use in production!
-- In production, use your application's /register endpoint instead
-- This creates a user with email: test@example.com, password: TestPassword123!

-- For testing ONLY - Remove this line in production:
-- INSERT INTO users (email, password, is_admin) 
-- VALUES ('test@example.com', 'pbkdf2:sha256:600000$...[hashed_value]', FALSE);

-- ========================================
-- Create Sessions Table (Optional)
-- ========================================
-- Useful for tracking user sessions and token invalidation
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token_hash),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- Verify Setup
-- ========================================
-- Show created tables
SHOW TABLES;

-- Show users table structure
DESCRIBE users;