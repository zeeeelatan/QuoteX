-- 用户注册登录与历史记录按用户隔离
-- 执行: psql -U your_user -d your_db -f add_auth_and_user_id.sql

-- user_profile: 增加登录字段
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS username VARCHAR(64) UNIQUE;
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE user_profile ALTER COLUMN employee_id DROP NOT NULL;

-- quote_history: 增加用户关联
ALTER TABLE quote_history ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_quote_history_user_id ON quote_history(user_id);
