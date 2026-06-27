-- 顧客對解卦的滿意度評分（1~5 星）。一筆問卦一個分數，可重新評分。
-- 未跑此 migration：讀取不受影響（顯示無評分），只有「存評分」會失敗（程式溫和略過）。
alter table sessions add column if not exists rating int;
