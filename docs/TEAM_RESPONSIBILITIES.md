# Team responsibilities

Who owns what for **lhs-erp-v7-help-doc-app** (Lighthouse ERP V7 Help Centre). Fill in the names in section 7 on handover day.

## 1. Teams and their one-line mission

| Team | Mission |
|---|---|
| **Development team** | Owns the source code, the content tools and the documentation of the repository. Builds, tests and packages every release. |
| **DevOps / Infrastructure team** | Owns the servers (Tomcat, nginx), DNS, HTTPS certificate, deployment, backups, monitoring and security patches. |
| **Content / Documentation team** | Owns the V7 user-guide PDFs (the real content) and decides what is published. |
| **QA / UAT (business testers)** | Test every release on UAT and give the written sign-off. |
| **Product owner** | Decides what changes are made and when; approves production release. |

## 2. RACI matrix

R = does the work, A = accountable (final say, one per row), C = consulted, I = informed.

| Activity | Dev | DevOps | Content | QA / UAT | Product owner |
|---|---|---|---|---|---|
| Source code, `webapp/`, `scripts/`, `deploy/` in Git | **A/R** | C | | | I |
| Code review and merge to `main` | **A/R** | | | | I |
| New feature / change request decision | C | C | C | | **A/R** |
| Version number, tag, CHANGELOG | **A/R** | I | | | I |
| Build the release package (`package_release.ps1`) | **A/R** | I | | | |
| Deploy to UAT | C | **A/R** | | I | |
| UAT testing and sign-off | I | | C | **R** | **A** |
| Deploy to Production (code release) | C | **A/R** | | I | A (approval) |
| Rollback decision and execution | C | **A/R** | | | I |
| nginx configuration (`deploy/nginx/`) in Git | R | **A** (applies it) | | | |
| Tomcat, Java, OS and nginx patching | | **A/R** | | | I |
| DNS record `help.lighthouseindia.com` | | **A/R** | | | I |
| HTTPS certificate request and renewal | | **A/R** | | | I |
| Firewall: only 80/443 public, 8888 closed to internet | | **A/R** | | | I |
| Backups of server content and restore test | | **A/R** | C | | I |
| Monitoring and availability alerts | | **A/R** | | | I |
| Source PDFs (`V7_MENU_HELP_DOC`) - create, update, back up | | C (backup) | **A/R** | | C |
| Add / replace PDFs on the server (`update_now.bat`) | | R | **A** | | |
| Content accuracy of the guides | | | **A/R** | C | I |
| Fixing a Reader-view conversion problem | **A/R** | | C | | |
| Documentation in `docs/` kept current | **A/R** | C (deploy / ops docs) | | | |
| Git repository access and branch protection | **A/R** | C | | | I |
| Incident: site down / wrong content | C | **A/R** (site) | **R** (content) | | I |

## 3. Development team

**Owns:** the Git repository, code quality, releases, developer documentation.

Responsibilities
1. Work only through branches and pull requests (`feature/...` from `develop`); never commit straight to `main` ([CONTRIBUTING.md](../CONTRIBUTING.md)).
2. Run `python scripts\check.py` before every commit; it must print `RESULT: ALL OK`.
3. Update [CHANGELOG.md](../CHANGELOG.md) and the affected document in `docs/` in the same commit as the change.
4. Bump the version with `python scripts\set_version.py X.Y.Z` for every release (this also refreshes the browser cache number).
5. Build the UAT and production packages, test them on a clean folder, and hand them to DevOps with the release notes.
6. Fix defects found in UAT or production; for a production bug use the hotfix flow in [RELEASE_PROCESS.md](RELEASE_PROCESS.md).
7. Keep the Excel deployment checklist script (`scripts/build_checklist_xlsx.py`) in line with the real deployment steps.
8. Answer "how does X work" questions with the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md); improve it when it is wrong or incomplete.

Hands over to DevOps: the package zip, the version number, the changelog entry, any change to `deploy/` files or settings.

