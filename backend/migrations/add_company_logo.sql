-- 为 company_info 表添加 company_logo 字段（存储 base64 格式的公司 Logo）
-- 若表已存在但缺少该列，运行此脚本添加
ALTER TABLE company_info ADD COLUMN IF NOT EXISTS company_logo TEXT;
