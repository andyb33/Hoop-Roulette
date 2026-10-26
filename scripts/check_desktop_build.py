"""Launch the real packaged native window and require gameplay + clean shutdown."""
import json
import subprocess
import sys
from pathlib import Path

executable = Path(sys.argv[1]).resolve()
report = Path("desktop-smoke.json").resolve()
try:
    process = subprocess.run([str(executable), "--smoke-test", str(report)], timeout=150)
except subprocess.TimeoutExpired:
    raise SystemExit("Native app did not close within 150 seconds")
if not report.exists():
    raise SystemExit(f"Native app did not write a QA report (exit {process.returncode})")
result = json.loads(report.read_text(encoding="utf-8"))
print(json.dumps(result, indent=2))
assert process.returncode == 0 and result.get("success") and result.get("server_stopped"), result
