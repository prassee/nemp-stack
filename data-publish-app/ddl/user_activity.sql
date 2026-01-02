-- ============================================================================
-- User Activity Table for Payment App Analytics
-- ============================================================================
-- This DDL captures extensive user activity data for comprehensive analytics
-- including behavioral patterns, transaction flows, and user engagement metrics.
-- ============================================================================

CREATE TABLE user_activity (
    -- ========================================================================
    -- PRIMARY IDENTIFIERS
    -- ========================================================================
    activity_id             BIGSERIAL PRIMARY KEY,
    activity_uuid           UUID NOT NULL DEFAULT gen_random_uuid(),
    
    -- ========================================================================
    -- USER IDENTIFICATION
    -- ========================================================================
    user_id                 BIGINT NOT NULL,
    user_uuid               UUID,
    username                VARCHAR(255),
    user_email              VARCHAR(320),
    user_phone              VARCHAR(20),
    user_tier               VARCHAR(50),                -- e.g., 'basic', 'premium', 'enterprise'
    user_kyc_status         VARCHAR(50),                -- e.g., 'pending', 'verified', 'rejected'
    user_account_age_days   INTEGER,                    -- days since account creation
    
    -- ========================================================================
    -- SESSION INFORMATION
    -- ========================================================================
    session_id              VARCHAR(128) NOT NULL,
    session_start_time      TIMESTAMP WITH TIME ZONE,
    session_sequence_number INTEGER,                    -- activity order within session
    is_new_session          BOOLEAN DEFAULT FALSE,
    
    -- ========================================================================
    -- ACTIVITY DETAILS
    -- ========================================================================
    activity_type           VARCHAR(100) NOT NULL,      -- e.g., 'login', 'payment', 'transfer', 'view'
    activity_category       VARCHAR(100),               -- e.g., 'authentication', 'transaction', 'navigation'
    activity_subcategory    VARCHAR(100),               -- e.g., 'p2p_transfer', 'bill_payment', 'merchant_payment'
    activity_action         VARCHAR(100),               -- e.g., 'initiate', 'confirm', 'cancel', 'retry'
    activity_status         VARCHAR(50) NOT NULL,       -- e.g., 'success', 'failed', 'pending', 'timeout'
    activity_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    activity_date           DATE GENERATED ALWAYS AS (activity_timestamp::DATE) STORED,
    activity_hour           SMALLINT GENERATED ALWAYS AS (EXTRACT(HOUR FROM activity_timestamp)::SMALLINT) STORED,
    activity_day_of_week    SMALLINT GENERATED ALWAYS AS (EXTRACT(DOW FROM activity_timestamp)::SMALLINT) STORED,
    
    -- ========================================================================
    -- TRANSACTION DETAILS (for payment-related activities)
    -- ========================================================================
    transaction_id          VARCHAR(128),
    transaction_reference   VARCHAR(128),
    transaction_type        VARCHAR(50),                -- e.g., 'debit', 'credit', 'reversal'
    payment_method          VARCHAR(50),                -- e.g., 'wallet', 'card', 'bank_transfer', 'upi'
    payment_instrument_id   VARCHAR(128),               -- masked card/account identifier
    payment_instrument_type VARCHAR(50),                -- e.g., 'visa', 'mastercard', 'savings_account'
    payment_channel         VARCHAR(50),                -- e.g., 'app', 'web', 'api', 'pos'
    
    -- ========================================================================
    -- MONETARY DETAILS
    -- ========================================================================
    amount                  DECIMAL(18, 4),
    currency_code           CHAR(3),                    -- ISO 4217 currency code
    amount_in_base_currency DECIMAL(18, 4),             -- converted to base currency for analytics
    base_currency_code      CHAR(3) DEFAULT 'USD',
    exchange_rate           DECIMAL(18, 8),
    fee_amount              DECIMAL(18, 4),
    tax_amount              DECIMAL(18, 4),
    total_amount            DECIMAL(18, 4),
    
    -- ========================================================================
    -- COUNTERPARTY INFORMATION
    -- ========================================================================
    counterparty_id         BIGINT,
    counterparty_type       VARCHAR(50),                -- e.g., 'user', 'merchant', 'biller', 'bank'
    counterparty_name       VARCHAR(255),
    counterparty_category   VARCHAR(100),               -- e.g., 'food', 'utilities', 'entertainment'
    merchant_id             VARCHAR(128),
    merchant_category_code  VARCHAR(10),                -- MCC code
    merchant_name           VARCHAR(255),
    merchant_country        CHAR(2),                    -- ISO 3166-1 alpha-2
    
    -- ========================================================================
    -- DEVICE INFORMATION
    -- ========================================================================
    device_id               VARCHAR(128),
    device_fingerprint      VARCHAR(256),
    device_type             VARCHAR(50),                -- e.g., 'mobile', 'tablet', 'desktop'
    device_os               VARCHAR(50),                -- e.g., 'ios', 'android', 'windows'
    device_os_version       VARCHAR(20),
    device_manufacturer     VARCHAR(100),
    device_model            VARCHAR(100),
    device_screen_resolution VARCHAR(20),
    app_version             VARCHAR(20),
    app_build_number        VARCHAR(20),
    sdk_version             VARCHAR(20),
    browser_name            VARCHAR(50),
    browser_version         VARCHAR(20),
    user_agent              TEXT,
    
    -- ========================================================================
    -- NETWORK & CONNECTIVITY
    -- ========================================================================
    ip_address              INET,
    ip_address_v6           INET,
    connection_type         VARCHAR(20),                -- e.g., 'wifi', '4g', '5g', 'ethernet'
    carrier_name            VARCHAR(100),
    network_latency_ms      INTEGER,
    
    -- ========================================================================
    -- GEOLOCATION
    -- ========================================================================
    latitude                DECIMAL(10, 8),
    longitude               DECIMAL(11, 8),
    geo_accuracy_meters     DECIMAL(10, 2),
    country_code            CHAR(2),                    -- ISO 3166-1 alpha-2
    country_name            VARCHAR(100),
    region_code             VARCHAR(10),
    region_name             VARCHAR(100),
    city_name               VARCHAR(100),
    postal_code             VARCHAR(20),
    timezone                VARCHAR(50),
    is_vpn_detected         BOOLEAN,
    is_proxy_detected       BOOLEAN,
    is_tor_detected         BOOLEAN,
    
    -- ========================================================================
    -- UI/UX INTERACTION METRICS
    -- ========================================================================
    screen_name             VARCHAR(100),
    previous_screen_name    VARCHAR(100),
    screen_view_duration_ms INTEGER,
    element_id              VARCHAR(100),               -- clicked button/link id
    element_type            VARCHAR(50),                -- e.g., 'button', 'link', 'card'
    element_position        VARCHAR(50),                -- e.g., 'header', 'footer', 'main'
    scroll_depth_percent    SMALLINT,
    interaction_count       INTEGER,                    -- taps/clicks on this screen
    form_field_name         VARCHAR(100),
    input_method            VARCHAR(50),                -- e.g., 'keyboard', 'voice', 'biometric'
    
    -- ========================================================================
    -- PERFORMANCE METRICS
    -- ========================================================================
    page_load_time_ms       INTEGER,
    api_response_time_ms    INTEGER,
    time_to_first_byte_ms   INTEGER,
    time_to_interactive_ms  INTEGER,
    client_render_time_ms   INTEGER,
    
    -- ========================================================================
    -- ERROR & EXCEPTION TRACKING
    -- ========================================================================
    error_code              VARCHAR(50),
    error_message           TEXT,
    error_category          VARCHAR(100),               -- e.g., 'network', 'validation', 'server', 'client'
    error_stack_trace       TEXT,
    retry_count             SMALLINT DEFAULT 0,
    is_retried              BOOLEAN DEFAULT FALSE,
    
    -- ========================================================================
    -- SECURITY & FRAUD DETECTION
    -- ========================================================================
    authentication_method   VARCHAR(50),                -- e.g., 'password', 'biometric', 'otp', 'sso'
    mfa_method              VARCHAR(50),                -- e.g., 'sms', 'email', 'authenticator', 'push'
    mfa_status              VARCHAR(20),
    risk_score              DECIMAL(5, 2),              -- 0.00 to 100.00
    risk_level              VARCHAR(20),                -- e.g., 'low', 'medium', 'high', 'critical'
    risk_factors            JSONB,                      -- detailed risk breakdown
    is_flagged_for_review   BOOLEAN DEFAULT FALSE,
    fraud_check_status      VARCHAR(20),
    fraud_check_provider    VARCHAR(50),
    is_trusted_device       BOOLEAN,
    device_trust_score      DECIMAL(5, 2),
    
    -- ========================================================================
    -- A/B TESTING & FEATURE FLAGS
    -- ========================================================================
    experiment_ids          TEXT[],                     -- active experiment IDs
    experiment_variants     JSONB,                      -- experiment:variant mapping
    feature_flags           JSONB,                      -- active feature flags
    
    -- ========================================================================
    -- MARKETING & ATTRIBUTION
    -- ========================================================================
    utm_source              VARCHAR(100),
    utm_medium              VARCHAR(100),
    utm_campaign            VARCHAR(255),
    utm_term                VARCHAR(255),
    utm_content             VARCHAR(255),
    referrer_url            TEXT,
    landing_page_url        TEXT,
    attribution_channel     VARCHAR(100),
    campaign_id             VARCHAR(128),
    promo_code              VARCHAR(50),
    
    -- ========================================================================
    -- CONTEXTUAL METADATA
    -- ========================================================================
    locale                  VARCHAR(10),                -- e.g., 'en-US', 'es-MX'
    language_code           CHAR(2),                    -- ISO 639-1
    is_first_time_action    BOOLEAN DEFAULT FALSE,
    is_repeat_action        BOOLEAN DEFAULT FALSE,
    days_since_last_activity INTEGER,
    lifetime_activity_count INTEGER,
    
    -- ========================================================================
    -- EXTENDED ATTRIBUTES (flexible schema)
    -- ========================================================================
    custom_attributes       JSONB,                      -- additional custom key-value pairs
    event_properties        JSONB,                      -- event-specific properties
    user_properties         JSONB,                      -- user properties snapshot at event time
    context_data            JSONB,                      -- additional contextual data
    
    -- ========================================================================
    -- DATA LINEAGE & AUDIT
    -- ========================================================================
    source_system           VARCHAR(50),                -- e.g., 'mobile_app', 'web_app', 'api'
    source_version          VARCHAR(20),
    ingestion_timestamp     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_timestamp    TIMESTAMP WITH TIME ZONE,
    data_quality_score      DECIMAL(5, 2),
    is_synthetic            BOOLEAN DEFAULT FALSE,      -- test/synthetic data flag
    is_backfilled           BOOLEAN DEFAULT FALSE,
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- ========================================================================
    -- CONSTRAINTS
    -- ========================================================================
    CONSTRAINT chk_activity_status CHECK (activity_status IN ('success', 'failed', 'pending', 'timeout', 'cancelled', 'unknown')),
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0 AND risk_score <= 100),
    CONSTRAINT chk_scroll_depth CHECK (scroll_depth_percent >= 0 AND scroll_depth_percent <= 100),
    CONSTRAINT chk_currency_code CHECK (currency_code ~ '^[A-Z]{3}$'),
    CONSTRAINT chk_country_code CHECK (country_code ~ '^[A-Z]{2}$')
);

