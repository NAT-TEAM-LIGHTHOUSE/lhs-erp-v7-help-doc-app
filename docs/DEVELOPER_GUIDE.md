# Lighthouse ERP V7 Help Centre — Developer & Maintenance Guide

> **Repository note.** This guide was written for the stand-alone deploy folder `D:\LHS_ERP_HELP_V7_DEPLOY`. In the Git repository
> `lhs-erp-v7-help-doc-app` that folder is the sub-folder **`webapp/`** (so `js\app.js` is `webapp\js\app.js`, `tools\update_now.bat` is
> `webapp\tools\update_now.bat`). Everything about *how the application works* (features, architecture, content naming rules, source walkthrough,
> Reader rules, recipes) is unchanged. For **deployment, releases, environments (DEV / UAT / PROD), maintenance and the technology list** use the newer
> documents: [DEPLOYMENT.md](DEPLOYMENT.md), [RELEASE_PROCESS.md](RELEASE_PROCESS.md), [MAINTENANCE.md](MAINTENANCE.md), [TECH_STACK.md](TECH_STACK.md).
> The cache-busting number is now set with `scripts/set_version.py` (§6.3 below describes the manual way). Where this guide and those documents differ, they win.

| | |
|---|---|
| **Product** | Lighthouse ERP V7 Help Centre (web application) |
| **Web build** | 7.0.32 (cache-busting number in `layout.html`) |
| **Content build** | 332 PDFs · 9 modules · 58 groups · generated 2026-10-27 |
| **Live URL (current)** | `http://192.168.100.21:8888/LHS_ERP_HELP/layout.html` |
| **Deploy folder (master copy)** | `D:\LHS_ERP_HELP_V7_DEPLOY` |
| **V7 PDF source folder** | `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC` |
| **Previous version (untouched)** | `D:\LHS_ERP_HELP` (V5 app) |
| **Technology** | Static HTML + CSS + vanilla JavaScript (no framework, no database, no server-side code) |

---

## 1. What the application does

The Help Centre shows the Lighthouse ERP V7 user-guide PDFs in a browser. A tree menu on the left is **built automatically from the folder names and file names** of the V7 documentation folder; clicking a menu item opens that document on the right, either as the original PDF or as an automatically formatted web page ("Reader" view).

It is a **static website**: everything is plain files that Tomcat (or any web server) serves. There is nothing to compile and no restart is needed after changes.

---

## 2. Complete feature list

### 2.1 Navigation and menu
- **Three-tab side menu**: *Modules* (V7 documents), *Guide* (overview and support topics), *Saved* (favourites and recently viewed).
- **Menu built from the folder tree**: Module → Group → Document, with the menu code shown for every item (`06`, `06.03`, `06.03.01.02`).
- **Menu codes shown as badges**, clear font, vertically aligned with the folder icon; titles always on a single line; the pane is wide enough (500 px, resizable up to 760 px) for the longest title.
- **Document counts** on every folder; groups with no PDF yet are dimmed and marked *Coming soon*.
- **Lazy-rendered tree** (fast with 300+ documents), **expand / collapse all**, **locate open document** (reveal in tree).
- **Keyboard navigation** in the tree (↑ ↓ ← → Home End Enter).
- **Resizable and collapsible side pane**; the width is remembered per browser.
- **Narrow screens**: the menu becomes a slide-over panel and opens by default on the home page.
- **Breadcrumbs** above every document; **Previous / Next document** arrows.
- **Deep links**: every document has its own URL (`#modules/<code>`, `#guide/<id>`); the browser Back / Forward buttons work.
- **Home page**: hero banner, module cards with group cards, document statistics, favourites and recently viewed.

### 2.2 Search
- **Global search box** (Ctrl+K or `/`): searches menu code, title and parent folder names, ranks exact code matches first, highlights matches, keyboard selectable.

### 2.3 Document viewing
- **Built-in PDF viewer** (PDF.js): light theme matching the application, page-number box, previous / next page, zoom in / out, *Fit width*, Ctrl + mouse-wheel zoom, selectable / copyable text, pages drawn only when scrolled to (fast with large PDFs). Falls back automatically to the browser's own viewer if a PDF cannot be opened. Switchable with `ui.viewer` in the properties file.
- **Reader view (HTML)**: every PDF is converted automatically, by fixed rules, into a clean responsive web page: section headings, numbered *Step* cards, bullet / numbered lists, tables, call-out boxes for Note / Remark / Example, compressed screenshots (click to enlarge, red annotation marks preserved), and an **"On this page"** outline with scroll tracking. Dark-mode aware, printable.
- **PDF | Reader switch** above each document; the choice is remembered.
- **"Document not available" page**: if a PDF is missing on the server (HTTP error, or an error web page returned instead of a PDF) a friendly page appears with *Back to group* and *Home* buttons — for every module document and every Guide topic.
- **Copy page for AI**: dropdown with *Copy page for AI* (clean Markdown of the open document), *Open in ChatGPT* and *Open in Claude* (opens a new chat with only "Read from <link to the page's Markdown copy> so I can ask questions about it" plus a one-line description; the full text is not pasted).
- **Copy link**, **Print**, **Download PDF**, **Save to favourites** (star).

