LIGHTHOUSE ERP V7 HELP CENTRE - DEPLOYMENT
==========================================

DEPLOY
  1. On the Tomcat server create the NEW folder  webapps\LHS_ERP_HELP_DOC_V7  (the old LHS_ERP_HELP is not touched).
  2. Copy the CONTENTS of this folder into it.
     Keep:  layout.html  index.html  css\  js\  images\  menu\  docs\  html\  guide\  config\  vendor\  WEB-INF\
     (tools\ is optional - it is only needed on the PC where you update the docs)
  3. Restart Tomcat once (WEB-INF\web.xml is read at start), then open
        http://192.168.100.21:8888/LHS_ERP_HELP_DOC_V7/layout.html
     and press Ctrl+F5 once to drop the old cached version.

MANUAL, ONE CLICK: after pasting PDFs, double-click tools\update_now.bat. It updates the menu,
  copies the PDFs and builds the Reader view for the new / changed ones in one go, then stops.
  (First time only: pip install pymupdf pillow.)

AUTOMATIC (optional): double-click tools\auto_update.bat and leave it running.
  Whenever a PDF is pasted into the V7 documentation folder, the menu, the docs\ copy and the
  Reader (HTML) view are updated by themselves within about 30 seconds - just press F5.
  Run it on the PC / server that holds the deploy folder (for Tomcat: the copy under webapps).
  First time only: pip install pymupdf pillow.   Log: tools\auto_update.log
  To start with Windows put a shortcut to auto_update.bat in the folder  shell:startup

ADD / CHANGE DOCUMENTS LATER (step by step, same as update_now.bat)
  1. Put the PDFs in the V7 documentation folder using the same structure:
        <NN-Module Name - ABBR>\<NN.NN-Group Name>\<NN.NN.NN.NN - Title>.pdf
     (an "NN.NN-... Overview.pdf" placed in a group folder becomes that group's overview)
  2. Double-click tools\build_v7.bat  (needs Python 3 on that PC).
     It copies the PDFs to docs\, regenerates menu\v7-menu.json and writes reports to
     ..\LHS_ERP_HELP_V7_REPORT\
  3. Double-click tools\build_html.bat to refresh the Reader view (first time: pip install pymupdf pillow).
     Only new / changed PDFs are converted. No manual editing - the layout follows fixed rules.
  4. Copy the updated docs\, html\ and menu\ folders to the server.

SHOW / HIDE BUTTONS  (config\app.properties)
  Copy link, Print, Download, Save, Copy page for AI, PDF|Reader switch and the Previous/Next
  arrows can each be turned off: open config\app.properties in Notepad, set the line to
  false (e.g.  ui.btn.print=false), save, then press Ctrl+F5. A missing line means "shown".
  No Tomcat restart is needed. Copy the config\ folder to the server with the rest.

COPY PAGE FOR AI
  "Copy page for AI" copies the document as Markdown (page link, PDF link, text; no screenshots).
  "Open in ChatGPT / Claude" opens a chat with only a link and one line of description:
      Read from <link to the page's .md file> so I can ask questions about it. ...
  (no long text is pasted; the AI reads the page, so the site must be public).
  The .md files are made next to every Reader page (html\...\x.md) by tools\build_md.py;
  update_now.bat and auto_update.bat run it for new pages. The public address is  site.url  in
  config\app.properties (if it changes: edit it, run  python tools\build_md.py --force , copy html\).
  WEB-INF\web.xml (copy it to the server) teaches Tomcat the .md and .webp file types.

PDF VIEWER
  PDFs open in the Help Centre's own light viewer (PDF.js, in vendor\pdfjs): page number box,
  previous / next page, zoom - / + , Fit width, selectable text, Ctrl + mouse wheel to zoom.
  If it cannot load a file it falls back to the browser's own viewer automatically.
  To always use the browser's viewer instead:  ui.viewer=native  in config\app.properties.
  PDF.js is Mozilla's open-source library (Apache 2.0) - copy the vendor\ folder to the server.

READER VIEW
  Every document has a PDF | Reader switch above it. Reader is generated from the PDF
  into html\ (same folder structure): headings, numbered steps, bullet lists, tables and
  screenshots, with an "On this page" outline. If a document has no html\ file yet, the
  switch offers the PDF instead. The choice is remembered per browser.

GUIDE TAB
  Guide topics read V7 PDFs from guide\ (file names: see guide\README.txt).
  A topic whose PDF is not in that folder opens the "Document not available" page.
  The old V5 topic PDFs were moved to D:\LHS_ERP_HELP_V7_ARCHIVE\lhstopics_v5.