-- ============================================================================
-- INDEXES FOR COMMON QUERY PATTERNS
-- ============================================================================

-- Primary lookup indexes
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_user_uuid ON user_activity(user_uuid);
CREATE INDEX idx_user_activity_session_id ON user_activity(session_id);
CREATE INDEX idx_user_activity_transaction_id ON user_activity(transaction_id);

-- Time-based analytics indexes
CREATE INDEX idx_user_activity_timestamp ON user_activity(activity_timestamp DESC);
CREATE INDEX idx_user_activity_date ON user_activity(activity_date DESC);
CREATE INDEX idx_user_activity_user_date ON user_activity(user_id, activity_date DESC);

-- Activity type analysis
CREATE INDEX idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX idx_user_activity_category ON user_activity(activity_category);
CREATE INDEX idx_user_activity_status ON user_activity(activity_status);
CREATE INDEX idx_user_activity_type_status ON user_activity(activity_type, activity_status);

-- Payment analytics indexes
CREATE INDEX idx_user_activity_payment_method ON user_activity(payment_method);
CREATE INDEX idx_user_activity_merchant ON user_activity(merchant_id);
CREATE INDEX idx_user_activity_mcc ON user_activity(merchant_category_code);
CREATE INDEX idx_user_activity_amount ON user_activity(amount) WHERE amount IS NOT NULL;

