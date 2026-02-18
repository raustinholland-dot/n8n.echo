#!/usr/bin/env python3
"""
ECHO Review Portal
- Receives execution ID from n8n via POST /receive
- Fetches the n8n form, injects wide-field CSS, serves it at /review
- Proxies form submission back to n8n
- Auto-opens browser on /review when triggered
"""

import subprocess
import threading
import time
import requests
from flask import Flask, request, Response, redirect

app = Flask(__name__)

N8N_BASE = "http://localhost:5678"
PORTAL_PORT = 5679

current_execution_id = None

WIDE_CSS = """
<style>
  body { max-width: 100% !important; padding: 0 40px !important; font-family: -apple-system, sans-serif; }
  .n8n-form, form, [class*="form"] { max-width: 100% !important; width: 100% !important; }
  textarea {
    width: 100% !important;
    min-height: 180px !important;
    font-size: 13px !important;
    font-family: -apple-system, monospace !important;
    padding: 10px !important;
    box-sizing: border-box !important;
    resize: vertical !important;
  }
  input[type="text"], input[type="email"] {
    width: 100% !important;
    font-size: 13px !important;
    padding: 8px !important;
    box-sizing: border-box !important;
  }
  label { font-weight: 600 !important; font-size: 13px !important; display: block; margin-top: 18px; margin-bottom: 4px; }
  button[type="submit"] {
    margin-top: 24px !important;
    padding: 12px 40px !important;
    font-size: 15px !important;
    background: #ff6d5a !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    cursor: pointer !important;
  }
  .container, main, [class*="container"] { max-width: 100% !important; padding: 20px 40px !important; }
</style>
"""


def open_browser(url, delay=1.5):
    time.sleep(delay)
    subprocess.Popen(["open", url])


@app.route("/receive", methods=["POST"])
def receive():
    global current_execution_id
    data = request.get_json(force=True)
    current_execution_id = data.get("execution_id")
    print(f"[portal] Received execution_id: {current_execution_id}")
    threading.Thread(
        target=open_browser, args=(f"http://localhost:{PORTAL_PORT}/review",), daemon=True
    ).start()
    return {"status": "ok", "execution_id": current_execution_id}, 200


@app.route("/review")
def review():
    if not current_execution_id:
        return "No active execution. Send a trigger email first.", 404
    n8n_url = f"{N8N_BASE}/form-waiting/{current_execution_id}"
    try:
        resp = requests.get(n8n_url, timeout=10)
        html = resp.text
        # Inject wide CSS before </head>
        if "</head>" in html:
            html = html.replace("</head>", WIDE_CSS + "</head>")
        else:
            html = WIDE_CSS + html
        # Rewrite form action to point back through portal proxy
        html = html.replace(
            f'action="/form-waiting/{current_execution_id}"',
            f'action="/submit/{current_execution_id}"'
        )
        # Also catch cases where action uses the full URL or relative path variations
        html = html.replace(
            f'action="http://localhost:5678/form-waiting/{current_execution_id}"',
            f'action="/submit/{current_execution_id}"'
        )
        return html
    except Exception as e:
        return f"Error fetching n8n form: {e}", 502


@app.route("/submit/<exec_id>", methods=["POST"])
def submit(exec_id):
    n8n_url = f"{N8N_BASE}/form-waiting/{exec_id}"
    try:
        resp = requests.post(
            n8n_url,
            data=request.form,
            headers={"Content-Type": request.content_type},
            allow_redirects=False,
            timeout=15,
        )
        if resp.status_code in (301, 302, 303):
            return redirect(resp.headers.get("Location", "/done"))
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("content-type", "text/html"))
    except Exception as e:
        return f"Error submitting to n8n: {e}", 502


@app.route("/done")
def done():
    return """
    <html><head><style>
      body { font-family: -apple-system, sans-serif; display: flex; align-items: center;
             justify-content: center; height: 100vh; margin: 0; background: #f5f5f5; }
      .box { text-align: center; padding: 40px; background: white; border-radius: 12px;
             box-shadow: 0 2px 20px rgba(0,0,0,0.1); }
      h2 { color: #333; } p { color: #666; }
    </style></head><body>
      <div class="box">
        <h2>Artifacts submitted</h2>
        <p>n8n is processing. Check your email for the final output.</p>
      </div>
    </body></html>
    """


if __name__ == "__main__":
    print(f"[echo_portal] Running on http://localhost:{PORTAL_PORT}")
    print(f"[echo_portal] Waiting for n8n to POST execution IDs to /receive")
    app.run(host="0.0.0.0", port=PORTAL_PORT, debug=False)
