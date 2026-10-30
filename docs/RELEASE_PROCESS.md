# Release process (phases from idea to production)

```
 1 PLAN ──► 2 DEVELOP ──► 3 REVIEW ──► 4 PACKAGE ──► 5 UAT ──► 6 RELEASE ──► 7 AFTER
 request    feature/*     pull request   -Env uat      business    main + tag     monitor,
 + ticket   + check.py    into develop   deploy UAT    sign-off    -Env prod      changelog
```

## Phase 1 - Plan
* Write the request (what, why, who asked, example screen / document). One change = one branch.
* Decide the type: **content only** (new PDF) → no Git, see MAINTENANCE.md. **Code / design / tools / settings** → continue.

## Phase 2 - Develop (developer PC)
```
git checkout develop && git pull
git checkout -b feature/<short-name>
```
* Edit `webapp/` (rules in [CONTRIBUTING.md](../CONTRIBUTING.md); architecture in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)).
* Test: `webapp\tools\run_local.bat` - menu, PDF view, Reader view, dark mode, phone width, a missing document.
* `python scripts\check.py` → **ALL OK**.
* If css / js / layout changed: `python scripts\set_version.py 7.0.NN` and add a `## [7.0.NN]` section to `CHANGELOG.md`.
* Update the affected file in `docs/`.

## Phase 3 - Review
* Push the branch, open a pull request into `develop` (template checklist). A second person reads the diff and tries it.
* Merge when approved. `develop` now holds everything for the next release.

## Phase 4 - Package for UAT
```
git checkout develop && git pull
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env uat
```
Install it as described in [DEPLOYMENT.md §3.2](DEPLOYMENT.md). Content in UAT should be a copy of production content so testers see real documents.

## Phase 5 - UAT (business sign-off)
Testers use the UAT address and tick every line. Record the result in the pull request / ticket.

| # | Test | Pass |
|---|---|---|
| 1 | Menu shows all modules; codes and titles on one line; search finds a code and a word | |
| 2 | 3 documents from different modules open in PDF view; zoom, page box, fit width work | |
| 3 | The same 3 in Reader view; headings, steps, tables, screenshots; screenshot enlarges | |
| 4 | A document that does not exist shows *Document not available* | |
| 5 | Favourites, recents, previous / next, dark mode, phone width | |
| 6 | Buttons hidden / shown as agreed (Copy link, Print, Download) | |
| 7 | Open in Claude / ChatGPT starts a chat with the correct link and description | |
| 8 | **The feature or fix of this release works as described in the request** | |
| 9 | Nothing that worked before is broken (regression: tests 1-7) | |

Sign-off line: `UAT passed for 7.0.NN - <name>, <date>`. Failed → back to Phase 2 on the same branch.

## Phase 6 - Release to production
```
git checkout main && git pull
git merge --no-ff develop
python scripts\check.py
git tag -a v7.0.NN -m "Release 7.0.NN"
git push origin main --tags
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1 -Env prod
```
Back up the live code files, install the PROD package ([DEPLOYMENT.md §3.2](DEPLOYMENT.md)), run the verification checklist (§6 there).
Announce the release (what changed - copy from `CHANGELOG.md`). Production releases happen outside peak hours; no restart or downtime is normally needed.

## Phase 7 - After release
* Watch the site for a day (MAINTENANCE.md §5). Keep the backup of the previous code for at least two weeks.
* `git checkout develop && git merge main` so `develop` contains the tag.
* Close the ticket with the version number.

## Hotfix (urgent production bug)
```
git checkout main && git pull && git checkout -b hotfix/<name>
… fix, check.py, set_version.py (next patch), CHANGELOG …
pull request into main  →  quick UAT of the fix  →  merge, tag, package -Env prod, deploy
then merge main back into develop
```

## Versioning
`MAJOR.MINOR.PATCH` (now `7.0.x`). Every release increments PATCH; a group of new features raises MINOR. `VERSION` is the single source;
`scripts/set_version.py` writes it into `layout.html` (`app.css?v=` and `app.js?v=`), which is what makes browsers load the new files.
Git tags are `v<version>`. Never reuse a version number.

## Content releases (no Git)
New or changed PDFs are not code. They follow MAINTENANCE.md §2. If a content change also needs a tool change (for example a new Reader rule),
it is a code release.
