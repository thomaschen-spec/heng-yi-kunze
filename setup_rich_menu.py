"""
執行方式：
  pip install Pillow requests
  python setup_rich_menu.py

需要輸入你的 LINE Channel Access Token（LINE Developers Console 取得）
"""
import os, struct, zlib, sys
import requests

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("請先安裝 Pillow：pip install Pillow")
    sys.exit(1)

# ── 設定 ──────────────────────────────────────────────────────────────────────
TOKEN = input("請貼上 LINE Channel Access Token：").strip()

CELLS = [
    ("統計", "📊", "今日 / 進行 / 歸檔"),
    ("待辦", "📋", "待回覆清單"),
    ("說明", "❓", "指令一覽"),
]

W, H = 2500, 843
BG   = (22, 40, 22)       # 深林綠
DIV  = (55, 85, 45)        # 分隔線
TEXT = (200, 220, 140)     # 嫩綠文字
SUB  = (140, 165, 90)      # 副標題色
ICON_BG = (35, 65, 35)     # 圖示背景

# ── 產生圖片 ──────────────────────────────────────────────────────────────────
img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# 分隔線
for x in [833, 1667]:
    draw.rectangle([x - 1, 0, x + 1, H], fill=DIV)

# 嘗試載入中文字型
font_paths = [
    "C:/Windows/Fonts/msjhbd.ttc",   # Windows 微軟正黑體 Bold
    "C:/Windows/Fonts/msjh.ttc",
    "C:/Windows/Fonts/kaiu.ttf",
    "/System/Library/Fonts/PingFang.ttc",             # macOS
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",  # Linux
]
font_big = font_small = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font_big   = ImageFont.truetype(fp, 130)
            font_mid   = ImageFont.truetype(fp, 75)
            font_small = ImageFont.truetype(fp, 55)
            print(f"使用字型：{fp}")
            break
        except Exception:
            pass

if font_big is None:
    print("⚠ 找不到中文字型，使用預設字型（文字可能不完整）")
    font_big   = ImageFont.load_default()
    font_mid   = font_big
    font_small = font_big

cell_w = W // 3
for i, (label, icon, sub) in enumerate(CELLS):
    cx = cell_w * i + cell_w // 2

    # 圓形背景
    r = 100
    draw.ellipse([cx - r, H//2 - 160 - r, cx + r, H//2 - 160 + r], fill=ICON_BG)

    # 圖示
    draw.text((cx, H//2 - 160), icon, fill=TEXT, font=font_mid, anchor="mm")

    # 主標題
    draw.text((cx, H//2 + 20), label, fill=TEXT, font=font_big, anchor="mm")

    # 副標題
    draw.text((cx, H//2 + 175), sub, fill=SUB, font=font_small, anchor="mm")

out_path = "rich_menu_bg.png"
img.save(out_path, "PNG")
print(f"圖片已建立：{out_path}")

# ── 建立 Rich Menu ────────────────────────────────────────────────────────────
headers_json = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

menu_body = {
    "size": {"width": 2500, "height": 843},
    "selected": True,
    "name": "Admin Quick Menu",
    "chatBarText": "📋 管理選單（點開）",
    "areas": [
        {
            "bounds": {"x": 0,    "y": 0, "width": 833,  "height": 843},
            "action": {"type": "message", "text": "統計"},
        },
        {
            "bounds": {"x": 833,  "y": 0, "width": 834,  "height": 843},
            "action": {"type": "message", "text": "待辦"},
        },
        {
            "bounds": {"x": 1667, "y": 0, "width": 833,  "height": 843},
            "action": {"type": "message", "text": "說明"},
        },
    ],
}

r1 = requests.post("https://api.line.me/v2/bot/richmenu", json=menu_body, headers=headers_json)
if r1.status_code != 200:
    print(f"❌ 建立選單失敗：{r1.text}")
    sys.exit(1)

menu_id = r1.json()["richMenuId"]
print(f"✅ 選單建立：{menu_id}")

# 上傳圖片
with open(out_path, "rb") as f:
    r2 = requests.post(
        f"https://api-data.line.me/v2/bot/richmenu/{menu_id}/content",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "image/png"},
        data=f.read(),
    )
if r2.status_code != 200:
    print(f"❌ 上傳圖片失敗：{r2.text}")
    sys.exit(1)
print("✅ 圖片上傳完成")

# 設為所有使用者預設
r3 = requests.post(
    f"https://api.line.me/v2/bot/user/all/richmenu/{menu_id}",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
if r3.status_code != 200:
    print(f"❌ 設定預設失敗：{r3.text}")
    sys.exit(1)

print("✅ 已設為預設圖文選單，馬上生效！")
print(f"\n選單 ID（備用）：{menu_id}")
