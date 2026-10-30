"""Lighthouse ERP V7 Help Centre - build tool.

Reads the V7 documentation folder (modules > groups > "code - title.pdf"),
copies the PDFs into  <deploy>/docs  and writes  <deploy>/menu/v7-menu.json
which drives the whole Help Centre. Re-run after adding / renaming PDFs.

    python tools/build_v7.py
    python tools/build_v7.py "D:\\LHS_ERP_HELP_V7\\V7_MENU_HELP_DOC"

Also writes CSV reports (documents needing attention) to  <deploy>/../LHS_ERP_HELP_V7_REPORT
Requires only Python 3.8+ (no extra packages).
"""
import csv, json, os, re, shutil, sys, time, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DEPLOY = os.path.dirname(HERE)
SOURCE = sys.argv[1] if len(sys.argv) > 1 else r'D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC'
REPORT = os.path.join(os.path.dirname(DEPLOY), 'LHS_ERP_HELP_V7_REPORT')

MODULE_RE = re.compile(r'^(\d{2})\s*-\s*(.*?)\s*-\s*([A-Za-z]+)\s*$')
GROUP_RE = re.compile(r'^(\d{2}\.\d{2})\s*-\s*(.*)$')
FILE_RE = re.compile(r'^\s*(\d{2}(?:\.\d{1,3}[A-Za-z]?){1,4})\s*[-\u2013\u2014_:]*\s*(.*)$')


def clean(text):
    text = re.sub(r'\s+', ' ', text).strip(' .')
    return re.sub(r'\((\w+) / ?(\w+)\)', r'(\1 / \2)', re.sub(r'\((\w+) (\w+)\)$', r'(\1 \2)', text))


def ascii_name(name):
    name = name.replace('\u2013', '-').replace('\u2014', '-')
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+\.', '.', name).strip()


def natkey(code):
    return [(int(p) if p.isdigit() else 0, p) for p in re.split(r'[.]', code)] + [(0, '')]


