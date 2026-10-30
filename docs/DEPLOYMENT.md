# Deployment guide

Covers: environments, one-time server setup, deploying **code** (UAT and Production), deploying **content** (PDFs / Reader pages),
verification, rollback. Paths are the current Windows servers; adjust if they move.

## 1. Environments
| | DEV | UAT | PROD |
|---|---|---|---|
| Purpose | developer PC | business testing of the next release | clients |
| Tomcat web app folder | - (`run_local.bat`) | `...\webapps\LHS_ERP_HELP_DOC_V7_UAT` | `...\webapps\LHS_ERP_HELP_DOC_V7` |
| Address | `http://localhost:8080/layout.html` | `http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7_UAT/layout.html` (internal only) | `https://help.lighthouseindia.com/docs/v7/` |
| Settings file | `webapp/config/app.properties` | `deploy/env/uat.app.properties` | `deploy/env/prod.app.properties` |
| Content (`docs/ html/ menu/`) | built locally | copy of production content (or its own test PDFs) | the real PDFs |

`...` = `C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74`. The old V5 help `webapps\LHS_ERP_HELP` is never touched by this project.

**Code and content are deployed separately.** A release package (zip) contains only code and settings; the PDFs, `docs\`, `html\` and
`menu\` stay on the server and are updated by the content tools (§5). So a code release never overwrites published documents.

## 2. One-time setup of a server

### 2.1 Tomcat web app folder
Create the empty folder `...\webapps\LHS_ERP_HELP_DOC_V7` (PROD) or `...\webapps\LHS_ERP_HELP_DOC_V7_UAT` (UAT). Tomcat deploys it by itself;
restart Tomcat once after the first copy so `WEB-INF\web.xml` (file types) is read. Do **not** change `server.xml` for the old V5 app.
Keep port 8888 closed to the internet on the router / firewall - only nginx (80, 443) is public.

### 2.2 nginx (PROD only)
1. Unzip nginx to `C:\nginx` (Windows) - ports 80 and 443 must be free (`netstat -ano | findstr ":80 :443"`).
2. Get the HTTPS certificate for `help.lighthouseindia.com` **before** starting nginx (win-acme `wacs.exe` needs port 80 free) or use the company certificate;
   save as `C:\nginx\ssl\fullchain.pem` and `privkey.pem`.
3. Merge [`deploy/nginx/help.lighthouseindia.com.conf`](../deploy/nginx/help.lighthouseindia.com.conf) into `C:\nginx\conf\nginx.conf` (inside `http { }`).
4. `nginx.exe -t` → must say *test is successful* → `start C:\nginx\nginx.exe`. After later changes: `nginx.exe -s reload`.
5. Make nginx start with Windows (NSSM service or a Task Scheduler "At startup" task).

### 2.3 Network
* DNS: A record `help` → public IP of the server.
* Router / firewall: forward TCP **80 and 443** to the nginx machine; allow them in Windows Firewall. **Do not** forward 8888.

### 2.4 Content tools (the PC / server that holds the PDFs)
Install Python 3.8+ and `pip install -r requirements.txt`. The tools live in `webapp\tools\` (they are inside every package).

## 3. Deploy a code release

### 3.1 Build the package (developer PC)
```
git checkout main            # production releases come from main (UAT from develop)
git pull
python scripts\check.py      # must say ALL OK
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env uat     # or -Env prod
```
Result: `dist\lhs-erp-v7-help-doc-app_<version>_<env>.zip`. It contains the folder `LHS_ERP_HELP_DOC_V7\` with
`layout.html index.html css js images vendor WEB-INF config tools VERSION.txt` - **no** `docs html menu`.
`config\app.properties` inside is the environment's file from `deploy\env\`.

### 3.2 Install on the server
UAT (folder name differs, so rename after unzipping):
1. Copy the zip to the server and unzip it to a temporary folder.
2. Copy the **contents** of `LHS_ERP_HELP_DOC_V7\` into `...\webapps\LHS_ERP_HELP_DOC_V7_UAT\` (overwrite).
3. No Tomcat restart (restart once only if `WEB-INF\web.xml` changed).
4. Open the UAT address, press **Ctrl+F5**, run the checklist in §6.

PROD: same, into `...\webapps\LHS_ERP_HELP_DOC_V7\`; then open `https://help.lighthouseindia.com/docs/v7/`, **Ctrl+F5**, run §6.

