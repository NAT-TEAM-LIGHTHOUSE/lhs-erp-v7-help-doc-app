"""Lighthouse ERP V7 Help Centre - automatic "Reader view" (HTML) builder.

Converts every PDF in  <deploy>/docs  into a clean, responsive HTML fragment in  <deploy>/html
using fixed layout rules (no manual editing):

  * cover page and page header / footer are dropped
  * bold UPPERCASE / large bold lines        -> section headings
  * short bold lines                         -> sub headings
  * "Step 1 : ..." lines                     -> numbered step cards
  * bullet glyph / "1." lines                -> lists
  * "Note / Remark / Example / Result:"      -> call-out boxes
  * ruled tables                             -> HTML tables
  * screenshots (with their red marks)       -> compressed WebP figures (click to zoom)
  * wrapped lines                            -> joined paragraphs

    pip install pymupdf pillow
    python tools/build_html.py                 (all documents; unchanged ones are skipped)
    python tools/build_html.py --force         (re-convert everything)
    python tools/build_html.py "docs/00-System Administration - SA"   (only one folder / file)
"""
import hashlib, html, io, os, re, subprocess, sys, time, warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
DEPLOY = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))          # optional local copy of the libraries
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        sys.exit('PyMuPDF is missing.  Run:  pip install pymupdf pillow')
try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow is missing.  Run:  pip install pymupdf pillow')

DOCS = os.path.join(DEPLOY, 'docs')
OUT = os.path.join(DEPLOY, 'html')
IMG = os.path.join(OUT, '_img')
RULES_VERSION = '2'                                       # bump when the rules change -> everything is rebuilt
HEAD_Y, FOOT_Y = 66, 782                                  # header / footer bands on A4 pages (points)
MAX_IMG_W = 1200                                          # px, widest stored screenshot
PUA = re.compile(r'[-​­]')
BULLET_FONTS = ('wingdings', 'symbol')
CALLOUT = re.compile(r'^(note|remarks?|example|result|important|tip|caution|warning)\s*[:\-]', re.I)
STEP = re.compile(r'^\s*step\s*(\d+)\s*[:\-.]*\s*(.*)$', re.I | re.S)
NUMBERED = re.compile(r'^\s*(\d{1,2})[.)]\s+(\S.*)$', re.S)
LEAD_BULLET = re.compile(r'^\s*[•●▪■⁃\-\*o]\s+(?=\S)')


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- page analysis
def span_html(spans):
    out = []
    for s in spans:
        t = PUA.sub('', s['text'])
        if not t.strip() and not t:
            continue
        font = s['font'].lower()
        bold = 'bold' in font or (s['flags'] & 16)
        ital = 'italic' in font or (s['flags'] & 2)
        t = esc(t)
        if t.strip():
            if bold: t = '<strong>' + t + '</strong>'
            if ital: t = '<em>' + t + '</em>'
        out.append(t)
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


def line_info(l):
    spans = list(l['spans'])
    while spans and not PUA.sub('', spans[0]['text']).strip() and not spans[0]['font'].lower().startswith(BULLET_FONTS):
        spans = spans[1:]
    while spans and not PUA.sub('', spans[-1]['text']).strip() and not spans[-1]['font'].lower().startswith(BULLET_FONTS):
        spans = spans[:-1]
    if not spans:
        return None
    first = spans[0]
    bullet = (first['font'].lower().startswith(BULLET_FONTS) or bool(re.match(r'^[•●▪]\s*$', first['text']))
              or bool(re.match(r'^[-]{1,2}\s*$', first['text'])))          # private-use glyph = Word list bullet
    if bullet:
        spans = spans[1:]
        if not any(PUA.sub('', x['text']).strip() for x in spans):
            x0, y0, x1, y1 = l['bbox']
            return {'marker': True, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'bullet': True, 'white': False}
    plain = re.sub(r'\s+', ' ', PUA.sub('', ''.join(s['text'] for s in spans))).strip()
    if len(plain) < 1:
        return None
    allbold = all(('bold' in s['font'].lower() or (s['flags'] & 16)) for s in spans if s['text'].strip())
    white = all(s['color'] in (0xffffff,) for s in spans if s['text'].strip())
    x0, y0, x1, y1 = l['bbox']
    return {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'size': round(max(s['size'] for s in spans), 1), 'bold': allbold,
            'white': white, 'bullet': bullet, 'plain': plain, 'html': span_html(spans), 'color': spans[0]['color']}


def inside(b, r, pad=2):
    return b[0] >= r[0] - pad and b[2] <= r[2] + pad and b[1] >= r[1] - pad and b[3] <= r[3] + pad


