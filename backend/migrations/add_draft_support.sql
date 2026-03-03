-- 添加草稿支持字段
-- 执行前请备份数据库

-- 添加 draft_stage 字段
ALTER TABLE quote_history ADD COLUMN IF NOT EXISTS draft_stage VARCHAR(50);

-- 添加 updated_at 字段
ALTER TABLE quote_history ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 添加 page_states 字段
ALTER TABLE quote_history ADD COLUMN IF NOT EXISTS page_states JSONB;

-- 为 updated_at 创建索引
CREATE INDEX IF NOT EXISTS idx_quote_history_updated_at ON quote_history(updated_at DESC);

-- 为 draft_stage 创建索引
CREATE INDEX IF NOT EXISTS idx_quote_history_draft_stage ON quote_history(draft_stage);

-- 更新现有记录的 updated_at 为 created_at
UPDATE quote_history SET updated_at = created_at WHERE updated_at IS NULL;
