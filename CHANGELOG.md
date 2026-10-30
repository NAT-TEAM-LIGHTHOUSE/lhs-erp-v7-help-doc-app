# Changelog

All notable changes to **lhs-erp-v7-help-doc-app**. Newest first. Version = the number in `VERSION`
(also the `?v=` cache number in `webapp/layout.html`). Format: [Keep a Changelog](https://keepachangelog.com).

## [7.0.32] - 2026-10-28 - UAT baseline
First version stored in Git. Everything below was built before the repository existed.

### Added
- "Open in ChatGPT / Open in Claude" send only a link to the page's Markdown copy plus a one-line description
  (`Read from <link>.md so I can ask questions about it.`). `tools/build_md.py` writes `x.md` beside every Reader page;
  the public address comes from `site.url` in `config/app.properties`.
- `WEB-INF/web.xml`: file types `md` and `webp` for Tomcat.
- Repository, environments (dev / UAT / prod), scripts, release process and documentation.
- `docs/TEAM_RESPONSIBILITIES.md` (who owns what: Dev, DevOps, Content, QA, Product owner, RACI, escalation) and
  `docs/HANDOVER.md` (day-one steps for the Development and DevOps teams).
- Red "V7" mark at the bottom of the side pane (left of the copyright line).

### Changed
- "Copy page for AI" copies text only (page link, PDF link, text, tables, steps); screenshots are left out.
- Copy link button hidden by default (`ui.btn.copyLink=false`).
- "V7" badge removed from the header title and from the home-page banner (the version mark is now in the side-pane footer).

## [7.0.0] - [7.0.31] - 2026-10 (built and tested before Git)
Build-by-build history was not recorded; the features that make up the baseline:

### Application
- Enterprise UI on the V5 concept: tree menu with menu-code badges on a single line, resizable side pane
  (open by default on narrow screens), tabs Modules / Guide, home page, breadcrumbs, search, favourites, recents,
  previous / next, light and dark theme, responsive layout.
- Menu generated from the V7 folder tree (`NN-Module - ABBR \ NN.NN-Group \ code - title.pdf`); no menu file is edited by hand.
- Own PDF viewer (PDF.js 3.11.174): page box, zoom, fit width, selectable text; browser viewer as fallback.
- **Reader (HTML) view** of every PDF, built by fixed rules: headings, numbered steps, lists, call-outs, tables,
  screenshots (WebP, de-duplicated), "On this page" outline. Only new / changed PDFs are converted.
- "Document not available" page for any missing PDF (including Guide topics).
- Feature flags in `config/app.properties` (Copy link, Print, Download, Save, Copy page for AI, PDF|Reader switch, Prev/Next, viewer).
- "Copy page for AI" dropdown.

### Tooling
- `tools/build_v7.py` (menu + `docs/` copy + reports), `tools/build_html.py` (Reader pages, per-PDF isolation, safe retry),
  `tools/update_now.bat` (one click), `tools/auto_update.py` (watches the folder).

### Deployment
- New Tomcat application `LHS_ERP_HELP_DOC_V7` next to the untouched V5 `LHS_ERP_HELP`;
  public address `https://help.lighthouseindia.com/docs/v7/` through nginx.
