"""Lighthouse ERP V7 Help Centre - automatic updater.

Leave this running. Whenever a PDF is pasted into (or changed / renamed / removed from) the V7
documentation folder it, once the copy has finished:

  1. rebuilds the menu and copies the PDFs         (tools/build_v7.py)
  2. converts new / changed PDFs to Reader HTML    (tools/build_html.py)

Nothing to click and nothing to edit. Refresh the browser (F5) afterwards.

    python tools/auto_update.py
    python tools/auto_update.py "D:\\LHS_ERP_HELP_V7\\V7_MENU_HELP_DOC"      (another source folder)

Needs Python 3 and, for the Reader view:  pip install pymupdf pillow
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else r'D:\LHS_ERP_HELP_V7\V7_MENU_HELP_DOC'
POLL = 15                      # seconds between looks at the folder
LOG = os.path.join(HERE, 'auto_update.log')


def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S  ') + msg
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


def signature():
    """Cheap fingerprint of every PDF under the source folder: (count, total size, newest change)."""
    n = size = newest = 0
    for r, _, fs in os.walk(SOURCE):
        for f in fs:
            if f.lower().endswith('.pdf') and not f.startswith('~$'):
                try:
                    st = os.stat(os.path.join(r, f))
                except OSError:
                    continue
                n += 1; size += st.st_size; newest = max(newest, int(st.st_mtime))
    return n, size, newest


def run(script, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, script)] + list(args), capture_output=True, text=True)
    out = (r.stdout or '').strip().splitlines()
    for line in out[-3:] if r.returncode == 0 else out[-6:] + (r.stderr or '').strip().splitlines()[-4:]:
        log('    ' + line)
    return r.returncode == 0


def update():
    log('Change detected - updating ...')
    if not run('build_v7.py', SOURCE):
        log('Menu build FAILED (see lines above).')
        return
    if run('build_html.py'):
        run('build_md.py')             # Markdown copy of each Reader page, for "Open in ChatGPT / Claude"
        log('Done. Refresh the browser (F5) to see the changes.')
    else:
        log('Reader view build reported a problem (menu and PDFs are updated).')


def main():
    if not os.path.isdir(SOURCE):
        sys.exit('Source folder not found: ' + SOURCE)
    log('Watching ' + SOURCE + '   (Ctrl+C to stop)')
    done = None
    pending, since = None, 0
    while True:
        try:
            sig = signature()
            if sig != done:
                if sig == pending and time.time() - since >= POLL:      # unchanged for a full poll: the copy has finished
                    update()
                    done, pending = signature(), None
                elif sig != pending:
                    pending, since = sig, time.time()
            time.sleep(POLL)
        except KeyboardInterrupt:
            log('Stopped.')
            return
        except Exception as e:                                          # never let one bad pass kill the watcher
            log('Error: %s' % e)
            time.sleep(POLL)


if __name__ == '__main__':
    main()
