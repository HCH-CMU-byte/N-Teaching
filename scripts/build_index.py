#!/usr/bin/env python3
"""
N-Teaching 首頁自動更新程式
===========================
做什麼：掃描 repo 裡每一個教學頁面（.html），讀取頁面 <head> 的 <meta name="nt:...">，
        然後「重新產生」首頁 index.html 中被標記圈起來的三個區塊：
          1. 導覽列（含下拉選單）   <!-- NT:NAV:START --> ... <!-- NT:NAV:END -->
          2. 搜尋框 + 全部分類卡片   <!-- NT:SECTIONS:START --> ... <!-- NT:SECTIONS:END -->
          3. Hero 的「主題模組」數字 <!--NT:COUNT-->9<!--/NT:COUNT-->
        標記以外的內容（版面、CSS、Hero 文字、Footer）完全不會被動到。

資料來源（優先順序高 → 低）：
    頁面自己的 <meta name="nt:...">   >   index-data/overrides.json   >   自動擷取

只用 Python 內建功能，不需安裝任何東西。
GitHub Actions 會在你上傳檔案後自動執行；也可以在自己電腦執行：
    python scripts/build_index.py            # 更新 index.html
    python scripts/build_index.py --dry-run  # 只檢查、不改檔案
"""
import html as H
import json
import re
import subprocess
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

# ============ 設定區（需要時才改這裡） ============
SCAN_DIRS = ["."]                      # 掃描哪些資料夾；頁面放在子資料夾時加入，例如 [".", "pages"]
INDEX_FILE = Path("index.html")
DATA_DIR = Path("index-data")
EXCLUDE_FILES = {"index.html", "404.html"}
EXCLUDE_DIRS = {".git", ".github", "scripts", "index-data", "assets", "node_modules", "_site"}
DEFAULT_ICON = "📄"
DEFAULT_STATUS = "已上線"
SUMMARY_MAX = 110                      # 沒有手動摘要時，自動擷取的字數上限
NEW_DAYS = 30                          # 幾天內更新過的頁面顯示 NEW 標記
UNCATEGORIZED_LABEL = "未分類 · Uncategorized（請在頁面補上 nt:category）"
# ================================================

NAV_START, NAV_END = "<!-- NT:NAV:START -->", "<!-- NT:NAV:END -->"
SEC_START, SEC_END = "<!-- NT:SECTIONS:START -->", "<!-- NT:SECTIONS:END -->"
COUNT_RE = re.compile(r"<!--NT:COUNT-->.*?<!--/NT:COUNT-->", re.S)

esc = lambda s: H.escape(str(s), quote=True)