Before overwriting, rename the current folder's code files or copy the whole web app folder to `...\BACKUP\LHS_ERP_HELP_DOC_V7_<old version>` (the `docs\` folder is large;
back up only `layout.html index.html css js images vendor WEB-INF config tools` - that is a few MB and is all a rollback needs).

> **Settings are overwritten on every release.** Do not edit `config\app.properties` directly on the server for a lasting change - change it in
> `deploy/env/*.app.properties`, commit it and release. (Quick emergency edits on the server are allowed but must be copied back to Git the same day.)

### 3.3 After a change of `site.url`
The Markdown pages contain absolute links built from `site.url`. After deploying to a new address run once on that server:
`python tools\build_md.py --force`.

## 4. First-time content on a new server
Building the Reader pages for all 332 PDFs from scratch takes a long time (tens of minutes). It is faster to copy the finished content:
```
robocopy "D:\<build PC>\webapp\docs" "...\webapps\LHS_ERP_HELP_DOC_V7\docs" /E
robocopy "D:\<build PC>\webapp\html" "...\webapps\LHS_ERP_HELP_DOC_V7\html" /E
robocopy "D:\<build PC>\webapp\menu" "...\webapps\LHS_ERP_HELP_DOC_V7\menu" /E
```
(`/E` copies new and changed files and never deletes. Use `/MIR` only when you really want the target to match exactly.)
Alternatively run `tools\update_now.bat` on the server; it builds everything from the V7 PDF folder.

## 5. Deploy content (new / changed PDFs)
See [MAINTENANCE.md §2](MAINTENANCE.md). In short: copy the PDF into the V7 folder → run `webapp\tools\update_now.bat`
(or leave `auto_update.bat` running on the server) → copy `docs\ html\ menu\` to Tomcat if the tools ran on another PC → users press F5.
No Tomcat restart, no nginx change.

## 6. Verification checklist (after every deployment)
- [ ] The address opens; the Lighthouse logo and the menu with 9 modules and code badges appear.
- [ ] `VERSION.txt` in the web app folder shows the released version, and after Ctrl+F5 the page loads `app.js?v=<that version>` (F12 → Network).
- [ ] Open one document in **PDF** view: pages draw, zoom and page box work.
- [ ] Switch to **Reader**: headings, steps, screenshots appear; click a screenshot to enlarge.
- [ ] Search a code (`06.03.01.02`) and a word (`freight`).
- [ ] Open a Guide topic: *Document not available* page (until V7 guide PDFs are added).
- [ ] Dark mode; phone width (menu opens by default).
- [ ] Buttons shown / hidden as in the environment's `app.properties` (Copy link, Print, Download are hidden).
- [ ] *Open in Claude / ChatGPT*: a new chat opens with `Read from <https://…/html/…md> …`; open that `.md` link in a browser - it must show text (not download).
- [ ] PROD only: `http://` redirects to `https://`; `https://help.lighthouseindia.com/` forwards to `/docs/v7/`; `…:8888` does not answer from outside.

## 7. Rollback
| Situation | Action |
|---|---|
| Bad code release | copy the backed-up code files (§3.2) back over the web app folder, Ctrl+F5. Or deploy the previous tag's package: `git checkout v7.0.31`, build the package, install. |
| Bad settings | restore `config\app.properties` from `deploy/env`, Ctrl+F5. |
| Bad content | re-run `update_now.bat` after fixing the PDF; `html\` of one document can be deleted and rebuilt (it is only rebuilt when missing or older than its PDF). |
| nginx problem | restore the previous `nginx.conf`, `nginx.exe -s reload`. Tomcat still answers on its internal address. |
| Everything | the old V5 help keeps working untouched at `…:8888/LHS_ERP_HELP/` (internal). |
