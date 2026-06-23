-- 在 Supabase SQL Editor 整段貼上執行即可（IF NOT EXISTS，可重複跑、不會動到既有資料）
-- Email 登入 + 回覆通知所需欄位
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS email text;

-- LIFF 顧客免密碼登入所需欄位
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS line_uid text;

-- 加查詢索引（email / line_uid 反查未結案問卦時用到）
CREATE INDEX IF NOT EXISTS idx_sessions_email    ON sessions (email);
CREATE INDEX IF NOT EXISTS idx_sessions_line_uid ON sessions (line_uid);
