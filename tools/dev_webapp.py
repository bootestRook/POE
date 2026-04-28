from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    backend = subprocess.Popen(
        [sys.executable, str(ROOT / "tools" / "webapp_server.py"), "--port", "8000"],
        cwd=ROOT,
    )
    vite = subprocess.Popen(
        ["npm.cmd" if os.name == "nt" else "npm", "run", "dev:vite", "--", "--port", "5173"],
        cwd=ROOT,
    )

    print("Dev WebApp:")
    print("  Frontend: http://127.0.0.1:5173")
    print("  API:      http://127.0.0.1:8000")

    try:
        while True:
            backend_code = backend.poll()
            vite_code = vite.poll()
            if backend_code is not None:
                return backend_code
            if vite_code is not None:
                return vite_code
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        stop_process(vite)
        stop_process(backend)


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
