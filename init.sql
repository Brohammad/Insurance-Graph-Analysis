-- PostgreSQL initialization script for MedAssist
-- Creates tables for conversation memory, session tracking, and analytics

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conversation history table
CREATE TABLE conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    intent VARCHAR(100),
    confidence FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Session metadata table
CREATE TABLE session_metadata (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    user_agent TEXT,
    ip_address INET,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Query analytics table
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    intent VARCHAR(100),
    confidence FLOAT,
    execution_time_ms INTEGER,
    kg_queries_count INTEGER DEFAULT 0,
    rag_queries_count INTEGER DEFAULT 0,
    is_hybrid BOOLEAN DEFAULT FALSE,
    is_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    response_length INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Error logs table
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'ERROR' CHECK (severity IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_conversation_session ON conversation_history(session_id);
CREATE INDEX idx_conversation_created ON conversation_history(created_at);
CREATE INDEX idx_conversation_intent ON conversation_history(intent);

CREATE INDEX idx_session_last_seen ON session_metadata(last_seen);
CREATE INDEX idx_session_user ON session_metadata(user_id);

CREATE INDEX idx_analytics_session ON query_analytics(session_id);
CREATE INDEX idx_analytics_created ON query_analytics(created_at);
CREATE INDEX idx_analytics_intent ON query_analytics(intent);
CREATE INDEX idx_analytics_success ON query_analytics(is_successful);

CREATE INDEX idx_errors_session ON error_logs(session_id);
CREATE INDEX idx_errors_created ON error_logs(created_at);
CREATE INDEX idx_errors_severity ON error_logs(severity);
CREATE INDEX idx_errors_resolved ON error_logs(resolved);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_conversation_updated_at BEFORE UPDATE ON conversation_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_session_updated_at BEFORE UPDATE ON session_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for session statistics
CREATE VIEW session_statistics AS
SELECT 
    s.session_id,
    s.user_id,
    s.message_count,
    s.total_queries,
    s.successful_queries,
    s.failed_queries,
    ROUND(
        CASE 
            WHEN s.total_queries > 0 THEN (s.successful_queries::FLOAT / s.total_queries * 100)
            ELSE 0
        END, 2
    ) AS success_rate,
    EXTRACT(EPOCH FROM (s.last_seen - s.first_seen)) / 60 AS session_duration_minutes,
    s.first_seen,
    s.last_seen
FROM session_metadata s;

-- Create view for intent distribution
CREATE VIEW intent_distribution AS
SELECT 
    intent,
    COUNT(*) AS query_count,
    ROUND(AVG(confidence), 2) AS avg_confidence,
    ROUND(AVG(execution_time_ms), 2) AS avg_execution_time_ms,
    SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) AS successful_count,
    ROUND(
        SUM(CASE WHEN is_successful THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100, 2
    ) AS success_rate
FROM query_analytics
WHERE intent IS NOT NULL
GROUP BY intent
ORDER BY query_count DESC;

-- Create view for error summary
CREATE VIEW error_summary AS
SELECT 
    error_type,
    COUNT(*) AS error_count,
    COUNT(CASE WHEN resolved THEN 1 END) AS resolved_count,
    COUNT(CASE WHEN NOT resolved THEN 1 END) AS unresolved_count,
    MAX(created_at) AS last_occurrence
FROM error_logs
GROUP BY error_type
ORDER BY error_count DESC;

-- Grant permissions (adjust as needed for your deployment)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medassist;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medassist;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO medassist;

-- Insert initial system message (optional)
INSERT INTO conversation_history (session_id, role, content, intent) VALUES 
('system', 'system', 'MedAssist database initialized successfully', 'system');

-- Create materialized view for daily analytics (refresh periodically)
CREATE MATERIALIZED VIEW daily_analytics AS
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) AS successful_queries,
    SUM(CASE WHEN is_hybrid THEN 1 ELSE 0 END) AS hybrid_queries,
    ROUND(AVG(execution_time_ms), 2) AS avg_execution_time_ms,
    ROUND(AVG(confidence), 2) AS avg_confidence,
    COUNT(DISTINCT session_id) AS unique_sessions
FROM query_analytics
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Create index on materialized view
CREATE INDEX idx_daily_analytics_date ON daily_analytics(date);

-- Comment on tables
COMMENT ON TABLE conversation_history IS 'Stores all conversation messages with intent classification';
COMMENT ON TABLE session_metadata IS 'Tracks session-level statistics and user information';
COMMENT ON TABLE query_analytics IS 'Detailed analytics for each query execution';
COMMENT ON TABLE error_logs IS 'System error tracking and debugging';
