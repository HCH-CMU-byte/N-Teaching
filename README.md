# Neuro AI assistance self-learning
# N-Teaching 首頁自動更新：使用說明

## 這套東西做什麼

**以後你只要上傳（或更新）一個教學 HTML，首頁會自動：**
1. 多一張卡片（圖示、分類、標題、摘要、關鍵字），格式與你現在的卡片完全相同
2. 卡片自動放進正確的分類區塊，導覽列的下拉選單也一起更新
3. 如果「即將上線」裡有同名的規劃項目（例如 `parkinsons_disease.html`），上傳後它會自動從規劃中消失、換成正式卡片
4. 30 天內更新的頁面有 NEW 標記；首頁多了搜尋框；Hero 的「主題模組」數字自動計算
5. **所有教學頁面共用同一個「統一頁首」**（見下一節），新頁面一上傳就自動有，不會再有頁面少了回首頁的入口

首頁的版面、CSS、Hero 文字、Footer 都**不會被動到**，程式只改三個被標記圈起來的區塊。

## 統一頁首：解決「每頁頁首不一樣、有的沒有回首頁」

**原本的問題**：每個頁面都各自手寫一份導覽列，所以
- 新增頁面後，舊頁面的導覽列不會更新（例如 `ncs.html` 的導覽列連到不存在的 `headache.html`，點了是 404）
- 5 個頁面（DLB、癲癇與精神疾病、像癲癇不是癲癇、延髓三徵候、概似比教材）完全沒有回首頁的連結
- 新做的頁面用了另一套頁首

**現在的做法**：導覽列只在 `assets/site-header.js` 一個地方，由程式依你的分類資料自動產生；每個頁面 `<body>` 開頭只放這一行：

```html
<script src="assets/site-header.js"></script>
```

- 頁首內容與首頁導覽列一致（logo 連回首頁、首頁、各分類下拉選單、目前所在分類會亮起來）
- 捲動離開頁首後，左下角會出現「⌂ 首頁」浮動按鈕，所以頁面再長也一定能回去
- **新頁面不用自己做導覽列**：上傳後 Actions 會自動在它的 `<body>` 開頭補上那一行
- 以後新增或改名頁面，所有頁面的導覽列會一起更新，不需要逐頁修改
- 頁面自己的「頁內導覽」（例如 DLB 的章節標籤、癲癇頁的分頁標籤、概似比教材的上方工具列）不受影響，會保留在統一頁首下方
- 不想在某個頁面顯示統一頁首，加 `<meta name="nt:header" content="false">`
- 頁首是「跟著頁面捲走」，不是固定在視窗上方：因為有些頁面自己已有固定的頁內導覽，兩條都固定會互相蓋住。回首頁靠左下角的浮動按鈕補上

## 運作原理

```
你上傳 HTML ──▶ GitHub 自動執行 scripts/build_index.py ──▶ 重寫 index.html 裡標記之間的內容
                                                          ──▶ 存回 repo ──▶ GitHub Pages 重新發佈
```

每個頁面的資料來源（優先順序由高到低）：
1. 頁面 `<head>` 裡的 `<meta name="nt:...">`（新頁面用這個）
2. `index-data/overrides.json`（你現有的 9 個舊頁面，我已經把首頁現有的文字原樣放進去了，不用改舊頁面）
3. 自動擷取（標題、第一段文字）

## 一次性設定（約 10 分鐘）

**步驟 1：上傳檔案到 repo。** 在 GitHub 的 repo 頁面按 **Add file → Upload files**，拖入：

| 檔案／資料夾 | 說明 |
|---|---|
| `index.html` | **會取代你現在的首頁**。內容和現在的首頁一樣，只是多了標記與搜尋框（原本的版本在 GitHub 的歷史紀錄裡找得回來） |
| `scripts/` 資料夾 | 內含 `build_index.py` 與 `site-header.template.js` |
| `index-data/` 資料夾 | 內含 `categories.json`、`planned.json`、`overrides.json` |
| 所有 `.html` 頁面（共 12 個，不含首頁與 `ncs_firebase_ready.html`） | 已改成使用統一頁首：舊的手寫導覽列已移除，換成上面那一行。**只動頁首，頁面內容沒有任何改動**。若你在 2026-10-18 之後修改過其中某頁，請先備份再覆蓋，或告訴我重新產生 |
| `assets/` 資料夾 | 內含 `site-header.js`（統一頁首，之後由程式自動更新） |

**步驟 2：建立自動執行的設定檔。** 因為 `.github` 是隱藏資料夾，拖曳上傳常會漏掉，建議用網頁建立：
Add file → **Create new file** → 檔名欄位輸入 `.github/workflows/update-index.yml`（輸入斜線會自動建立資料夾）→ 貼上 zip 裡同名檔案的全部內容 → Commit。

**步驟 3：確認權限。** repo 的 Settings → Actions → General → Workflow permissions，選 **Read and write permissions** → Save。

**步驟 4：確認它跑起來。** 到 **Actions** 頁籤，點「自動更新首頁索引」→ **Run workflow**。變成綠色勾勾就完成（約 1 分鐘）。點進去可以看到每個頁面的檢查報告。

## 以後每次新增頁面

