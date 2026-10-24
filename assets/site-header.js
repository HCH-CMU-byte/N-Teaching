/* ============================================================
   HCH-FYH Neurology 統一頁首（自動產生，請勿手動修改）
   - 來源範本：scripts/site-header.template.js
   - 產生程式：scripts/build_index.py（每次上傳頁面後由 GitHub Actions 自動重新產生）
   - 每個教學頁面只需要在 <body> 開頭放一行：
       <script src="assets/site-header.js"></script>
   功能：站台導覽列（與首頁一致、含下拉選單）、目前所在分類標示、
         捲動後出現的「回首頁」浮動按鈕。
   ============================================================ */
(function () {
  if (window.__ntHeader) return;
  window.__ntHeader = true;

  var DATA = {"cats":[{"key":"electro","nav":"神經傳導","items":[{"file":"ncs.html","title":"神經傳導檢查判讀"}],"planned":[],"menu":false},{"key":"ultrasound","nav":"神經超音波","items":[{"file":"neuro-ultrasound.html","title":"神經超音波檢查"}],"planned":[],"menu":false},{"key":"headache","nav":"頭痛","items":[{"file":"migraine_headache.html","title":"偏頭痛治療近五年進展"}],"planned":[],"menu":false},{"key":"dementia","nav":"失智症","items":[{"file":"dementia.html","title":"失智症總覽"},{"file":"neuroDG-classification_dementia.html","title":"神經退化性疾病：分類與診斷標準新進展"},{"file":"DLB_clinical_guide.html","title":"路易氏體失智症（DLB）"},{"file":"dementia_reversible.html","title":"可治療的失智類疾病"},{"file":"dementia-imaging-evidence-review.html","title":"輔助失智症診斷的影像研究：實證回顧與檢查選擇"},{"file":"ad_integrated_care.html","title":"阿茲海默症整合照護與藥物治療"},{"file":"bpsd_management.html","title":"跨失智症類型精神行為症狀（BPSD）管理"},{"file":"bpsd-refractory-tx_dementia.html","title":"BPSD 治療高原期：藥效不佳或副作用限制劑量時的下一步"},{"file":"anorexia_food_refusal.html","title":"食慾不振與拒食的鑑別與實證處置"},{"file":"ddx_bulbar dysfunction.html","title":"延髓三徵候的鑑別診斷"},{"file":"delirium-prognosis_dementia.html","title":"急性譫妄的預後評估、認知恢復指標與長期認知障礙"}],"planned":[],"menu":false},{"key":"epilepsy","nav":"癲癇","items":[{"file":"epilepsy_psychiatry.html","title":"癲癇與精神疾病"},{"file":"seizure_mimics.html","title":"像癲癇，不是癲癇"}],"planned":[],"menu":false},{"key":"cerebrovascular","nav":"腦血管疾病","items":[{"file":"stroke_progression.html","title":"惡化型腦中風／早期神經惡化（END）"},{"file":"cvt-evidence-update_stroke.html","title":"腦靜脈竇血栓（CVT）實證更新｜臨床・診斷・治療"}],"planned":[],"menu":false},{"key":"movement","nav":"動作障礙","items":[{"file":"movement_medication.html","title":"帕金森病用藥實證指南"},{"file":"uric-acid-nervous-system_PD.html","title":"尿酸與神經系統：從基礎機轉到臨床證據的實證回顧"}],"planned":[],"menu":false},{"key":"neuromuscular","nav":"神經肌肉","items":[{"file":"myasthenic-crisis.html","title":"肌無力危象治療流程（2026 實證更新）"},{"file":"recurrent-bulbar-mg.html","title":"肌無力危象血漿置換後復發性延髓功能障礙之處置"}],"planned":[],"menu":false},{"key":"other","nav":"其他教材","items":[{"file":"LR_teaching.html","title":"臨床概似比推理教材"}],"planned":[],"menu":true}],"other":[]};

  var script = document.currentScript;
  var src = (script && script.src) || '';
  var base = src ? src.replace(/assets\/site-header\.js[^]*$/, '') : '';
  var here = '';
  try { here = decodeURIComponent((location.pathname.split('/').pop()) || ''); } catch (e) { here = ''; }
  if (!here) here = 'index.html';

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function url(f) {
    if (f.charAt(0) === '#') return base + 'index.html' + f;
    return base + f.split('/').map(encodeURIComponent).join('/');
  }
  function isHere(f) { return f.split('/').pop() === here; }

  /* ---------- 樣式（全部加 nt- 前綴，避免和各頁面原本的 CSS 互相影響） ---------- */
  var css =
    '.nt-bar,.nt-bar *{box-sizing:border-box;margin:0;padding:0;line-height:1.4;letter-spacing:0;text-transform:none}' +
    '.nt-bar{position:relative;z-index:10000;background:#0d1117;border-bottom:1px solid rgba(255,255,255,.08);' +
      'font-family:"Noto Sans TC",-apple-system,"Segoe UI",sans-serif;font-size:14px;color:#8b949e;width:100%}' +
    '.nt-in{max-width:1180px;margin:0 auto;padding:0 20px;height:52px;display:flex;align-items:center;gap:6px}' +
    '.nt-bar a{text-decoration:none;color:#8b949e;font-weight:400;font-style:normal}' +
    '.nt-bar .nt-logo{font-family:"Noto Serif TC",serif;font-size:15px;font-weight:700;color:#58a6ff;margin-right:18px;white-space:nowrap;flex-shrink:0}' +
    '.nt-links{display:flex;align-items:center;gap:2px;flex-wrap:nowrap;min-width:0}' +
    '.nt-item{position:relative}' +
    '.nt-bar .nt-top{display:block;padding:7px 12px;border-radius:6px;font-size:14px;white-space:nowrap;transition:background .12s,color .12s}' +
    '.nt-bar .nt-top:hover,.nt-item:focus-within>.nt-top{background:#1c2128;color:#e6edf3}' +
    '.nt-bar .nt-top.nt-on{color:#58a6ff;background:rgba(88,166,255,.10)}' +
    '.nt-menu{display:none;position:absolute;top:100%;left:0;margin-top:2px;min-width:230px;background:#161b22;' +
      'border:1px solid rgba(255,255,255,.18);border-radius:8px;padding:6px;box-shadow:0 8px 28px rgba(0,0,0,.5)}' +
    '.nt-item:hover>.nt-menu,.nt-item:focus-within>.nt-menu,.nt-item.nt-open>.nt-menu{display:block}' +
    '.nt-bar .nt-menu a{display:block;padding:8px 14px;font-size:14px;border-radius:6px;white-space:nowrap}' +
    '.nt-bar .nt-menu a:hover{background:#1c2128;color:#e6edf3}' +
    '.nt-bar .nt-menu a.nt-cur{color:#58a6ff;background:rgba(88,166,255,.10)}' +
    '.nt-bar .nt-menu a.nt-soon{color:#6e7681;font-style:italic;pointer-events:none}' +
    '.nt-sep{height:1px;background:rgba(255,255,255,.08);margin:5px 4px}' +
    '.nt-burger{display:none;margin-left:auto;background:none;border:1px solid rgba(255,255,255,.18);color:#e6edf3;' +
      'border-radius:6px;padding:5px 10px;font-size:16px;cursor:pointer;font-family:inherit}' +
    '.nt-home{position:fixed;left:16px;bottom:16px;z-index:9990;display:flex;align-items:center;gap:6px;' +
      'background:#161b22;color:#e6edf3;border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:9px 15px 9px 12px;' +
      'font:500 13px "Noto Sans TC",-apple-system,sans-serif;text-decoration:none;box-shadow:0 6px 20px rgba(0,0,0,.35);' +
      'opacity:0;transform:translateY(8px);pointer-events:none;transition:opacity .18s,transform .18s}' +
    '.nt-home.nt-show{opacity:1;transform:none;pointer-events:auto}' +
    '.nt-home:hover{background:#1c2128;border-color:#58a6ff;color:#58a6ff}' +
    '@media (max-width:820px){' +
      '.nt-in{flex-wrap:wrap;height:auto;min-height:52px;padding:6px 14px}' +
      '.nt-burger{display:block}' +
      '.nt-links{display:none;width:100%;flex-direction:column;align-items:stretch;padding:6px 0 10px}' +
      '.nt-bar.nt-mobile-open .nt-links{display:flex}' +
      '.nt-menu{display:block;position:static;border:none;box-shadow:none;background:transparent;padding:0 0 4px 12px;margin:0}' +
      '.nt-bar .nt-menu a{padding:6px 12px;font-size:13px}' +
    '}' +
    '@media print{.nt-bar,.nt-home{display:none!important}}';

  /* ---------- 導覽列內容 ---------- */
  function build() {
    var html = '<div class="nt-in">' +
      '<a class="nt-logo" href="' + esc(url('index.html')) + '">⬡ HCH-FYH Neurology</a>' +
      '<button class="nt-burger" type="button" aria-label="開啟選單" aria-expanded="false">☰</button>' +
      '<div class="nt-links" role="navigation" aria-label="站台導覽">' +
      '<div class="nt-item"><a class="nt-top" href="' + esc(url('index.html')) + '">首頁</a></div>';

    (DATA.cats || []).forEach(function (c) {
      var live = c.items || [], plan = c.planned || [];
      if (!live.length && !plan.length) return;
      var on = live.some(function (p) { return isHere(p.file); });
      var nav = c.nav || c.label;
      if (live.length === 1 && !plan.length && !c.menu) {
        html += '<div class="nt-item"><a class="nt-top' + (on ? ' nt-on' : '') + '" href="' + esc(url(live[0].file)) + '">' + esc(nav) + '</a></div>';
        return;
      }
      var head = live.length ? url(live[0].file) : url('#cat-' + c.key);
      html += '<div class="nt-item"><a class="nt-top' + (on ? ' nt-on' : '') + '" href="' + esc(head) + '">' + esc(nav) + ' ▾</a><div class="nt-menu">';
      live.forEach(function (p) {
        html += '<a href="' + esc(url(p.file)) + '"' + (isHere(p.file) ? ' class="nt-cur" aria-current="page"' : '') + '>' + esc(p.title) + '</a>';
      });
      if (live.length && plan.length) html += '<div class="nt-sep"></div>';
      plan.forEach(function (p) { html += '<a class="nt-soon" href="#" tabindex="-1">' + esc(p.title) + '（整理中）</a>'; });
      html += '</div></div>';
    });

    var other = DATA.other || [];
    if (other.length) {
      var onO = other.some(function (p) { return isHere(p.file); });
      html += '<div class="nt-item"><a class="nt-top' + (onO ? ' nt-on' : '') + '" href="#" onclick="return false">未分類 ▾</a><div class="nt-menu">';
      other.forEach(function (p) {
        html += '<a href="' + esc(url(p.file)) + '"' + (isHere(p.file) ? ' class="nt-cur"' : '') + '>' + esc(p.title) + '</a>';
      });
      html += '</div></div>';
    }
    return html + '</div></div>';
  }

  function mount() {
    if (document.querySelector('.nt-bar')) return;
    var st = document.createElement('style');
    st.id = 'nt-bar-css';
    st.appendChild(document.createTextNode(css));
    (document.head || document.documentElement).appendChild(st);

    var bar = document.createElement('div');
    bar.className = 'nt-bar';
    bar.innerHTML = build();

    if (script && script.parentNode === document.body) {
      document.body.insertBefore(bar, script);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }

    /* 手機選單 */
    var burger = bar.querySelector('.nt-burger');
    burger.addEventListener('click', function () {
      var open = bar.classList.toggle('nt-mobile-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    /* 觸控裝置：點分類名稱展開／收合下拉（桌機用滑鼠移上去即可） */
    bar.querySelectorAll('.nt-item').forEach(function (it) {
      var top = it.querySelector('.nt-top');
      if (!it.querySelector('.nt-menu')) return;
      top.addEventListener('click', function (e) {
        if (window.matchMedia('(hover:none)').matches && !it.classList.contains('nt-open')) {
          e.preventDefault();
          bar.querySelectorAll('.nt-open').forEach(function (o) { o.classList.remove('nt-open'); });
          it.classList.add('nt-open');
        }
      });
    });
    document.addEventListener('click', function (e) {
      if (!bar.contains(e.target)) bar.querySelectorAll('.nt-open').forEach(function (o) { o.classList.remove('nt-open'); });
    });

    /* 浮動「回首頁」按鈕：捲動離開頁首後出現，確保任何位置都能回去 */
    var home = document.createElement('a');
    home.className = 'nt-home';
    home.href = url('index.html');
    home.setAttribute('aria-label', '回到首頁');
    home.innerHTML = '<span aria-hidden="true">⌂</span><span>首頁</span>';
    document.body.appendChild(home);
    function onScroll() {
      var past = bar.getBoundingClientRect().bottom < 0;
      home.classList.toggle('nt-show', past);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (script && script.parentNode === document.body && document.body) {
    mount();
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