-- Geographic analysis
CREATE INDEX idx_user_activity_country ON user_activity(country_code);
CREATE INDEX idx_user_activity_city ON user_activity(city_name);
CREATE INDEX idx_user_activity_geo ON user_activity(latitude, longitude) WHERE latitude IS NOT NULL;

-- Device and platform analysis
CREATE INDEX idx_user_activity_device ON user_activity(device_type, device_os);
CREATE INDEX idx_user_activity_app_version ON user_activity(app_version);

-- Fraud and risk analysis
CREATE INDEX idx_user_activity_risk ON user_activity(risk_level) WHERE risk_level IS NOT NULL;
CREATE INDEX idx_user_activity_flagged ON user_activity(is_flagged_for_review) WHERE is_flagged_for_review = TRUE;
CREATE INDEX idx_user_activity_ip ON user_activity(ip_address);

-- Error analysis
CREATE INDEX idx_user_activity_errors ON user_activity(error_code) WHERE error_code IS NOT NULL;

-- Marketing attribution
CREATE INDEX idx_user_activity_campaign ON user_activity(campaign_id) WHERE campaign_id IS NOT NULL;
CREATE INDEX idx_user_activity_utm ON user_activity(utm_source, utm_medium, utm_campaign);

-- JSONB indexes for flexible querying
CREATE INDEX idx_user_activity_custom_attrs ON user_activity USING GIN (custom_attributes);
CREATE INDEX idx_user_activity_risk_factors ON user_activity USING GIN (risk_factors);
CREATE INDEX idx_user_activity_feature_flags ON user_activity USING GIN (feature_flags);

