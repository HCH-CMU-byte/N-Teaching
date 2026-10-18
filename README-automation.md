# N-Teaching 自動更新索引：使用說明

## 這套東西做什麼

**以後你只要上傳（或更新）一個教學 HTML，首頁就會自動：**
1. 多一張可點選的摘要卡片（圖示、分類、標題、摘要、關鍵字、更新日期）
2. 卡片自動放進正確的分類區塊
3. 出現在「最近更新」，30 天內的頁面會有 NEW 標記
4. 可以被搜尋、被分類按鈕篩選

你不用再手動改首頁。

## 運作原理（三步，不需要看懂程式）

```
你上傳 HTML ──▶ GitHub 自動執行 build_index.py ──▶ 產生 _data/pages.json
                                                        │
首頁的 {% include page-index.html %} 讀取這份資料 ◀──────┘
```

`build_index.py` 會讀每個頁面最上方的 5 行「身分證」（meta 標籤），所以**每個新頁面只要多貼這 5 行**。

## 一次性設定（只做一次，約 10 分鐘）

**步驟 1：放檔案。** 把這個資料夾裡的檔案放進你的 repo，位置要一樣：

| 檔案 | 放在哪裡 |
|---|---|
| `scripts/build_index.py` | repo 的 `scripts/` 資料夾 |
| `_includes/page-index.html` | `_includes/` 資料夾 |
| `_includes/nt-card.html` | `_includes/` 資料夾 |
| `_data/categories.yml` | `_data/` 資料夾（和你的 nav.yml 同一層） |
| `.github/workflows/pages.yml` | `.github/workflows/` 資料夾 |
| `_config.snippet.yml` 的內容 | 貼進你現有的 `_config.yml` |

> 在 GitHub 網頁上建立資料夾的方法：按 Add file → Create new file，檔名欄位輸入 `scripts/build_index.py`（輸入斜線就會自動建立資料夾），再貼上內容。

**步驟 2：改 Pages 設定。** 到 repo 的 Settings → Pages → **Build and deployment → Source**，選 **GitHub Actions**。
（原本是「Deploy from a branch」。改了之後，網站改由上面的 `pages.yml` 發佈，這樣索引資料才能每次自動更新。）

**步驟 3：在首頁放索引。** 打開 `index.html`：
- 確認檔案**最上面**有這兩行（沒有的話加上去）：
  ```
  ---
  ---
  ```
- 在你想顯示索引的位置貼上這一行：
  ```
  {% include page-index.html %}
  ```
  原本手動寫的卡片可以刪掉。

**步驟 4：確認。** 到 repo 的 **Actions** 頁籤，應該會看到一個「建置並發佈 N-Teaching」正在跑；變成綠色勾勾（約 1–3 分鐘）就完成了。

## 以後每次新增頁面

1. 在新頁面 `<head>` 裡（`<title>` 前面）貼上這 5 行，改成該頁的內容：

```html
<meta name="nt:category" content="dementia">
<meta name="nt:summary" content="一兩句話的摘要，會顯示在卡片上。">
<meta name="nt:icon" content="🧠">
<meta name="nt:tags" content="PET, DLB, 影像">
<meta name="nt:updated" content="2026-10-18">
```

2. 上傳 HTML（或更新既有的檔案）。
3. 等 1–3 分鐘，首頁就更新了。

**分類代號**（`nt:category` 要填這些之一）：`dementia`、`stroke`、`movement`、`neuromuscular`、`epilepsy`、`tools`。
要新增分類：打開 `_data/categories.yml`，複製一段，改 `key`、`name`、`color` 即可。

**有些欄位忘了填也沒關係：**
- 沒填 `nt:category` → 放進「未分類」區塊，之後補上就會歸位
- 沒填 `nt:summary` → 自動擷取頁面第一段說明文字
- 沒填 `nt:updated` → 用檔案最後一次上傳的日期
- 想讓某個頁面不出現在索引 → 加 `<meta name="nt:hide" content="true">`

## 出問題時看哪裡

- **首頁沒更新**：Actions 頁籤看有沒有紅色叉叉；點進去看哪一步失敗。
- **新頁面跑到「未分類」**：Actions 紀錄裡的「產生索引資料」那一步會寫原因（例如分類代號打錯字）。
- **提醒「標籤可能不對稱」**：該頁面有 `<div>` 等標籤開關數量不一致，建議檢查；這只是提醒，不會擋住網站發佈。
- 主要分支如果叫 `master`，把 `pages.yml` 裡的 `main` 改成 `master`。
- 頁面如果放在子資料夾（例如 `pages/`），打開 `scripts/build_index.py`，把 `SCAN_DIRS = ["."]` 改成 `SCAN_DIRS = ["pages"]`（或 `[".", "pages"]`）。

## 想在自己電腦先檢查（選用）

在 repo 資料夾執行 `python scripts/build_index.py`，會列出每個頁面缺什麼資料。
