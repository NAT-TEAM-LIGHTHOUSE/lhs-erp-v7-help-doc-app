# Handover - Development and DevOps teams

Everything a new team member needs on day one. Version at handover: see [`VERSION`](../VERSION).

## 1. What is being handed over

| Item | Where | Notes |
|---|---|---|
| Source code and documents | private Git repository `lhs-erp-v7-help-doc-app` (working copy `D:\lhs-erp-v7-help-doc-app`) | first push: README.md section "First push" |
| Ready-to-deploy release | `D:\LHS_ERP_HELP_DOC_V7_FINAL` | `01_DEPLOY_THIS_FOLDER` (about 1 GB, includes PDFs and Reader pages), `02_PACKAGES` (code-only zips), `03_DOCUMENTATION` |
| Deployment checklist | `03_DOCUMENTATION\LHS_ERP_HELP_DOC_V7_Deployment_Checklist.xlsx` | 63 items; tick while deploying |
| All documents in one HTML | `03_DOCUMENTATION\lhs-erp-v7-help-doc-app_documentation.html` | search box + full source code; open in a browser |
| Source PDFs (the real content) | `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC` | not in Git; back it up |
| Production address | `https://help.lighthouseindia.com/docs/v7/` | nginx to Tomcat web app `LHS_ERP_HELP_DOC_V7` |

## 2. Read in this order

| Team | Documents |
|---|---|
| Developers | [README.md](../README.md) > [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) > [CONTRIBUTING.md](../CONTRIBUTING.md) > [RELEASE_PROCESS.md](RELEASE_PROCESS.md) > [TECH_STACK.md](TECH_STACK.md) > [CLAUDE.md](../CLAUDE.md) (if an AI assistant is used) |
| DevOps | [DEPLOYMENT.md](DEPLOYMENT.md) > Excel checklist > [MAINTENANCE.md](MAINTENANCE.md) > [TECH_STACK.md](TECH_STACK.md) > `deploy/nginx/help.lighthouseindia.com.conf` |
| Both | [TEAM_RESPONSIBILITIES.md](TEAM_RESPONSIBILITIES.md) |

## 3. Developer day-one steps
1. Get access to the private repository; clone it.
2. Install Python 3.8+ and Git; `pip install -r requirements.txt`.
3. Run `webapp\tools\update_now.bat` (builds menu + Reader pages from the PDF folder), then `webapp\tools\run_local.bat` and open http://localhost:8080/layout.html.
4. Run `python scripts\check.py` - expected `RESULT: ALL OK`.
5. Create `develop` and protect `main` (see README "First push") if not already done.
6. Make a small change on a `feature/` branch, run the checks, open a pull request - this proves the flow works.

## 4. DevOps day-one steps
1. Open the Excel checklist; fill the Summary sheet (names, date, server).
2. Check server access: Tomcat folder `C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74\webapps`, nginx host, DNS panel for `lighthouseindia.com`.
3. Deploy `01_DEPLOY_THIS_FOLDER\LHS_ERP_HELP_DOC_V7` to `webapps\`, restart Tomcat once, test `http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/layout.html` (Ctrl+F5).
4. Make it public: nginx config, DNS record, HTTPS certificate; confirm port 8888 is closed to the internet.
5. Run the verification list (checklist sheet 4) and send the result to the product owner.
6. Set up backups and monitoring (TEAM_RESPONSIBILITIES.md section 4).

## 5. Facts that are easy to get wrong
* Production settings come from `deploy/env/prod.app.properties`; the file in `webapp/config/` is for developers (`site.url` empty). A code package already carries the right file for its environment.
* Code packages never contain `docs/`, `html/` or `menu/`; unzipping a new release over the web app keeps the published documents.
* After changing `app.css` or `app.js`, bump the version (`scripts\set_version.py`), otherwise browsers keep the old file.
* The menu is generated from folder and file names - never edit `menu\v7-menu.json` by hand.
* The site has no login; "Save" (favourites) is stored in each user's own browser only.
* The old V5 help (`LHS_ERP_HELP`) is a separate application: do not touch it.
* `D:\LHS_ERP_HELP_V7_DEPLOY` is an old working copy; delete it only after the go-live is verified.

## 6. Acceptance of the handover
| Check | Dev | DevOps |
|---|---|---|
| Access to repository / servers received | | |
| Documents read, questions answered | | |
| Local run (Dev) / UAT deploy (DevOps) done once | | |
| Contacts table in TEAM_RESPONSIBILITIES.md filled | | |
| Name and date | | |
