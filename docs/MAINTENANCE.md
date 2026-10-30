# Maintenance runbook

## 1. What is where
| Thing | Location | Backed up by |
|---|---|---|
| **Source PDFs** (the real content) | `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC\<NN-Module - ABBR>\<NN.NN-Group>\<code - title>.pdf` | file-server backup - **most important** |
| Code, tools, settings, docs | this Git repository | Git server |
| Live web app | Tomcat `webapps\LHS_ERP_HELP_DOC_V7` (generated `docs\ html\ menu\` inside) | rebuilt from PDFs; code from Git |
| nginx config and certificates | `C:\nginx\conf`, `C:\nginx\ssl` | copy of `deploy/nginx/*.conf` is in Git; keep a copy of the certificate files |
| Reports (documents needing attention) | `D:\LHS_ERP_HELP_V7_REPORT\*.csv` | regenerated at each update |
| Old V5 help | `D:\LHS_ERP_HELP`, Tomcat `LHS_ERP_HELP` | untouched, internal |

## 2. Routine tasks

### Add or replace a document
1. Put the PDF in the V7 folder, correct module / group folder, name `code - title.pdf`
   (code like `06.03.01.02`; a 2-part code such as `06.03` is the group's own document).
2. Run `webapp\tools\update_now.bat` on the PC / server that holds the web app (or leave `auto_update.bat` running; it acts about 30 seconds after the copy ends).
   It updates the menu, copies the PDF to `docs\`, builds the Reader page `html\….html` and the Markdown copy `….md`. **Already converted PDFs are skipped.**
3. If the tools ran on another PC, copy `docs\ html\ menu\` to the server (`robocopy … /E`).
4. Users press **F5**. No restart.

### Remove or rename a document
Delete / rename the PDF in the V7 folder, run the update. Old copies stay in `docs\` and `html\` until removed by hand: delete the matching
`docs\…\x.pdf`, `html\…\x.html` and `x.md` (names are the same as the PDF). Orphan screenshots in `html\_img\` are harmless (about 77 MB).

### Force a rebuild
Wrong Reader result after a rule change: `python webapp\tools\build_html.py --force` (all) or delete one `html\…\x.html` and run the update.
Changed `site.url`: `python webapp\tools\build_md.py --force`.

### Guide tab topics
Save the V7 PDF as `guide\<name>.pdf` (names in `webapp/guide/README.txt`: `AboutLighthouseERP`, `Concepts`, `Glossary`, `Lighthouse` …). No update needed.

### Show / hide a button
Edit the line in `deploy/env/<env>.app.properties`, commit, release (or emergency-edit `config\app.properties` on the server and copy the change back to Git). Ctrl+F5.

### Update documentation
Edit `docs/*.md` with the code change; keep `CHANGELOG.md` current.

## 3. Periodic tasks
| When | Task |
|---|---|
| each update | read `D:\LHS_ERP_HELP_V7_REPORT\v7_documents_needing_attention.csv` - fix wrongly named files, then run the update again |
| monthly | check free disk (`docs\` ≈ 940 MB and growing); check `nginx` and Tomcat logs for errors; open 3 random documents in both views |
| before the certificate expires (Let's Encrypt: every 60-90 days) | confirm automatic renewal worked (win-acme task / `certbot renew --dry-run`); browsers show the expiry in the padlock |
| quarterly | `pip list --outdated` for pymupdf / pillow - upgrade on a developer PC, run `build_html.py --force` into a test folder, compare a few pages, then roll out through UAT; check for a newer PDF.js 3.x security release |
| yearly | review who has access to the Git repository and the servers; test restoring the site from Git + the PDF backup on a spare machine |

## 4. Environment facts
* The site makes **no database or server calls**: it only reads files. Losing `docs\ html\ menu\` is not data loss - they are regenerated from the PDFs.
* Users' favourites / recents / theme live in their own browser; nothing to back up.
* The Help Centre is intentionally **public**: everything in `docs\` and `html\` can be opened by anyone with the link. Never put internal-only documents in the V7 folder.

## 5. Monitoring and logs
| What | How |
|---|---|
| Is the site up? | open `https://help.lighthouseindia.com/docs/v7/`; optional: an uptime service that checks this URL every 5 minutes |
| nginx | `C:\nginx\logs\access.log`, `error.log` |
| Tomcat | `...\apache-tomcat-9.0.74\logs\localhost_access_log.*.txt`, `catalina.*.log` |
| Content tools | console window of `update_now.bat`; `webapp\tools\auto_update.log` for the watcher; CSV reports in `D:\LHS_ERP_HELP_V7_REPORT` (`v7_all_documents`, `v7_coverage_by_group`, `v7_documents_needing_attention`) |
| Browser problems | press F12 → Console; ask the user for a screenshot of the message |

## 6. Troubleshooting
| Symptom | Likely cause → fix |
|---|---|
| Page shows old design after a release | browser cache → **Ctrl+F5**; check the `?v=` number in `layout.html` really changed |
| Menu is empty / "could not load menu" | `menu\v7-menu.json` missing → run `update_now.bat`; opened via `file://` → use the web address |
| A document says *Document not available* | the PDF is not in `docs\` → copy it into the V7 folder and update; or the file name does not follow the pattern (see attention report) |
| Reader switch offers only PDF | no `html\…\x.html` yet → run the update; one known PDF type can fail → see `build_html` message, PDF view still works |
| Screenshots in Reader do not show | `html\_img\` not copied to the server, or `webp` type missing → copy the folder; make sure `WEB-INF\web.xml` is deployed and Tomcat restarted once |
| `.md` link downloads a file / shows garbage | `md` file type missing → deploy `WEB-INF\web.xml`, restart Tomcat |
| ChatGPT / Claude cannot read the page | the site must be reachable from the internet; `site.url` must be the public address; open the `.md` link yourself to test; run `build_md.py --force` after changing `site.url` |
| `https://help…` shows nginx 502 | Tomcat stopped → start the Tomcat service; check `127.0.0.1:8888` |
| `…/docs/v7` loses styling | the address was opened without the trailing slash and not redirected → check the two `location = …` lines in nginx |
| Certificate warning | certificate expired → renew (win-acme / certbot), `nginx.exe -s reload` |
| Buttons you hid are back | `config\app.properties` was overwritten by a package built with the wrong `-Env`, or JS cached → fix the env file, redeploy, Ctrl+F5 |
| `update_now.bat`: "No module named fitz/pymupdf" | `pip install -r requirements.txt` |
| Update seems stuck on one PDF | each PDF is converted in its own process with a time limit; wait or press Ctrl+C and re-run - finished pages are kept |

## 7. Security notes
* No logins, no personal data, no secrets in the repository or the site. Do not add any.
* `config\app.properties` is readable by anyone who types its URL; it contains only on/off switches and the public address.
* Only nginx is public; Tomcat (8888) must stay closed to the internet. Keep nginx, Tomcat and Java patched.
* The "Open in ChatGPT / Claude" buttons only send a **link** (the page's public address); nothing else is sent by the page itself.
* Keep the repository **private** and limit access to people who maintain the site.

## 8. Contacts and ownership
Who owns what (RACI), the duties of each team and the contacts table are in [TEAM_RESPONSIBILITIES.md](TEAM_RESPONSIBILITIES.md). Fill in the names there.
