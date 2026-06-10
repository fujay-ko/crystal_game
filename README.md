# 💎 水晶遊戲 Crystal Game

> 一款以 Python 程式控制角色、收集地圖上所有水晶的教學用益智遊戲。
> 專為初學者設計，透過實際撰寫程式碼來學習 Python 基礎語法。

---

## 🎮 遊戲介紹

玩家需要透過撰寫 Python 程式碼，控制地圖上的角色移動，依序收集 5 顆不同顏色的水晶（紅、橙、綠、藍、黑）。每一關對應一顆水晶，難度逐漸提升，引導學生學習從基本移動、轉彎、迴圈到條件判斷等程式概念。

### 教學目標

| 關卡 | 水晶顏色 | 學習概念 |
|------|----------|----------|
| 第一關 | 🔴 紅色 | 基本移動指令 |
| 第二關 | 🟠 橙色 | 轉彎操作 |
| 第三關 | 🟢 綠色 | `for` 迴圈 |
| 第四關 | 🔵 藍色 | `if-else` 條件判斷 |
| 第五關 | ⚫ 黑色 | 綜合挑戰 |

---

## 🗂️ 專案結構

```
crystal_game-main/
│
├── main.py               # 學生練習區（主要修改這個檔案）
├── game_lib.py           # 遊戲核心引擎（請勿修改）
├── index.html            # 網頁版遊戲（使用 Skulpt 在瀏覽器執行）
├── download_deps.py      # 自動下載網頁版所需函式庫
├── start_web.bat         # Windows 一鍵啟動網頁版腳本
│
├── js/                   # 網頁版 JS 模組
│   ├── constants.js      #   常數、關卡設定、LAYOUT 座標
│   ├── utils.js          #   工具函式（clone、delay、log）
│   ├── state.js          #   遊戲狀態管理（g_*/d_*）
│   ├── assets.js         #   圖片與音效載入
│   ├── renderer.js       #   Canvas 繪圖
│   ├── animation.js      #   動畫系統（rAF 驅動）
│   └── ui.js             #   CodeMirror、Skulpt 橋接、UI 事件
│
├── lib/                  # 網頁版前端函式庫
│   ├── skulpt.min.js         # Skulpt Python 直譯器
│   ├── skulpt-stdlib.js      # Skulpt 標準函式庫
│   ├── codemirror.min.js     # 程式碼編輯器
│   ├── codemirror.min.css    # 編輯器樣式
│   ├── dracula.min.css       # 編輯器 Dracula 主題
│   └── python.min.js         # CodeMirror Python 語法高亮
│
└── material/             # 遊戲素材（圖片、音效）
    ├── bg_*.png              # 背景圖
    ├── wall_*.png            # 牆壁圖塊
    ├── road_*.png            # 道路圖塊
    ├── crystal_*.png         # 水晶圖示（紅/橙/綠/藍/黑）
    ├── mc*.png               # 角色（四個方向）
    ├── arrow*.png            # 方向箭頭
    ├── m1~m5.png             # 關卡提示地圖圖片
    ├── victory.png / defeat.png  # 勝利/失敗畫面
    └── *.mp3                 # 音效（取得水晶、碰牆、勝利、失敗）
```

---

## 🚀 執行方式

### 方式一：桌面版（使用 pygame）

**環境需求：**
- Python 3.x
- pygame 套件

**安裝 pygame：**
```bash
pip install pygame
```

**啟動遊戲：**
```bash
python main.py
```

**桌面版快捷操作：**
- `M` 鍵 — 切換靜音
- `ESC` 鍵 — 返回主選單／離開遊戲

---

### 方式二：網頁版（使用瀏覽器）

不需要安裝 Python 或 pygame，直接在瀏覽器中執行。

**步驟 1：下載前端函式庫（首次使用）**
```bash
python download_deps.py
```

**步驟 2：啟動本地伺服器**

- **Windows**：直接雙擊 `start_web.bat`
- **macOS / Linux**：
  ```bash
  python -m http.server 8000
  ```

**步驟 3：開啟瀏覽器，前往**
```
http://localhost:8000/index.html
```

**網頁版快捷操作：**
- `Ctrl+Enter` 或 `F5` — 執行程式
- 新手首次使用會自動顯示操作導覽

---

## ✏️ 如何撰寫程式

開啟 `main.py`，在各關卡的函式中填入你的程式碼。

### 可用指令

| 指令 | 說明 |
|------|------|
| `move_forward()` | 角色向前走一格 |
| `turn_left()` | 角色向左轉（原地轉向） |
| `turn_right()` | 角色向右轉（原地轉向） |
| `get_crystal()` | 取得腳下的水晶（沒有水晶則失敗） |
| `is_forward_path()` | 感測器：前方是否有路（`1` = 有路，`0` = 牆壁） |
| `reach_crystal()` | 感測器：是否站在水晶位置（`True` / `False`） |

### 範例程式碼

```python
def stage1():
    """第一關：走到紅色水晶並取得它"""
    move_forward()
    get_crystal()

def stage3():
    """第三關：用 for 迴圈走多步"""
    for i in range(3):
        move_forward()
    get_crystal()

def stage4():
    """第四關：用條件判斷自動轉彎"""
    while not reach_crystal():
        if is_forward_path():
            move_forward()
        else:
            turn_right()
    get_crystal()
```

---

## 🗺️ 地圖說明

遊戲地圖為 8×8 的格子，`0` 代表牆壁，`1` 代表可行走的道路。

```
0 0 0 0 0 0 0 0
0 1 1 1 1 1 1 0
0 1 0 0 0 0 0 0
0 1 0 1 1 1 1 0
0 1 0 1 [角色] 1 0   ← 角色起始位置 (第4列, 第3行)，面朝上
0 1 0 0 0 0 1 0
0 1 1 1 1 1 1 0
0 0 0 0 0 0 0 0
```

角色起始位置：第 4 列、第 3 行，面朝**上（北）**。

---

## 🛡️ 防護機制

### 無限迴圈防護（桌面版）
- 每個遊戲指令（移動、轉彎、收集）都有計數器
- 超過 500 個指令自動中斷，顯示「指令數量過多」提示
- 按 `R` 重新開始或 `Q` 離開

### 無限迴圈防護（網頁版）
- 每個 Skulpt 指令都有步驟計數，上限 200 步
- 執行超過 20 秒自動逾時中斷
- 學生可以放心嘗試不同寫法

---

## 🎯 新功能

| 功能 | 桌面版 | 網頁版 |
|------|:------:|:------:|
| 指令計數器 | ✅ 過關時顯示 | ✅ 執行完顯示 |
| 音效開關 | ✅ `M` 鍵切換 | ✅ 按鈕切換 |
| 單關重置 | ✅ 重新編輯即可 | ✅ 按鈕恢復範本 |
| 新手導覽 | — | ✅ 首次使用引導 |
| 進度記憶 | — | ✅ localStorage 自動儲存 |
| 響應式佈局 | — | ✅ 支援手機平板 |

---

## 📁 兩種版本的差異

| | 桌面版（`main.py` + `game_lib.py`） | 網頁版（`index.html`） |
|---|---|---|
| 執行環境 | Python + pygame | 瀏覽器（不需安裝） |
| 程式碼編輯 | 使用文字編輯器修改 `main.py` | 內建 CodeMirror 編輯器 |
| Python 引擎 | 原生 CPython | Skulpt（瀏覽器內 Python） |
| 適合對象 | 有安裝 Python 環境的學生 | 快速體驗、課堂示範 |
