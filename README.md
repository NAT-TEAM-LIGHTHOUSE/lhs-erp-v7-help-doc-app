# lhs-erp-v7-help-doc-app

**Lighthouse ERP V7 Help Centre** - a static web application that shows the V7 user-guide PDFs in a searchable
tree menu, with its own PDF viewer, an automatic HTML "Reader" view of every PDF, and "ask ChatGPT / Claude" buttons.

| | |
|---|---|
| Current version | see [`VERSION`](VERSION) · history in [`CHANGELOG.md`](CHANGELOG.md) |
| Public address (production) | `https://help.lighthouseindia.com/docs/v7/` |
| Hosting | Apache Tomcat 9 (web app `LHS_ERP_HELP_DOC_V7`) behind nginx |
| Technology | HTML + CSS + vanilla JavaScript (no framework, no database, no server-side code); Python 3 tools for content |
| Repository | **private** - company internal |

## How it works in one minute
```
V7 PDFs (folder tree)  --tools-->  menu\v7-menu.json + docs\ (PDF copies) + html\ (Reader pages + .md)  --Tomcat/nginx-->  users
   you add / replace PDFs           run update_now.bat (or auto_update.bat)                                  browser
```
* The menu is **generated from folder and file names** - nothing is edited by hand.
* Adding a document = copy the PDF into the right folder and run `update_now.bat`.
* The repository holds **code, config, tools and docs only**. PDFs and everything generated from them (about 1 GB) are
  **not** in Git; they are rebuilt on the server.

## Repository layout
```
lhs-erp-v7-help-doc-app/
├─ README.md  CHANGELOG.md  VERSION  CONTRIBUTING.md  CLAUDE.md
├─ webapp/                      <- exactly what runs on Tomcat (one folder = one web app)
│  ├─ layout.html  index.html   page shell
│  ├─ css/app.css  js/app.js    the whole UI (one stylesheet, one script)
│  ├─ config/app.properties     button switches + public address (DEV defaults)
│  ├─ WEB-INF/web.xml           Tomcat file types (md, webp)
│  ├─ vendor/pdfjs/             PDF.js (Mozilla, Apache-2.0)
│  ├─ images/  guide/
│  └─ tools/                    content tools: build_v7.py  build_html.py  build_md.py  auto_update.py  *.bat
├─ deploy/
│  ├─ env/uat.app.properties  prod.app.properties      per-environment settings
│  └─ nginx/help.lighthouseindia.com.conf              public front door
├─ scripts/                     developer helpers: check.py  set_version.py  package_release.ps1
├─ docs/                        all documentation (start with docs/README.md)
└─ .github/pull_request_template.md
```
Generated, git-ignored folders appear inside `webapp/` when you run the tools: `docs/`, `html/`, `menu/v7-menu.json`.

## Quick start (developer PC, Windows)
1. Install **Python 3.8+** and **Git**; once: `pip install pymupdf pillow` (only needed to build Reader pages).
2. `git clone <private repo URL>` → open the folder.
3. Put (or point to) the V7 PDFs, then double-click `webapp\tools\update_now.bat`
   (default source `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC`; other folder: `update_now.bat "D:\path"`).
4. `webapp\tools\run_local.bat` → http://localhost:8080/layout.html
   (do not open `layout.html` by double-click: browsers block loading the menu from `file://`).
5. Before every commit: `python scripts\check.py`.

## First push to the private repository (once)
Create an **empty private** repository on GitHub / GitLab / Azure DevOps (no README, no .gitignore), then in this folder:
```
git init -b main
git add .
git commit -m "chore: baseline lhs-erp-v7-help-doc-app 7.0.32 (UAT)"
git remote add origin <private repository URL>
git push -u origin main
git tag -a v7.0.32 -m "UAT baseline" && git push origin v7.0.32
git checkout -b develop && git push -u origin develop
```
Then protect `main` (pull request + approval required) in the repository settings. Check with `git status` that no `webapp/docs`, `webapp/html` or PDFs are listed - they are git-ignored.

## Documentation
| Document | For |
|---|---|
| [docs/README.md](docs/README.md) | index of all documents |
| [docs/HANDOVER.md](docs/HANDOVER.md) | **start here** - handover to the Development and DevOps teams, day-one steps |
| [docs/TEAM_RESPONSIBILITIES.md](docs/TEAM_RESPONSIBILITIES.md) | who is responsible for what (RACI), contacts, escalation |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | **deploy to UAT and Production**, rollback, verification |
| [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md) | branches, versions, UAT sign-off, how a change reaches production |
| [docs/MAINTENANCE.md](docs/MAINTENANCE.md) | day-to-day runbook, adding documents, certificates, troubleshooting |
| [docs/TECH_STACK.md](docs/TECH_STACK.md) | every technology, version and licence |
| [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | features, architecture, content rules, source walkthrough, recipes |

## Environments
| Environment | Purpose | Web app / address | Settings |
|---|---|---|---|
| **DEV** | developer PC | `http://localhost:8080/layout.html` | `webapp/config/app.properties` |
| **UAT** | business testing before release | Tomcat `LHS_ERP_HELP_DOC_V7_UAT` (internal address) | `deploy/env/uat.app.properties` |
| **PROD** | clients | `https://help.lighthouseindia.com/docs/v7/` | `deploy/env/prod.app.properties` |

The old V5 help (`LHS_ERP_HELP`) is a separate application and is not part of this repository.