# ---------------------------------------------------------------- 讀頁面
class PageParser(HTMLParser):
    """取出 <title>、meta，以及第一段說明文字。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.lede, self.first_p = "", {}, "", ""
        self._in_title, self._skip, self._p = False, 0, None

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
            if text:
                if not self.lede and ("lede" in self._p["cls"] or "hero-sub" in self._p["cls"]
                                      or "section-intro" in self._p["cls"]):
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


def load_json(name, default):
    p = DATA_DIR / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("❌ %s 格式有誤（通常是少了逗號或引號）：%s" % (p, e))


def git_date(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             capture_output=True, text=True, check=False).stdout.strip()
        return out or None
    except Exception:
        return None


def tag_balance_warnings(text):
    clean = re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.S | re.I)
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
    return re.sub(r"\s*[|｜]\s*(N-Teaching|HCH-FYH).*$", "", t)


def find_pages():
    for d in SCAN_DIRS:
        for f in sorted(Path(d).rglob("*.html")):
            if set(f.parts) & EXCLUDE_DIRS or f.name in EXCLUDE_FILES or f.name.startswith("_"):
                continue
            yield f


def split_tags(v):
    if isinstance(v, list):
        return [str(t).strip() for t in v if str(t).strip()]
    return [t.strip() for t in re.split(r"[,，、]", v or "") if t.strip()]


def collect(cat_keys, overrides):
    pages, report = [], []
    for f in find_pages():
        text = f.read_text(encoding="utf-8", errors="replace")
        p = PageParser()
        p.feed(text)
        m = p.meta
        key = f.as_posix()
        ov = overrides.get(key, {}) if isinstance(overrides.get(key), dict) else {}

        if str(m.get("nt:hide", ov.get("hide", ""))).lower() in ("true", "1", "yes"):
            continue

        get = lambda field: m.get("nt:" + field) or ov.get(field)
        source = "meta" if m.get("nt:category") else ("overrides" if ov else "自動")
        notes = []

        cat = get("category") or ""
        if not cat:
            notes.append("沒有 nt:category → 放入「未分類」")
        elif cat not in cat_keys or cat == "soon":
            notes.append("分類代號「%s」不存在 → 放入「未分類」（可用的代號：%s）" %
                         (cat, "、".join(k for k in cat_keys if k != "soon")))
            cat = ""

        summary = get("summary") or ""
        if not summary:
            summary = shorten(m.get("description") or p.lede or p.first_p, SUMMARY_MAX)
            notes.append("沒有摘要 → 自動擷取：" + (summary[:28] + "…" if summary else "（找不到文字）"))

        updated = m.get("nt:updated") or git_date(f) or \
            datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        try:
            order = float(get("order")) if get("order") is not None else 100.0
        except ValueError:
            order = 100.0

        for w in tag_balance_warnings(text):
            notes.append("標籤可能不對稱：" + w)

        pages.append({
            "file": key,
            "category": cat,
            "title": get("title") or clean_title(p.title) or f.stem,
            "summary": summary,
            "icon": get("icon") or DEFAULT_ICON,
            "label": get("label") or "",
            "tags": split_tags(m.get("nt:tags") or ov.get("tags")),
            "status": get("status") or DEFAULT_STATUS,
            "order": order,
            "updated": updated,
            "replaces": m.get("nt:replaces", ""),
            "source": source,
        })
        report.append((key, source, notes))
    return pages, report


# ---------------------------------------------------------------- 產生 HTML
def href(file_):
    return quote(file_, safe="/#")


def is_new(updated):
    try:
        return (date.today() - datetime.strptime(updated, "%Y-%m-%d").date()).days <= NEW_DAYS
    except ValueError:
        return False


def card_live(pg, color, default_label):
    cls = "topic-card" + (" card-" + color if color else "")
    label = pg["label"] or default_label
    new = ' <span class="coming-badge" style="color:var(--teal);border-color:var(--teal-bd);">NEW</span>' \
        if is_new(pg["updated"]) else ""
    tags = ""
    if pg["tags"]:
        tags = '\n<div class="card-tags">' + "".join('<span class="tag">%s</span>' % esc(t)
                                                      for t in pg["tags"][:4]) + "</div>"
    search = " ".join([pg["title"], pg["summary"], label] + pg["tags"])
    return (
        '<a class="%s" href="%s" data-text="%s" title="最後更新：%s">\n'
        '<span class="card-icon">%s</span>\n'
        '<div class="card-category">%s%s</div>\n'
        '<div class="card-title">%s</div>\n'
        '<div class="card-desc">%s</div>%s\n'
        '<div class="card-footer"><span>%s</span><span class="arrow">→</span></div>\n'
        '</a>'
    ) % (cls, esc(href(pg["file"])), esc(search), esc(pg["updated"]), esc(pg["icon"]),
         esc(label), new, esc(pg["title"]), esc(pg["summary"]), tags, esc(pg["status"]))


def card_planned(pl, color):
    cls = "topic-card" + (" card-" + color if color else "") + " coming-soon"
    search = " ".join([pl["title"], pl.get("desc", ""), pl.get("label", "")])
    return (
        '<div class="%s" data-text="%s">\n'
        '<span class="card-icon">%s</span>\n'
        '<div class="card-category">%s</div>\n'
        '<div class="card-title">%s<span class="coming-badge">%s</span></div>\n'
        '<div class="card-desc">%s</div>\n'
        '<div class="card-footer"><span>規劃中</span></div>\n'
        '</div>'
    ) % (cls, esc(search), esc(pl.get("icon", "📝")), esc(pl.get("label", "")), esc(pl["title"]),
         esc(pl.get("badge", "規劃中")), esc(pl.get("desc", "")))


SEARCH_BLOCK = """<style>
.nt-search{max-width:880px;margin:36px auto 0;padding:0 24px;}
.nt-search input{width:100%;font:inherit;font-size:15px;padding:12px 16px;border-radius:10px;border:1px solid var(--border2);background:var(--bg2);color:var(--text);}
.nt-search input::placeholder{color:var(--text3);}
.nt-search input:focus{outline:2px solid var(--blue);outline-offset:1px;}
.nt-empty{display:none;max-width:880px;margin:40px auto;padding:0 24px;color:var(--text3);text-align:center;}
</style>
<div class="nt-search"><input id="ntSearch" type="search" placeholder="搜尋標題、摘要或關鍵字（例如：PET、BPSD、癲癇）" aria-label="搜尋教學頁面"></div>
<div class="nt-empty" id="ntEmpty">找不到符合的頁面，換個關鍵字試試。</div>"""

SEARCH_JS = """<script>
(function(){
  var input = document.getElementById('ntSearch');
  if(!input) return;
  var secs = document.querySelectorAll('.nt-section');
  input.addEventListener('input', function(){
    var q = input.value.trim().toLowerCase(), total = 0;
    secs.forEach(function(sec){
      var n = 0;
      sec.querySelectorAll('.topic-card').forEach(function(c){
        var ok = !q || (c.getAttribute('data-text') || '').toLowerCase().indexOf(q) > -1;
        c.style.display = ok ? '' : 'none'; if(ok) n++;
      });
      sec.style.display = n ? '' : 'none'; total += n;
    });
    document.getElementById('ntEmpty').style.display = total ? 'none' : 'block';
  });
})();
</script>"""


def build_nav(cats, live_by, planned_by):
    out = ['<a href="index.html" class="active">首頁</a>']
    for c in cats:
        if c.get("planned_only"):
            continue
        live, plan = live_by.get(c["key"], []), [p for p in planned_by.get(c["key"], []) if p.get("in_nav")]
        if not live and not plan:
            continue
        nav = c.get("nav") or c["label"]
        if len(live) == 1 and not plan:
            out.append('<a href="%s">%s</a>' % (esc(href(live[0]["file"])), esc(nav)))
            continue
        head = href(live[0]["file"]) if live else "#cat-" + c["key"]
        items = ['<a href="%s">%s</a>' % (esc(href(p["file"])), esc(p["title"])) for p in live]
        if live and plan:
            items.append('<div class="dropdown-divider"></div>')
        items += ['<a href="%s" class="disabled">%s（整理中）</a>' % (esc(p["id"] if p["id"].startswith("#")
                                                                      else "#" + p["id"] if "." not in p["id"] else p["id"]),
                                                                     esc(p["title"])) for p in plan]
        out.append('<div class="nav-dropdown">\n<a href="%s">%s</a>\n<div class="dropdown-menu">\n%s\n</div>\n</div>'
                   % (esc(head), esc(nav), "\n".join(items)))
    return "\n".join(out)


def build_sections(cats, live_by, planned_by, uncategorized):
    blocks = []

    def section(key, label, cards):
        blocks.append('<div class="nt-section">\n<div class="section-label" id="cat-%s"><span>%s</span></div>\n'
                      '<div class="card-grid">\n%s\n</div>\n</div>' % (key, esc(label), "\n\n".join(cards)))

    for c in cats:
        cards = [card_live(p, c["color"], "") for p in live_by.get(c["key"], [])]
        cards += [card_planned(p, p.get("color") or c["color"]) for p in planned_by.get(c["key"], [])]
        if cards:
            section(c["key"], c["label"], cards)
    if uncategorized:
        section("uncategorized", UNCATEGORIZED_LABEL, [card_live(p, "", "") for p in uncategorized])
    return SEARCH_BLOCK + "\n" + "\n".join(blocks) + "\n" + SEARCH_JS


def replace_block(text, start, end, new):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        sys.exit("❌ 在 %s 找不到標記 %s … %s。請確認首頁是使用附帶的 index.html（已含標記）。"
                 % (INDEX_FILE, start, end))
    return pat.sub(lambda m: start + "\n" + new + "\n" + end, text, count=1)


# ---------------------------------------------------------------- 主程式
def main():
    dry = "--dry-run" in sys.argv
    strict = "--strict" in sys.argv

    cats = load_json("categories.json", [])
    planned_all = load_json("planned.json", [])
    overrides = {k: v for k, v in load_json("overrides.json", {}).items() if not k.startswith("_")}
    if not cats:
        sys.exit("❌ 找不到 index-data/categories.json")
    cat_keys = [c["key"] for c in cats]

    pages, report = collect(cat_keys, overrides)
    pages.sort(key=lambda p: (p["order"], p["title"]))

    present = {p["file"] for p in pages} | {p["replaces"] for p in pages if p["replaces"]}
    planned = [p for p in planned_all if p["id"] not in present]
    gone = [p["title"] for p in planned_all if p["id"] in present]

    live_by, planned_by, uncategorized = {}, {}, []
    for p in pages:
        (live_by.setdefault(p["category"], []) if p["category"] else uncategorized).append(p)
    for p in planned:
        planned_by.setdefault(p["category"], []).append(p)

    if not INDEX_FILE.exists():
        sys.exit("❌ 找不到 %s（請在 repo 根目錄執行）" % INDEX_FILE)
    old = INDEX_FILE.read_text(encoding="utf-8")
    new = replace_block(old, NAV_START, NAV_END, build_nav(cats, live_by, planned_by))
    new = replace_block(new, SEC_START, SEC_END, build_sections(cats, live_by, planned_by, uncategorized))
    if not COUNT_RE.search(new):
        sys.exit("❌ 在 index.html 找不到 <!--NT:COUNT-->…<!--/NT:COUNT--> 標記")
    new = COUNT_RE.sub("<!--NT:COUNT-->%d<!--/NT:COUNT-->" % len(pages), new, count=1)

    changed = new != old
    if changed and not dry:
        INDEX_FILE.write_text(new, encoding="utf-8")

    # ---- 報告
    print("=" * 62)
    print("頁面 %d 個 ｜ 規劃中 %d 個 ｜ 未分類 %d 個 ｜ index.html：%s" %
          (len(pages), len(planned), len(uncategorized),
           ("（試跑，未寫入）會更新" if dry else "已更新") if changed else "沒有變動"))
    print("=" * 62)
    for title in gone:
        print("✔ 規劃中的「%s」已有對應頁面，自動從「即將上線」移除" % title)
    bad = 0
    for name, source, notes in report:
        print("  [%-9s] %s" % (source, name))
        for n in notes:
            bad += 1
            print("       ▲ " + n)
    for name in overrides:
        if not Path(name).exists() and not overrides[name].get("hide"):
            print("▲ overrides.json 內的 %s 在 repo 裡找不到檔案" % name)
    print("\n" + ("所有頁面的資料都完整。" if not bad else
                  "以上 ▲ 只是提醒，不會阻止網站更新；補上資料後下次就會變正確。"))
    if strict and bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
