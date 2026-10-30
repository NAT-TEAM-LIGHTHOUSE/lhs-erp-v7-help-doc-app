# Guidance for AI coding assistants (Claude Code etc.)

Project: **lhs-erp-v7-help-doc-app** - static Help Centre for Lighthouse ERP V7 (Tomcat behind nginx). Read `README.md` first,
then `docs/DEVELOPER_GUIDE.md` sections 3, 7, 8 for architecture, content rules and the source walkthrough.

## Layout
* `webapp/` = the deployed application. `webapp/js/app.js` is one IIFE (no libraries); `webapp/css/app.css` the only stylesheet.
* `webapp/tools/` = Python content tools (`build_v7.py` menu + PDF copies, `build_html.py` Reader pages, `build_md.py` Markdown copies, `auto_update.py`).
* `deploy/` = nginx config + per-environment `*.app.properties`. `scripts/` = developer helpers. `docs/` = documentation.

## Rules
1. **Run `python scripts/check.py` before declaring a change done.** It must print `ALL OK`.
2. Changing anything in `webapp/css`, `webapp/js` or `webapp/layout.html` ⇒ run `python scripts/set_version.py <next 7.0.N>` and add a
   `## [version]` section at the top of `CHANGELOG.md`. (The `?v=` number in `layout.html` busts the browser cache; both markers must match `VERSION`.)
3. **Relative URLs only** in html/css/js (the site lives under `/docs/v7/`). No CDN, no external fonts, no frameworks, no server-side code.
4. Never hand-edit or commit generated output: `webapp/docs/`, `webapp/html/`, `webapp/menu/v7-menu.json`. Fix the rule in `webapp/tools/*.py`, then rebuild.
5. Button switches live in `webapp/config/app.properties` (DEV) and `deploy/env/*.app.properties` (UAT / PROD). A new key must be added to **all three**
   files and to `need` in `scripts/check.py`, and parsed in `applyFlags()` in `app.js`.
6. Match the surrounding code style (comment density, naming, ES5-style `var` and function declarations in `app.js`).
7. Do not weaken privacy: the page makes no calls to the internet except user-clicked links (ChatGPT / Claude, e-invoice, company site).
8. Keep docs in step: behaviour change ⇒ update the relevant file in `docs/` in the same commit.

## Useful commands (Windows)
```
python scripts/check.py                                   # all checks
python scripts/set_version.py 7.0.33                      # bump version everywhere
webapp\tools\run_local.bat                                # http://localhost:8080/layout.html
webapp\tools\update_now.bat                               # rebuild menu + Reader + Markdown (needs: pip install pymupdf pillow)
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env uat    # deployment zip in dist\
```

## Known traps
* Opening `layout.html` via `file://` cannot load the menu - use a local server.
* A hidden browser pane does not run `requestAnimationFrame`/IntersectionObserver code (PDF viewer, scroll spy) - show the pane when testing.
* The PDF viewer draws pages lazily from scroll position (`pvUpdate`), not with IntersectionObserver.
* `build_html.py` converts each PDF in a subprocess; two known PDFs crash PyMuPDF's table finder and use the `LHS_SAFE=1` retry.
* Menu codes in folder / file names drive everything; wrong names show up in the CSV reports in `..\LHS_ERP_HELP_V7_REPORT\`.
