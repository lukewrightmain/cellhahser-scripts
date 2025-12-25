#!/usr/bin/env python3
"""Cellhasher Termux SSH Setup

Runs on the host machine (Windows/macOS/Linux) using the Python configured in Cellhasher Settings.
Uses adb to:
- verify Termux is installed
- push a Termux bash script to the device
- open Termux and execute the script to install/configure OpenSSH

NOTE: This script contains a placeholder token __TERMUX_SSH_PASSWORD__ that is replaced by the
Rust backend before execution.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
import time

# Provided by Rust via template replacement.
# After replacement, this should be a valid Python string literal.
TERMUX_SSH_PASSWORD = __TERMUX_SSH_PASSWORD__

ADB = os.environ.get("adb_path", "adb")
DEVICES = os.environ.get("devices", "").split()


def _creationflags() -> int:
    if sys.platform == "win32":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return 0


def run(args: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    print("[host]", " ".join(args))
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture,
        creationflags=_creationflags(),
    )


def check_termux_installed(device_id: str) -> bool:
    cp = run([ADB, "-s", device_id, "shell", "pm", "list", "packages", "com.termux"], check=False)
    return "com.termux" in (cp.stdout or "")


def main() -> int:
    if not DEVICES:
        print("[error] No devices provided (env var 'devices' is empty)")
        return 2

    if not isinstance(TERMUX_SSH_PASSWORD, str) or not TERMUX_SSH_PASSWORD.strip():
        print("[error] TERMUX_SSH_PASSWORD is empty")
        return 2

    device_id = DEVICES[0]
    print(f"[info] Setting up Termux SSH on: {device_id}")

    if not check_termux_installed(device_id):
        print("[error] Termux is not installed on the device")
        return 3

    # Bash script executed inside Termux.
    # We embed password safely using shlex.quote for POSIX shells.
    pw = shlex.quote(TERMUX_SSH_PASSWORD)
    termux_bash_script = f"""#!/data/data/com.termux/files/usr/bin/bash
set -e

TERMUX_SSH_PASSWORD={pw}

if command -v sshd >/dev/null 2>&1; then
  echo "OpenSSH already installed (sshd found)"
else
  pkg update -y
  pkg install -y openssh
fi

# Update password (Termux's passwd prompts twice)
if [ -n "$TERMUX_SSH_PASSWORD" ]; then
  printf '%s\n%s\n' "$TERMUX_SSH_PASSWORD" "$TERMUX_SSH_PASSWORD" | passwd
fi

# Start sshd if not already running
if ! pgrep -x sshd >/dev/null 2>&1; then
  sshd
fi

echo "Termux SSH ready"
"""

    # Temp debugging aid: print the exact Termux bash script we will run.
    print("[debug] Termux bash script to run:\n" + termux_bash_script)

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", delete=False, suffix=".sh") as f:
        f.write(termux_bash_script)
        local_script_path = f.name

    device_script_path = "/data/local/tmp/setup_ssh.sh"

    # Stop Termux first.
    run([ADB, "-s", device_id, "shell", "am", "force-stop", "com.termux"], check=False)
    time.sleep(1)

    # Push script.
    run([ADB, "-s", device_id, "push", local_script_path, device_script_path])
    run([ADB, "-s", device_id, "shell", "chmod", "755", device_script_path])

    # Launch Termux UI and run script (via keyboard injection).
    run([ADB, "-s", device_id, "shell", "am", "start", "-n", "com.termux/.app.TermuxActivity"], check=False)
    time.sleep(4)

    # ADB input text uses %s for spaces.
    typed = "bash%s" + device_script_path
    run([ADB, "-s", device_id, "shell", "input", "text", typed], check=False)
    time.sleep(0.5)
    run([ADB, "-s", device_id, "shell", "input", "keyevent", "66"], check=False)

    print("[info] Setup triggered. If Termux is open, you should see output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
