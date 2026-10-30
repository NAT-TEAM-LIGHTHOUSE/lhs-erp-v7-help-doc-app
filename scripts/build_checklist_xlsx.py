"""
Builds the deployment checklist workbook (Excel) for one release.

    python scripts\\build_checklist_xlsx.py [output.xlsx]

Default output: dist\\LHS_ERP_HELP_DOC_V7_Deployment_Checklist.xlsx   (needs: pip install openpyxl)
Sheets: Summary (live progress), 1 Pre-Deployment, 2 Tomcat Deploy, 3 nginx and Network, 4 Verification,
        5 Rollback and Sign-off, Reference. Tick each row by choosing a Status from the drop-down.
"""
import datetime
import os
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = open(os.path.join(ROOT, 'VERSION'), encoding='ascii').read().strip()
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'LHS_ERP_HELP_DOC_V7_Deployment_Checklist.xlsx')

FONT = 'Arial'
RED, DARK, GREY, LIGHT = 'C8102E', '1F2937', 'F3F4F6', 'FDECEF'
thin = Side(style='thin', color='D1D5DB')
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
STATUSES = ['Pending', 'Done', 'N/A', 'Blocked', 'Failed']


def L(*lines):
    return '\n'.join(lines)


def f(bold=False, size=10, color='000000', italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def fill(c):
    return PatternFill('solid', start_color=c, end_color=c)


TOM = r'C:\APP_SERVER_TOMCAT\apache-tomcat-9.0.74'
REL = r'D:\LHS_ERP_HELP_DOC_V7_FINAL'
INT = 'http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/layout.html'
PUB = 'https://help.lighthouseindia.com/docs/v7/'
MD = '01-Master%20Data%20Management%20-%20MDM/01.01-Accounts%20Classification%20Master%20Setup/01.01.07.01%20-%20Posting%20Master.md'

# ---------------------------------------------------------------- checklist content
# (id, task, how, expected, owner)      ('#', 'Section title') rows are section bands
PRE = [
    ('#', 'A. Decide and confirm (before the deployment window)'),
    ('1.01', 'Confirm deployment date, time window and the people needed',
     L('Deployer, server administrator, network / router owner, DNS (domain) owner, business approver.', 'Write names and phone numbers in the Reference sheet.'),
     'Everyone is available during the window.', 'Project lead'),
    ('1.02', 'Confirm what is deployed tomorrow',
     L(r'PRODUCTION web app folder: LHS_ERP_HELP_DOC_V7 (checked internally first, then made public through nginx).',
       r'If UAT first: use the UAT package and folder LHS_ERP_HELP_DOC_V7_UAT instead (see Reference sheet).'),
     'Decision recorded in Remarks (PROD or UAT).', 'Project lead'),
    ('1.03', 'Management confirms that every document in the Help Centre may be public',
     'All 332 PDFs and Reader pages become openable by anyone with the link (the Help Centre is intentionally public).',
     'Approval received (name/date in Remarks).', 'Business owner'),
    ('1.04', 'Release folder is complete on the build PC',
     L(rf'Open {REL}', r'Check: 01_DEPLOY_THIS_FOLDER\LHS_ERP_HELP_DOC_V7 , 02_PACKAGES (3 zip files) , 03_DOCUMENTATION (html + this checklist).',
       r'Open 01_DEPLOY_THIS_FOLDER\LHS_ERP_HELP_DOC_V7\VERSION.txt'),
     f'VERSION.txt reads "lhs-erp-v7-help-doc-app {VERSION} (prod)".', 'Deployer'),
    ('1.05', 'Git repository pushed (private) and tagged',
     L('Repository name: lhs-erp-v7-help-doc-app (private).', f'git tag v{VERSION} pushed (commands: README.md, "First push").'),
     'Code and docs are safely stored in Git.', 'Developer'),
    ('#', 'B. Prepare the server'),
    ('1.06', 'Remote access to the server works with administrator rights',
     r'RDP / console access; can create folders under ' + TOM + r'\webapps and restart the Tomcat service.',
     'Logged in successfully.', 'Server admin'),
    ('1.07', 'Free disk space on the Tomcat drive is at least 3 GB',
     L('The content is about 1 GB (docs 941 MB + html 74 MB). Check in Explorer: drive > Properties.'),
     'At least 3 GB free. Note the value in Remarks.', 'Server admin'),
    ('1.08', 'Tomcat is running and the OLD V5 help works (baseline)',
     L(r'Open http://192.168.100.21:8888/LHS_ERP_HELP/', 'It must stay unchanged by this deployment. Note the Tomcat Windows service name.'),
     'V5 help opens normally.', 'Server admin'),
    ('1.09', 'The folder LHS_ERP_HELP_DOC_V7 does NOT exist yet under webapps (or you know what is in it)',
     rf'Look in {TOM}\webapps . If it exists, rename it to LHS_ERP_HELP_DOC_V7_OLD_<date> first.',
     'Clean target.', 'Server admin'),
    ('1.10', 'Decide how the release folder reaches the server',
     L(r'Network share / USB drive / RDP drive redirection / zip then copy. The folder is about 1 GB (3,834 files).',
       'Copying a single zip is faster than many small files: zip the folder on the build PC if the network is slow.'),
     'Method agreed.', 'Deployer'),
    ('1.11', 'Public access prerequisites are known (needed only for the nginx part, sheet 3)',
     L('Static public IP of the server: ______  (note in Reference sheet).', 'Router / firewall login available.', 'DNS panel for lighthouseindia.com available.',
       'Decide the certificate method: win-acme (free Let\'s Encrypt) or the company certificate.'),
     'All four answered. If any is missing, deploy internally tomorrow and make it public later.', 'Network admin'),
]

TOMCAT = [
    ('#', 'A. Copy the web app to Tomcat'),
    ('2.01', 'Open the Tomcat webapps folder on the server', rf'{TOM}\webapps', 'Folder open.', 'Deployer'),
    ('2.02', 'Create the NEW folder  LHS_ERP_HELP_DOC_V7',
     L(r'Do NOT touch the existing LHS_ERP_HELP folder (old V5 help).', r'Do NOT change conf\server.xml.'),
     'Empty folder exists.', 'Deployer'),
    ('2.03', 'Copy docs and html first (the big folders)',
     L(rf'From: {REL}\01_DEPLOY_THIS_FOLDER\LHS_ERP_HELP_DOC_V7\docs  and  ...\html  and  ...\menu',
       rf'To:   {TOM}\webapps\LHS_ERP_HELP_DOC_V7',
       r'Command example (run on the server):',
       rf'robocopy "<source>\LHS_ERP_HELP_DOC_V7" "{TOM}\webapps\LHS_ERP_HELP_DOC_V7" /E'),
     'Copy finishes without errors.', 'Deployer'),
    ('2.04', 'Copy the remaining files and folders',
     r'layout.html, index.html, README.txt, VERSION.txt, css, js, images, vendor, WEB-INF, config, guide, tools  (the robocopy above already includes them).',
     'All items present in the target folder.', 'Deployer'),
    ('2.05', 'Verify the copy is complete',
     L(r'PowerShell on the server:',
       rf'cd {TOM}\webapps\LHS_ERP_HELP_DOC_V7',
       r'(Get-ChildItem docs -Recurse -Filter *.pdf).Count',
       r'(Get-ChildItem html -Recurse -Filter *.html | ? {$_.FullName -notmatch "_img"}).Count',
       r'(Get-ChildItem html -Recurse -Filter *.md).Count',
       r'(Get-ChildItem html\_img).Count'),
     'PDFs = 332,  Reader html = 332,  md = 332,  images = 2814.', 'Deployer'),
    ('2.06', 'Check the key files', r'WEB-INF\web.xml exists;  config\app.properties has  site.url=https://help.lighthouseindia.com/docs/v7/ ;  VERSION.txt reads 7.0.32 (prod).',
     'All three confirmed.', 'Deployer'),
    ('#', 'B. Start and test internally'),
    ('2.07', 'Restart the Tomcat service once',
     L('Reason: WEB-INF\\web.xml (file types md and webp) is read at start.', 'Services > Apache Tomcat > Restart  (or bin\\shutdown.bat then bin\\startup.bat).'),
     'Tomcat is running again; V5 help still opens.', 'Server admin'),
    ('2.08', 'Open the new Help Centre internally', L(INT, 'Press Ctrl+F5 once.'), 'Home page, logo and menu with 9 modules appear.', 'Deployer'),
    ('2.09', 'Check the old V5 help still works', r'http://192.168.100.21:8888/LHS_ERP_HELP/', 'V5 opens exactly as before.', 'Deployer'),
    ('2.10', 'Markdown pages are served as text',
     L(f'Open: http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/html/{MD}'), 'Text is displayed in the browser (it must not download a file).', 'Deployer'),
    ('2.11', 'Screenshots (webp) load', 'Open any document > Reader view.', 'Screenshots are visible.', 'Deployer'),
    ('2.12', 'Folders are not listed in the browser',
     L('Open  .../LHS_ERP_HELP_DOC_V7/docs/   and   .../LHS_ERP_HELP_DOC_V7/config/'), 'No file listing is shown (404 or an empty/forbidden page).', 'Deployer'),
    ('#', 'C. Content updater on the server (optional - can be done after go-live)'),
    ('2.13', 'Install Python 3.8+ and the PDF libraries on the machine that will update documents',
     L('python --version', 'pip install pymupdf pillow'), 'Both commands succeed.', 'Server admin'),
    ('2.14', 'Test one update run (only if the V7 PDF folder is reachable from the server)',
     L(r'Double-click tools\update_now.bat   (default source folder D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC; other: update_now.bat "D:\path")',
       'Run it twice: the second run must convert 0 documents.'), 'Finishes with "Done". Menu and pages unchanged.', 'Server admin'),
    ('2.15', 'Optional: start the automatic updater with Windows',
     r'Put a shortcut to tools\auto_update.bat in  shell:startup .', 'Shortcut created.', 'Server admin'),
]

NGINX = [
    ('#', 'A. Prerequisites (public access)'),
    ('3.01', 'Ports 80 and 443 are free on the machine that will run nginx',
     r'netstat -ano | findstr ":80 :443"     (if IIS or another program uses them, stop or move it)', 'No program is listening on 80 / 443.', 'Server admin'),
    ('3.02', 'Download nginx (stable, Windows zip) from nginx.org and unzip to C:\\nginx',
     'Use the official site only. Note the version in Remarks.', 'C:\\nginx\\nginx.exe exists.', 'Server admin'),
    ('3.03', 'DNS: create the record in the lighthouseindia.com DNS panel',
     L('Type A   Name: help   Value: <public IP>   (or CNAME if the host gave a name).', 'Check:  nslookup help.lighthouseindia.com'),
     'The name resolves to the public IP (may take a few minutes).', 'DNS owner'),
    ('3.04', 'Router / firewall: forward TCP 80 and 443 to the nginx machine',
     L('Also allow inbound 80 and 443 in Windows Firewall.', 'Do NOT forward port 8888 (Tomcat stays internal).'),
     'Ports 80 and 443 reach the server from outside.', 'Network admin'),
    ('3.05', 'Get the HTTPS certificate BEFORE starting nginx',
     L('win-acme (wacs.exe): create a certificate for help.lighthouseindia.com (needs DNS + port 80 reachable and free), or use the company certificate.',
       r'Save as C:\nginx\ssl\fullchain.pem and C:\nginx\ssl\privkey.pem (names used in the config).'),
     'Both files exist. Expiry date noted in Remarks.', 'Server admin'),
    ('#', 'B. Configure and start nginx'),
    ('3.06', 'Put the server blocks into nginx.conf',
     L(r'Source: repository file deploy\nginx\help.lighthouseindia.com.conf  (also in the final folder: 02_PACKAGES source zip and the HTML documentation).',
       r'Paste the two server { } blocks inside http { } of C:\nginx\conf\nginx.conf (keep the existing events{} / http{} settings and mime.types).'),
     'File saved.', 'Server admin'),
    ('3.07', 'Check the two values in the config',
     L('proxy_pass http://127.0.0.1:8888/LHS_ERP_HELP_DOC_V7/;',
       'Works because nginx runs on the SAME machine as Tomcat. If nginx runs on another machine, use http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/ instead.',
       'ssl_certificate paths match step 3.05.'),
     'Both values correct.', 'Server admin'),
    ('3.08', 'Test the configuration', r'C:\nginx\nginx.exe -t', 'Message: "test is successful".', 'Server admin'),
    ('3.09', 'Start nginx', r'start C:\nginx\nginx.exe      (later changes: nginx.exe -s reload)', r'nginx.exe appears in Task Manager; no error in C:\nginx\logs\error.log.', 'Server admin'),
    ('3.10', 'Make nginx start with Windows', 'NSSM service or a Task Scheduler task "At startup" running C:\\nginx\\nginx.exe.', 'Verified after the next reboot (or scheduled for it).', 'Server admin'),
    ('#', 'C. Test from outside the office network (use a phone on mobile data)'),
    ('3.11', 'Public address opens', PUB, 'Help Centre loads with a valid padlock (no certificate warning).', 'Deployer'),
    ('3.12', 'HTTP redirects to HTTPS', 'http://help.lighthouseindia.com', 'Browser ends on https://...', 'Deployer'),
    ('3.13', 'Root address forwards', 'https://help.lighthouseindia.com/', 'Ends on https://help.lighthouseindia.com/docs/v7/', 'Deployer'),
    ('3.14', 'Address without trailing slash is corrected', 'https://help.lighthouseindia.com/docs/v7', 'Ends on .../docs/v7/ with the normal design.', 'Deployer'),
    ('3.15', 'Tomcat port is NOT reachable from outside', 'From the phone: http://<public IP>:8888/', 'Connection fails / times out.', 'Deployer'),
    ('3.16', 'Other paths are not published', 'https://help.lighthouseindia.com/anything', '404 Not Found.', 'Deployer'),
    ('3.17', 'Certificate renewal is automatic', 'win-acme scheduled task exists (Task Scheduler) or the company renewal date is in the calendar.', 'Renewal date / task noted in Remarks.', 'Server admin'),
]

VERIFY = [
    ('#', 'A. Functional tests - run on the INTERNAL address first, then repeat the starred (*) tests on the PUBLIC address'),
    ('4.01', 'Home page and menu', 'Logo, title "Lighthouse ERP Help Centre", 9 modules in the menu, menu codes shown as badges on one line.', 'As described.', 'Tester'),
    ('4.02', 'Search *', 'Search the code 06.03.01.02, then the word  freight.', 'Matching documents are listed; clicking opens them.', 'Tester'),
    ('4.03', 'PDF view *', 'Open 01.01.07.01 Posting Master. Scroll, zoom + / -, Fit width, type a page number.', 'Pages draw (11 pages); controls work; no black browser viewer.', 'Tester'),
    ('4.04', 'Reader view *', 'Click the Reader switch on the same document. Click a screenshot to enlarge.', 'Headings, numbered steps, tables and screenshots show; "On this page" outline works.', 'Tester'),
    ('4.05', 'Three more documents from different modules', 'Open one from each of 3 modules in both views (note them in Remarks).', 'All open; no error.', 'Tester'),
    ('4.06', 'Missing document page', 'Open the Guide tab and click a topic.', '"Document not available" page appears (V7 guide PDFs are not added yet).', 'Tester'),
    ('4.07', 'Favourites, recent, previous / next', 'Star a document; reload; use the arrows.', 'All work and are remembered.', 'Tester'),
    ('4.08', 'Dark mode', 'Toggle the theme; reload.', 'Theme changes and is remembered; text readable.', 'Tester'),
    ('4.09', 'Phone / narrow screen *', 'Open the site on a phone.', 'Menu opens by default; documents are readable.', 'Tester'),
    ('4.10', 'Hidden buttons', 'Look at the document toolbar.', 'Copy link, Print and Download are NOT shown; Save (star) and Copy page for AI are shown.', 'Tester'),
    ('4.11', 'Copy page for AI > Copy', 'Click Copy page for AI > Copy, paste into Notepad.', 'Title, menu code, Page link, PDF link, then the text and tables (no screenshots).', 'Tester'),
    ('4.12', 'Open in Claude *', 'Click Open in Claude.', f'A new tab opens with: Read from {PUB}html/....md so I can ask questions about it. (link + one line, no long text).', 'Tester'),
    ('4.13', 'Open in ChatGPT *', 'Click Open in ChatGPT.', 'Same prompt as above.', 'Tester'),
    ('4.14', 'The .md link opens as text *', 'Open the link from 4.12 in a browser tab (public address only).', 'Plain text of the page is displayed.', 'Tester'),
    ('4.15', 'Ask the AI a question', 'In Claude or ChatGPT ask: "What are the steps to create a Posting Master?"', 'The AI reads the page and answers from it (depends on the AI service being able to open the link).', 'Tester'),
    ('4.16', 'No errors in the browser console', 'Press F12 > Console while opening a document.', 'No red errors.', 'Tester'),
    ('4.17', 'Browsers', 'Repeat 4.01 - 4.04 in Chrome and Edge (and Safari / Firefox if available).', 'Same result in each.', 'Tester'),
    ('4.18', 'New version is loaded', 'F12 > Network > reload with Ctrl+F5: look at app.js.', f'Request is app.js?v={VERSION}.', 'Tester'),
    ('4.19', 'Speed', 'Open a large PDF and a Reader page with many screenshots.', 'Usable within a few seconds on the office network.', 'Tester'),
    ('4.20', 'Old V5 help untouched', 'http://192.168.100.21:8888/LHS_ERP_HELP/', 'Still works.', 'Tester'),
]

ROLLBACK = [
    ('Problem found after deployment', 'What to do'),
    ('New Help Centre misbehaves (internal only)', rf'Nothing to restore: it is a separate folder. Stop the test, fix, copy the corrected files over {TOM}\webapps\LHS_ERP_HELP_DOC_V7 and press Ctrl+F5. The V5 help is unaffected.'),
    ('Need to take the new site offline quickly', rf'Rename {TOM}\webapps\LHS_ERP_HELP_DOC_V7 to LHS_ERP_HELP_DOC_V7_OFF (the public address then shows an error; V5 keeps working).'),
    ('Public address broken or certificate problem', r'Stop nginx: C:\nginx\nginx.exe -s stop. Tomcat and the internal address keep working. Fix the certificate / config, nginx -t, start again.'),
    ('Wrong button settings or wrong site address', r'Edit config\app.properties on the server (or copy deploy\env\prod.app.properties), press Ctrl+F5. If site.url changed run: python tools\build_md.py --force'),
    ('A single document looks wrong', r'Delete its html\...\<name>.html and .md on the server, run tools\update_now.bat (or re-copy the files from the release folder).'),
    ('Whole deployment must be removed', r'Stop nginx (or remove the nginx config + reload), delete the DNS record, delete the folder LHS_ERP_HELP_DOC_V7. Old V5 help is untouched throughout.'),
]

REFERENCE = [
    ('Item', 'Value', 'Notes'),
    ('Project / Git repository', 'lhs-erp-v7-help-doc-app', 'Private repository'),
    ('Release version', VERSION, 'Also in VERSION.txt and app.js?v='),
    ('Tomcat web app folder (PROD)', rf'{TOM}\webapps\LHS_ERP_HELP_DOC_V7', 'New folder; the old LHS_ERP_HELP is not touched'),
    ('Tomcat web app folder (UAT, optional)', rf'{TOM}\webapps\LHS_ERP_HELP_DOC_V7_UAT', 'Use package ..._uat.zip'),
    ('Internal address (PROD)', INT, ''),
    ('Public address', PUB, 'Trailing slash required'),
    ('Release folder (build PC)', REL, '01 = copy this, 02 = packages, 03 = documentation'),
    ('Folder to copy to the server', rf'{REL}\01_DEPLOY_THIS_FOLDER\LHS_ERP_HELP_DOC_V7', 'about 1 GB, 3,834 files'),
    ('Code-only packages', rf'{REL}\02_PACKAGES', 'prod / uat zips (code + settings only) and the source zip'),
    ('Documentation (HTML)', rf'{REL}\03_DOCUMENTATION\lhs-erp-v7-help-doc-app_documentation.html', 'Open in any browser'),
    ('PDF source folder (content)', r'D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC', 'Back this up - it is the real content'),
    ('nginx folder', r'C:\nginx', r'config: C:\nginx\conf\nginx.conf, certificates: C:\nginx\ssl'),
    ('nginx config template', r'deploy\nginx\help.lighthouseindia.com.conf (in the repository)', ''),
    ('Content update (one click)', r'tools\update_now.bat', 'Adds new / changed PDFs: menu, docs, Reader pages, Markdown'),
    ('Server public IP', '', 'FILL IN'),
    ('Tomcat Windows service name', '', 'FILL IN'),
    ('Contact - project lead', '', 'FILL IN name / phone'),
    ('Contact - server administrator', '', 'FILL IN'),
    ('Contact - network / router', '', 'FILL IN'),
    ('Contact - DNS / domain owner', '', 'FILL IN'),
    ('Contact - business approver', '', 'FILL IN'),
]


# ---------------------------------------------------------------- builders
def title_row(ws, text, sub, cols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=cols)
    ws['A1'] = text
    ws['A1'].font = f(True, 14, 'FFFFFF')
    ws['A1'].fill = fill(RED)
    ws['A1'].alignment = Alignment(vertical='center', indent=1)
    ws.row_dimensions[1].height = 28
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cols)
    ws['A2'] = sub
    ws['A2'].font = f(False, 9, '4B5563', True)
    ws['A2'].alignment = Alignment(wrap_text=True, vertical='center', indent=1)
    ws.row_dimensions[2].height = 28


