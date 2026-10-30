# Documentation index

| Document | Read it when you want to ... |
|---|---|
| [../README.md](../README.md) | understand the project in one page and start working |
| [HANDOVER.md](HANDOVER.md) | **hand the project to a new Dev / DevOps team**: what is delivered, day-one steps, acceptance |
| [TEAM_RESPONSIBILITIES.md](TEAM_RESPONSIBILITIES.md) | see who owns what: Dev, DevOps, Content, QA, Product owner (RACI), contacts, escalation |
| [DEPLOYMENT.md](DEPLOYMENT.md) | **install / update UAT and Production**, verify, roll back |
| [RELEASE_PROCESS.md](RELEASE_PROCESS.md) | know how a change travels: branch → review → UAT → production; hotfixes; versioning |
| [MAINTENANCE.md](MAINTENANCE.md) | run the site day to day: add documents, certificates, backups, monitoring, troubleshooting |
| [TECH_STACK.md](TECH_STACK.md) | see every technology, its version and licence, and what each server needs |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | learn the features, architecture, content naming rules, source code and recipes in depth |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | follow the branch / commit / version rules |
| [../CLAUDE.md](../CLAUDE.md) | brief an AI assistant that helps with development |
| [../CHANGELOG.md](../CHANGELOG.md) | see what changed in each version |

Keep these documents in the same commit as the change they describe.

**One-page HTML version** of everything (with search box and the complete source code): `python scripts/build_docs_html.py` → `dist/docs/lhs-erp-v7-help-doc-app_documentation.html` (needs `pip install markdown`).

**Deployment checklist (Excel)** with live progress summary, for every release: `python scripts/build_checklist_xlsx.py` → `dist/LHS_ERP_HELP_DOC_V7_Deployment_Checklist.xlsx` (needs `pip install openpyxl`). Review the items in `scripts/build_checklist_xlsx.py` when the deployment steps change.
