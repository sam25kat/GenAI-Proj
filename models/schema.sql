-- PromptSense Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    preferences JSONB DEFAULT '{
        "tone": "professional",
        "expertise_level": "intermediate",
        "preferred_domains": []
    }',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    original_prompt TEXT,
    enhanced_prompt TEXT,
    intent TEXT,
    domain TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vector_saved BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_vector_saved ON messages(vector_saved);

-- Insert demo users
INSERT INTO users (id, email, name, preferences) VALUES
(1, 'demo@promptsense.ai', 'Demo User', '{
    "tone": "friendly",
    "expertise_level": "beginner",
    "preferred_domains": ["technology", "coding"]
}'),
(2, 'advanced@promptsense.ai', 'Advanced User', '{
    "tone": "professional",
    "expertise_level": "advanced",
    "preferred_domains": ["finance", "data-science"]
}')
ON CONFLICT (email) DO NOTHING;
