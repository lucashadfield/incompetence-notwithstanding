#!/usr/bin/env python3
"""Throwaway upload page for getting cover images off a phone onto this box.

    python3 tools/upload_server.py [port] [dest]

Serves a mobile-friendly multi-file upload form on 0.0.0.0 so it's reachable
over the tailnet. Files land in ./uploads/. Kill it when you're done.

No auth, no TLS, no upload size limit, and the whole request body is read into
memory. Tailnet-only, run it for the minute you need it and kill it.
"""
import html
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
DEST = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "uploads")
os.makedirs(DEST, exist_ok=True)

PAGE = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Upload covers</title>
<style>
 body{{font:16px/1.5 -apple-system,system-ui,sans-serif;background:#FAF6EA;color:#1F2E2B;
      margin:0;padding:2rem 1.25rem;max-width:34rem}}
 h1{{font-size:1.25rem;letter-spacing:-.02em;margin:0 0 .25rem}}
 p{{color:#4E635E;margin:0 0 1.5rem}}
 input[type=file]{{display:block;width:100%;padding:1.25rem;background:#FFFDF6;
      border:1px solid #1F2E2B;margin-bottom:1rem}}
 button{{font:inherit;padding:.85rem 1.5rem;background:#26706C;color:#FAF6EA;border:0;
      box-shadow:4px 4px 0 #A9CFD2}}
 ul{{padding-left:1.1rem}} li{{font-family:ui-monospace,monospace;font-size:.85rem}}
</style></head><body>
<h1>Upload covers</h1><p>Files land in <code>{dest}</code>.</p>
<form method=post enctype=multipart/form-data>
<input type=file name=f multiple accept="image/*">
<button type=submit>Upload</button></form>
{msg}
<h2 style="font-size:.9rem;margin-top:2rem">Already here</h2><ul>{listing}</ul>
</body></html>"""


def render(msg=""):
    files = sorted(os.listdir(DEST))
    listing = "".join(
        f"<li>{html.escape(f)} — {os.path.getsize(os.path.join(DEST, f)) // 1024} KB</li>"
        for f in files
    ) or "<li>nothing yet</li>"
    return PAGE.format(dest=html.escape(DEST), msg=msg, listing=listing).encode()


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(render())

    def do_POST(self):
        ctype = self.headers.get("Content-Type", "")
        m = re.search(r"boundary=(.+)", ctype)
        if not m:
            return self._send(b"no boundary", 400)
        boundary = m.group(1).strip('"').encode()
        body = self.rfile.read(int(self.headers["Content-Length"]))
        saved = []
        for part in body.split(b"--" + boundary):
            head, _, data = part.partition(b"\r\n\r\n")
            fn = re.search(rb'filename="([^"]*)"', head)
            if not fn or not fn.group(1):
                continue
            name = os.path.basename(fn.group(1).decode("utf-8", "replace"))
            # Each part ends with the CRLF that precedes the next boundary.
            # Strip exactly those two bytes: rstrip(b"\r\n--") would eat any
            # trailing 0x0d / 0x0a / 0x2d byte of the file itself, which
            # silently truncates binaries whose last byte happens to match.
            if data.endswith(b"\r\n"):
                data = data[:-2]
            if not data:
                continue
            path = os.path.join(DEST, name)
            stem, ext = os.path.splitext(name)
            n = 1
            while os.path.exists(path):
                path = os.path.join(DEST, f"{stem}-{n}{ext}")
                n += 1
            with open(path, "wb") as fh:
                fh.write(data)
            saved.append(os.path.basename(path))
        msg = (
            "<p style='color:#26706C'>Saved: " + html.escape(", ".join(saved)) + "</p>"
            if saved else "<p>Nothing saved.</p>"
        )
        self._send(render(msg))

    def log_message(self, *a):
        sys.stderr.write("%s - %s\n" % (self.address_string(), a[0] % a[1:]))


print(f"upload server on http://0.0.0.0:{PORT}/  →  {DEST}", flush=True)
ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
