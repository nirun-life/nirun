# pylint: disable=print-used

import subprocess
import sys

ODOO_PATH = r"C:\Users\nutcha\odoo"
CONFIG_PATH = r"C:\Users\nutcha\Documents\nirun\odoo.conf"

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

result = subprocess.run(
    [
        sys.executable,
        "odoo-bin",
        "-c",
        CONFIG_PATH,
        "--test-enable",
        "-i",
        "ni_device",
        "--stop-after-init",
    ],
    cwd=ODOO_PATH,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

output = (result.stdout or "") + (result.stderr or "")

print(f"\n{CYAN}========== TEST RESULTS =========={RESET}")  # noqa: T201
for line in output.splitlines():
    if "FAIL" in line:
        print(f"{RED}❌ {line}{RESET}")  # noqa: T201
    elif "ERROR" in line and "test_" in line:
        print(f"{YELLOW}⚠️  {line}{RESET}")  # noqa: T201
    elif "ok" in line:
        print(f"{GREEN}✅ {line}{RESET}")  # noqa: T201
    elif "Ran " in line or "failures" in line or "error(s)" in line:
        print(f"{CYAN}{line}{RESET}")  # noqa: T201
print(f"{CYAN}=================================={RESET}")  # noqa: T201
