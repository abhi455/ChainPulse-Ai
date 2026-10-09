from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

API_LOG = LOG_DIR / "api.log"
STREAMLIT_LOG = LOG_DIR / "streamlit.log"

HOST = "127.0.0.1"
PORT = 8000


def port_open() -> bool:
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.settimeout(0.5)

    try:
        return sock.connect_ex(
            (HOST, PORT)
        ) == 0
    finally:
        sock.close()


def wait_for_api(timeout: int = 30) -> bool:
    start = time.time()

    while time.time() - start < timeout:

        if port_open():

            try:
                with urlopen(
                    f"http://{HOST}:{PORT}/api/v1/health",
                    timeout=2,
                ):
                    return True
            except Exception:
                pass

        time.sleep(0.5)

    return False


def start_api():

    log = API_LOG.open(
        "a",
        encoding="utf-8",
    )

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=str(ROOT),
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=getattr(
            subprocess,
            "CREATE_NO_WINDOW",
            0,
        ),
    )


def main():

    print("=" * 60)
    print("CHAINPULSE AI")
    print("=" * 60)

    api_process = None

    if port_open():

        print("API: already running")

    else:

        print("API: starting...")

        api_process = start_api()

        if not wait_for_api():

            print("")
            print("API FAILED TO START")
            print("")
            print(
                API_LOG.read_text(
                    encoding="utf-8",
                    errors="replace",
                )[-8000:]
            )

            if api_process:
                api_process.kill()

            input(
                "\nPress Enter to close..."
            )

            raise SystemExit(1)

        print("API: READY")

    print("STREAMLIT: starting...")

    streamlit_log = STREAMLIT_LOG.open(
        "a",
        encoding="utf-8",
    )

    streamlit_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/streamlit/app.py",
            "--server.headless",
            "true",
        ],
        cwd=str(ROOT),
        stdout=streamlit_log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=getattr(
            subprocess,
            "CREATE_NO_WINDOW",
            0,
        ),
    )

    print("CHAINPULSE: READY")
    print("")
    print("Open:")
    print("http://localhost:8501")
    print("")
    print("Close this launcher to stop ChainPulse.")

    try:

        while True:

            if streamlit_process.poll() is not None:
                break

            if api_process is not None:
                if api_process.poll() is not None:

                    print("")
                    print(
                        "API STOPPED. Restarting..."
                    )

                    api_process = start_api()

                    if not wait_for_api():
                        print(
                            "API restart failed. "
                            "Check logs/api.log"
                        )
                        break

            time.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:

        if streamlit_process.poll() is None:
            streamlit_process.terminate()

        if api_process is not None:
            if api_process.poll() is None:
                api_process.terminate()

        print("")
        print("CHAINPULSE STOPPED")


if __name__ == "__main__":
    main()
