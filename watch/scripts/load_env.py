"""Tiny .env loader (standard library only).

Usage in any script:
    import load_env
    load_env.load()
    key = os.environ["ROBLOX_API_KEY"]

Never prints values.
"""
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / ".env"


def parse(path=DEFAULT_PATH):
    """Return {NAME: value} from a .env file. Skips blank lines and # comments."""
    values = {}
    path = Path(path)
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        # Allow NAME="value" or NAME='value'
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if name:
            values[name] = value
    return values


def load(path=DEFAULT_PATH, override=False):
    """Put .env values into os.environ. Existing env vars win unless override=True."""
    for name, value in parse(path).items():
        if override or name not in os.environ:
            os.environ[name] = value
