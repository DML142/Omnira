#!/usr/bin/env python3
"""Smoke-test the built process, including actual SIGTERM handling."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
env = {**os.environ, 'OMNIRA_GATEWAY_ADDR': f'127.0.0.1:{port}'}
process = subprocess.Popen([str(ROOT / 'bin/gateway')], env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    deadline = time.monotonic() + 10
    while True:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/healthz', timeout=1) as response:
                if response.status != 200 or json.load(response) != {'status': 'ok'}:
                    raise RuntimeError('Unexpected health response')
            break
        except (urllib.error.URLError, TimeoutError):
            if process.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError('Gateway did not become healthy')
            time.sleep(0.05)
    process.send_signal(signal.SIGTERM)
    output, errors = process.communicate(timeout=12)
    if process.returncode != 0 or errors:
        raise RuntimeError(f'Gateway shutdown failed: {process.returncode} {errors}')
    entries = [json.loads(line) for line in output.splitlines()]
    if not any(entry['msg'] == 'gateway stopped' for entry in entries):
        raise RuntimeError('Graceful process exit was not recorded')
finally:
    if process.poll() is None:
        process.kill()
        process.wait(timeout=5)
print('Gateway process checks passed: health and SIGTERM shutdown.')
