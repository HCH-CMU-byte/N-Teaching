#!/usr/bin/env python3
"""
N-Teaching 索引產生器
=====================
做什麼：掃描網站裡的每一個教學頁面（.html），讀取頁面 <head> 裡的
        <meta name="nt:..."> 資料，整理成 _data/pages.json。
        首頁的索引（卡片方格）會自動讀這個檔案，所以你只要上傳新頁面，
        索引就會跟著更新。

這個程式只用 Python 內建功能，不需要安裝任何東西。
GitHub Actions 會在每次你上傳檔案後自動執行它；你也可以在自己電腦上執行：
    python scripts/build_index.py
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

# ============ 設定區（需要時才改這裡） ============
SCAN_DIRS = ["."]                       # 要掃描的資料夾；"." = 網站根目錄。頁面放在子資料夾就加進來，例如 ["." , "pages"]
EXCLUDE_FILES = {"index.html", "404.html"}
EXCLUDE_DIRS = {"_site", "_layouts", "_includes", "_data", ".github", ".git",
                "assets", "node_modules", "scripts", "vendor"}
DEFAULT_CATEGORY = "uncategorized"      # 沒填分類，或分類代號不在 categories.yml 時，會放進「未分類」
DEFAULT_ICON = "📄"
SUMMARY_MAX = 110                       # 沒有手動摘要時，自動擷取的字數上限
OUTPUT = "_data/pages.json"
CATEGORIES_FILE = "_data/categories.yml"
# ================================================


class PageParser(HTMLParser):
    """從一個 HTML 檔案取出標題、meta 資料，以及第一段說明文字。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.lede = ""
        self.first_p = ""
        self._in_title = False
        self._skip = 0          # 在 <script>/<style> 裡面時不收文字
        self._p = None          # 目前正在收集的 <p>

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag in ("script", "style"):
            self._skip += 1
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key and "content" in a:
                self.meta[key.strip().lower()] = (a["content"] or "").strip()
        elif tag == "p" and self._p is None:
            self._p = {"cls": a.get("class", ""), "text": ""}

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag == "p" and self._p is not None:
            text = re.sub(r"\s+", " ", self._p["text"]).strip()
            cls = self._p["cls"]
            if text:
                if not self.lede and ("lede" in cls or "section-intro" in cls):
                    self.lede = text
                if not self.first_p and len(text) >= 20:
                    self.first_p = text
            self._p = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        elif self._p is not None:
            self._p["text"] += data


def read_category_keys():
    """從 categories.yml 取出所有分類代號（不需要 YAML 套件）。"""
    p = Path(CATEGORIES_FILE)
    if not p.exists():
        return []
    return re.findall(r"^\s*-\s*key:\s*([A-Za-z0-9_-]+)", p.read_text(encoding="utf-8"), re.M)


def git_date(path):
    """用 git 取得檔案最後一次修改日期；失敗就回傳 None。"""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             capture_output=True, text=True, check=False).stdout.strip()
        return out or None
    except Exception:
        return None


def tag_balance_warnings(html):
    """簡易檢查：主要區塊標籤的開關數量是否一致（略過 script/style/註解）。"""
    clean = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.S)
    warns = []
    for tag in ("div", "section", "main", "nav", "header", "footer", "ul", "ol", "table", "svg"):
        o = len(re.findall(r"<%s[\s>]" % tag, clean, flags=re.I))
        c = len(re.findall(r"</%s>" % tag, clean, flags=re.I))
        if o != c:
            warns.append("<%s> 開 %d 次、關 %d 次" % (tag, o, c))
    return warns


def shorten(text, limit):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip("，、；：, ") + "…"


def clean_title(t):
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s*[|｜]\s*N-Teaching.*$", "", t)


def find_pages():
    seen = set()
    for d in SCAN_DIRS:
        base = Path(d)
        for f in sorted(base.rglob("*.html")):
            parts = set(f.parts)
            if parts & EXCLUDE_DIRS or f.name in EXCLUDE_FILES or f.name.startswith("_"):
                continue
            if f not in seen:
                seen.add(f)
                yield f


def main():
    strict = "--strict" in sys.argv
    cat_keys = read_category_keys()
    pages, problems = [], []

    for f in find_pages():
        html = f.read_text(encoding="utf-8", errors="replace")
        p = PageParser()
        p.feed(html)
        m = p.meta

        if m.get("nt:hide", "").lower() in ("true", "1", "yes"):
            continue

        notes = []
        raw_cat = m.get("nt:category", "").strip()
        cat = raw_cat
        if not raw_cat:
            notes.append("沒有填 nt:category → 放入「未分類」")
            cat = DEFAULT_CATEGORY
        elif cat_keys and raw_cat not in cat_keys:
            notes.append("分類代號「%s」不在 categories.yml → 放入「未分類」" % raw_cat)
            cat = DEFAULT_CATEGORY

        summary = m.get("nt:summary") or ""
        if not summary:
            summary = shorten(m.get("description") or p.lede or p.first_p, SUMMARY_MAX)
            notes.append("沒有填 nt:summary → 自動擷取：" + (summary[:30] + "…" if summary else "（找不到文字）"))

        title = clean_title(m.get("nt:title") or p.title) or f.stem
        updated = m.get("nt:updated") or git_date(f) or \
            datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        tags = [t.strip() for t in re.split(r"[,，、]", m.get("nt:tags", "")) if t.strip()]

        for w in tag_balance_warnings(html):
            notes.append("標籤可能不對稱：" + w)

        pages.append({
            "file": f.as_posix(),
            "title": title,
            "summary": summary,
            "category": cat,
            "icon": m.get("nt:icon") or DEFAULT_ICON,
            "tags": tags,
            "updated": updated,
        })
        problems.append((f.as_posix(), notes))

    pages.sort(key=lambda x: (x["updated"], x["title"]), reverse=True)

    out = Path(OUTPUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("=" * 60)
    print("索引已更新：共 %d 個頁面 → %s" % (len(pages), OUTPUT))
    print("=" * 60)
    bad = 0
    for name, notes in problems:
        if notes:
            bad += 1
            print("\n▲ " + name)
            for n in notes:
                print("    - " + n)
    if not bad:
        print("所有頁面的資料都完整。")
    else:
        print("\n（以上提醒不會阻止網站更新；補上 meta 資料後下次就會變正確。）")
    if strict and bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
