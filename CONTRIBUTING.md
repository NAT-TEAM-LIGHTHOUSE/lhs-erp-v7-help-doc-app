# Contributing

Short rules so every change is traceable from idea to production. Details of the release flow: [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md).

## Branches
| Branch | Meaning | Who merges |
|---|---|---|
| `main` | **what is in production** (every commit on `main` is a tagged release) | maintainer only, after UAT sign-off |
| `develop` | integrated work being tested in UAT | after review |
| `feature/<short-name>` | one change, from `develop` (e.g. `feature/robots-txt`) | pull request into `develop` |
| `hotfix/<short-name>` | urgent production fix, from `main` | pull request into `main` **and** `develop` |

Never commit directly to `main`.

## Day-to-day
1. `git checkout develop && git pull` → `git checkout -b feature/<name>`
2. Change the code in `webapp/` (see [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) §8-9 and the recipes).
3. Test locally: `webapp\tools\run_local.bat` - menu, a PDF, Reader view, dark mode, phone width (about 400 px).
4. `python scripts\check.py` must say **ALL OK**.
5. If `webapp/css`, `webapp/js` or `webapp/layout.html` changed: `python scripts\set_version.py 7.0.NN` and add a
   section at the top of `CHANGELOG.md` (browsers keep the old files until the number changes).
6. Commit, push the branch, open a pull request into `develop` (the template lists the checklist).

## Commit messages
`type: short summary` - types: `feat`, `fix`, `ui`, `tools`, `docs`, `deploy`, `chore`.
Examples: `fix: reader tables lose first column`, `deploy: nginx gzip for markdown`.

## Version numbers
`MAJOR.MINOR.PATCH`, currently `7.0.x`: PATCH for every released change, MINOR for a new feature set, MAJOR for the ERP generation.
The single source is the file `VERSION`; `scripts/set_version.py` copies it into `layout.html`.

## Rules of the codebase
* No frameworks and no CDN: everything the page needs is inside `webapp/`. No server-side code.
* **Relative links only** (`css/app.css`, never `/css/app.css`): the site is served under `/docs/v7/` in production.
* Never edit generated files (`webapp/docs/`, `webapp/html/`, `webapp/menu/v7-menu.json`) - change the rules in `webapp/tools/*.py` and rebuild.
* Never commit PDFs, generated folders, certificates or passwords (the project has no secrets).
* One stylesheet (`css/app.css`) and one script (`js/app.js`): keep the existing section order and naming style.
