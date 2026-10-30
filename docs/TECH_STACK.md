# Technology used

## Application (runs in the user's browser)
| Item | What / version | Why | Licence |
|---|---|---|---|
| HTML5, CSS3 (custom properties, grid, flex) | hand-written, `webapp/layout.html`, `webapp/css/app.css` | one page shell, light and dark themes | own code |
| JavaScript | plain ES5/ES2015 in one script `webapp/js/app.js`, no framework, no build step | menu, search, viewer, Reader, flags, "ask AI" | own code |
| **PDF.js** | 3.11.174 (UMD build) in `webapp/vendor/pdfjs/` | the Help Centre's own PDF viewer | Apache-2.0 (Mozilla) |
| Browser features used | `fetch`, `localStorage`, hash routing, `DOMParser`, Clipboard API | no plug-ins | - |
| Supported browsers | current Chrome, Edge, Firefox, Safari (desktop and phone) | | |
| Storage | the user's own browser (`localStorage`, keys prefixed `lhs7.`): theme, view, favourites, recents, pane width | no cookies, no accounts | - |
| Internet calls | none by itself. Only when a user clicks: ChatGPT / Claude (with the page link), the company site and e-invoice links in the footer | privacy | - |

## Web server (production)
| Item | What / version | Role |
|---|---|---|
| **Apache Tomcat** | 9.0.74 at `C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74` (Windows), listening on 8888 | serves the static web app folder `webapps\LHS_ERP_HELP_DOC_V7` (UAT: `LHS_ERP_HELP_DOC_V7_UAT`). Any static server would do; Tomcat is simply what already runs. |
| `WEB-INF/web.xml` | Servlet 3.1 descriptor | only adds the `md` and `webp` file types |
| **nginx** | stable (Windows zip or Linux package) | public front door: HTTPS, redirects, publishes only `/docs/v7/`, hides Tomcat |
| TLS certificate | Let's Encrypt (win-acme on Windows, certbot on Linux) or the company certificate | HTTPS |
| DNS | `help.lighthouseindia.com` → public IP (A record) | |
| Old V5 help | `LHS_ERP_HELP` application on the same Tomcat | untouched, internal only |

## Content tools (run on the maintenance PC or the server)
| Item | What / version | Role |
|---|---|---|
| Python | 3.8 or newer (developed and tested with 3.14) | runs `webapp/tools/*.py` |
| `build_v7.py` | standard library only | reads the PDF folder tree → `menu/v7-menu.json`, copies PDFs to `docs/`, writes CSV reports |
| `build_html.py` | **PyMuPDF** + **Pillow** (`pip install -r requirements.txt`) | PDF → Reader HTML + WebP screenshots (`html/`) |
| `build_md.py` | standard library only | Reader HTML → Markdown copy for the AI buttons |
| `auto_update.py` | standard library only | watches the folder, runs the three steps above |
| Windows `.bat` files | `update_now`, `auto_update`, `build_*`, `run_local` | one-click wrappers |
| Licence note | PyMuPDF is dual-licensed (AGPL-3.0 / commercial). It is used **only as an internal build tool**; it is not shipped or served. Confirm with the company's legal contact if the tools are ever distributed to third parties. | |

## Development tooling
| Item | Role |
|---|---|
| Git (private repository: GitHub / GitLab / Azure DevOps) | version control, pull requests, tags = releases |
| `scripts/check.py` | pre-commit checks (Python syntax, JS syntax with Node.js, version consistency, relative paths, config keys) |
| `scripts/set_version.py` | one place to set the version |
| `scripts/package_release.ps1` | builds the UAT / PROD deployment zip (Windows PowerShell 5.1+) |
| Node.js (optional) | only for the JS syntax check in `check.py` |
| Claude Code (optional) | AI-assisted development - rules in `CLAUDE.md` |

## Data volumes (production, October 2026)
332 PDFs · 9 modules · 58 groups · `docs/` ≈ 940 MB · `html/` ≈ 80 MB (332 pages + about 2,800 images) · app code ≈ 2 MB.
Allow **at least 3 GB** free on the Tomcat server for growth and the package copies.

## Minimum requirements
| Machine | Needs |
|---|---|
| User's PC / phone | any current browser, JavaScript on |
| Server | Windows or Linux, Tomcat 8.5+ (or any static web server), about 3 GB free disk, nginx for the public address |
| Maintenance PC / server (for adding documents) | Windows 10+, Python 3.8+, `pip install -r requirements.txt`, read access to the V7 PDF folder |
| Developer PC | the above + Git; Node.js 18+ optional |
