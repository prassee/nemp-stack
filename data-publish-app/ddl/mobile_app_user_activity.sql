-- ============================================================================
-- Mobile App User Activity Monitoring Table (MySQL Optimized)
-- ============================================================================
-- Captures mobile app user activity with app-specific events stored in JSON
-- Optimized for MySQL 8.0+ with JSON support and functional indexes
-- ============================================================================

CREATE TABLE mobile_app_user_activity (
    -- ========================================================================
    -- PRIMARY IDENTIFIERS
    -- ========================================================================
    activity_id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    activity_uuid           CHAR(36) NOT NULL DEFAULT (UUID()),
    
    -- ========================================================================
    -- USER IDENTIFICATION
    -- ========================================================================
    user_id                 BIGINT UNSIGNED NOT NULL,
    user_uuid               CHAR(36),
    username                VARCHAR(255),
    user_email              VARCHAR(320),
    user_phone              VARCHAR(20),
    user_display_name       VARCHAR(255),
    user_tier               VARCHAR(50) COMMENT 'e.g., free, basic, premium, enterprise',
    user_status             VARCHAR(50) COMMENT 'e.g., active, inactive, suspended',
    
    -- ========================================================================
    -- SESSION INFORMATION
    -- ========================================================================
    session_id              VARCHAR(128) NOT NULL,
    session_uuid            CHAR(36),
    session_start_time      DATETIME(3),
    session_sequence_num    INT UNSIGNED COMMENT 'Activity order within session',
    is_new_session          TINYINT(1) DEFAULT 0,
    
    -- ========================================================================
    -- ACTIVITY DETAILS
    -- ========================================================================
    activity_type           VARCHAR(100) NOT NULL COMMENT 'e.g., app_open, screen_view, button_click, payment, login',
    activity_category       VARCHAR(100) COMMENT 'e.g., navigation, transaction, authentication, engagement',
    activity_action         VARCHAR(100) COMMENT 'e.g., tap, swipe, scroll, submit, cancel',
    activity_label          VARCHAR(255) COMMENT 'Descriptive label for the activity',
    activity_value          DECIMAL(18, 4) COMMENT 'Numeric value associated with activity',
    activity_status         ENUM('success', 'failed', 'pending', 'timeout', 'cancelled', 'error') NOT NULL DEFAULT 'success',
    activity_timestamp      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    activity_date           DATE AS (DATE(activity_timestamp)) STORED,
    activity_hour           TINYINT UNSIGNED AS (HOUR(activity_timestamp)) STORED,
    activity_day_of_week    TINYINT UNSIGNED AS (DAYOFWEEK(activity_timestamp)) STORED,
    
    -- ========================================================================
    -- DEVICE DETAILS
    -- ========================================================================
    device_id               VARCHAR(128) COMMENT 'Unique device identifier (IDFV/Android ID)',
    device_advertising_id   VARCHAR(128) COMMENT 'IDFA/GAID for attribution',
    device_fingerprint      VARCHAR(256),
    device_type             ENUM('phone', 'tablet', 'wearable', 'other') DEFAULT 'phone',
    device_os               ENUM('ios', 'android', 'other') NOT NULL,
    device_os_version       VARCHAR(20),
    device_manufacturer     VARCHAR(100),
    device_model            VARCHAR(100),
    device_brand            VARCHAR(100),
    device_screen_width     SMALLINT UNSIGNED,
    device_screen_height    SMALLINT UNSIGNED,
    device_screen_density   DECIMAL(5, 2) COMMENT 'Screen density (DPI)',
    device_language         VARCHAR(10),
    device_timezone         VARCHAR(50),
    device_battery_level    TINYINT UNSIGNED COMMENT 'Battery percentage 0-100',
    device_battery_charging TINYINT(1),
    device_storage_free_mb  INT UNSIGNED,
    device_ram_total_mb     INT UNSIGNED,
    device_ram_free_mb      INT UNSIGNED,
    is_rooted_jailbroken    TINYINT(1) DEFAULT 0,
    is_emulator             TINYINT(1) DEFAULT 0,
    
    -- ========================================================================
    -- APP DETAILS
    -- ========================================================================
    app_version             VARCHAR(20) NOT NULL,
    app_build_number        VARCHAR(20),
    app_bundle_id           VARCHAR(255),
    app_install_source      VARCHAR(100) COMMENT 'e.g., play_store, app_store, sideload',
    app_install_date        DATE,
    app_update_date         DATE,
    sdk_version             VARCHAR(20),
    
    -- ========================================================================
    -- NETWORK & IP ADDRESS
    -- ========================================================================
    ip_address              VARCHAR(45) NOT NULL COMMENT 'IPv4 or IPv6 address',
    ip_address_type         ENUM('ipv4', 'ipv6') AS (
        CASE WHEN ip_address LIKE '%.%.%.%' THEN 'ipv4' ELSE 'ipv6' END
    ) STORED,
    connection_type         ENUM('wifi', '2g', '3g', '4g', '5g', 'ethernet', 'unknown') DEFAULT 'unknown',
    carrier_name            VARCHAR(100),
    carrier_country_code    VARCHAR(5),
    network_ssid            VARCHAR(100) COMMENT 'WiFi network name (hashed for privacy)',
    is_vpn_detected         TINYINT(1) DEFAULT 0,
    is_proxy_detected       TINYINT(1) DEFAULT 0,
    
    -- ========================================================================
    -- GEOLOCATION (Lat/Long)
    -- ========================================================================
    latitude                DECIMAL(10, 8) COMMENT 'GPS latitude',
    longitude               DECIMAL(11, 8) COMMENT 'GPS longitude',
    geo_accuracy_meters     DECIMAL(10, 2),
    geo_altitude_meters     DECIMAL(10, 2),
    geo_speed_mps           DECIMAL(10, 2) COMMENT 'Speed in meters per second',
    geo_heading             DECIMAL(5, 2) COMMENT 'Direction in degrees',
    geo_source              ENUM('gps', 'network', 'ip', 'manual', 'unknown') DEFAULT 'unknown',
    geo_timestamp           DATETIME(3) COMMENT 'When location was captured',
    
    -- ========================================================================
    -- DEMOGRAPHY & GEOLOCATION (Derived)
    -- ========================================================================
    country_code            CHAR(2) COMMENT 'ISO 3166-1 alpha-2',
    country_name            VARCHAR(100),
    region_code             VARCHAR(10),
    region_name             VARCHAR(100),
    city_name               VARCHAR(100),
    district_name           VARCHAR(100),
    postal_code             VARCHAR(20),
    timezone_name           VARCHAR(50),
    timezone_offset_mins    SMALLINT,
    locale                  VARCHAR(10) COMMENT 'e.g., en_US, es_MX',
    language_code           CHAR(2) COMMENT 'ISO 639-1',
    currency_code           CHAR(3) COMMENT 'ISO 4217 local currency',
    
    -- ========================================================================
    -- UI/UX METRICS
    -- ========================================================================
    screen_name             VARCHAR(100) COMMENT 'Current screen/view name',
    screen_class            VARCHAR(100) COMMENT 'Screen class/component name',
    previous_screen_name    VARCHAR(100),
    screen_view_duration_ms INT UNSIGNED COMMENT 'Time spent on screen',
    screen_orientation      ENUM('portrait', 'landscape') DEFAULT 'portrait',
    element_id              VARCHAR(100) COMMENT 'Tapped element identifier',
    element_type            VARCHAR(50) COMMENT 'e.g., button, link, card, input',
    element_text            VARCHAR(255) COMMENT 'Element label/text',
    element_position_x      SMALLINT UNSIGNED,
    element_position_y      SMALLINT UNSIGNED,
    scroll_depth_percent    TINYINT UNSIGNED COMMENT '0-100 scroll percentage',
    scroll_direction        ENUM('up', 'down', 'left', 'right'),
    gesture_type            VARCHAR(50) COMMENT 'e.g., tap, double_tap, long_press, swipe, pinch',
    interaction_count       INT UNSIGNED COMMENT 'Number of interactions on screen',
    keyboard_visible        TINYINT(1),
    input_field_name        VARCHAR(100),
    input_method            VARCHAR(50) COMMENT 'e.g., keyboard, voice, paste, autofill',
    accessibility_enabled   TINYINT(1) DEFAULT 0,
    dark_mode_enabled       TINYINT(1) DEFAULT 0,
    font_scale              DECIMAL(3, 2) DEFAULT 1.00,
    
    -- ========================================================================
    -- PAGE LOAD METRICS
    -- ========================================================================
    page_load_time_ms       INT UNSIGNED COMMENT 'Total page load time',
    time_to_first_paint_ms  INT UNSIGNED,
    time_to_interactive_ms  INT UNSIGNED,
    dom_content_loaded_ms   INT UNSIGNED,
    resource_load_time_ms   INT UNSIGNED,
    render_time_ms          INT UNSIGNED,
    frame_rate_fps          TINYINT UNSIGNED COMMENT 'Average FPS during activity',
    dropped_frames          INT UNSIGNED,
    memory_usage_mb         INT UNSIGNED,
    cpu_usage_percent       TINYINT UNSIGNED,
    
    -- ========================================================================
    -- API INTERACTION DATA (JSON)
    -- ========================================================================
    api_interaction_data    JSON COMMENT 'Detailed API call information including request/response metadata',
    /*
    Expected structure:
    {
        "endpoint": "/api/v1/payments",
        "method": "POST",
        "request_id": "req_abc123",
        "request_timestamp": "2024-01-15T10:30:00.123Z",
        "response_timestamp": "2024-01-15T10:30:00.456Z",
        "response_time_ms": 333,
        "http_status_code": 200,
        "request_size_bytes": 1024,
        "response_size_bytes": 2048,
        "request_headers": {"Content-Type": "application/json"},
        "response_headers": {"X-Request-ID": "req_abc123"},
        "request_body_hash": "sha256:...",
        "cache_hit": false,
        "retries": [
            {"attempt": 1, "timestamp": "...", "error": "timeout"},
            {"attempt": 2, "timestamp": "...", "status": 200}
        ],
        "dns_lookup_ms": 10,
        "tcp_connect_ms": 20,
        "tls_handshake_ms": 30,
        "server_processing_ms": 200,
        "content_transfer_ms": 73
    }
    */
    
    -- ========================================================================
    -- ERROR & RETRY STATUS
    -- ========================================================================
    error_code              VARCHAR(50),
    error_message           TEXT,
    error_type              VARCHAR(100) COMMENT 'e.g., network_error, validation_error, server_error, client_error',
    error_source            VARCHAR(100) COMMENT 'e.g., api, ui, sdk, system',
    error_stack_trace       TEXT,
    is_error                TINYINT(1) AS (error_code IS NOT NULL) STORED,
    retry_count             TINYINT UNSIGNED DEFAULT 0,
    retry_status            ENUM('not_applicable', 'pending', 'in_progress', 'success', 'failed', 'exhausted') DEFAULT 'not_applicable',
    max_retries_allowed     TINYINT UNSIGNED DEFAULT 3,
    last_retry_timestamp    DATETIME(3),
    retry_backoff_ms        INT UNSIGNED COMMENT 'Backoff time before next retry',
    
    -- ========================================================================
    -- APP-SPECIFIC EVENTS (Generic JSON Column)
    -- ========================================================================
    app_event_data          JSON COMMENT 'App-specific event data in flexible JSON format',
    /*
    Expected structure varies by activity_type. Examples:
    
    For payment events:
    {
        "payment_id": "pay_123",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "card",
        "card_last_four": "4242",
        "merchant_name": "Coffee Shop",
        "category": "food_beverage"
    }
    
    For screen_view events:
    {
        "content_id": "product_456",
        "content_type": "product_detail",
        "content_name": "Premium Headphones",
        "search_query": "wireless headphones",
        "filters_applied": ["price_under_100", "brand_sony"]
    }
    
    For feature_usage events:
    {
        "feature_name": "biometric_login",
        "feature_version": "2.0",
        "settings": {"face_id": true, "touch_id": false},
        "success": true
    }
    */
    
    -- ========================================================================
    -- METADATA & AUDIT
    -- ========================================================================
    source_platform         VARCHAR(50) DEFAULT 'mobile_app',
    ingestion_timestamp     DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    processing_status       ENUM('raw', 'processed', 'enriched', 'failed') DEFAULT 'raw',
    data_quality_flags      SET('missing_user', 'missing_location', 'invalid_timestamp', 'suspicious_activity'),
    is_synthetic            TINYINT(1) DEFAULT 0 COMMENT 'Test/synthetic data flag',
    is_internal_user        TINYINT(1) DEFAULT 0 COMMENT 'Internal employee flag',
    created_at              DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at              DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    
    -- ========================================================================
    -- INDEXES
    -- ========================================================================
    
    -- Unique constraint on activity UUID
    UNIQUE INDEX idx_activity_uuid (activity_uuid),
    
    -- Primary lookup indexes
    INDEX idx_user_id (user_id),
    INDEX idx_user_uuid (user_uuid),
    INDEX idx_username (username),
    INDEX idx_session_id (session_id),
    
    -- Time-based indexes (critical for analytics)
    INDEX idx_activity_timestamp (activity_timestamp DESC),
    INDEX idx_activity_date (activity_date DESC),
    INDEX idx_user_activity_date (user_id, activity_date DESC),
    
    -- Activity type analysis
    INDEX idx_activity_type (activity_type),
    INDEX idx_activity_status (activity_status),
    INDEX idx_activity_type_status (activity_type, activity_status),
    INDEX idx_activity_category (activity_category),
    
    -- Device analysis
    INDEX idx_device_id (device_id),
    INDEX idx_device_os (device_os),
    INDEX idx_device_os_version (device_os, device_os_version),
    INDEX idx_app_version (app_version),
    
    -- Network and IP
    INDEX idx_ip_address (ip_address),
    INDEX idx_connection_type (connection_type),
    
    -- Geolocation
    INDEX idx_country_code (country_code),
    INDEX idx_city (country_code, city_name),
    INDEX idx_lat_long (latitude, longitude),
    
    -- UI/UX analysis
    INDEX idx_screen_name (screen_name),
    INDEX idx_screen_flow (previous_screen_name, screen_name),
    
    -- Error tracking
    INDEX idx_error_code (error_code),
    INDEX idx_is_error (is_error),
    INDEX idx_retry_status (retry_status),
    
    -- Composite indexes for common queries
    INDEX idx_user_type_date (user_id, activity_type, activity_date DESC),
    INDEX idx_session_sequence (session_id, session_sequence_num),
    INDEX idx_user_screen_time (user_id, screen_name, activity_timestamp DESC)
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  ROW_FORMAT=DYNAMIC
  COMMENT='Mobile app user activity monitoring with JSON event storage';


-- ============================================================================
-- FUNCTIONAL INDEXES ON JSON COLUMNS (MySQL 8.0+)
-- ============================================================================

-- Index on API endpoint from api_interaction_data
ALTER TABLE mobile_app_user_activity ADD INDEX idx_api_endpoint (
    (CAST(api_interaction_data->>'$.endpoint' AS CHAR(255) COLLATE utf8mb4_unicode_ci))
);

-- Index on HTTP status code from api_interaction_data
ALTER TABLE mobile_app_user_activity ADD INDEX idx_api_http_status (
    (CAST(api_interaction_data->>'$.http_status_code' AS UNSIGNED))
);

-- Index on API response time for performance analysis
ALTER TABLE mobile_app_user_activity ADD INDEX idx_api_response_time (
    (CAST(api_interaction_data->>'$.response_time_ms' AS UNSIGNED))
);

-- Index on payment amount from app_event_data (for payment activities)
ALTER TABLE mobile_app_user_activity ADD INDEX idx_event_amount (
    (CAST(app_event_data->>'$.amount' AS DECIMAL(18,4)))
);

-- Index on feature name from app_event_data
ALTER TABLE mobile_app_user_activity ADD INDEX idx_event_feature (
    (CAST(app_event_data->>'$.feature_name' AS CHAR(100) COLLATE utf8mb4_unicode_ci))
);


-- ============================================================================
-- PARTITIONING BY DATE (for high-volume deployments)
-- ============================================================================
-- Uncomment and modify for production use with partitioning

/*
ALTER TABLE mobile_app_user_activity
PARTITION BY RANGE (TO_DAYS(activity_date)) (
    PARTITION p_2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
    PARTITION p_2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01')),
    PARTITION p_2024_03 VALUES LESS THAN (TO_DAYS('2024-04-01')),
    PARTITION p_2024_04 VALUES LESS THAN (TO_DAYS('2024-05-01')),
    PARTITION p_2024_05 VALUES LESS THAN (TO_DAYS('2024-06-01')),
    PARTITION p_2024_06 VALUES LESS THAN (TO_DAYS('2024-07-01')),
    PARTITION p_2024_07 VALUES LESS THAN (TO_DAYS('2024-08-01')),
    PARTITION p_2024_08 VALUES LESS THAN (TO_DAYS('2024-09-01')),
    PARTITION p_2024_09 VALUES LESS THAN (TO_DAYS('2024-10-01')),
    PARTITION p_2024_10 VALUES LESS THAN (TO_DAYS('2024-11-01')),
    PARTITION p_2024_11 VALUES LESS THAN (TO_DAYS('2024-12-01')),
    PARTITION p_2024_12 VALUES LESS THAN (TO_DAYS('2025-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
*/


-- ============================================================================
-- STORED PROCEDURE: Add new monthly partition
-- ============================================================================
/*
DELIMITER //

CREATE PROCEDURE add_monthly_partition(IN partition_date DATE)
BEGIN
    DECLARE partition_name VARCHAR(20);
    DECLARE next_month DATE;
    
    SET partition_name = CONCAT('p_', DATE_FORMAT(partition_date, '%Y_%m'));
    SET next_month = DATE_ADD(partition_date, INTERVAL 1 MONTH);
    
    SET @sql = CONCAT(
        'ALTER TABLE mobile_app_user_activity REORGANIZE PARTITION p_future INTO (',
        'PARTITION ', partition_name, ' VALUES LESS THAN (TO_DAYS(''', next_month, ''')),',
        'PARTITION p_future VALUES LESS THAN MAXVALUE)'
    );
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;
*/


-- ============================================================================
-- VIEWS FOR COMMON ANALYTICS QUERIES
-- ============================================================================

-- Daily activity summary view
CREATE OR REPLACE VIEW v_daily_activity_summary AS
SELECT 
    activity_date,
    activity_type,
    device_os,
    country_code,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    SUM(CASE WHEN activity_status = 'success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN activity_status = 'failed' THEN 1 ELSE 0 END) as failed_count,
    SUM(CASE WHEN is_error = 1 THEN 1 ELSE 0 END) as error_count,
    AVG(page_load_time_ms) as avg_page_load_ms,
    AVG(CAST(api_interaction_data->>'$.response_time_ms' AS UNSIGNED)) as avg_api_response_ms
FROM mobile_app_user_activity
GROUP BY activity_date, activity_type, device_os, country_code;


-- Error summary view
CREATE OR REPLACE VIEW v_error_summary AS
SELECT 
    activity_date,
    error_code,
    error_type,
    error_source,
    device_os,
    app_version,
    COUNT(*) as error_count,
    COUNT(DISTINCT user_id) as affected_users,
    SUM(CASE WHEN retry_status = 'success' THEN 1 ELSE 0 END) as retry_success_count,
    SUM(CASE WHEN retry_status = 'exhausted' THEN 1 ELSE 0 END) as retry_exhausted_count
FROM mobile_app_user_activity
WHERE is_error = 1
GROUP BY activity_date, error_code, error_type, error_source, device_os, app_version;


-- Screen flow analysis view
CREATE OR REPLACE VIEW v_screen_flow AS
SELECT 
    previous_screen_name,
    screen_name,
    COUNT(*) as transition_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(screen_view_duration_ms) as avg_duration_ms
FROM mobile_app_user_activity
WHERE screen_name IS NOT NULL
GROUP BY previous_screen_name, screen_name
ORDER BY transition_count DESC;


-- ============================================================================
-- TABLE COMMENTS
-- ============================================================================
-- Note: MySQL doesn't support column comments in the same way as PostgreSQL's COMMENT ON
-- Column comments are already included inline in the table definition above