### 2.4 Personalisation and look
- **Light / dark theme** (remembers the choice; follows the operating-system setting on first visit).
- **Favourites and Recently viewed** (stored in the browser).
- **Keyboard-shortcuts help** dialog.
- Fully responsive (desktop, tablet, phone), accessible (skip link, ARIA roles, visible focus), print stylesheet.

### 2.5 Administration without programming
- **Feature flags** in `config/app.properties`: each of Copy link, Print, Download, Save, Copy page for AI, PDF|Reader switch and Previous/Next can be switched on / off; also the choice of PDF viewer.
- **Automatic content update**: paste PDFs into the V7 folder, run `update_now.bat` (or leave `auto_update.bat` running) — menu, PDF copies and Reader pages are rebuilt for new / changed files only. No manual editing.
- **Reports** (CSV) listing documents that need attention, coverage per group and every indexed document.
- **Per-document isolation**: a PDF that crashes the converter only loses its own Reader page; it still opens as a PDF.

---

## 3. Architecture

```
 ┌──────────────── PC that maintains content ────────────────┐         ┌──────── Tomcat server ────────┐
 │  V7_MENU_HELP_DOC\  (the PDFs, organised in folders)       │         │ webapps\LHS_ERP_HELP\          │
 │            │                                               │  copy   │   layout.html  css\  js\       │
 │   tools\build_v7.py  ──► docs\  +  menu\v7-menu.json       │ ──────► │   config\  images\  vendor\    │
 │   tools\build_html.py ─► html\  (+ html\_img\*.webp)       │         │   docs\  html\  menu\  guide\  │
 └────────────────────────────────────────────────────────────┘         └───────────────┬────────────────┘
                                                                                         │ plain HTTP (GET/HEAD)
                                                                              ┌──────────▼─────────┐
                                                                              │  User's browser     │
                                                                              │  js/app.js builds   │
                                                                              │  menu, viewer, search│
                                                                              └─────────────────────┘
```

**Runtime flow in the browser**

1. `layout.html` loads `css/app.css` and `js/app.js`.
2. `app.js` fetches `config/app.properties` (feature flags) and `menu/v7-menu.json` (the whole menu) and builds the tree in memory.
3. The URL hash (`#modules/06.03.01.02`) selects a document. The app checks the PDF exists (HTTP HEAD), then shows it in the built-in viewer (`vendor/pdfjs`) or, in Reader mode, fetches `html/<same path>.html` and injects it.
4. Everything the user saves (favourites, theme, width) stays in the browser's `localStorage`.

**Build flow (on the maintenance PC)**

```
V7_MENU_HELP_DOC  ──build_v7.py──►  docs\ (copies, ASCII-safe names)   menu\v7-menu.json   reports (CSV)
docs\*.pdf        ──build_html.py─►  html\<same path>.html              html\_img\<hash>.webp
```

---

## 4. Folder and file structure

```
LHS_ERP_HELP_V7_DEPLOY\                 ← deploy folder (copy this to Tomcat webapps\LHS_ERP_HELP)
├─ layout.html            Page shell: top bar, side menu, toolbar, viewer panes, SVG icon sprite
├─ index.html             Redirects to layout.html
├─ css\app.css            All styling (tokens, light/dark, menu, viewer, reader, responsive, print)
├─ js\app.js              Whole application logic (≈ 880 lines)
├─ config\app.properties  Feature flags / viewer choice (plain text)
├─ menu\v7-menu.json      GENERATED menu (do not edit by hand)
├─ docs\                  GENERATED copy of the V7 PDFs (same folder structure)         ≈ 940 MB
├─ html\                  GENERATED Reader pages + html\_img\ screenshots (WebP)         ≈ 80 MB
├─ guide\                 V7 Guide-tab PDFs (currently only README.txt — topics show "not available")
├─ images\                lhs-logo.png, lhs-icon.png (menu icon), faq.png (favicon)
├─ vendor\pdfjs\          PDF.js 3.11.174 (pdf.min.js, pdf.worker.min.js) — Mozilla, Apache 2.0
├─ tools\                 Maintenance scripts (see §8) — only needed on the maintenance PC
│    build_v7.py / .bat      menu + copy PDFs + reports
│    build_html.py / .bat    PDF → Reader HTML
│    update_now.bat          one click: build_v7 then build_html
│    auto_update.py / .bat   watches the PDF folder and updates by itself
│    run_local.bat           local test server on http://localhost:8080
└─ README.txt             Short operator notes

Outside the deploy folder
D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC\    the master PDFs (input)
D:\LHS_ERP_HELP_V7_REPORT\              CSV reports written by build_v7.py
D:\LHS_ERP_HELP_V7_ARCHIVE\lhstopics_v5 old V5 Guide PDFs (not used)
D:\LHS_ERP_HELP_V7_DEVDOC\              this guide + source-code zip
D:\LHS_ERP_HELP\                        previous V5 application (unchanged)
```

---

## 5. Deployment requirements