1. 在新頁面 `<head>` 裡（`<title>` 前面）貼上這幾行，改成該頁的內容（**不需要自己做導覽列**，統一頁首會自動補上）：

```html
<meta name="nt:category" content="dementia">
<meta name="nt:label" content="BPSD">
<meta name="nt:icon" content="💊">
<meta name="nt:summary" content="一兩句話的摘要，會顯示在卡片上。">
<meta name="nt:tags" content="BPSD, 藥物治療, 非藥物介入">
<meta name="nt:order" content="5">
<meta name="nt:updated" content="2026-10-18">
```

2. 上傳 HTML。
3. 等 1–3 分鐘，首頁就更新了（不需要碰 index.html）。

**欄位說明**

| 欄位 | 必填？ | 說明 |
|---|---|---|
| `nt:category` | 建議必填 | 分類代號，見下表。沒填會放進首頁最下方的「未分類」 |
| `nt:summary` | 建議 | 卡片上的說明。沒填會自動擷取頁面第一段文字 |
| `nt:label` | 選填 | 卡片上方的小標（英文短詞，例如 `DLB`）。沒填就空白 |
| `nt:icon` | 選填 | 卡片圖示 emoji，預設 📄 |
| `nt:tags` | 選填 | 關鍵字，用逗號分隔，卡片最多顯示 4 個，搜尋也會用到 |
| `nt:order` | 選填 | 同一分類裡的順序（數字小的在前），預設 100 |
| `nt:title` | 選填 | 卡片標題。沒填就用網頁 `<title>`（會自動去掉「｜HCH-FYH…」後綴） |
| `nt:status` | 選填 | 卡片左下角文字，預設「已上線」；例如「已上線 · 持續更新中」 |
| `nt:updated` | 選填 | 最後更新日期（YYYY-MM-DD）。沒填就用 GitHub 上最後一次修改日期（舊頁面的日期則記在 `overrides.json`） |
| `nt:replaces` | 選填 | 想讓某個「規劃中」項目消失時，填它的 id（見 `planned.json`） |
| `nt:hide` | 選填 | 填 `true` 就不放進首頁，也不會補統一頁首（例如純工具頁） |
| `nt:header` | 選填 | 填 `false` 代表這頁不要統一頁首 |

**分類代號：**`electro`（電生理）、`ultrasound`（神經超音波）、`headache`（頭痛）、`dementia`（失智症）、`epilepsy`（癲癇）、`cerebrovascular`（腦血管疾病）、`movement`（動作障礙）

## 常見操作

- **新增分類**：打開 `index-data/categories.json`，複製一段，改 `key`（英文小寫）、`label`（區塊標題）、`color`（`blue`／`teal`／`purple`／`amber`／`pink`／`red` 之一）、`nav`（導覽列短名）。分類出現的順序就是 json 裡的順序。
- **新增「即將上線」項目**：打開 `index-data/planned.json`，複製一段，改內容。`id` 填未來頁面的檔名，頁面上傳後它會自動消失。
- **修改舊頁面的卡片文字**：改 `index-data/overrides.json` 裡該檔名的欄位；或在該頁面加 `nt:` meta（meta 優先）。
- **目前在首頁「未分類」的兩個頁面**：`LR_teaching.html`、`ddx_bulbar dysfunction.html`。它們原本不在首頁。要歸類的話，加 meta，或在 `overrides.json` 加兩段；若需要新分類（例如「臨床推理」），先在 `categories.json` 新增。
- **`ncs_firebase_ready.html`**：已設定為不顯示（它是判讀工具，不是教學頁面）；想顯示就把 `overrides.json` 裡那段刪掉。

## 出問題時看哪裡

- **首頁沒更新**：Actions 頁籤看有沒有紅色叉叉，點進去看哪一步失敗。第 3 步的權限沒設會導致「存回 repo」失敗。
- **某個頁面沒有頁首**：Actions 紀錄會寫「已在 xxx 補上統一頁首」或「找不到 <body> 標籤」。頁面若把 `<body>` 寫成特殊形式才會找不到。
- **頁首位置怪怪的**：確認頁面沒有自己再做一條導覽列；若有，刪除它即可。
- **新頁面跑到「未分類」**：Actions 紀錄裡「更新首頁索引」那一步會寫原因（例如分類代號打錯字）。
- **提醒「標籤可能不對稱」**：該頁面 `<div>` 等標籤的開關數量不一致，建議檢查；只是提醒，不會擋住更新。
- **`index-data` 的 json 改壞了**：Actions 會顯示哪個檔案格式有誤（通常是少了逗號或引號）。
- 主要分支如果叫 `master`，把設定檔裡的 `main` 改成 `master`。
- 頁面如果放在子資料夾，打開 `scripts/build_index.py`，把 `SCAN_DIRS = ["."]` 改成 `[".", "pages"]`。

## 目前不會自動更新的地方

- `index.html`（首頁）的導覽列是由程式寫入首頁，與統一頁首內容一致；`ncs_firebase_ready.html`（判讀工具）沒有加統一頁首。
- Hero 的「互動病例」數字與「指引最新更新」年份：維持手動。

## 想在自己電腦先檢查（選用）

在 repo 資料夾執行 `python scripts/build_index.py --dry-run`，會列出每個頁面缺什麼資料，但不會改任何檔案。
