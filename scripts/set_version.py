"""
Sets the release version in ONE go:  VERSION file  +  the cache-busting numbers in webapp\\layout.html
(browsers keep old css / js until this number changes).

    python scripts\\set_version.py 7.0.33

Then add a section for it at the top of CHANGELOG.md.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'\d+\.\d+\.\d+', sys.argv[1]):
        sys.exit('usage: python scripts\\set_version.py MAJOR.MINOR.PATCH   (e.g. 7.0.33)')
    ver = sys.argv[1]
    lay = os.path.join(ROOT, 'webapp', 'layout.html')
    with open(lay, encoding='utf-8') as f:
        s = f.read()
    s, n = re.subn(r'((?:app\.css|app\.js)\?v=)\d+\.\d+\.\d+', r'\g<1>' + ver, s)
    if n != 2:
        sys.exit('expected 2 version markers (app.css, app.js) in layout.html, found %d' % n)
    with open(lay, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    with open(os.path.join(ROOT, 'VERSION'), 'w', encoding='ascii', newline='\n') as f:
        f.write(ver + '\n')
    print('version set to %s  (VERSION + layout.html). Now add it to CHANGELOG.md.' % ver)


if __name__ == '__main__':
    main()
