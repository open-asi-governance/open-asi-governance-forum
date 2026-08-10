#!/usr/bin/env python3
"""NEGATIVE CONTROL for responsiveness_check.

Serves what a health endpoint serves when a component fails: HTTP 503 with a body whose
`status` is "unhealthy". Nothing else is perturbed -- the transport is fine, the endpoint
answers, and it answers that it is not healthy.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

BODY = json.dumps({"status": "unhealthy",
                   "components": {"database": {"status": "unavailable"}},
                   "timestamp": "2026-08-10T00:00:00Z"}).encode()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(503)                     # service unavailable
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(BODY)))
        self.end_headers()
        self.wfile.write(BODY)
    def log_message(self, *a): pass

HTTPServer(("127.0.0.1", 8080), H).serve_forever()