def overlaps(a, b, pad=4):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def figure_regions(page, text_boxes):
    """Merge nearby embedded images into figure rectangles."""
    rects = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] == 1:
            r = list(b['bbox'])
            if (r[2] - r[0]) < 24 or (r[3] - r[1]) < 24:                  # icons, bullets, page-number badges
                continue
            if r[1] < HEAD_Y and r[3] < HEAD_Y + 10 or r[1] > FOOT_Y:      # header / footer art
                continue
            rects.append(r)
    merged = True
    while merged:
        merged = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if overlaps(rects[i], rects[j], 6):
                    a, b = rects[i], rects[j]
                    rects[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del rects[j]
                    merged = True
                    break
            if merged:
                break
    return sorted(rects, key=lambda r: (r[1], r[0]))


def save_figure(page, rect):
    clip = fitz.Rect(rect) & page.rect
    if clip.is_empty:
        return None
    zoom = min(2.2, MAX_IMG_W / max(clip.width, 1))
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=72, method=4)
    data = buf.getvalue()
    name = hashlib.sha1(data).hexdigest()[:14] + '.webp'
    os.makedirs(IMG, exist_ok=True)
    path = os.path.join(IMG, name)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(data)
    return name, pix.width, pix.height


def cell_text(page, c):
    if not c:
        return ''
    words = page.get_text('words', clip=fitz.Rect(c))
    words.sort(key=lambda w: (round(w[3] / 4), w[0]))
    lines, last = [], None
    for w in words:
        key = round(w[3] / 4)
        if last is None or key != last:
            lines.append([]); last = key
        lines[-1].append(PUA.sub('', w[4]))
    return '\n'.join(re.sub(r'\s+', ' ', ' '.join(l)).strip() for l in lines).strip()


