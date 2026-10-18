"""brain.py - helper for the Obsidian brain vault (standard library only).

Commands:
  next-id PREFIX        next free id for PREFIX this year, from REGISTRY.md
  search WORDS...       registry lines containing ALL the words, highest value first
  add NOTE.md           add or replace the note's REGISTRY.md line from its frontmatter
  log ACTION ID TEXT    append one CHANGELOG.md line
  check                 every note has an id and a registry line, every registry path exists

Vault path: BRAIN_PATH environment variable, default C:/AI-Lab/brain.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(os.environ.get("BRAIN_PATH", "C:/AI-Lab/brain"))
REGISTRY = VAULT / "REGISTRY.md"
CHANGELOG = VAULT / "CHANGELOG.md"

# Folders whose notes are not registered, and root files that are vault plumbing, not notes.
SKIP_FOLDERS = {"00 System", "80 Archive", "90 Inbox"}
SKIP_ROOT_FILES = {"REGISTRY.md", "CHANGELOG.md", "README.md"}

VALUE_RANK = {"critical": 0, "high": 1, "medium": 2}
STATUSES = {"active", "paused", "done", "archived"}
REQUIRED = ["id", "type", "status", "value", "summary"]
ID_RE = re.compile(r"^([A-Z]+)-(\d{4})-(\d{3,})$")


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def read_text(path):
    # utf-8-sig also accepts files that Windows tools saved with a BOM
    return path.read_text(encoding="utf-8-sig")


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def registry_lines():
    """Return (all raw lines, list of parsed entries). Entry = dict with the six fields."""
    if not REGISTRY.exists():
        fail(f"REGISTRY.md not found at {REGISTRY}")
    raw = read_text(REGISTRY).splitlines()
    entries = []
    for n, line in enumerate(raw, 1):
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        parts = s.split("|")
        if len(parts) != 6:
            entries.append({"bad": True, "lineno": n, "line": s})
            continue
        e = dict(zip(["id", "type", "status", "path", "value", "summary"], (p.strip() for p in parts)))
        e["lineno"], e["line"] = n, s
        entries.append(e)
    return raw, entries


def frontmatter(path):
    """Return the frontmatter as a dict, or None if the file has none."""
    lines = read_text(path).splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"').strip("'")
    return None  # never closed


def vault_notes():
    """All .md notes that must be registered."""
    for p in sorted(VAULT.rglob("*.md")):
        rel = p.relative_to(VAULT)
        if rel.parts[0].startswith(".") or rel.parts[0] in SKIP_FOLDERS:
            continue
        if len(rel.parts) == 1 and rel.name in SKIP_ROOT_FILES:
            continue
        yield p, rel.as_posix()


def cmd_next_id(args):
    if len(args) != 1:
        fail("usage: next-id PREFIX   (e.g. next-id PRJ)")
    prefix = args[0].upper()
    if not prefix.isalpha():
        fail(f"prefix must be letters only, got '{args[0]}'")
    year = datetime.now().year
    _, entries = registry_lines()
    highest = 0
    for e in entries:
        m = ID_RE.match(e.get("id", ""))
        if m and m.group(1) == prefix and int(m.group(2)) == year:
            highest = max(highest, int(m.group(3)))
    print(f"{prefix}-{year}-{highest + 1:03d}")


def cmd_search(args):
    if not args:
        fail("usage: search WORD [WORD ...]")
    words = [w.lower() for w in args]
    _, entries = registry_lines()
    hits = [e for e in entries if not e.get("bad") and all(w in e["line"].lower() for w in words)]
    hits.sort(key=lambda e: VALUE_RANK.get(e["value"], 99))
    if not hits:
        print(f"No registry lines match: {' '.join(args)}")
        return
    for e in hits:
        print(e["line"])


def cmd_add(args):
    if len(args) != 1:
        fail("usage: add NOTE.md")
    note = Path(args[0])
    if not note.is_absolute():
        note = (Path.cwd() / note) if (Path.cwd() / note).exists() else (VAULT / note)
    note = note.resolve()
    if not note.exists():
        fail(f"note not found: {args[0]}")
    try:
        rel = note.relative_to(VAULT.resolve()).as_posix()
    except ValueError:
        fail(f"note is not inside the vault ({VAULT}): {note}")

    fm = frontmatter(note)
    if fm is None:
        fail(f"{rel} has no frontmatter (it must start with a --- block)")
    missing = [k for k in REQUIRED if not fm.get(k)]
    if missing:
        fail(f"{rel} is missing frontmatter field(s): {', '.join(missing)}")
    if not ID_RE.match(fm["id"]):
        fail(f"{rel} has a badly formed id '{fm['id']}' (expected like PRJ-2026-001)")
    if fm["value"] not in VALUE_RANK:
        fail(f"{rel} has value '{fm['value']}', must be one of: {', '.join(VALUE_RANK)}")
    if fm["status"] not in STATUSES:
        fail(f"{rel} has status '{fm['status']}', must be one of: {', '.join(sorted(STATUSES))}")
    for k in REQUIRED:
        if "|" in fm[k]:
            fail(f"{rel} field '{k}' contains '|', which would break REGISTRY.md")

    new_line = "|".join([fm["id"], fm["type"], fm["status"], rel, fm["value"], fm["summary"]])
    raw, entries = registry_lines()
    for e in entries:
        if not e.get("bad") and e["path"] == rel and e["id"] != fm["id"]:
            fail(f"{rel} is already registered under a different id ({e['id']})")

    replaced = False
    out = []
    for line in raw:
        parts = line.strip().split("|")
        if not line.strip().startswith("<!--") and parts[0].strip() == fm["id"]:
            if not replaced:
                out.append(new_line)
                replaced = True
            continue  # drops duplicate lines for the same id
        out.append(line)
    if not replaced:
        out.append(new_line)
    write_text(REGISTRY, "\n".join(out) + "\n")
    print(f"{'Replaced' if replaced else 'Added'}: {new_line}")


def cmd_log(args):
    if len(args) < 3:
        fail("usage: log ACTION ID TEXT   (e.g. log UPDATED PRJ-2026-001 Set next step)")
    action, note_id, text = args[0].upper(), args[1], " ".join(args[2:]).strip()
    if not action.isalpha():
        fail(f"ACTION must be one word of letters (e.g. CREATED, UPDATED), got '{args[0]}'")
    if "|" in text or "\n" in text:
        fail("TEXT must be one line with no '|'")
    _, entries = registry_lines()
    if note_id not in {e.get("id") for e in entries}:
        fail(f"id {note_id} is not in REGISTRY.md (run add first)")
    line = f"{datetime.now():%Y-%m-%d %H:%M} | {action} | {note_id} | {text}"
    existing = read_text(CHANGELOG) if CHANGELOG.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    write_text(CHANGELOG, existing + line + "\n")
    print(f"Logged: {line}")


def cmd_check(args):
    if not VAULT.is_dir():
        print(f"Vault folder not found: {VAULT}")
        print("0 registered notes, 1 problems")
        sys.exit(1)
    problems = []
    if not REGISTRY.exists():
        problems.append("REGISTRY.md is missing")
        entries = []
    else:
        _, entries = registry_lines()

    good = [e for e in entries if not e.get("bad")]
    for e in entries:
        if e.get("bad"):
            problems.append(f"REGISTRY.md line {e['lineno']} is not id|type|status|path|value|summary: {e['line']}")
    if not good:
        problems.append("REGISTRY.md has no entries")

    by_id = {}
    for e in good:
        if e["id"] in by_id:
            problems.append(f"id {e['id']} is registered more than once")
        by_id[e["id"]] = e
        if not (VAULT / e["path"]).is_file():
            problems.append(f"{e['id']}: registry path does not exist: {e['path']}")

    for path, rel in vault_notes():
        fm = frontmatter(path) or {}
        nid = fm.get("id")
        if not nid:
            problems.append(f"{rel}: no id in frontmatter")
        elif nid not in by_id:
            problems.append(f"{rel}: id {nid} has no registry line")
        elif by_id[nid]["path"] != rel:
            problems.append(f"{rel}: id {nid} is registered with a different path ({by_id[nid]['path']})")

    for p in problems:
        print(f"PROBLEM: {p}")
    print(f"{len(good)} registered notes, {len(problems)} problems")
    sys.exit(1 if problems else 0)


COMMANDS = {"next-id": cmd_next_id, "search": cmd_search, "add": cmd_add, "log": cmd_log, "check": cmd_check}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
