-- Phase V: Full-text search and performance indexes
-- Run against Neon PostgreSQL after models are created

-- Task extensions
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);
CREATE INDEX IF NOT EXISTS idx_task_due_date ON task(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_task_recurrence_parent ON task(recurrence_parent_id) WHERE recurrence_parent_id IS NOT NULL;

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_task_title_search ON task USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_task_desc_search ON task USING gin(to_tsvector('english', COALESCE(description, '')));

-- Tag lookups
CREATE INDEX IF NOT EXISTS idx_tag_user_name ON tag(user_id, name);
CREATE INDEX IF NOT EXISTS idx_tasktag_task ON tasktag(task_id);
CREATE INDEX IF NOT EXISTS idx_tasktag_tag ON tasktag(tag_id);

-- Audit
CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_event_id ON audit_entries(event_id);
CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp ON audit_entries(user_id, timestamp);

-- Reminder
CREATE INDEX IF NOT EXISTS idx_reminder_pending ON reminder_schedule(remind_at) WHERE status = 'pending';

-- Conversation
CREATE INDEX IF NOT EXISTS idx_session_user_active ON conversationhistory(user_id, is_active, updated_at);

-- Outbox
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished ON outboxevent(created_at) WHERE published_at IS NULL;