def checklist_sheet(wb, name, title, sub, rows, owners=True):
    ws = wb.create_sheet(name)
    heads = ['#', 'Task', 'How / details', 'Expected result', 'Owner', 'Status', 'Done on (date / time)', 'Remarks / evidence']
    title_row(ws, title, sub, len(heads))
    for c, h in enumerate(heads, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = f(True, 10, 'FFFFFF')
        cell.fill = fill(DARK)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[4].height = 24
    widths = [7, 38, 62, 40, 15, 12, 18, 36]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = w
    r = 5
    for row in rows:
        if row[0] == '#':
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(heads))
            c = ws.cell(row=r, column=1, value=row[1])
            c.font = f(True, 10, DARK)
            c.fill = fill(LIGHT)
            c.alignment = Alignment(vertical='center', indent=1)
            ws.row_dimensions[r].height = 22
            r += 1
            continue
        num, task, how, exp, owner = row
        vals = [num, task, how, exp, owner, 'Pending', None, None]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = f(c == 2)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical='top', horizontal='center' if c in (1, 5, 6, 7) else 'left')
        ws.cell(row=r, column=7).number_format = 'dd-mmm-yyyy hh:mm'
        ws.cell(row=r, column=6).font = f(True)
        for c in (5, 6, 7, 8):                     # cells the user fills in
            ws.cell(row=r, column=c).fill = fill('FFFBEB')
        longest = max(len(str(how)) / 62, len(str(exp)) / 40, len(task) / 38, how.count('\n') + 1 if how else 1)
        ws.row_dimensions[r].height = min(max(30, 14 * (int(longest) + 1)), 150)
        r += 1
    last = r - 1
    dv = DataValidation(type='list', formula1='"%s"' % ','.join(STATUSES), allow_blank=False, showErrorMessage=True,
                        errorTitle='Status', error='Choose: ' + ', '.join(STATUSES))
    ws.add_data_validation(dv)
    dv.add('F5:F%d' % last)
    rng = 'F5:F%d' % last
    ws.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Done"'], fill=fill('C6EFCE'), font=Font(name=FONT, bold=True, color='006100')))
    ws.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Failed"'], fill=fill('FFC7CE'), font=Font(name=FONT, bold=True, color='9C0006')))
    ws.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Blocked"'], fill=fill('FFEB9C'), font=Font(name=FONT, bold=True, color='9C5700')))
    ws.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"N/A"'], fill=fill('E5E7EB'), font=Font(name=FONT, color='6B7280')))
    ws.freeze_panes = 'C5'
    ws.sheet_view.zoomScale = 100
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = '4:4'
    ws.oddFooter.center.text = 'Page &P of &N'
    return ws, last


