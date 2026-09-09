#!/usr/bin/env python3
"""Deterministic repository integrity checks for district.local.

This script answers only questions with binary answers. It does not judge
whether a claim about the lab is true. It judges whether the repository
represents its own evidence correctly.

Its output is machine output. A finding here is Captured, and citable.

Usage:
    python3 validate.py                 human-readable report
    python3 validate.py --json PATH     also write findings to PATH

Exit code 0 when no ERROR finding exists. Exit code 1 when one does.
"""

import argparse
from functools import lru_cache
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))

PLUGIN_SKILL = os.environ.get(
    "TECH_COMPASS_PLUGIN_DIR",
    os.path.expanduser(
        "~/Library/Application Support/Claude/local-agent-mode-sessions/"
        "skills-plugin/e4cae822-02a9-4ae0-8856-cd46d660357d/"
        "12594764-2482-4e4c-b314-e6b4aec41b08/skills/tech-compass"
    ),
)

# The evidence-log six-section schema entered force on this date. Exercises
# dated before it are grandfathered as historical records. Retrofitting them
# would alter a dated artifact to satisfy a later rule.
EVIDENCE_LOG_SCHEMA_DATE = "2026-09-05"

# Exercises before this date filed the evidence-log inside evidence/. The
# reports of that era link to it there. Moving it would break five historical
# links, so the old location is recorded, not corrected.
EVIDENCE_LOG_ROOT_DATE = "2026-09-01"

# The three-line capture header entered use on this date. Adoption is 0 of 82
# files before it and near-total after it. Earlier files are grandfathered.
CAPTURE_HEADER_DATE = "2026-09-02"

# A certificate, a request, or a key is an artifact the exercise produced. It
# is not a capture, and it carries no header.
ARTIFACT_SUFFIXES = (".pem", ".req", ".cer", ".crt", ".der", ".csr")

CARRYOVER_WORD_CAP = 400

REPORT_SECTIONS = [
    "What I set out to do",
    "The setup",
    "What I did",
    "Where Raymond was consulted",
    "What the box said",
    "What broke, and why",
    "What I'd do differently",
    "Open questions",
]

EVIDENCE_LOG_SECTIONS = [
    "Captured",
    "Not captured, and why",
    "Where Raymond was consulted",
    "Corrections",
    "Open questions",
    "Not started",
]

EVIDENCE_PATH = re.compile(r"exercises/[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+/evidence/[^\s`)\]|,]+")
LINE_SUFFIX = re.compile(r":[0-9]+$")


def cited_paths(text):
    """Evidence paths in text, with any trailing :NN line reference stripped.

    A citation may name a line, as in `.../02-role-assignment.md:81`. The line
    number is part of the citation, not part of the filename. Stripping it here
    stops a valid line citation from being reported as a missing file.
    """
    return [LINE_SUFFIX.sub("", m) for m in EVIDENCE_PATH.findall(text)]
# Header wording varies. Match the meaning, not one spelling.
HOST_MARKER = re.compile(r"^\s*Host\b", re.MULTILINE | re.IGNORECASE)
UTC_MARKER = re.compile(r"UTC", re.IGNORECASE)
GUEST_EXEC = re.compile(r'"(out-data|exited)"')
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TABLE_ROW = re.compile(r"^\|(.+)\|\s*$", re.MULTILINE)

findings = []


def add(severity, check, message, path=None):
    findings.append(
        {"severity": severity, "check": check, "message": message, "path": path}
    )


@lru_cache(maxsize=None)
def read(path):
    """Read a repository file once per validation run.

    Several independent checks inspect the same reports, logs, and evidence.
    The repository is treated as a stable snapshot for the duration of one
    invocation, so caching avoids repeated disk reads without changing results.
    """
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def repo_path(*parts):
    return os.path.join(REPO, *parts)


@lru_cache(maxsize=1)
def exercises():
    root = repo_path("exercises")
    if not os.path.isdir(root):
        return ()
    return tuple(sorted(
        d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))
    ))


@lru_cache(maxsize=1)
def tracked_markdown():
    out = subprocess.run(
        ["git", "-C", REPO, "ls-files", "*.md"],
        capture_output=True, text=True, check=False,
    )
    return tuple(p for p in out.stdout.splitlines() if p)


@lru_cache(maxsize=None)
def git(*args):
    out = subprocess.run(
        ["git", "-C", REPO] + list(args), capture_output=True, text=True, check=False
    )
    return tuple(out.stdout.splitlines()) if out.returncode == 0 else ()


