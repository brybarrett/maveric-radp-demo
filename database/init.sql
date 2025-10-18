-- DocBot Platform Database Initialization
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create database if not exists (handled by docker-compose environment variables)
-- Database: docbot
-- User: docbot_user

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::VARCHAR,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    client VARCHAR(100) NOT NULL,
    mode VARCHAR(50) DEFAULT 'full_overview',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Create index on client for filtering
CREATE INDEX IF NOT EXISTS idx_conversations_client ON conversations(client);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(255) PRIMARY KEY DEFAULT uuid_generate_v4()::VARCHAR,
    conversation_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    sources JSONB,
    visualization JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Create index on conversation_id for faster message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Create index on timestamp for chronological ordering
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at on conversations
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional - can be removed for production)
-- Uncomment the lines below if you want test data

-- INSERT INTO conversations (session_id, client, mode) VALUES
--     ('demo-session-001', 'demo', 'full_overview'),
--     ('maveric-session-001', 'maveric', 'general');

-- INSERT INTO messages (conversation_id, role, content) VALUES
--     ((SELECT id FROM conversations WHERE session_id = 'demo-session-001'), 'user', 'Hello, what can you help me with?'),
--     ((SELECT id FROM conversations WHERE session_id = 'demo-session-001'), 'assistant', 'Hi! I can help you understand DocBot and its capabilities. Would you like a full tour or do you have specific questions?');

-- Grant permissions to docbot_user (if needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO docbot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO docbot_user;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'DocBot database initialized successfully!';
    RAISE NOTICE 'Tables created: conversations, messages';
    RAISE NOTICE 'Indexes created for performance optimization';
    RAISE NOTICE 'Triggers configured for automatic timestamp updates';
END $$;