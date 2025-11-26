-- Migration: Add Conversations Support
-- This script adds conversation tracking to PromptSense

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add conversation_id to messages table
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Migrate existing messages to a default conversation per user
DO $$
DECLARE
    user_record RECORD;
    new_conversation_id INTEGER;
BEGIN
    -- For each user with messages but no conversation
    FOR user_record IN
        SELECT DISTINCT user_id
        FROM messages
        WHERE conversation_id IS NULL
    LOOP
        -- Create a default conversation for this user
        INSERT INTO conversations (user_id, title, created_at, updated_at)
        VALUES (
            user_record.user_id,
            'Previous Conversation',
            (SELECT MIN(timestamp) FROM messages WHERE user_id = user_record.user_id),
            (SELECT MAX(timestamp) FROM messages WHERE user_id = user_record.user_id)
        )
        RETURNING id INTO new_conversation_id;

        -- Update all messages for this user to belong to this conversation
        UPDATE messages
        SET conversation_id = new_conversation_id
        WHERE user_id = user_record.user_id AND conversation_id IS NULL;
    END LOOP;
END $$;

-- Add trigger to update updated_at timestamp on conversations
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    WHEN (NEW.conversation_id IS NOT NULL)
    EXECUTE FUNCTION update_conversation_timestamp();