def table_rows(text, start_heading, end_heading=None):
    """Return data rows of the markdown table under one heading."""
    start = text.find("## " + start_heading)
    if start < 0:
        return []
    end = text.find("## " + end_heading, start + 1) if end_heading else len(text)
    if end < 0:
        end = len(text)
    rows = []
    for match in TABLE_ROW.finditer(text[start:end]):
        cells = [c.strip() for c in match.group(1).split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if cells[0] in ("Claim",):
            continue
        rows.append(cells)
    return rows


def sections_in_order(text, required):
    """Return the required headings that are missing or out of order."""
    present = [h.strip() for h in HEADING.findall(text)]
    missing = [s for s in required if s not in present]
    order = [present.index(s) for s in required if s in present]
    disordered = order != sorted(order)
    return missing, disordered


# --- checks ----------------------------------------------------------------

def check_ledger():
    path = repo_path("verified-claims.md")
    if not os.path.exists(path):
        add("ERROR", "ledger", "verified-claims.md is missing")
        return
    text = read(path)

    for cells in table_rows(text, "Confirmed", "Retired"):
        if len(cells) < 2:
            continue
        for cited in cited_paths(cells[1]):
            if not os.path.exists(repo_path(cited)):
                add("ERROR", "ledger-evidence-missing",
                    "Confirmed row cites a file that does not exist: %s" % cited,
                    "verified-claims.md")

    for cells in table_rows(text, "Retired"):
        if len(cells) >= 2 and not cells[1]:
            add("ERROR", "ledger-retired-no-reason",
                "Retired row has an empty reason: %s" % cells[0][:70],
                "verified-claims.md")


def check_references():
    for rel in tracked_markdown():
        text = read(repo_path(rel))
        for cited in set(cited_paths(text)):
            if not os.path.exists(repo_path(cited)):
                add("ERROR", "reference-missing",
                    "references a file that does not exist: %s" % cited, rel)


def check_reports():
    for name in exercises():
        rel = "exercises/%s/report.md" % name
        path = repo_path(rel)
        if not os.path.exists(path):
            add("WARN", "no-report", "exercise has no report.md", "exercises/" + name)
            continue
        missing, disordered = sections_in_order(read(path), REPORT_SECTIONS)
        for section in missing:
            add("ERROR", "report-section-missing",
                "report is missing the required section: %s" % section, rel)
        if disordered:
            add("ERROR", "report-section-order",
                "required sections do not appear in the prescribed order", rel)


def check_evidence_logs():
    for name in exercises():
        rel = "exercises/%s/evidence-log.md" % name
        path = repo_path(rel)
        date = name[:10]
        if not os.path.exists(path):
            # A misplaced log still exists. check_layout reports the location.
            if os.path.exists(repo_path("exercises", name, "evidence", "evidence-log.md")):
                continue
            if date >= EVIDENCE_LOG_SCHEMA_DATE:
                add("ERROR", "evidence-log-missing",
                    "exercise has no evidence-log.md", "exercises/" + name)
            continue
        if date < EVIDENCE_LOG_SCHEMA_DATE:
            add("INFO", "evidence-log-grandfathered",
                "predates the six-section schema, kept as a historical record", rel)
            continue
        missing, disordered = sections_in_order(read(path), EVIDENCE_LOG_SECTIONS)
        for section in missing:
            add("ERROR", "evidence-log-section-missing",
                "evidence-log is missing the required section: %s" % section, rel)
        if disordered:
            add("ERROR", "evidence-log-section-order",
                "required sections do not appear in the prescribed order", rel)


def check_evidence_files():
    """Check each capture by its kind, not by its file extension.

    A guest exec capture must carry an exit code. Every other capture must
    name its command, its host, and a UTC timestamp.
    """
    for name in exercises():
        folder = repo_path("exercises", name, "evidence")
        date = name[:10]
        if not os.path.isdir(folder):
            add("WARN", "no-evidence-dir", "exercise has no evidence/ directory",
                "exercises/" + name)
            continue

        if date < CAPTURE_HEADER_DATE:
            add("INFO", "capture-header-grandfathered",
                "captures predate the capture-header convention",
                "exercises/" + name)

        for entry in sorted(os.listdir(folder)):
            rel = "exercises/%s/evidence/%s" % (name, entry)
            full = os.path.join(folder, entry)
            if not os.path.isfile(full) or entry == "evidence-log.md":
                continue
            try:
                head = read(full)[:4000]
            except UnicodeDecodeError:
                add("WARN", "evidence-unreadable", "file is not UTF-8 text", rel)
                continue

            if GUEST_EXEC.search(head):
                if "exitcode" not in head:
                    add("WARN", "evidence-no-exitcode",
                        "guest exec capture has no exitcode field", rel)
                continue

            if date < CAPTURE_HEADER_DATE or entry.endswith(ARTIFACT_SUFFIXES):
                continue
            # Whether a command appears verbatim is not decidable by pattern
            # without false positives. That question belongs to semantic review.
            missing = []
            if not HOST_MARKER.search(head):
                missing.append("host")
            if not UTC_MARKER.search(head):
                missing.append("UTC timestamp")
            if missing:
                add("WARN", "evidence-header",
                    "capture header has no %s" % ", ".join(missing), rel)


def check_layout():
    """The evidence-log belongs at the exercise root, not inside evidence/."""
    for name in exercises():
        misplaced = repo_path("exercises", name, "evidence", "evidence-log.md")
        if not os.path.exists(misplaced):
            continue
        rel = "exercises/%s/evidence/evidence-log.md" % name
        if name[:10] < EVIDENCE_LOG_ROOT_DATE:
            add("INFO", "evidence-log-nested-historical",
                "evidence-log sits inside evidence/, the layout of that era", rel)
        else:
            add("ERROR", "evidence-log-misplaced",
                "evidence-log.md sits inside evidence/ instead of the exercise root",
                rel)


def check_evidence_immutability():
    """A closed exercise has a report. Its evidence is a historical record."""
    closed = {
        name for name in exercises()
        if os.path.exists(repo_path("exercises", name, "report.md"))
    }
    changed = set(git("diff", "--name-only")) | set(git("diff", "--cached", "--name-only"))
    for rel in sorted(changed):
        parts = rel.split("/")
        if len(parts) > 3 and parts[0] == "exercises" and parts[2] == "evidence":
            if parts[1] in closed:
                add("ERROR", "evidence-modified",
                    "evidence of a closed exercise is modified in the tree", rel)


def check_carryover():
    path = repo_path("CARRYOVER.md")
    if not os.path.exists(path):
        add("ERROR", "carryover-missing", "CARRYOVER.md is missing")
        return
    words = len(read(path).split())
    if words > CARRYOVER_WORD_CAP:
        add("ERROR", "carryover-length",
            "carryover is %d words, over the %d word cap" % (words, CARRYOVER_WORD_CAP),
            "CARRYOVER.md")


def check_skill_sync():
    repo_skill = repo_path(".claude", "skills", "tech-compass")
    if not os.path.isdir(PLUGIN_SKILL):
        add("INFO", "skill-sync-skipped",
            "plugin copy not found on this host, two-copy check skipped")
        return
    for rel in ["SKILL.md", "references/gotchas.md", "references/credential-scan.md"]:
        a, b = os.path.join(repo_skill, rel), os.path.join(PLUGIN_SKILL, rel)
        if not os.path.exists(b):
            add("ERROR", "skill-sync-missing", "plugin copy has no %s" % rel)
        elif read(a) != read(b):
            add("ERROR", "skill-sync-drift",
                "plugin copy of %s differs from the repo copy" % rel)


CHECKS = [
    check_ledger,
    check_references,
    check_reports,
    check_evidence_logs,
    check_evidence_files,
    check_layout,
    check_evidence_immutability,
    check_carryover,
    check_skill_sync,
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", metavar="PATH", help="write findings to PATH")
    parser.add_argument("--quiet", action="store_true", help="print errors only")
    args = parser.parse_args()

    for check in CHECKS:
        check()

    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for finding in findings:
        counts[finding["severity"]] += 1

    for severity in ("ERROR", "WARN", "INFO"):
        if args.quiet and severity != "ERROR":
            continue
        rows = [f for f in findings if f["severity"] == severity]
        if not rows:
            continue
        print("\n%s (%d)" % (severity, len(rows)))
        for finding in rows:
            where = finding["path"] or "-"
            print("  %-32s %s" % (finding["check"], where))
            print("  %-32s %s" % ("", finding["message"]))

    print("\n%d ERROR, %d WARN, %d INFO" % (counts["ERROR"], counts["WARN"], counts["INFO"]))

    if args.json:
        head = git("rev-parse", "HEAD")
        payload = {
            "commit": head[0] if head else None,
            "counts": counts,
            "findings": findings,
        }
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("wrote %s" % args.json)

    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
