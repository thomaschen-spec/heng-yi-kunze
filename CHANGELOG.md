# 修改記錄

## 功能說明

多使用者易經諮詢平台。顧客在前台提問，管理員（小老師）在後台手動解卦回覆。無 AI 自動回覆。

---

## Bug 修復總覽（2026-06）

### 資料庫錯誤處理

| # | 問題 | 修法 |
|---|------|------|
| 1 | `get_messages()` 連線失敗時回傳 `[]`，無法分辨「DB 錯誤」與「真的沒訊息」 | 改回傳 `None`，呼叫端顯示重試按鈕 |
| 2 | `get_all_sessions()` 失敗時回傳 `[]`，後台以為真的沒資料 | 同上，改回傳 `None` |
| 3 | `get_archived_sessions()` 失敗時同上 | 同上 |
| 4 | `get_session()` 無法區分「session 不存在」與「DB 斷線」 | 加 `_DB_ERROR` sentinel 物件，兩種情況分別處理 |
| 5 | `_enrich()` 的 `messages` 欄位若 Supabase 回傳 `null` 會 crash | 改為 `s.get("messages") or []` |
| 6 | DB 斷線時 init_state 仍觸發 localStorage redirect，造成無窮重新載入 | 加 `_db_unreachable` flag，斷線時不執行 redirect JS |

### 操作結果回報

| # | 問題 | 修法 |
|---|------|------|
| 7 | `close_session()` 失敗時仍導向後台首頁（靜默失敗） | 改回傳 `bool`，只有成功才導航 |
| 8 | `delete_session()` 沒有回傳值，刪除失敗時仍清除狀態 | 改回傳 `bool`，所有刪除確認按鈕都先確認成功才處理 |
| 9 | `set_admin_password()` 寫入失敗時仍顯示「密碼已更新」 | 改回傳 `bool`，只有成功才顯示 success |
| 10 | `add_message()` 失敗後 admin 回覆頁仍 rerun（清空編輯中的文字） | 加回傳值判斷，失敗時保留 textarea 內容 |
| 11 | `add_message()` 失敗後顧客追加提問頁仍觸發 LINE 通知與 rerun | 同上 |
| 12 | `close_session()` 未更新 `updated_at` 欄位 | 加入 `updated_at` 到 PATCH payload |

### 狀態管理

| # | 問題 | 修法 |
|---|------|------|
| 13 | 顧客點「← 首頁」後，localStorage 未清除，下次開啟又自動跳回舊對話 | 加 `_clear_storage_quiet` flag，主動離開時靜默清除 localStorage |
| 14 | 結案/session 被刪除後顧客重訪，localStorage redirect → DB 找不到 → 錯誤頁 → redirect 無窮迴圈 | `_clear_storage` flag：偵測到 session 不存在時清除 localStorage 並顯示提示 |
| 15 | `_del_confirm_*` 狀態在各種導航路徑下殘留（後台首頁按鈕、登出、查看按鈕、歸檔返回） | 在所有導航入口加入 cleanup loop |
| 16 | `_del_arch_confirm_*` 在登出時未清除 | 同上 |
| 17 | admin 打開不同 session 的刪除確認框後，若在歸檔頁點「查看」，舊確認框殘留 | 「查看」按鈕加入 cleanup |
| 18 | reply_ver 的 textarea key 未含 sid，admin 在 session A 打字再切到 B，內容可能殘留 | key 改為 `reply_txt_{sid}_{reply_ver}` |
| 19 | 登出後 admin_pw session key 仍保留，下次進入管理入口密碼欄預填 | 登出時 `pop("admin_pw", None)` |
| 20 | 歸檔頁可同時開多個刪除確認對話框 | 點刪除前先清除所有其他 `_del_arch_confirm_*` |

### 空值 / None 防護

| # | 問題 | 修法 |
|---|------|------|
| 21 | `_html.escape(s["customer_name"])` 若欄位為 `null` 會 TypeError（後台列表、歸檔列表、回覆頁） | 全部加 `or "（未知）"` 保護 |
| 22 | admin 回覆頁 markdown 顯示 `sess["customer_name"]` 未加 None 防護 | 加 `or "（未知）"` |
| 23 | `init_state()` 與 `show_home()` lookup 設定 `customer_name` 時未加 None 防護 | 加 `or ""` |
| 24 | `show_chat()` 追加提問時 `send_notification(sess["customer_name"], ...)` 未加保護 | 加 `or ""` |
| 25 | admin 搜尋姓名時 `(s["customer_name"]).lower()` 若為 None 會 crash | 改 `(s["customer_name"] or "").lower()` |
| 26 | admin 姓氏分組排序時同上 | 改 `s["customer_name"] or ""` |

### UX 問題

| # | 問題 | 修法 |
|---|------|------|
| 27 | 顧客在「找不到諮詢記錄」錯誤頁沒有返回按鈕 | 加「← 返回首頁」按鈕 |
| 28 | admin 在「找不到問卦記錄」錯誤頁沒有返回按鈕 | 加「← 返回」按鈕 |
| 29 | admin 在 DB 斷線錯誤頁（show_admin_reply）只有重試，沒有返回按鈕 | 加「← 返回」按鈕 |
| 30 | 歸檔詳情頁的「刪除此記錄」是一鍵刪除，無確認對話框 | 改為兩步確認（與其他刪除路徑一致） |
| 31 | 查詢記錄時密碼欄空白點送出→靜默無反應 | 加「請輸入查詢密碼」錯誤提示 |
| 32 | admin 修改密碼：`new_pw2` 沒填也不提示空白欄位 | `not new_pw2` 也加入空白判斷 |
| 33 | admin 修改密碼驗證順序：在確認新密碼一致前就打 DB（浪費一次 API 呼叫） | 重排順序：空白→長度→一致性→核對舊密碼 |
| 34 | 查詢密碼太長會撐爆 chat-hdr 標題欄（admin 回覆頁） | 截至 40 字元後加 `…` |
| 35 | LINE token 未設定時，測試訊息按鈕仍可點（送出空 Bearer） | `disabled=not token` |
| 36 | 顧客送出問卦後 LINE 通知阻塞 UI 最多 10 秒才跳轉 | `st.success()` 移至通知前，timeout 降為 5 秒 |

### 資料完整性

| # | 問題 | 修法 |
|---|------|------|
| 37 | `add_message()` 失敗後 orphaned session 殘留在 DB（phone lookup 會找到空 session） | 加入失敗時 `delete_session(sid)` 清理 |

### 功能新增

| # | 功能 | 說明 |
|---|------|------|
| F1 | 查詢密碼找回 | admin 後台回覆頁顯示顧客的查詢密碼，方便協助找回；顧客端加「忘記密碼？請告知小老師姓名」提示 |

---

*共修復 37 個 bug，新增 1 項功能。*
