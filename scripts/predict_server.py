# -*- coding: utf-8 -*-
"""Small local HTTP server that exposes the literary scorer to index.php."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Runtime bootstrap
# ---------------------------------------------------------------------------
def rerun_with_venv_python():
    repo_root = Path(__file__).resolve().parent.parent
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    current_python = Path(sys.executable).resolve()
    if venv_python.exists() and current_python != venv_python.resolve():
        command = [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]]
        raise SystemExit(subprocess.call(command, cwd=repo_root))


rerun_with_venv_python()

from predict_core import LiteraryPredictor, read_sentences_from_text


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------
class PredictHandler(BaseHTTPRequestHandler):
    predictor: LiteraryPredictor
    batch_size: int = 4

    def log_message(self, format, *args):
        return

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_GET(self):
        if urlparse(self.path).path == "/health":
            self.send_json(200, {"ok": True, "ready": True})
            return
        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/predict":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            text = str(payload.get("text", "")).strip()
            sentences = read_sentences_from_text(text)
            if not sentences:
                self.send_json(400, {"ok": False, "error": "No sentence found."})
                return
            rows = self.predictor.predict(sentences, batch_size=self.batch_size)
            self.send_json(200, {"ok": True, "results": rows})
        except Exception as exc:
            self.send_json(500, {"ok": False, "error": str(exc)})


# ---------------------------------------------------------------------------
# Server entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Small local prediction server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", default="models/literary_parsbert_light.joblib")
    parser.add_argument("--batch_size", type=int, default=4)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    PredictHandler.predictor = LiteraryPredictor(repo_root / args.model)
    PredictHandler.batch_size = args.batch_size

    server = ThreadingHTTPServer((args.host, args.port), PredictHandler)
    print(f"Prediction server is ready at http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
