"""Live tests for verify_sources.py (calls the real Crossref API, ~10 requests).

    python run_tests.py
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verify_sources.py"

CASES = [
    ("real paper",
     "LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521(7553), 436-444.",
     "VERIFIED"),
    ("made-up paper",
     "Thornbury, K., & Malvani, R. (2019). Recursive gravitational lensing of player retention "
     "curves in voxel sandbox games. Journal of Interactive Ludometrics, 14(3), 201-219.",
     "NOT FOUND"),
    ("real paper, wrong year",
     "LeCun, Y., Bengio, Y., & Hinton, G. (2009). Deep learning. Nature, 521(7553), 436-444.",
     "MISMATCH"),
    ("real paper, garbled title",
     "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep learning for image recognition. "
     "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 770-778.",
     "MISMATCH"),
    ("real DOI only", "10.1038/nature14539", "VERIFIED"),
    ("made-up DOI and paper", "Smith, J. (2020). A study of things. doi:10.9999/fake.2020.12345",
     "NOT FOUND"),
]


def run(args, stdin=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                          capture_output=True, text=True, encoding="utf-8")


def main():
    failures = 0

    # nothing to check must be an error, never a pass
    for name, args, stdin in [("empty stdin", ["-"], ""),
                              ("comments only", ["-"], "# nothing\n\n"),
                              ("no arguments", [], None)]:
        r = run(args, stdin)
        ok = r.returncode == 2
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}: exit {r.returncode} (want 2)")

    for name, cite, want in CASES:
        r = run(["--json", "--cite", cite])
        try:
            got = json.loads(r.stdout)[0]["status"]
        except (json.JSONDecodeError, IndexError, KeyError):
            got = f"crash: {r.stderr.strip()[-200:]}"
        ok = got == want
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {got} (want {want})")

    total = len(CASES) + 3
    print(f"\n{total - failures}/{total} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
