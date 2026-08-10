#!/usr/bin/env python3
"""NEGATIVE CONTROL for connectivity_check.

Reproduces AS-01's failure state: the process is alive and holds the listening socket, and the
capability behind it is dead. It accepts the TCP connection and then serves nothing at all.
"""
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 8080)); s.listen(8)
print("listening on 8080, serving nothing", flush=True)
while True:
    conn, _ = s.accept()          # accept, then hold it open and answer nothing
    try: conn.recv(65535)
    except Exception: pass