def build():
    wb = Workbook()
    summary = wb.active
    summary.title = 'Summary'
    sheets = []
    for name, title, sub, rows in [
        ('1 Pre-Deployment', '1. Pre-deployment - confirm and prepare', 'Do this BEFORE the deployment window. Choose a Status in column F for every row; yellow cells are yours to fill.', PRE),
        ('2 Tomcat Deploy', '2. Deploy to Tomcat and test internally', 'New folder on the existing Tomcat; the old V5 help is not touched.', TOMCAT),
        ('3 nginx and Network', '3. Make it public - nginx, DNS, HTTPS', 'Needed only for the public address https://help.lighthouseindia.com/docs/v7/ . If something is missing, finish sheets 1, 2 and 4 (internal) and do this later.', NGINX),
        ('4 Verification', '4. Verification and acceptance tests', 'Run on the internal address, then repeat the tests marked * on the public address.', VERIFY),
    ]:
        ws, last = checklist_sheet(wb, name, title, sub, rows)
        sheets.append((name, title.split('. ', 1)[1], last))

    # --- rollback / sign-off
    rb = wb.create_sheet('5 Rollback and Sign-off')
    title_row(rb, '5. Rollback guide and sign-off', 'Reference only - nothing here is ticked unless a problem occurs.', 3)
    for c, w in enumerate([44, 100, 4], 1):
        rb.column_dimensions[chr(64 + c)].width = w
    r = 4
    for i, (a, b) in enumerate(ROLLBACK):
        for c, v in enumerate((a, b), 1):
            cell = rb.cell(row=r, column=c, value=v)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            cell.font = f(i == 0 or c == 1, 10, 'FFFFFF' if i == 0 else '000000')
            if i == 0:
                cell.fill = fill(DARK)
        rb.row_dimensions[r].height = 22 if i == 0 else 34
        r += 1
    r += 1
    rb.cell(row=r, column=1, value='Sign-off').font = f(True, 12, RED)
    r += 1
    for label in ['Release version deployed', 'Deployed by (name)', 'Deployment date / time', 'Verified by (name)', 'Business approval (name)', 'Comments / open points']:
        rb.cell(row=r, column=1, value=label).font = f(True)
        rb.cell(row=r, column=1).border = BORDER
        cell = rb.cell(row=r, column=2, value=VERSION if label.startswith('Release') else None)
        cell.fill = fill('FFFBEB')
        cell.border = BORDER
        cell.font = f()
        r += 1

    # --- reference
    rf = wb.create_sheet('Reference')
    title_row(rf, 'Reference - paths, addresses, contacts', 'Copy-ready values. Yellow cells are for you to fill in.', 3)
    for c, w in enumerate([38, 78, 52], 1):
        rf.column_dimensions[chr(64 + c)].width = w
    r = 4
    for i, row in enumerate(REFERENCE):
        for c, v in enumerate(row, 1):
            cell = rf.cell(row=r, column=c, value=v if v != '' else None)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            cell.font = f(i == 0 or c == 1, 10, 'FFFFFF' if i == 0 else '000000')
            if i == 0:
                cell.fill = fill(DARK)
            elif c == 2 and v == '':
                cell.fill = fill('FFFBEB')
        r += 1
    rf.freeze_panes = 'A5'

    # --- summary (formulas)
    s = summary
    title_row(s, 'LHS ERP Help Centre V7 - Deployment checklist', 'Project: lhs-erp-v7-help-doc-app   |   Web app folder: LHS_ERP_HELP_DOC_V7   |   Public address: ' + PUB, 7)
    for c, w in enumerate([34, 12, 12, 12, 12, 12, 14], 1):
        s.column_dimensions[chr(64 + c)].width = w
    s['A4'] = 'Release version'
    s['B4'] = VERSION
    s['A5'] = 'Target deployment date'
    s['B5'] = datetime.date(2026, 10, 29)
    s['B5'].number_format = 'dd-mmm-yyyy'
    s['A6'] = 'Deployment target'
    s['B6'] = 'PRODUCTION (LHS_ERP_HELP_DOC_V7)'
    s['A7'] = 'Deployed by'
    for rr in range(4, 8):
        s.cell(row=rr, column=1).font = f(True)
    for ref in ('B4', 'B5', 'B6', 'B7'):
        s[ref].font = Font(name=FONT, size=10, color='0000FF')
        s[ref].fill = fill('FFFF00')
    for rr in range(4, 8):
        s.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
    s['E5'] = '<- edit if the date changes'
    s['E5'].font = f(False, 9, '6B7280', True)

    hr = 9
    for c, h in enumerate(['Sheet', 'Total', 'Done', 'Pending', 'Blocked / Failed', 'N/A', '% complete'], 1):
        cell = s.cell(row=hr, column=c, value=h)
        cell.font = f(True, 10, 'FFFFFF')
        cell.fill = fill(DARK)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER
    s.row_dimensions[hr].height = 30
    r = hr + 1
    for name, label, last in sheets:
        q = "'%s'!$F$5:$F$%d" % (name, last)
        s.cell(row=r, column=1, value=label)
        s.cell(row=r, column=2, value='=COUNTIF(%s,"Done")+COUNTIF(%s,"Pending")+COUNTIF(%s,"Blocked")+COUNTIF(%s,"Failed")+COUNTIF(%s,"N/A")' % ((q,) * 5))
        s.cell(row=r, column=3, value='=COUNTIF(%s,"Done")' % q)
        s.cell(row=r, column=4, value='=COUNTIF(%s,"Pending")' % q)
        s.cell(row=r, column=5, value='=COUNTIF(%s,"Blocked")+COUNTIF(%s,"Failed")' % (q, q))
        s.cell(row=r, column=6, value='=COUNTIF(%s,"N/A")' % q)
        s.cell(row=r, column=7, value='=IFERROR(C%d/(B%d-F%d),0)' % (r, r, r))
        r += 1
    first, lastr = hr + 1, r - 1
    s.cell(row=r, column=1, value='TOTAL')
    for c in range(2, 7):
        col = chr(64 + c)
        s.cell(row=r, column=c, value='=SUM(%s%d:%s%d)' % (col, first, col, lastr))
    s.cell(row=r, column=7, value='=IFERROR(C%d/(B%d-F%d),0)' % (r, r, r))
    for rr in range(first, r + 1):
        for c in range(1, 8):
            cell = s.cell(row=rr, column=c)
            cell.border = BORDER
            cell.font = f(rr == r or c == 1)
            cell.alignment = Alignment(horizontal='left' if c == 1 else 'center', vertical='center')
        s.cell(row=rr, column=7).number_format = '0%'
        s.row_dimensions[rr].height = 20
    for c in range(1, 8):
        s.cell(row=r, column=c).fill = fill(GREY)
    s.conditional_formatting.add('E%d:E%d' % (first, r), CellIsRule(operator='greaterThan', formula=['0'], fill=fill('FFC7CE'), font=Font(name=FONT, bold=True, color='9C0006')))
    s.conditional_formatting.add('G%d:G%d' % (first, r), CellIsRule(operator='equal', formula=['1'], fill=fill('C6EFCE'), font=Font(name=FONT, bold=True, color='006100')))
    s.cell(row=r + 1, column=1, value='Overall status').font = f(True)
    s.cell(row=r + 1, column=2, value='=IF(E%d>0,"ATTENTION - blocked / failed items",IF(G%d=1,"COMPLETE","In progress"))' % (r, r)).font = f(True, 11, RED)
    s.merge_cells(start_row=r + 1, start_column=2, end_row=r + 1, end_column=5)

    n = r + 3
    s.cell(row=n, column=1, value='How to use this workbook').font = f(True, 12, RED)
    notes = [
        'Work through the sheets in order: 1 Pre-Deployment > 2 Tomcat Deploy > 3 nginx and Network > 4 Verification. Sheet 5 is the rollback guide and sign-off; Reference holds paths and contacts.',
        'For every row choose a Status (Pending, Done, N/A, Blocked, Failed) in the Status column, then fill Done on (e.g. 29-Oct-2026 10:15) and Remarks / evidence (e.g. "332 PDFs counted").',
        'Yellow cells are for you to fill in. This Summary updates by itself: it counts the Status choices on each sheet. Overall status shows ATTENTION when any row is Blocked or Failed.',
        'Example row:  2.05  Verify the copy is complete | Status: Done | Done on: 29-Oct-2026 10:40 | Remarks: PDFs 332, html 332, md 332, images 2814.',
        'Mark a row N/A only if it does not apply (for example optional rows, or all of sheet 3 if the public address is made later). Do not skip a row silently.',
        'Never change conf\\server.xml and never touch the old LHS_ERP_HELP (V5) folder: the new site lives in its own folder LHS_ERP_HELP_DOC_V7.',
        'Rows 3.xx need a public IP, DNS and router access. If these are not ready tomorrow, deploy and verify internally (sheets 1, 2, 4) and schedule sheet 3 separately.',
    ]
    for i, t in enumerate(notes, 1):
        s.merge_cells(start_row=n + i, start_column=1, end_row=n + i, end_column=7)
        c = s.cell(row=n + i, column=1, value='%d.  %s' % (i, t))
        c.font = f()
        c.alignment = Alignment(wrap_text=True, vertical='top')
        s.row_dimensions[n + i].height = 30
    k = n + len(notes) + 2
    s.cell(row=k, column=1, value='Status colours').font = f(True)
    for j, (txt, bg, fg) in enumerate([('Done', 'C6EFCE', '006100'), ('Pending', 'FFFFFF', '000000'), ('Blocked', 'FFEB9C', '9C5700'), ('Failed', 'FFC7CE', '9C0006'), ('N/A', 'E5E7EB', '6B7280')]):
        cell = s.cell(row=k + 1 + j, column=1, value=txt)
        cell.fill = fill(bg)
        cell.font = Font(name=FONT, bold=True, color=fg)
        cell.border = BORDER
    s.sheet_view.showGridLines = False
    s.page_setup.orientation = 'portrait'
    s.page_setup.fitToWidth = 1
    s.page_setup.fitToHeight = 0
    s.sheet_properties.pageSetUpPr.fitToPage = True
    for ws in wb.worksheets:
        if ws.title != 'Summary':
            ws.sheet_properties.tabColor = RED if ws.title[0].isdigit() else '6B7280'
    summary.sheet_properties.tabColor = DARK

    wb.calculation.fullCalcOnLoad = True            # Excel recalculates the Summary formulas when the file is opened
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    total = sum(1 for rows in (PRE, TOMCAT, NGINX, VERIFY) for x in rows if x[0] != '#')
    print('written %s  (%d checklist items)' % (OUT, total))


if __name__ == '__main__':
    build()