## 4. DevOps / Infrastructure team

**Owns:** everything that runs on a server or on the network.

Responsibilities
1. **Servers.** Tomcat 9 web app `LHS_ERP_HELP_DOC_V7` (and `LHS_ERP_HELP_DOC_V7_UAT` on UAT) next to the untouched V5 `LHS_ERP_HELP`. Do not change `conf\server.xml`.
2. **Deploy** by following [DEPLOYMENT.md](DEPLOYMENT.md) and the Excel checklist `LHS_ERP_HELP_DOC_V7_Deployment_Checklist.xlsx`. Code releases are unzipped over the web app; they never contain `docs/`, `html/` or `menu/`, so published documents stay.
3. **nginx** public front door: apply `deploy/nginx/help.lighthouseindia.com.conf` (`/docs/v7/` to `http://127.0.0.1:8888/LHS_ERP_HELP_DOC_V7/`). Only 80/443 are public; **port 8888 must never be reachable from the internet**.
4. **DNS and HTTPS:** keep the record for `help.lighthouseindia.com` and the certificate valid; renew before expiry.
5. **Settings per environment:** production uses `deploy/env/prod.app.properties` (it contains `site.url=https://help.lighthouseindia.com/docs/v7/`). Confirm it after every deployment.
6. **Backups:** daily copy of the webapp folder `docs/`, `html/` and `config/` (content is rebuildable from the source PDFs, but the build takes time). Test a restore once per quarter.
7. **Monitoring:** alert if `https://help.lighthouseindia.com/docs/v7/` or `.../html/<any>.md` does not answer 200; watch disk space (the app is about 1 GB and grows with new PDFs).
8. **Security:** patch Java, Tomcat, nginx and the OS; keep the repository private; no secrets in the repository or the site ([MAINTENANCE.md](MAINTENANCE.md) section 7).
9. **Rollback:** keep the previous release package; follow DEPLOYMENT.md section 7 when a release must be undone.
10. Run the verification list (DEPLOYMENT.md section 6) after every deployment and report the result to the product owner.

## 5. Content / Documentation team

**Owns:** the PDF guides, not the code.

1. Keep the master copy in `D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC` (or its successor) and back it up.
2. Follow the naming rule `NN-Module - ABBR \ NN.NN-Group \ code - title.pdf`: the menu is built from these names ([DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) section on content).
3. To publish: copy the new / changed PDF into the right folder and run `webapp\tools\update_now.bat` on the server (DevOps may do this on request). Only new / changed PDFs are converted.
4. Check the Reader view of every new guide once; report a layout problem to the Development team with the PDF name.
5. Remember that the guides are public on the internet and are read by ChatGPT / Claude through the generated `.md` copies: do not put passwords, customer data or internal-only text in a PDF.

## 6. QA / UAT and Product owner

* **QA / UAT:** test every release on UAT with the checklist in [RELEASE_PROCESS.md](RELEASE_PROCESS.md) phase 5 (menu, search, PDF and Reader view, Copy page for AI, Open in ChatGPT / Claude, light / dark theme, phone width). Give a written pass / fail.
* **Product owner:** approves the scope of each release and the production go-live; decides priorities of change requests.

## 7. Contacts (fill in on handover)

| Role | Team | Name | Phone / e-mail |
|---|---|---|---|
| Product owner | | | |
| Lead developer | Development | | |
| Backup developer | Development | | |
| DevOps lead | DevOps | | |
| Server / nginx admin | DevOps | | |
| DNS / domain owner (lighthouseindia.com) | DevOps | | |
| Content owner | Content | | |
| UAT lead | QA | | |

## 8. Escalation

| Problem | First call | Then |
|---|---|---|
| Site not opening / error 502 / 404 | DevOps | Development (if after a release) |
| Wrong or outdated guide text | Content | Product owner |
| Page looks broken, button missing, Reader layout wrong | Development | |
| Certificate warning in the browser | DevOps | |
| Need to add a feature | Product owner | Development |
