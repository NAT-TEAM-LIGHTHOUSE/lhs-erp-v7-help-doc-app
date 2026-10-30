"""
Writes a Markdown copy (x.md) next to every Reader page (x.html) in html\\ .
"Open in ChatGPT / Claude" then sends  "Read from <link to x.md> so I can ask questions about it."

  python tools\\build_md.py            only pages that are new / changed (safe to run any time)
  python tools\\build_md.py --force    rebuild every .md

Needs nothing but Python. The public address for the links comes from  site.url  in config\\app.properties
(e.g. site.url=https://help.lighthouseindia.com/docs/v7/ ). Empty = site-relative links.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
DEPLOY = os.path.dirname(HERE)
HTML = os.path.join(DEPLOY, 'html')


def site_url():
    try:
        with open(os.path.join(DEPLOY, 'config', 'app.properties'), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('site.url') and '=' in line:
                    u = line.split('=', 1)[1].strip()
                    return u if not u or u.endswith('/') else u + '/'
    except OSError:
        pass
    return ''


class ToMd(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.out, self.buf, self.fig = base, [], [], 0
        self.mode = None          # h2 / h3 / p / li / step / note / cell
        self.list_tag, self.n_li = None, 0
        self.step_n = ''
        self.rows, self.row = [], None
        self.in_n = False

    def flush(self, fmt='%s'):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).replace('** **', ' ').strip()
        self.buf = []
        if t:
            self.out.append(fmt % t)

    def handle_starttag(self, tag, a):
        a = dict(a)
        c = a.get('class', '') or ''
        if tag in ('h2', 'h3', 'p'):
            self.flush(); self.mode = tag
        elif tag in ('ul', 'ol'):
            self.flush(); self.list_tag, self.n_li = tag, 0
        elif tag == 'li':
            self.flush(); self.mode = 'li'; self.n_li += 1
        elif tag == 'div' and 'rv-step' in c:
            self.flush(); self.mode = 'step'; self.step_n = ''
        elif tag == 'span' and 'rv-n' in c:
            self.in_n = True
        elif tag == 'div' and 'rv-note' in c:
            self.flush(); self.mode = 'note'
        elif tag == 'div' and 'rv-meta' in c:
            self.flush(); self.mode = 'meta'
        elif tag == 'table':
            self.flush(); self.rows = []
        elif tag == 'tr':
            self.row = []
        elif tag in ('td', 'th'):
            self.flush(); self.mode = 'cell'
        elif tag in ('b', 'strong'):
            self.buf.append('**')
        elif tag == 'br':
            self.buf.append(' ')
        elif tag == 'img':
            self.flush()            # screenshots are left out: an AI cannot use them, the step text says it all

    def handle_endtag(self, tag):
        if tag in ('b', 'strong'):
            self.buf.append('**')
        elif tag == 'span' and self.in_n:
            self.in_n = False
            self.step_n = re.sub(r'\s+', '', ''.join(self.buf)); self.buf = []
        elif tag == 'h2':
            self.flush('## %s'); self.mode = None
        elif tag == 'h3':
            self.flush('### %s'); self.mode = None
        elif tag == 'p':
            self.flush(); self.mode = None
        elif tag == 'li':
            self.flush(('%d. %%s' % self.n_li) if self.list_tag == 'ol' else '- %s')
            # consecutive list items are joined into one block at the end
            self.mode = None
        elif tag in ('ul', 'ol'):
            self.list_tag = None
            self.out.append('\x00LISTEND')
        elif tag == 'div':
            if self.mode == 'step':
                self.flush('**Step ' + self.step_n + ':** %s'); self.mode = None
            elif self.mode == 'note':
                self.flush('> %s'); self.mode = None
            elif self.mode == 'meta':
                self.flush('_%s_'); self.mode = None
        elif tag in ('td', 'th'):
            t = re.sub(r'\s+', ' ', ''.join(self.buf)).replace('** **', ' ').strip().replace('|', '/')
            self.buf = []
            if self.row is not None:
                self.row.append(t)
            self.mode = None
        elif tag == 'tr':
            if self.row:
                self.rows.append(self.row)
            self.row = None
        elif tag == 'table':
            if self.rows:
                cols = max(len(r) for r in self.rows)
                lines = ['| ' + ' | '.join(r + [''] * (cols - len(r))) + ' |' for r in self.rows]
                lines.insert(1, '|' + ' --- |' * cols)
                self.out.append('\n'.join(lines))
            self.rows = []

    def handle_data(self, d):
        if self.mode is not None or self.in_n or self.buf:
            self.buf.append(d)

    def result(self):
        self.flush()
        blocks, cur = [], []
        for o in self.out:
            if o == '\x00LISTEND':
                if cur:
                    blocks.append('\n'.join(cur)); cur = []
            elif o.startswith('- ') or re.match(r'\d+\. ', o):
                cur.append(o)
            else:
                if cur:
                    blocks.append('\n'.join(cur)); cur = []
                blocks.append(o)
        if cur:
            blocks.append('\n'.join(cur))
        return '\n\n'.join(blocks)


def build(path, base):
    rel = os.path.relpath(path, HTML).replace(os.sep, '/')
    parts = rel[:-5].split('/')
    stem = parts[-1]
    m = re.match(r'^([\d.]+)\s*-\s*(.+)$', stem)
    code, title = (m.group(1), m.group(2)) if m else ('', stem)
    with open(path, encoding='utf-8') as f:
        p = ToMd(base)
        p.feed(f.read())
    head = '# %s\n\n' % title
    if code:
        head += 'Menu code: %s\n' % code
    head += 'Source: Lighthouse ERP V7 Help Centre' + (' > ' + ' > '.join(parts[:-1]) if len(parts) > 1 else '') + '\n'
    head += 'PDF: %s%s\n\n' % (base, quote('docs/' + rel[:-5] + '.pdf', safe='/%:@'))
    return head + p.result() + '\n'


def main():
    force = '--force' in sys.argv
    base = site_url()
    n = skipped = 0
    for r, _, fs in os.walk(HTML):
        if os.path.basename(r) == '_img':
            continue
        for f in fs:
            if not f.endswith('.html'):
                continue
            src = os.path.join(r, f)
            dst = src[:-5] + '.md'
            if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                skipped += 1
                continue
            with open(dst, 'w', encoding='utf-8', newline='\n') as o:
                o.write(build(src, base))
            n += 1
    print('markdown pages written: %d, already up to date: %d   (links: %s)' % (n, skipped, base or 'relative'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
