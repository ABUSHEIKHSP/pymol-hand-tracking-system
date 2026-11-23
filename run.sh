#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -f ".venv/bin/activate" ]]; then
    echo "Virtual environment not found. Run: bash install.sh"
    exit 1
fi

if [[ ! -s "gesture_recognizer.task" ]]; then
    echo "MediaPipe model not found. Run: bash install.sh"
    exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

# Verify that PyMOL's XML-RPC server is reachable before opening the webcam.
python - <<'PY'
import socket
import sys

host = "127.0.0.1"
port = 9123

try:
    with socket.create_connection((host, port), timeout=2):
        pass
except OSError:
    print(
        "PyMOL XML-RPC server is not reachable at "
        f"http://{host}:{port}.\n"
        "Start PyMOL first with: pymol -R",
        file=sys.stderr,
    )
    sys.exit(1)
PY

exec python main.py
