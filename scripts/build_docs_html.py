"""
Builds ONE browsable HTML page from all documentation + the complete source code:

    python scripts\\build_docs_html.py            ->  dist\\docs\\lhs-erp-v7-help-doc-app_documentation.html

Open it in any browser (double-click). Needs the 'markdown' package:  pip install markdown
The file is generated (dist\\ is git-ignored); rebuild it after changing any .md file.
"""
import html
import os
import re
import sys
import time

try:
    import markdown
except ImportError:
    sys.exit('Missing package:  pip install markdown')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'docs', 'lhs-erp-v7-help-doc-app_documentation.html')

DOCS = [   # (id, nav title, file)
    ('readme', 'Overview', 'README.md'),
    ('handover', 'Handover (Dev and DevOps)', 'docs/HANDOVER.md'),
    ('teams', 'Team responsibilities', 'docs/TEAM_RESPONSIBILITIES.md'),
    ('deployment', 'Deployment', 'docs/DEPLOYMENT.md'),
    ('release', 'Release process', 'docs/RELEASE_PROCESS.md'),
    ('maintenance', 'Maintenance runbook', 'docs/MAINTENANCE.md'),
    ('techstack', 'Technology used', 'docs/TECH_STACK.md'),
    ('developer', 'Developer guide', 'docs/DEVELOPER_GUIDE.md'),
    ('contributing', 'Contributing rules', 'CONTRIBUTING.md'),
    ('claude', 'AI assistant rules', 'CLAUDE.md'),
    ('changelog', 'Changelog', 'CHANGELOG.md'),
]
SOURCES = [
    'deploy/nginx/help.lighthouseindia.com.conf', 'deploy/env/uat.app.properties', 'deploy/env/prod.app.properties',
    'scripts/check.py', 'scripts/set_version.py', 'scripts/package_release.ps1', 'scripts/build_docs_html.py', 'scripts/build_checklist_xlsx.py',
    'webapp/layout.html', 'webapp/index.html', 'webapp/css/app.css', 'webapp/js/app.js', 'webapp/config/app.properties',
    'webapp/WEB-INF/web.xml', 'webapp/guide/README.txt', 'webapp/README.txt',
    'webapp/tools/build_v7.py', 'webapp/tools/build_html.py', 'webapp/tools/build_md.py', 'webapp/tools/auto_update.py',
    'webapp/tools/update_now.bat', 'webapp/tools/auto_update.bat', 'webapp/tools/build_v7.bat', 'webapp/tools/build_html.bat',
    'webapp/tools/run_local.bat', 'requirements.txt', '.gitignore', '.gitattributes', 'VERSION',
]
DOC_ID = {os.path.basename(f).lower(): i for i, _, f in DOCS}
SRC_ID = {os.path.basename(f).lower(): 'src-' + re.sub(r'[^a-z0-9]+', '-', f.lower()) for f in SOURCES}


def read(rel):
    with open(os.path.join(ROOT, *rel.split('/')), encoding='utf-8') as f:
        return f.read()


def fix_links(h):
    def one(m):
        href, text = m.group(1), m.group(2)
        if href.startswith(('http://', 'https://', 'mailto:')):
            return m.group(0)
        if href.startswith('#'):
            return m.group(0)
        path, _, frag = href.partition('#')
        base = os.path.basename(path).lower()
        if base in DOC_ID:
            return '<a href="#doc-%s">%s</a>' % (DOC_ID[base], text)
        if base in SRC_ID:
            return '<a href="#%s">%s</a>' % (SRC_ID[base], text)
        return '<code>%s</code>' % text
    return re.sub(r'<a href="([^"]*)">(.*?)</a>', one, h, flags=re.S)


def convert(doc_id, text):
    def slug(value, sep):
        s = re.sub(r'[^\w\s-]', '', value.lower()).strip()
        return doc_id + '-' + re.sub(r'[\s_-]+', sep, s)
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'],
                           extension_configs={'toc': {'toc_depth': '2', 'slugify': slug}})
    body = md.convert(text)
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, flags=re.S)
    return fix_links(body), [(i, re.sub(r'<[^>]+>', '', t)) for i, t in heads]


