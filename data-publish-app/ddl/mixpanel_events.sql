-- ============================================================================
-- Event Tracking Schema (Single Tenant, OLTP Optimized)
-- ============================================================================
-- Simplified schema for single-tenant deployments.
-- Removed: multi-tenant fields, group analytics, generic lookup tables
-- ============================================================================

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id                          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id                     VARCHAR(255) NOT NULL,
    
    -- Profile
    email                       VARCHAR(320),
    phone                       VARCHAR(50),
    full_name                   VARCHAR(255),
    first_name                  VARCHAR(100),
    last_name                   VARCHAR(100),
    avatar_url                  TEXT,
    
    -- Location
    city                        VARCHAR(255),
    region                      VARCHAR(255),
    country_code                CHAR(2),
    timezone                    VARCHAR(100),
    
    -- Last known device info
    os_name                     VARCHAR(50),
    browser_name                VARCHAR(100),
    app_version                 VARCHAR(50),
    device_model                VARCHAR(100),
    
    -- Custom properties
    properties                  JSON,
    
    -- Timestamps
    created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_seen_at                DATETIME,
    
    UNIQUE INDEX idx_user_id (user_id),
    INDEX idx_email (email)
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- EVENTS TABLE
-- ============================================================================
CREATE TABLE events (
    id                          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    insert_id                   VARCHAR(128),
    
    -- Core
    event_name                  VARCHAR(255) NOT NULL,
    user_id                     VARCHAR(255) NOT NULL,
    event_time                  BIGINT NOT NULL,
    
    -- Session
    session_id                  VARCHAR(128),
    
    -- Device
    device_id                   VARCHAR(255),
    os_name                     VARCHAR(50),
    os_version                  VARCHAR(50),
    device_model                VARCHAR(100),
    
    -- Browser (web)
    browser_name                VARCHAR(100),
    browser_version             VARCHAR(50),
    
    -- App (mobile)
    app_version                 VARCHAR(50),
    
    -- Location
    ip_address                  VARCHAR(45),
    country_code                CHAR(2),
    city                        VARCHAR(255),
    
    -- Page/Screen
    page_url                    TEXT,
    page_title                  VARCHAR(500),
    screen_name                 VARCHAR(255),
    referrer                    TEXT,
    
    -- Experiments
    experiment_id               VARCHAR(128),
    variant_id                  VARCHAR(128),
    
    -- Revenue
    revenue                     DECIMAL(18, 4),
    currency_code               CHAR(3),
    
    -- Custom properties
    properties                  JSON,
    
    -- Timestamps
    created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_dedup (insert_id),
    INDEX idx_user_id (user_id),
    INDEX idx_session (session_id)
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- EXPERIMENTS TABLE (Master Data)
-- ============================================================================
CREATE TABLE experiments (
    id                          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    experiment_id               VARCHAR(128) NOT NULL,
    experiment_name             VARCHAR(255) NOT NULL,
    description                 TEXT,
    status                      ENUM('draft', 'running', 'paused', 'completed') DEFAULT 'draft',
    created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_experiment_id (experiment_id)
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- EXPERIMENT VARIANTS TABLE
-- ============================================================================
CREATE TABLE experiment_variants (
    id                          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    experiment_id               VARCHAR(128) NOT NULL,
    variant_id                  VARCHAR(128) NOT NULL,
    variant_name                VARCHAR(255) NOT NULL,
    weight                      DECIMAL(5, 2) DEFAULT 50.00,
    created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_variant (experiment_id, variant_id),
    CONSTRAINT fk_experiment FOREIGN KEY (experiment_id) 
        REFERENCES experiments(experiment_id) ON DELETE CASCADE
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;
