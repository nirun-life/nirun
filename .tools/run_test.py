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
BOLD = "\033[1m"
RESET = "\033[0m"

MODULES = [
    "ni_community_care",
    "ni_device",
]

result = subprocess.run(
    [
        sys.executable,
        "odoo-bin",
        "-c",
        CONFIG_PATH,
        "--test-enable",
        "-i",
        ",".join(MODULES),
        "--stop-after-init",
    ],
    cwd=ODOO_PATH,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

output = (result.stdout or "") + (result.stderr or "")

# จัดกลุ่ม log ตาม module
module_logs = {m: [] for m in MODULES}

for line in output.splitlines():
    for module in MODULES:
        if f"odoo.addons.{module}" in line or f"odoo.tests.stats: {module}" in line:
            module_logs[module].append(line)
            break

# แสดงผลแยกตาม module
for module in MODULES:
    logs = module_logs[module]

    started = [line for line in logs if "Starting" in line]
    failed = [line for line in logs if "FAIL:" in line]
    errors = [
        line
        for line in logs
        if "ERROR:" in line and "test_" in line and "FAIL:" not in line
    ]

    failed_names = [line.split("FAIL:")[-1].strip() for line in failed]
    error_names = [line.split("ERROR:")[-1].strip() for line in errors]
    passed = [
        line
        for line in started
        if not any(name in line for name in failed_names + error_names)
    ]

    # ดึง summary จาก odoo.tests.stats
    summary = next((line for line in logs if "odoo.tests.stats" in line), None)
    total = len(started)

    print(f"\n{BOLD}{CYAN}{'=' * 50}{RESET}")
    print(f"{BOLD}{CYAN} MODULE: {module.upper()}{RESET}")
    print(
        f"{CYAN} Total: {total}  {GREEN}Passed: {len(passed)}  {RED}Failed: {len(failed)}  {YELLOW}Errors: {len(errors)}{RESET}"
    )
    if summary:
        print(f"{CYAN} {summary.strip()}{RESET}")
    print(f"{CYAN}{'=' * 50}{RESET}")

    for line in failed:
        print(f"{RED}❌ FAIL  {line.strip()}{RESET}")
    for line in errors:
        print(f"{YELLOW}⚠️  ERROR {line.strip()}{RESET}")
    for line in passed:
        name = line.split("Starting ")[-1].strip()
        print(f"{GREEN}✅ PASS  {name}{RESET}")

    if not logs:
        print(f"{YELLOW}  ไม่พบ log ของ module นี้{RESET}")

print(f"\n{CYAN}{'=' * 50}{RESET}\n")