CSS = '''
:root{--brand:#c8102e;--text:#17202e;--muted:#5a6779;--line:#e2e6ec;--bg:#f5f7fa;--code:#f1f3f7}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:14px}
body{margin:0;font:15px/1.65 "Segoe UI",Roboto,Arial,sans-serif;color:var(--text);background:var(--bg)}
.wrap{display:grid;grid-template-columns:310px minmax(0,1fr);max-width:1500px;margin:0 auto}
nav{position:sticky;top:0;align-self:start;height:100vh;overflow:auto;padding:20px 16px 40px;border-right:1px solid var(--line);background:#fff;font-size:13.5px}
nav .brand{font-weight:700;color:var(--brand);font-size:15px;line-height:1.3}nav .sub{color:var(--muted);font-size:12px;margin:2px 0 12px}
nav input{width:100%;padding:7px 10px;border:1px solid var(--line);border-radius:8px;font:inherit;margin-bottom:10px}
nav details{margin:2px 0}nav summary{cursor:pointer;font-weight:600;padding:5px 2px;list-style:none}nav summary::before{content:"\\25B8  ";color:var(--muted)}
nav details[open]>summary::before{content:"\\25BE  "}
nav a{display:block;color:var(--text);text-decoration:none;padding:2px 0 2px 16px}nav a:hover,nav summary a:hover{color:var(--brand)}
nav summary a{display:inline;padding:0}nav .app a{padding-left:2px}
main{padding:30px clamp(18px,4vw,60px) 90px;background:#fff;min-height:100vh;min-width:0}
.doc{padding-bottom:30px;margin-bottom:34px;border-bottom:6px solid var(--line)}
h1{font-size:28px;margin:0 0 14px;color:var(--brand)}h2{font-size:22px;margin:40px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line)}h3{font-size:17px;margin:24px 0 8px}
table{border-collapse:collapse;width:100%;margin:12px 0 20px;font-size:14px;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:7px 11px;vertical-align:top;text-align:left}th{background:#f1f3f7}
code{font:13px Consolas,"Cascadia Mono",monospace;background:var(--code);padding:1px 5px;border-radius:4px}
pre{background:#101827;color:#e8edf5;padding:14px 16px;border-radius:10px;overflow:auto;font-size:12.5px;line-height:1.5}pre code{background:none;padding:0;color:inherit;font-size:inherit}
details.src{border:1px solid var(--line);border-radius:10px;margin:10px 0;background:#fafbfc}details.src>summary{cursor:pointer;padding:10px 14px}
details.src pre{margin:0;border-radius:0 0 10px 10px;max-height:72vh}.meta{color:var(--muted);font-weight:400;font-size:12.5px}
blockquote{margin:12px 0;padding:6px 14px;border-left:4px solid var(--brand);background:#fdf2f4}hr{border:0;border-top:1px solid var(--line);margin:28px 0}
.top{display:none}
@media(max-width:900px){.wrap{grid-template-columns:1fr}nav{position:static;height:auto;max-height:60vh;border-right:0;border-bottom:1px solid var(--line)}}
@media print{nav{display:none}.wrap{display:block}body{background:#fff}main{padding:0}details.src{break-inside:avoid-page}details.src[open] pre{max-height:none}h2{break-after:avoid}.doc{break-before:page}}
'''

JS = '''
var q=document.getElementById("q");
q&&q.addEventListener("input",function(){var t=q.value.toLowerCase();
 document.querySelectorAll("nav details").forEach(function(d){var any=!t;d.querySelectorAll("a").forEach(function(a){var m=!t||a.textContent.toLowerCase().indexOf(t)>=0;a.style.display=m?"":"none";if(m)any=true});
 d.style.display=any?"":"none";if(t&&any)d.open=true;});});
document.querySelectorAll("nav a").forEach(function(a){a.addEventListener("click",function(){var h=a.getAttribute("href");if(h&&h[0]=="#"){var el=document.getElementById(h.slice(1));
 while(el){if(el.tagName=="DETAILS")el.open=true;el=el.parentElement;}}});});
if(location.hash){var e=document.getElementById(location.hash.slice(1));while(e){if(e.tagName=="DETAILS")e.open=true;e=e.parentElement;}}
'''


def main():
    ver = read('VERSION').strip()
    navs, bodies = [], []
    for i, (doc_id, title, rel) in enumerate(DOCS):
        body, heads = convert(doc_id, read(rel))
        bodies.append('<section class="doc" id="doc-%s">%s</section>' % (doc_id, body))
        links = ''.join('<a href="#%s">%s</a>' % (hid, html.escape(t)) for hid, t in heads)
        navs.append('<details%s><summary><a href="#doc-%s">%s</a></summary>%s</details>' % (' open' if i == 0 else '', doc_id, html.escape(title), links))
    src_nav, src_body = [], []
    for rel in SOURCES:
        sid = 'src-' + re.sub(r'[^a-z0-9]+', '-', rel.lower())      # unique per path (two README.txt files exist)
        text = read(rel)
        src_nav.append('<a href="#%s">%s</a>' % (sid, html.escape(rel)))
        src_body.append('<details class="src" id="%s"><summary><b>%s</b> <span class="meta">%d lines</span></summary><pre><code>%s</code></pre></details>'
                        % (sid, html.escape(rel), text.count('\n') + 1, html.escape(text)))
    navs.append('<details class="app"><summary><a href="#appendix-source">Appendix - complete source code</a></summary>%s</details>' % ''.join(src_nav))
    appendix = ('<section class="doc" id="appendix-source"><h1>Appendix - complete source code</h1>'
                '<p>Every file of the repository except the PDFs and generated folders, exactly as in version <b>%s</b>. Click a name to expand.</p>%s</section>'
                % (ver, '\n'.join(src_body)))
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>lhs-erp-v7-help-doc-app - Documentation</title><style>%s</style></head><body><div class="wrap">'
            '<nav><div class="brand">lhs-erp-v7-help-doc-app</div><div class="sub">Lighthouse ERP V7 Help Centre &middot; version %s</div>'
            '<input id="q" type="search" placeholder="Filter sections..." aria-label="Filter sections">%s</nav>'
            '<main>%s%s<p class="meta">Generated %s from the repository (scripts/build_docs_html.py).</p></main></div><script>%s</script></body></html>'
            % (CSS.replace('\\\\', '\\'), ver, ''.join(navs), '\n'.join(bodies), appendix, time.strftime('%Y-%m-%d %H:%M'), JS))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page)
    print('written %s  (%d KB, %d documents, %d source files)' % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) // 1024, len(DOCS), len(SOURCES)))


if __name__ == '__main__':
    main()