-- Composite indexes for common query patterns
CREATE INDEX idx_user_activity_user_type_date ON user_activity(user_id, activity_type, activity_date DESC);
CREATE INDEX idx_user_activity_funnel ON user_activity(user_id, activity_type, activity_timestamp);

-- ============================================================================
-- PARTITIONING (Optional - for high-volume deployments)
-- ============================================================================
-- Uncomment below to create a partitioned version of the table by month
-- 
-- CREATE TABLE user_activity_partitioned (
--     LIKE user_activity INCLUDING ALL
-- ) PARTITION BY RANGE (activity_date);
-- 
-- CREATE TABLE user_activity_y2024m01 PARTITION OF user_activity_partitioned
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- -- Add more partitions as needed

-- ============================================================================
-- TRIGGER FOR updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_user_activity_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_activity_updated_at
    BEFORE UPDATE ON user_activity
    FOR EACH ROW
    EXECUTE FUNCTION update_user_activity_timestamp();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE user_activity IS 'Comprehensive user activity tracking table for payment app analytics';
COMMENT ON COLUMN user_activity.activity_id IS 'Auto-incrementing primary key';
COMMENT ON COLUMN user_activity.activity_uuid IS 'Globally unique identifier for the activity event';
COMMENT ON COLUMN user_activity.user_id IS 'Internal user identifier';
COMMENT ON COLUMN user_activity.session_id IS 'Unique session identifier for grouping user activities';
COMMENT ON COLUMN user_activity.activity_type IS 'Type of activity performed (login, payment, transfer, etc.)';
COMMENT ON COLUMN user_activity.risk_score IS 'Fraud risk score from 0-100, higher means riskier';
COMMENT ON COLUMN user_activity.custom_attributes IS 'Flexible JSONB field for additional custom attributes';