def table_html(rows):
    rows = [[(c or '').strip() for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ''
    flat = ' '.join(c for r in rows for c in r)
    if 'Process Help Document' in flat or 'Release Version' in flat:              # document-information block
        def pick(label):
            m = re.search(label + r'\s*[:\-]?\s*(\d[\d.]*\d|\d)', flat.replace('\n', ' '))
            return m.group(1) if m else ''
        bits = [('Release version', pick('Release Version')), ('Release date', pick('Release Date'))]
        bits = ['%s <b>%s</b>' % (k, esc(v)) for k, v in bits if v]
        return '<div class="rv-meta">%s</div>' % ' &middot; '.join(bits) if bits else ''
    head = [c for c in rows[0] if c]
    if head and all(len([c for c in r if c]) <= len(head) for r in rows):           # merged cells left gaps: close them
        rows = [[c for c in r if c] for r in rows]
        rows = [r + [''] * (len(head) - len(r)) for r in rows]
    else:                                                                            # otherwise only drop blank columns
        n = max(len(r) for r in rows)
        rows = [r + [''] * (n - len(r)) for r in rows]
        keep = [j for j in range(n) if any(r[j] for r in rows)]
        rows = [[r[j] for j in keep] for r in rows]
    out = ['<div class="rv-tablewrap"><table class="rv-table">']
    out.append('<thead><tr>' + ''.join('<th>%s</th>' % esc(c) for c in rows[0]) + '</tr></thead><tbody>')
    for r in rows[1:]:
        out.append('<tr>' + ''.join('<td>%s</td>' % esc(c).replace('\n', '<br>') for c in r) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def page_items(page, pno):
    """Ordered list of items on one page: ('line', info) / ('table', html) / ('fig', rect)."""
    items, boxes = [], []
    tables = []
    try:
        for t in ([] if os.environ.get('LHS_SAFE') else page.find_tables().tables):      # LHS_SAFE: retry mode for PDFs that crash table detection
            rows = [[cell_text(page, c) for c in row.cells] for row in t.rows]
            if rows and len(rows) >= 1 and max(len(r) for r in rows) >= 2:
                tables.append((tuple(t.bbox), rows))
    except Exception:
        pass
    figs = figure_regions(page, boxes)
    for bbox, rows in tables:
        items.append((bbox[1], bbox[0], 'table', table_html(rows)))
    for r in figs:
        if any(inside(r, tb, 4) for tb, _ in tables):
            continue
        items.append((r[1], r[0], 'fig', r))
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            bb = l['bbox']
            if bb[3] < HEAD_Y or bb[1] > FOOT_Y:
                continue
            if any(inside(bb, tb, 3) for tb, _ in tables) or any(inside(bb, fr, 3) for fr in figs):
                continue
            info = line_info(l)
            if info and not info['white']:
                items.append((info['y0'], info['x0'], 'line', info))
    items.sort(key=lambda t: (round(t[0] / 3), t[1]))
    return items, figs


# ---------------------------------------------------------------- document assembly
def merge_row_lines(lines):
    """Lines sitting on the same baseline (different text blocks) become one line."""
    out, marker = [], None
    for ln in lines:
        if ln.get('marker'):
            if out and abs(out[-1]['y0'] - ln['y0']) < 9 and out[-1]['x0'] >= ln['x0']:
                out[-1]['bullet'] = True                          # glyph sorted after its text
            else:
                marker = ln
            continue
        if marker is not None:                                    # a lone bullet glyph belongs to the text beside it
            if abs(marker['y0'] - ln['y0']) < 9 and ln['x0'] >= marker['x0']:
                ln = dict(ln); ln['bullet'] = True
            marker = None
        if out and abs(out[-1]['y0'] - ln['y0']) < 3 and not ln['bullet'] and out[-1]['x1'] <= ln['x0'] + 6:
            p = out[-1]
            p['html'] += ' ' + ln['html']; p['plain'] += ' ' + ln['plain']; p['x1'] = ln['x1']
            p['bold'] = p['bold'] and ln['bold']
        else:
            out.append(dict(ln))
    return out


def classify(ln):
    t = ln['plain']
    m = STEP.match(t)
    if m:
        return 'step'
    if ln['bold'] and ln['size'] >= 14 and len(t) < 90:
        return 'h2'
    if ln['bold'] and ln['size'] >= 10.5 and t.upper() == t and len(t) < 70 and re.search('[A-Z]', t):
        return 'h2'
    if ln['bold'] and len(t) <= 64 and not t.endswith(('.', ',', ';')) and not ln['bullet']:
        return 'h3'
    if ln['bullet'] or LEAD_BULLET.match(t):
        return 'li'
    if NUMBERED.match(t):
        return 'ol'
    if CALLOUT.match(t):
        return 'note'
    return 'p'


def build_blocks(pages):
    """Flatten pages into blocks: dict(kind, html) with paragraph merging."""
    blocks, prev = [], None
    for kind, payload in pages:
        if kind == 'table':
            blocks.append({'k': 'table', 'h': payload}); prev = None; continue
        if kind == 'fig':
            blocks.append({'k': 'fig', 'h': payload}); prev = None; continue
        ln = payload
        k = classify(ln)
        text = ln['html']
        if k == 'li':
            text = LEAD_BULLET.sub('', text)
        elif k == 'ol':
            text = NUMBERED.sub(lambda m: m.group(2), text, count=1)
        elif k == 'step':
            m = STEP.match(re.sub(r'</?(strong|em)>', '', ln['html']))
            blocks.append({'k': 'step', 'n': m.group(1), 'h': m.group(2).strip() or ''}); prev = ln; continue
        if k in ('h2', 'h3'):
            text = re.sub(r'</?strong>', '', text)
            if blocks and blocks[-1]['k'] == k and prev is not None and ln['y0'] - prev['y1'] < 6 and abs(ln['size'] - prev['size']) < .5:
                blocks[-1]['h'] += ' ' + text
            else:
                blocks.append({'k': k, 'h': text, 'sz': ln['size']})
            prev = ln; continue
        cont = (prev is not None and blocks and blocks[-1]['k'] in ('p', 'li', 'ol', 'note', 'step') and k in ('p',)
                and abs(ln['size'] - prev['size']) < .6 and 0 <= ln['y0'] - prev['y1'] < ln['size'] * .55 and ln['x0'] >= prev['x0'] - 2)
        if cont:
            blocks[-1]['h'] += ' ' + text
        else:
            blocks.append({'k': k, 'h': text})
        prev = ln
    return short_runs_to_lists(blocks)


def short_runs_to_lists(blocks):
    """Three or more one-line sentences in a row (two after a lead-in ending with ':') read as a bullet list."""
    plain = lambda b: re.sub(r'<[^>]+>', '', b['h']).strip()
    out, i = [], 0
    while i < len(blocks):
        j = i
        while j < len(blocks) and blocks[j]['k'] == 'p' and 3 <= len(plain(blocks[j])) <= 150 and not plain(blocks[j]).endswith(':'):
            j += 1
        lead = out and out[-1]['k'] == 'p' and plain(out[-1]).endswith(':')
        if j - i >= (2 if lead else 3):
            out += [{'k': 'li', 'h': b['h']} for b in blocks[i:j]]
            i = j
        else:
            out.append(blocks[i]); i += 1
    return out


def blocks_html(blocks, imgs):
    seen_h2 = False
    kept = []
    for b in blocks:                                            # the large document-title line repeats the title: drop it
        if b['k'] == 'h2' and not seen_h2 and b.get('sz', 0) >= 17:
            continue
        seen_h2 = seen_h2 or b['k'] == 'h2'
        kept.append(b)
    blocks = kept
    blocks = [b for j, b in enumerate(blocks)
              if not (b['k'] == 'h2' and (j + 1 >= len(blocks) or blocks[j + 1]['k'] in ('h2',)))]
    out, i, sec_open, n_sec = [], 0, False, 0
    out.append('<article class="rv">')
    while i < len(blocks):
        b = blocks[i]; k = b['k']
        if k == 'h2':
            if sec_open: out.append('</section>')
            n_sec += 1; sec_open = True
            out.append('<section class="rv-sec"><h2 id="s%d">%s</h2>' % (n_sec, b['h']))
        elif k == 'h3':
            out.append('<h3>%s</h3>' % b['h'])
        elif k == 'step':
            out.append('<div class="rv-step"><span class="rv-n">%s</span><div class="rv-st">%s</div></div>' % (b['n'], b['h'] or 'Step ' + b['n']))
        elif k in ('li', 'ol'):
            tag = 'ul' if k == 'li' else 'ol'
            out.append('<%s class="rv-list">' % tag)
            while i < len(blocks) and blocks[i]['k'] == k:
                out.append('<li>%s</li>' % blocks[i]['h']); i += 1
            out.append('</%s>' % tag)
            continue
        elif k == 'note':
            m = CALLOUT.match(re.sub(r'<[^>]+>', '', b['h']))
            kind = m.group(1).lower() if m else 'note'
            out.append('<div class="rv-note rv-%s">%s</div>' % ('warn' if kind in ('important', 'caution', 'warning') else 'info', b['h']))
        elif k == 'table':
            out.append(b['h'])
        elif k == 'fig':
            name, w, h = b['h']
            out.append('<figure class="rv-fig"><img loading="lazy" decoding="async" src="html/_img/%s" width="%d" height="%d" alt=""></figure>' % (name, w, h))
        else:
            out.append('<p>%s</p>' % b['h'])
        i += 1
    if sec_open:
        out.append('</section>')
    out.append('</article>')
    return '\n'.join(out)


def convert(pdf, dst):
    doc = fitz.open(pdf)
    flow = []
    for pno, page in enumerate(doc):
        if pno == 0 and len(doc) > 1:          # cover page
            continue
        items, figs = page_items(page, pno)
        for _, _, kind, payload in items:
            if kind == 'fig':
                saved = save_figure(page, payload)
                if saved:
                    flow.append(('fig', saved))
            elif kind == 'table':
                if payload:
                    flow.append(('table', payload))
            else:
                flow.append(('line', payload))
    # row-merge only consecutive lines
    merged, buf = [], []
    for kind, p in flow:
        if kind == 'line':
            buf.append(p)
        else:
            merged += [('line', x) for x in merge_row_lines(buf)]; buf = []
            merged.append((kind, p))
    merged += [('line', x) for x in merge_row_lines(buf)]
    blocks = build_blocks(merged)
    # a document with no headings still reads well; remove empty paragraphs
    blocks = [b for b in blocks if b['k'] in ('fig', 'table') or re.sub(r'<[^>]+>', '', b['h']).strip()]
    doc_html = blocks_html(blocks, None)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('<!--rv%s-->\n' % RULES_VERSION + doc_html)
    return len(blocks)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--one':             # worker mode
        pdf = os.path.abspath(sys.argv[2])
        print(convert(pdf, os.path.join(OUT, os.path.splitext(os.path.relpath(pdf, DOCS))[0] + '.html')))
        return
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    target = os.path.abspath(args[0]) if args else DOCS
    pdfs = []
    if os.path.isfile(target):
        pdfs = [target]
    else:
        for r, _, fs in os.walk(target):
            pdfs += [os.path.join(r, f) for f in fs if f.lower().endswith('.pdf')]
    pdfs.sort()
    done = skipped = failed = 0
    t0 = time.time()
    for i, pdf in enumerate(pdfs, 1):
        rel = os.path.relpath(pdf, DOCS)
        dst = os.path.join(OUT, os.path.splitext(rel)[0] + '.html')
        if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(pdf):
            skipped += 1                                           # already converted and the PDF has not changed: leave it alone
            continue
        # each PDF runs in its own process: a rare crash inside the PDF library only loses that one document
        try:
            cmd = [sys.executable, os.path.abspath(__file__), '--one', pdf]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if r.returncode != 0:                                  # library crash: retry without table detection
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=dict(os.environ, LHS_SAFE='1'))
            if r.returncode != 0:
                raise RuntimeError((r.stderr or 'exit code %s' % r.returncode).strip().splitlines()[-1][:160] if (r.stderr or '').strip() else 'exit code %s' % r.returncode)
            done += 1
            print('[%d/%d] %s  (%s blocks)' % (i, len(pdfs), rel, r.stdout.strip() or '?'), flush=True)
        except Exception as e:                                    # keep going; that doc simply has no reader view
            failed += 1
            print('[%d/%d] FAILED %s : %s' % (i, len(pdfs), rel, e), flush=True)
    print('Converted: %d | unchanged: %d | failed: %d | %.0fs' % (done, skipped, failed, time.time() - t0))


if __name__ == '__main__':
    main()
