from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_HOST = "127.0.0.1"
API_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173


def main() -> int:
    backend = start_process_if_needed(
        "API",
        [sys.executable, str(ROOT / "tools" / "webapp_server.py"), "--host", API_HOST, "--port", str(API_PORT)],
        API_HOST,
        API_PORT,
    )
    vite = start_process_if_needed(
        "Frontend",
        [
            "npm.cmd" if os.name == "nt" else "npm",
            "run",
            "dev:vite",
            "--",
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
            "--strictPort",
        ],
        FRONTEND_HOST,
        FRONTEND_PORT,
    )
    processes = [process for process in (backend, vite) if process is not None]

    print("Dev WebApp:")
    print(f"  Frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    print(f"  API:      http://{API_HOST}:{API_PORT}")

    try:
        while True:
            for process in processes:
                process_code = process.poll()
                if process_code is not None:
                    return process_code
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        for process in reversed(processes):
            stop_process(process)


def start_process_if_needed(label: str, args: list[str], host: str, port: int) -> subprocess.Popen[bytes] | None:
    if is_port_open(host, port):
        print(f"{label} already running on http://{host}:{port}; reusing it.")
        return None
    return subprocess.Popen(args, cwd=ROOT)


def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
