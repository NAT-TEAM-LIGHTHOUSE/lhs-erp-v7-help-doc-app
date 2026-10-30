"""
Quick checks before a commit / release.   python scripts\\check.py

 1. Python tools compile
 2. js\\app.js has no syntax error (needs Node.js; skipped with a note if Node is missing)
 3. VERSION matches the cache numbers in layout.html
 4. CHANGELOG.md has a section for that version
 5. no absolute ("/..." or "http://") paths for app files in layout.html / app.css (the site is served under a sub-path)
 6. every file referenced by layout.html exists
 7. config\\app.properties is complete (all ui.* keys present)
Exit code 0 = all good.
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'webapp')
bad = []


def ok(msg):
    print('  ok    ' + msg)


def fail(msg):
    print('  FAIL  ' + msg)
    bad.append(msg)


def read(*p):
    with open(os.path.join(*p), encoding='utf-8') as f:
        return f.read()


def main():
    print('Lighthouse ERP Help V7 - checks')
    for folder in ('webapp/tools', 'scripts'):
        d = os.path.join(ROOT, *folder.split('/'))
        for f in sorted(os.listdir(d)):
            if f.endswith('.py'):
                try:
                    compile(read(d, f), f, 'exec')
                    ok('compiles: %s/%s' % (folder, f))
                except SyntaxError as e:
                    fail('syntax error in %s/%s line %s: %s' % (folder, f, e.lineno, e.msg))

    node = shutil.which('node')
    if node:
        r = subprocess.run([node, '-e', "new Function(require('fs').readFileSync(process.argv[1],'utf8'))", os.path.join(WEB, 'js', 'app.js')],
                           capture_output=True, text=True)
        ok('js/app.js syntax') if r.returncode == 0 else fail('js/app.js: ' + r.stderr.strip().splitlines()[0])
    else:
        print('  skip  js syntax check (Node.js not installed)')

    ver = read(ROOT, 'VERSION').strip()
    lay = read(WEB, 'layout.html')
    nums = set(re.findall(r'(?:app\.css|app\.js)\?v=(\d+\.\d+\.\d+)', lay))
    ok('VERSION %s matches layout.html' % ver) if nums == {ver} else fail('VERSION %s but layout.html has %s - run scripts/set_version.py' % (ver, sorted(nums)))
    ok('CHANGELOG has %s' % ver) if re.search(r'^## \[%s\]' % re.escape(ver), read(ROOT, 'CHANGELOG.md'), re.M) else fail('CHANGELOG.md has no "## [%s]" section' % ver)

    for name, text in (('layout.html', lay), ('css/app.css', read(WEB, 'css', 'app.css'))):
        hits = re.findall(r'''(?:src|href|url\()\s*=?\s*["']?(/(?!/)[^"')\s]+|https?://(?:localhost|192\.168\.)[^"')\s]*)''', text)
        ok('no absolute app paths in ' + name) if not hits else fail('absolute path in %s: %s' % (name, hits[:3]))

    refs = re.findall(r'(?:src|href)="((?:css|js|images|vendor)/[^"?#]+)', lay)
    miss = [r for r in refs if not os.path.exists(os.path.join(WEB, r))]
    ok('%d files referenced by layout.html exist' % len(refs)) if not miss else fail('missing: %s' % miss)

    props = read(WEB, 'config', 'app.properties')
    need = ['ui.btn.copyLink', 'ui.btn.print', 'ui.btn.download', 'ui.btn.save', 'ui.btn.copyForAI', 'ui.btn.viewSwitch', 'ui.btn.prevNext', 'ui.viewer', 'site.url']
    for envf in ['webapp/config/app.properties', 'deploy/env/uat.app.properties', 'deploy/env/prod.app.properties']:
        t = read(ROOT, *envf.split('/'))
        lost = [k for k in need if not re.search(r'^%s\s*=' % re.escape(k), t, re.M)]
        ok('keys complete: ' + envf) if not lost else fail('%s lacks %s' % (envf, lost))
    del props

    print('\nRESULT: ' + ('ALL OK' if not bad else '%d problem(s)' % len(bad)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