### 5.1 Server (where users open the site)
| Item | Requirement |
|---|---|
| Web server | Apache Tomcat 8.5 / 9 / 10 (already running on 192.168.100.21:8888). Any static web server works (IIS, Apache httpd, nginx). |
| Java / runtime | Whatever Tomcat already uses. The application itself has no server code. |
| Disk | ≈ **1.1 GB** for the full deploy folder (docs 940 MB + html 80 MB + the rest). Plan for growth: every new PDF adds its size plus ≈ 0.25 MB of Reader files. |
| Network | Plain HTTP GET / HEAD. No database, no outbound internet needed (PDF.js is bundled). |
| MIME types | `.pdf`, `.json`, `.js`, `.css`, `.html`, `.png` are standard. If Reader screenshots do not show, add to `conf\web.xml` (or the app's `WEB-INF\web.xml`): `<mime-mapping><extension>webp</extension><mime-type>image/webp</mime-type></mime-mapping>` |
| Reverse proxy | If a proxy sits in front of Tomcat it must pass through `.properties`, `.webp`, `.pdf` and the HTTP `HEAD` method. |
| Restart | **Not required** for any content or code change. |

### 5.2 Users' PCs (clients)
- Current **Chrome, Edge or Firefox** (2021 or newer). Internet Explorer is not supported.
- JavaScript enabled; `localStorage` allowed (otherwise only favourites / theme are not remembered).
- No plug-ins. A PDF reader is *not* required (the app has its own viewer).
- Screens from phone to 4K are supported; recommended ≥ 1280 px wide for the docked 500 px menu.

### 5.3 Maintenance PC (where content is added)
| Item | Requirement |
|---|---|
| OS | Windows 10 or later (the `.bat` helpers). The Python scripts also run on Linux / macOS. |
| Python | **3.8 or newer** on PATH (`python --version`). |
| Python packages | **Only for the Reader view:** `pip install pymupdf pillow`. The menu builder needs nothing extra. |
| Disk | Space for the PDFs, the `docs\` copy and `html\`. |
| Network | None needed (a one-time internet connection to `pip install`). |

---

## 6. How to deploy

### 6.1 First deployment (new application; the old V5 site stays as it is)
1. Create the new folder `C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74\webapps\LHS_ERP_HELP_DOC_V7`. The existing `webapps\LHS_ERP_HELP` is not touched, so no backup is needed.
2. On the maintenance PC make sure the deploy folder is complete and up to date: run `tools\update_now.bat` once (it is safe to run any time).
3. **Copy the contents** of `D:\LHS_ERP_HELP_V7_DEPLOY` into `webapps\LHS_ERP_HELP_DOC_V7`. Required: `layout.html, index.html, css\, js\, config\, images\, vendor\, menu\, docs\, html\, guide\, WEB-INF\`. `tools\` is optional.
   *Tip:* copy `docs\` and `html\` first (large), then the small files last so users never see a half-updated menu.
4. Tomcan deploys the new folder by itself; if the site does not answer, restart Tomcat once (it reads `WEB-INF\web.xml` at start). Open `http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/layout.html` (internal test address) and press **Ctrl+F5** once. Public address: §16.
5. Run the verification checklist in §6.4.

### 6.2 Routine content update (new / changed PDFs)
1. Put the PDFs into `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC\<NN-Module - ABBR>\<NN.NN-Group>\` using the naming rules in §7.
2. Double-click **`tools\update_now.bat`** (or keep **`tools\auto_update.bat`** running — it does the same automatically about 30 seconds after files stop changing).
3. Copy the changed `docs\`, `html\` and `menu\` folders to Tomcat (overwrite).
4. Users press **F5**.

If the maintenance PC *is* the Tomcat server, run the scripts from the copy under `webapps\LHS_ERP_HELP\tools` — then step 3 is not needed.

### 6.2.1 The flow when a new PDF arrives (simple version)

**You only copy the PDF into the right folder. Nothing else is edited by hand.**

```
 copy PDF into the V7 folder          (<Module>\<Group>\<code - title>.pdf)
            |
            v
 auto_update.bat is running?  --yes--> wait about 30 seconds (automatic)
            |no
            v
 double-click tools\update_now.bat     (one click, finishes by itself)
            |
            v   the tool, by itself:
   1. reads the file name  ->  new menu entry (code + title) in menu\v7-menu.json
   2. copies the PDF       ->  docs\   (ASCII-safe name)
   3. builds the Reader    ->  html\   (headings, steps, tables, screenshots)
   4. writes a Markdown copy ->  html\ x.md  (the page that ChatGPT / Claude are asked to read)
            |
            v
 users press F5  ->  the document is in the menu, with both PDF and Reader view
```

- **Where the tools run:** the scripts write into the deploy folder next to them. If you run them from the copy under `webapps\LHS_ERP_HELP\tools` on the Tomcat server, the site is updated directly and nothing needs copying. If you run them on another PC, copy `docs\`, `html\` and `menu\` to the server afterwards (§6.2).
- **Best setup for "just copy and it appears":** on the Tomcat server keep a shortcut to `tools\auto_update.bat` in `shell:startup`, and point it at the folder users paste into (`auto_update.bat "<folder>"`; default `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC`).
- **Already converted PDFs are never converted again.** Only new files, or files whose PDF is newer than their Reader page, are processed. To force a rebuild of everything use `build_html.py --force` (rare, e.g. after rules change).
- **Replacing a PDF** (same name, newer file) refreshes its `docs\` copy and its Reader page the same way.
- **A file named wrongly** (no code, wrong folder) still opens as a PDF where possible but shows in the attention report `D:\LHS_ERP_HELP_V7_REPORT\` — fix the name and run the update again.
- **If the Reader page cannot be made** for one PDF, the PDF view still works and the Reader switch offers the PDF instead.

### 6.3 Code or design change
1. Edit `layout.html`, `css\app.css` or `js\app.js` in the deploy folder.
2. **Bump the cache number**: in `layout.html` change `?v=7.0.32` to the next number in **both** places (`app.css?v=…` and `app.js?v=…`). Without this, browsers keep the old files.
3. Test locally (`tools\run_local.bat` → `http://localhost:8080/layout.html`).
4. Copy the changed files to Tomcat; users press Ctrl+F5.

### 6.4 Verification checklist (after every deployment)
- [ ] Site opens; Lighthouse logo and menu with codes appear.
- [ ] Menu shows 9 modules; counts look right (compare with `v7_coverage_by_group.csv`).
- [ ] Open one document in **PDF** view: pages draw, zoom and page box work.
- [ ] Switch to **Reader**: headings, steps, screenshots appear; click a screenshot to enlarge.
- [ ] Search for a menu code (e.g. `06.03.01.02`) and a word (e.g. `freight`).
- [ ] Open a Guide topic: the *Document not available* page appears (until V7 guide PDFs exist).
- [ ] Toggle dark mode; resize the browser to phone width.
- [ ] Buttons shown / hidden as set in `config\app.properties`.

### 6.5 Rollback
Restore the backed-up `webapps\LHS_ERP_HELP` folder (or copy back the previous `css\`, `js\`, `layout.html`). No restart needed; users press Ctrl+F5.

### 6.6 Local testing without Tomcat
Double-click `tools\run_local.bat` → opens `http://localhost:8080/layout.html`. **Never open `layout.html` by double-clicking it (file://)** — browsers block loading the menu and PDFs that way; the page shows an explanatory message.

---

## 7. Content rules (how the menu is created)

The menu is generated from names only — there is no list to edit.

```
V7_MENU_HELP_DOC\
 └─ 06-Logistics and Transportation Management- SCM\        ← module folder   NN-Name - ABBR
     └─ 06.03-Outbound Logistics and Freight Management\    ← group folder    NN.NN-Name
         └─ 06.03.01.02 - Sale Freight Quotation.pdf        ← document        code - Title.pdf
```

| Rule | Detail |
|---|---|
| Module folder | `NN-Name - ABBR` e.g. `02-Finance and Accounting Management - FIN` |
| Group folder | `NN.NN-Name` e.g. `02.04-Account Receivable (AR)` |
| Document file | Starts with the menu code (`NN.NN.NN.NN`, 2–5 parts) then a separator (` - `, `_`, `:`) and the title |
| Group overview | A file whose code has only 2 parts (`00.02 - … Overview.pdf`) becomes that group's own document |
| Module overview documents | PDFs without a code inside an `Overview docs` folder (e.g. the Production manuals) appear under **Overview Documents** in that module |
| Sorting | By menu code, numerically |
| Names | En/em dashes and non-ASCII characters are converted to plain ASCII in the `docs\` copy (URLs stay safe). |
| Word files | `.docx` are ignored (listed in the report). Export to PDF first. |

`tools\build_v7.py` writes three CSV reports to `D:\LHS_ERP_HELP_V7_REPORT\`:
- `v7_documents_needing_attention.csv` — duplicate codes, code/folder mismatch, PDFs without a code, empty groups.
- `v7_coverage_by_group.csv` — document count per group.
- `v7_all_documents.csv` — every indexed document and its path.

Known items today (30): two duplicate-code pairs (`01.03.01.72`, `01.03.03.02`), one file in the wrong folder (`02.02.04.03` inside `02.04`), and 27 groups that still have no PDF.

### 7.1 `menu\v7-menu.json` format
```json
{ "version": "V7", "generated": "2026-10-27 17:42", "count": 332,
  "modules": [ { "code": "06", "name": "Logistics and Transportation Management", "abbr": "SCM",
      "overview": [ { "title": "...", "path": "docs/.../x.pdf" } ],
      "groups": [ { "code": "06.03", "name": "Outbound ...", "doc": null, "docTitle": null,
          "items": [ { "code": "06.03.01.02", "title": "Sale Freight Quotation",
                       "path": "docs/06-.../06.03.01.02 - Sale Freight Quotation.pdf" } ] } ] } ],
  "guide": [] }
```
Generated file — re-create it with `build_v7.py`; never edit by hand.

---

## 8. Source code guide

### 8.1 `layout.html` (≈ 160 lines)
Static page shell. Key element ids the code relies on: `q` (search), `panel` (tree), `docbar` / `crumbs` / `docTitle` / `chips`, toolbar buttons `aAi`, `viewSeg`, `aPrev`, `aNext`, `aFav`, `aLink`, `aPrint`, `aDown`, the stage panes `home`, `section`, `pdfwrap` (`pv` custom viewer + `frame` fallback iframe), `reader` (`rvBody`, `rvToc`), `pdfMissing`, and the inline **SVG icon sprite** (`<symbol id="i-…">`). Add a new icon by adding a `<symbol>` and using `<svg><use href="#i-name"/></svg>`.

### 8.2 `css/app.css` (≈ 350 lines)
Sections in order: design tokens (`:root` light, `:root[data-theme="dark"]`), base, top bar, side menu and tree (`.trow .tc .tn`), tabs, docbar and toolbar, PDF wrapper, home and cards, search results, responsive (`@media 900px / 640px`), **Reader view** (`.rv*`), **Copy page for AI** (`.aimenu`), **built-in PDF viewer** (`.pv*`), feature-flag helper. Colours come only from the tokens (`--brand` #c8102e etc.) — change the tokens to re-theme.

### 8.3 `js/app.js` (≈ 880 lines, one IIFE, no libraries)

| Area | Main functions / objects |
|---|---|
| Helpers & storage | `$ $$ esc ic url`, `store.get/set` (all keys prefixed `lhs7.`), state object `S` |
| Data model | `mk, register, buildModules, buildGuide, GUIDE (topic list), count, ancestors, flat` |
| Tree rendering | `rowHtml, liFor, treeDom, setOpen, markSelected, reveal, showView, savedDom`, keyboard handler |
| Navigation | `go(n)` (single entry point), `paintBar` (breadcrumbs, chips), `route` (hash → node), `pushHash` |
| Documents | `showDoc, checkDoc, showMissing` (availability check + error page) |
| Built-in PDF viewer | `PV` state, `pvOpen, pvBuild, pvLayout, pvUpdate, pvRender, pvTrack, pvGo, pvZoom, pvFallback` |
| Reader view | `readerUrl, loadReader, readerNone, buildToc, spy, setDocView`, image lightbox |
| Copy page for AI | `mdInline, mdFromReader, docMarkdown, copyText, aiAction` |
| Home / section pages | `showHome, showSection, childRow, findGuide` |
| Search | `buildSearch, runSearch, hl, resItem, renderResults, setActive, closeResults` |
| Favourites / recent | star-button handler (`#aFav`), `pushRecent`, `updateSavedBadge` |
| Feature flags | `FLAG_TARGETS, parseProps, applyFlags, loadConfig` |
| Layout & theme | `toggleSidebar, openSidebar`, sidebar resize (`sbw2`) and collapse (`sbc`), `applyTheme`, `shortcuts` dialog, `toast` |
| Start-up | `init()` → `loadConfig()` + fetch `menu/v7-menu.json` → build trees → `route()` |

**Data flow rule:** every way of opening something (tree click, search, favourites, Previous/Next, URL hash) ends in `go(node)`.

**Stored in the browser (`localStorage`, prefix `lhs7.`):** `theme`, `view` (active tab), `favs`, `recent`, `sbw2` (menu width), `sbc` (menu collapsed), `docview` (`pdf` / `reader`).

**URL hash routes:** `#home`, `#modules/<code>`, `#guide/<id>`.

**Keyboard:** Ctrl+K or `/` search · `[` show/hide menu · arrows/Home/End/Enter in the tree · Esc closes dialogs/menus.

### 8.4 `config/app.properties`
```
ui.btn.copyLink=true      ui.btn.print=false        ui.btn.download=false
ui.btn.save=true          ui.btn.copyForAI=true     ui.btn.viewSwitch=true
ui.btn.prevNext=true      ui.viewer=custom          (custom | native)
```
`true / false / yes / no / on / off / 1 / 0`, any case. Missing key or file = shown / custom. Save the file and press Ctrl+F5 — no restart. **To add a new flag:** add the key → CSS selector pair to `FLAG_TARGETS` in `app.js`, and a line to the properties file.

### 8.5 `tools/build_v7.py`
Walks `V7_MENU_HELP_DOC`, validates names with `MODULE_RE / GROUP_RE / FILE_RE`, copies PDFs incrementally (size + modified time) into `docs\` with ASCII-safe names, writes `menu\v7-menu.json` and the CSV reports. Usage: `python tools\build_v7.py ["<other source folder>"]`.

### 8.6 `tools/build_html.py` — the Reader conversion rules
Uses **PyMuPDF** (text, tables, page rendering) and **Pillow** (WebP). Every PDF is converted in its **own process** (a crash loses only that page; it is retried once without table detection, `LHS_SAFE=1`). Existing Reader pages are **kept** unless the PDF is newer, or `--force` is given.

Rules (in order of effect):

| Input in the PDF | Output |
|---|---|
| Page 1 (cover) | dropped |
| Header (top 66 pt) and footer (bottom, below 782 pt), tiny icons < 24 pt | dropped |
| Document-information table (Document Name / Release Version…) | small "Release version · date" line |
| Bold, UPPERCASE, ≥ 10.5 pt, < 70 chars — or bold ≥ 14 pt | `<h2>` section heading |
| Other short bold line (≤ 64 chars, no final full stop) | `<h3>` |
| First very large title line (≥ 17 pt) / headings with no body | dropped |
| `Step 1 :`, `Step1:-` … | numbered **step card** |
| Word bullet glyph (Wingdings / Symbol / private-use glyph) or `•`, `-` | `<li>` in a bullet list |
| `1.` / `1)` lines | numbered list |
| 3+ one-line sentences in a row (2 after a line ending with `:`) | bullet list |
| `Note:`, `Remark:`, `Example:`, `Result:`, `Important:` … | call-out box |
| Ruled tables | HTML table (blank / merged-cell columns removed) |
| Embedded images | merged into one figure, rendered from the page (so red annotation boxes stay), max 1200 px wide, WebP quality 72, de-duplicated by hash into `html\_img\` |
| Wrapped lines of the same style | joined into one paragraph |

Tunable constants at the top of the file: `HEAD_Y, FOOT_Y, MAX_IMG_W`, regexes `STEP, NUMBERED, CALLOUT`, thresholds inside `classify()` and `short_runs_to_lists()`. After changing rules, re-convert with `python tools\build_html.py --force` (or a folder / single PDF path). `RULES_VERSION` is written into each page (`<!--rvN-->`) for information.

**Template assumption:** the rules were tuned on the two Word-exported PDF templates used by V7 (module 01–05 style and the 06 Logistics style). A very different layout may convert less neatly — the PDF view is always available.

### 8.6.1 `tools/build_md.py` — Markdown copy for AI
Writes `x.md` beside every Reader page `x.html` (title, menu code, breadcrumb, PDF link, text, tables, steps; screenshots are left out because an AI cannot use them). Only new / changed pages are written (`--force` = all). It uses only the Python standard library. The links use `site.url` from `config\app.properties` (`https://help.lighthouseindia.com/docs/v7/`); if you change the address, change that line and run `python tools\build_md.py --force`. It runs from `update_now.bat` and `auto_update.py` after the Reader build.

*How the buttons use it:* *Open in ChatGPT / Claude* open a new chat with only a link and one line about the document: `Read from <link to x.md> so I can ask questions about it. It is the Lighthouse ERP V7 user guide "<title>" (menu code …), <module > group>.` (same idea as the InfluxDB docs). Nothing long is pasted and there is no length limit; the AI reads the page itself, so the site must be reachable from the internet. The link always uses `site.url`, even when the page is opened from the office network. A document without a Reader page gets its PDF link instead. *Copy page for AI* still copies the full Markdown text (page link, PDF link, text, tables, steps; no screenshots) to the clipboard.

`WEB-INF\web.xml` only adds two file types Tomcat does not know (`md` → `text/markdown`, `webp` → `image/webp`). It contains no security rules and no server-side code.

### 8.7 `tools/auto_update.py`
Polls the V7 folder every 15 s; when the set of PDFs (count, total size, newest time) is unchanged for one full poll, it runs `build_v7.py` then `build_html.py`. Log: `tools\auto_update.log`. Start with Windows by placing a shortcut to `auto_update.bat` in `shell:startup`.

---

## 9. Common maintenance recipes

| Task | How |
|---|---|
| Add / replace a document | Put the PDF in the V7 folder → `update_now.bat` → copy `docs\ html\ menu\` to Tomcat |
| Remove a document | Delete it from the V7 folder **and** from `docs\` (and its `html\…html`) → `update_now.bat` → copy |
| Add Guide-tab content | Put V7 PDFs in `guide\` named as in the `GUIDE` list in `app.js` (e.g. `AboutLighthouseERP.pdf`, `Glossary.pdf`, `Lighthouse.pdf` = Getting started). New topic: add an entry to the `GUIDE` array. |
| Hide / show a toolbar button | `config\app.properties` |
| Use the browser's PDF viewer | `ui.viewer=native` |
| Change the logo | Replace `images\lhs-logo.png` / `lhs-icon.png` (same file names), bump the cache number |
| Change colours / fonts | Edit tokens at the top of `css\app.css`; bump the cache number |
| Change the default menu width | `--sbw` in `app.css` (current `min(500px, 40vw)`); to reset everyone's saved width change the storage key `sbw2` in `app.js` |
| Change the heading text | `layout.html` (`brand-title`) and the hero text in `showHome` (`app.js`) |
| Upgrade PDF.js | Replace the two files in `vendor\pdfjs\` with the same-version-family UMD build (3.x); update the version string in `pvLib()`; retest |
| Re-format all Reader pages | `python tools\build_html.py --force` |
| Move to another server / URL | Copy the whole folder; all paths are relative, nothing to change |

---

## 10. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Blank page / "opened directly from disk" message | Page opened as `file://`. Use Tomcat or `tools\run_local.bat`. |
| Old design after deploying | Browser cache. Press Ctrl+F5; ensure the `?v=` number was bumped in `layout.html`. |
| Menu shows "could not be loaded" | `menu\v7-menu.json` missing / not copied, or JSON broken → re-run `build_v7.py` and copy `menu\`. |
| A document shows **Document not available** | The PDF is not on the server at the path shown on the page — copy `docs\` again / check name. |
| Reader says "not available for this document yet" | No file in `html\` for it → run `update_now.bat` (or `build_html.py`), copy `html\`. |
| Reader screenshots missing (grey boxes) | `html\_img\` not copied, or server lacks the `image/webp` MIME mapping (§5.1). |
| PDF viewer shows the browser's black viewer | PDF.js failed to load (is `vendor\` copied?) or `ui.viewer=native`. |
| Menu code / counts wrong | Check naming rules (§7) and the CSV reports. |
| `build_html` says PyMuPDF is missing | `pip install pymupdf pillow`. |
| One PDF has no Reader page and `FAILED` in the log | It crashed the converter twice; the PDF still works. Report the file name for rule tuning. |
| Buttons not hiding | Edit the correct `config\app.properties` (the live copy), Ctrl+F5. |
| Slow first PDF open on weak network | PDFs are large (screenshots). Nothing is wrong; pages stream in as you scroll. |

---

## 11. Security and privacy notes

- The site is public to anyone who can reach the server; it contains no login, no secrets, no personal data. `config\app.properties` is readable by anyone who types its URL (it only holds on/off button settings, so never put passwords in it). It must stay in `config\` because the page reads it from the browser; a JSP-based hiding option was tried and removed on purpose (no server-side code in this application).
- *Open in ChatGPT / Open in Claude* sends the document text to those outside services **only when a user clicks it**. If that is not acceptable for internal documents, set `ui.btn.copyForAI=false`.
- PDF.js and all scripts are served from the same server; the app makes no calls to the internet except the user-initiated links above and the (existing) footer / e-invoice links.
- Favourites, recents, theme and width stay in each user's own browser.

---

## 12. Known limitations and backlog ideas

- **Guide tab** topics have no V7 PDFs yet (they show *Document not available*) — supply files in `guide\`.
- **27 groups** have no PDF yet and show *Coming soon*; 30 items in the attention report (§7).
- **Reader rules** are template-based; unusual PDFs may need rule tuning (§8.6). Two PDFs (`00.04.04.14 PAN OCR`, `00.05.01.06 Account Health Check Dashboard`) crash PyMuPDF's table finder and are converted without table detection (tables appear as text).
- No full-text search inside document **content** yet (search covers codes, titles and folder names). A good next step: build a search index from the Reader HTML during `build_html.py`.
- No analytics / usage statistics.
- The Word documents in the Production *Overview docs* folder were converted to PDF; their `.docx` originals remain beside them.
- Idea: automatic deployment (robocopy / scheduled task) from the maintenance PC to Tomcat.

---

## 13. Testing checklist for developers

1. `python -m py_compile tools\*.py` and `node -e "new Function(require('fs').readFileSync('js/app.js','utf8'))"` (syntax).
2. Local server (`run_local.bat`): load home, open documents of several modules, both views.
3. Missing-file test: rename a PDF in `docs\` temporarily → the *Document not available* page must appear → restore.
4. Flag test: set a flag to `false`, reload → button gone.
5. Narrow-width test (≈ 400 px wide) and dark mode.
6. Run `update_now.bat` twice: the second run must convert **0** documents.

---

## 14. Version notes

| Build | Notes |
|---|---|
| V7 web app 7.0.x | New enterprise UI; menu generated from the V7 folder tree; guide topics via `guide\`; "document not available" page; Reader (HTML) view with automatic conversion; Copy page for AI; built-in PDF viewer; feature flags; single-line wide menu with code badges; one-click / automatic updater. |
| V5 (previous) | `D:\LHS_ERP_HELP`, XML-driven menu (`menu.xml`, `mainmenu.xml`), jQuery tree. Left untouched as a fallback. |

---

## 15. Version control — where to keep the source (Git or SVN)

**Recommendation: Git, in a private repository** (GitHub private repo, or the company's own GitLab / Bitbucket / Azure DevOps). SVN also works and is fine if the company already runs an SVN server; the rules below are the same. Git is preferred because branches, history and rollback are simpler and tools are widely known. Nothing in the application depends on either.

### 15.1 What goes into version control, and what does not

| Put in the repository (small, text) | Keep OUT of the repository |
|---|---|
| `layout.html`, `index.html`, `css\`, `js\`, `config\app.properties` | `docs\` (≈ 940 MB of PDF copies — rebuilt from the V7 folder) |
| `tools\*.py`, `tools\*.bat` | `html\` (≈ 80 MB generated Reader pages) |
| `vendor\pdfjs\` (third-party, small), `images\` | `menu\v7-menu.json` (generated) |
| `guide\README.txt`, `README.txt`, `DEVELOPER_GUIDE.md` | `guide\*.pdf`, `tools\auto_update.log`, `__pycache__` |

The deploy folder already contains a ready `.gitignore` with these exclusions. Total repository size is then about 1 MB.

**The PDFs themselves** (`D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC`) are the real content. Options: (a) keep them on a file server with regular backup (simplest, recommended); (b) a separate SVN repository (SVN handles large binary files better than Git); (c) Git with Git LFS. Do not mix them into the code repository.

### 15.2 One-time setup (Git)
```
cd D:\LHS_ERP_HELP_V7_DEPLOY
git init
git add .
git commit -m "V7 Help Centre 7.0.32 baseline"
git branch -M main
git remote add origin <URL of the private repository>
git push -u origin main
```
(SVN: import the same files with `svn import`, and set `svn:ignore` for `docs`, `html`, `menu\v7-menu.json`.)

### 15.3 Day-to-day working flow
1. **Content only (new PDFs):** no Git action — copy the PDFs, run the update (§6.2.1). Back up the PDF folder.
2. **Code / design change:** edit → test locally (§6.6) → bump the `?v=` number in `layout.html` (§6.3) → `git commit` with a clear message → `git tag v7.0.NN` → deploy the changed files to Tomcat.
3. **Branches (optional):** `main` = what is deployed; make a branch `feature-xyz` for bigger changes and merge after testing.
4. **Rollback:** `git checkout v7.0.27 -- js css layout.html`, copy to Tomcat, Ctrl+F5.
5. **Keep the guide current:** when behaviour changes, update `DEVELOPER_GUIDE.md` in the same commit.

### 15.4 Rebuilding a server from scratch
Clone the repository → install the PDFs into the V7 folder (from backup) → run `tools\update_now.bat` (rebuilds `docs\`, `html\`, `menu\`) → copy to `webapps\LHS_ERP_HELP` (§6.1).

---

## 16. Publishing on the internet — `https://help.lighthouseindia.com/docs/v7/` (nginx in front of Tomcat)

nginx is the only front server used (ports 80 / 443). Tomcat stays as it is and is only reached by nginx. Paths below are examples; adjust them to the server.

### 16.1 Steps
1. **DNS** (domain panel): `help` → A record to the server's public IP (or CNAME if the host gives a name).
2. **Public IP / router:** forward TCP 80 and 443 to the machine that runs nginx. Do **not** forward 8888.
3. **Tomcat:** V7 is a **new, separate application** in `C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74\webapps\LHS_ERP_HELP_DOC_V7\`. The existing `webapps\LHS_ERP_HELP` (V5) is **not touched** and keeps working at `http://192.168.100.21:8888/LHS_ERP_HELP/`. Do not change `server.xml`. Keep port 8888 closed to the internet in the firewall / router (only 80 and 443 are forwarded); nginx publishes only `/docs/v7/`, so the old application is never exposed publicly. No backup of the old application is needed for this setup.
4. **Certificate (HTTPS):** `certbot --nginx -d help.lighthouseindia.com` (Let's Encrypt, renews itself). Or use the company's wildcard certificate.
5. Install the configuration below, test, reload.
6. Run the checks in §16.3.

### 16.2 nginx (`/etc/nginx/conf.d/help.lighthouseindia.com.conf`)
```nginx
server {
    listen 80;
    server_name help.lighthouseindia.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name help.lighthouseindia.com;

    ssl_certificate     /etc/letsencrypt/live/help.lighthouseindia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/help.lighthouseindia.com/privkey.pem;

    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    gzip on;
    gzip_types text/css application/javascript application/json text/plain image/svg+xml;

    # the Help Centre lives at https://help.lighthouseindia.com/docs/v7/
    location = /docs/v7 { return 301 /docs/v7/; }          # the trailing slash is required (relative links)
    location = /       { return 302 /docs/v7/; }

    location /docs/v7/ {
        proxy_pass http://127.0.0.1:8888/LHS_ERP_HELP_DOC_V7/;  # /docs/v7/x  ->  Tomcat /LHS_ERP_HELP_DOC_V7/x
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location / { return 404; }                              # nothing else is published
}
```
Test and apply: `nginx -t && nginx -s reload`. *Option:* because the site is only static files, nginx can serve it directly (replace the `proxy_pass` block with `root <path to webapps>/LHS_ERP_HELP; try_files $uri =404;`) and Tomcat is then not needed for this site at all.

### 16.3 Checks after going live
- [ ] `http://help.lighthouseindia.com` redirects to `https://`, and the padlock is valid.
- [ ] The site opens, a PDF draws and scrolls (large PDFs need range requests — they are passed through), the Reader view and screenshots load.
- [ ] `https://help.lighthouseindia.com:8888` and `http://<public IP>:8888` do **not** answer from the internet.
- [ ] `/docs/v7/docs/`, `/docs/v7/html/` and `/docs/v7/config/` show no folder listing.
- [ ] Copy link in the toolbar gives an `https://help.lighthouseindia.com/docs/v7/layout.html#…` link.
- [ ] Only documents meant for clients are in `docs\`, `html\` (everything there is public).

### 16.4 Publishing notes
- The application uses only relative links, so it works unchanged under `/docs/v7/`. Always give clients the address **with** the trailing slash (`…/docs/v7/`); nginx redirects the version without it. The app's own `docs\` folder then appears as `/docs/v7/docs/…`, which is normal.
- Update links to the old `192.168.100.21:8888/...` address (ERP help menu, e-mails).
- After a content update nothing changes in nginx — just refresh the files on Tomcat (§6.2).
- Consider `ui.btn.copyForAI=false` for the public site (§11).

---

## Appendix A — Source files

The complete source (every file listed in §4 except the generated `docs\`, `html\`, `menu\v7-menu.json` and the third-party PDF.js files) is delivered in two forms next to this guide:

1. `LHS_ERP_HELP_V7_SOURCE.zip` — ready to unzip into a deploy folder.
2. **Appendix B in `DEVELOPER_GUIDE.html`** — the full text of each source file, for reading and printing.