def copy_pdf(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        s, d = os.stat(src), os.stat(dst)
        if s.st_size == d.st_size and int(s.st_mtime) <= int(d.st_mtime) + 2:
            return False
    shutil.copy2(src, dst)
    return True


def main():
    if not os.path.isdir(SOURCE):
        sys.exit('Source folder not found: ' + SOURCE)
    docs_root = os.path.join(DEPLOY, 'docs')
    modules, issues, copied, total = [], [], 0, 0
    seen_codes = {}

    for mname in sorted(os.listdir(SOURCE)):
        mpath = os.path.join(SOURCE, mname)
        if not os.path.isdir(mpath):
            continue
        mm = MODULE_RE.match(mname)
        if not mm:
            issues.append(['Folder not recognised as a module', mname, '']); continue
        mod = {'code': mm.group(1), 'name': clean(mm.group(2)), 'abbr': mm.group(3).upper(), 'groups': [], 'overview': []}
        groups = {}
        for gname in sorted(os.listdir(mpath)):
            gpath = os.path.join(mpath, gname)
            if not os.path.isdir(gpath):
                if gname.lower().endswith('.docx') and not gname.startswith('~$'):
                    issues.append(['Word file (not shown in app)', os.path.join(mname, gname), 'Export to PDF'])
                continue
            gm = GROUP_RE.match(gname)
            if gm:
                g = {'code': gm.group(1), 'name': clean(gm.group(2)), 'items': [], 'doc': None}
                groups[g['code']] = g; mod['groups'].append(g)
        for gname in sorted(os.listdir(mpath)):
            gpath = os.path.join(mpath, gname)
            if not os.path.isdir(gpath):
                continue
            gm = GROUP_RE.match(gname)
            for fname in sorted(os.listdir(gpath)):
                fpath = os.path.join(gpath, fname)
                rel_issue = os.path.join(mname, gname, fname)
                low = fname.lower()
                if low == 'thumbs.db' or fname.startswith('~$'):
                    continue
                if low.endswith('.docx') or low.endswith('.doc'):
                    if not os.path.exists(os.path.splitext(fpath)[0] + '.pdf'):
                        issues.append(['Word file (not shown in app)', rel_issue, 'Export to PDF'])
                    continue
                if not low.endswith('.pdf'):
                    continue
                fm = FILE_RE.match(fname[:-4])
                if not fm and gm is None and gname.lower().startswith('overview'):
                    # uncoded manual in a module's "Overview docs" folder -> module-level overview document
                    dest_rel = '/'.join([ascii_name(mname), ascii_name(gname), ascii_name(fname)])
                    if copy_pdf(fpath, os.path.join(docs_root, *dest_rel.split('/'))): copied += 1
                    total += 1
                    mod['overview'].append({'title': clean(fname[:-4].replace('_', ' ')), 'path': 'docs/' + dest_rel})
                    continue
                if not fm:
                    issues.append(['PDF name has no menu code', rel_issue, 'Rename as "NN.NN.NN.NN - Title.pdf"']); continue
                code, title = fm.group(1), clean(fm.group(2)) or fm.group(1)
                dest_rel = '/'.join([ascii_name(mname), ascii_name(gname), ascii_name(fname)])
                if copy_pdf(fpath, os.path.join(docs_root, *dest_rel.split('/'))): copied += 1
                total += 1
                url = 'docs/' + dest_rel
                if len(code.split('.')) == 2:             # "00.02-... Overview.pdf" -> the group's own document
                    g = groups.get(code)
                    if g: g['doc'] = url; g['docTitle'] = title
                    else: issues.append(['Overview PDF has no matching group', rel_issue, code])
                    continue
                target = groups.get(gm.group(1)) if gm else None
                if gm and code[:5] != gm.group(1):
                    issues.append(['File code does not match its folder', rel_issue, 'Folder ' + gm.group(1)])
                if target is None:
                    issues.append(['No folder for this code', rel_issue, code]); continue
                if code in seen_codes:
                    issues.append(['Duplicate menu code', rel_issue, 'Also: ' + seen_codes[code]])
                seen_codes[code] = rel_issue
                target['items'].append({'code': code, 'title': title, 'path': url})
        for g in mod['groups']:
            g['items'].sort(key=lambda i: natkey(i['code']))
            if not g['items'] and not g['doc']:
                issues.append(['Group has no PDFs yet', mod['code'] + '-' + mod['name'] + ' / ' + g['code'] + ' ' + g['name'], 'Add documents'])
        mod['groups'].sort(key=lambda g: natkey(g['code']))
        mod['overview'].sort(key=lambda o: o['title'].lower())
        modules.append(mod)
        if not mod['groups']:
            issues.append(['Module has no groups', mname, ''])

    guide = []
    gdir = os.path.join(DEPLOY, 'guide')
    if os.path.isdir(gdir):
        guide = sorted('guide/' + f for f in os.listdir(gdir) if f.lower().endswith('.pdf'))
    out = {'version': 'V7', 'generated': time.strftime('%Y-%m-%d %H:%M'), 'count': total, 'modules': modules, 'guide': guide}
    os.makedirs(os.path.join(DEPLOY, 'menu'), exist_ok=True)
    with open(os.path.join(DEPLOY, 'menu', 'v7-menu.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    os.makedirs(REPORT, exist_ok=True)
    with open(os.path.join(REPORT, 'v7_documents_needing_attention.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['Issue', 'Where', 'Suggested action']); w.writerows(sorted(issues))
    with open(os.path.join(REPORT, 'v7_coverage_by_group.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['Module', 'Group', 'Documents', 'Overview PDF'])
        for m in modules:
            for g in m['groups']:
                w.writerow([m['code'] + ' ' + m['name'], g['code'] + ' ' + g['name'], len(g['items']), 'Yes' if g['doc'] else ''])
    with open(os.path.join(REPORT, 'v7_all_documents.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['Module', 'Group', 'Code', 'Title', 'Path'])
        for m in modules:
            for g in m['groups']:
                for i in g['items']:
                    w.writerow([m['code'] + ' ' + m['name'], g['code'] + ' ' + g['name'], i['code'], i['title'], i['path']])
    print('Modules: %d | Groups: %d | PDFs indexed: %d | newly copied: %d | issues: %d' % (
        len(modules), sum(len(m['groups']) for m in modules), total, copied, len(issues)))
    print('Menu  :', os.path.join(DEPLOY, 'menu', 'v7-menu.json'))
    print('Report:', REPORT)


if __name__ == '__main__':
    main()
