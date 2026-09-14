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

# The rule that a capture block holds machine output, unedited except for
# redactions named in place, was first written down on this date, in
# exercises/2026-09-14-device-code-detection/evidence/06. Exercises dated
# before it are grandfathered, as the evidence-log schema and the capture
# header already are. Retrofitting them would alter a dated artifact to
# satisfy a later rule.
CAPTURE_FIDELITY_DATE = "2026-09-14"

# Acknowledged defects in published captures, one row per file, each citing
# the record that supersedes it. This is a registry, not a severity rule. It
# downgrades the listed path and nothing else. A path absent from HEAD is
# still editable and is never downgraded, so a new defect fails at full
# severity and cannot be registered away. The registry only shrinks: a row
# that matches no finding is reported as stale and is meant to be deleted.
SUPERSEDED_CAPTURES = {
    "exercises/2026-09-14-device-code-detection/evidence/"
    "01-device-code-lands-in-the-non-interactive-stream.md":
        "exercises/2026-09-14-device-code-detection/evidence/"
        "06-corrected-full-captures-superseding-01-02-03.md",
    "exercises/2026-09-14-device-code-detection/evidence/"
    "02-three-audit-events-and-the-one-named-consent-hides-the-widening.md":
        "exercises/2026-09-14-device-code-detection/evidence/"
        "06-corrected-full-captures-superseding-01-02-03.md",
    "exercises/2026-09-14-device-code-detection/evidence/"
    "03-the-interactive-stream-holds-the-flow-and-cannot-name-it.md":
        "exercises/2026-09-14-device-code-detection/evidence/"
        "06-corrected-full-captures-superseding-01-02-03.md",
}

# A capture block holds machine output. The only alteration the repository
# permits is a redaction named in place. A shortened rendering leaves one of
# these three marks. Each matches inside a double-quoted value only, so prose
# that happens to carry three dots is out of scope.
TRUNCATED_ID = re.compile(r'"[0-9a-fA-F]{4,}(?:-[0-9a-fA-F]{4,})*-\.\.\."')
ELLIPSIS_IN_VALUE = re.compile(r'"[^"\n]*\S[ \t]*\.\.\.[ \t]*\S[^"\n]*"')
BRACKET_NOTE = re.compile(r'"\[([^"\[\]]{4,})\]"')

# A citation written as a backticked path fragment that stops at a dash and
# three dots. `check_references` cannot see it: its path regex needs the full
# `exercises/<date-slug>/` prefix, and most of these are relative.
ABBREVIATED_PATH = re.compile(r"`([^`\n]*/[^`\n]*?)-\.\.\.`")

# `[redacted]`, `[REDACTED-NEW-BREAKGLASS-UPN]` and `[REDACTED: operator source
# IP]` are the marker the credential-scan procedure asks for, not a shortening.
REDACTION_NOTE = re.compile(r"^\s*redact", re.IGNORECASE)

# A superseding record reproduces the shortened renderings it itemises, so it
# matches every pattern above by doing its job. Its filename carries the
# two-digit prefixes of the files it replaces.
SUPERSEDING_NAME = re.compile(r"-superseding-[0-9]{2}(?:-[0-9]{2})*\.md$")

CODE_FENCE = re.compile(r"^\s*```")
CODE_SPAN = re.compile(r"`([^`\n]+)`")

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


def frozen_evidence():
    """Paths that `check_evidence_frozen` forbids editing.

    A file is frozen when it sits under `exercises/<name>/evidence/`, that
    exercise holds a `report.md`, and the file already exists in HEAD. A file
    absent from HEAD has never been published and is still editable, so it is
    not frozen.
    """
    closed = {
        name for name in exercises()
        if os.path.exists(repo_path("exercises", name, "report.md"))
    }
    published = set(git("ls-tree", "-r", "HEAD", "--name-only"))
    out = set()
    for rel in published:
        parts = rel.split("/")
        if len(parts) > 3 and parts[0] == "exercises" and parts[2] == "evidence":
            if parts[1] in closed:
                out.add(rel)
    return out


def check_references():
    """A broken reference is an ERROR, except inside frozen evidence.

    Decision 2026-09-14. `CLAUDE.md` requires a wrong published claim to be
    corrected on the record rather than by silent edit. `check_evidence_frozen`
    forbids touching a closed exercise's evidence at all. A broken path inside
    such a file therefore cannot be cleared in place, and as an ERROR it made
    `validate.py` permanently unclean, which costs the binary answer that every
    session start depends on.

    Evidence immutability is the stronger guarantee and it is kept. The remedy
    for a broken reference in frozen evidence is a new file that supersedes it,
    as `exercises/2026-09-14-device-code-detection/evidence/06-...` does. The
    finding is reported as a WARN under its own code so it stays visible and
    stops blocking. Everywhere else a broken reference remains an ERROR.
    """
    frozen = frozen_evidence()
    for rel in tracked_markdown():
        text = read(repo_path(rel))
        for cited in set(cited_paths(text)):
            if not os.path.exists(repo_path(cited)):
                if rel in frozen:
                    add("WARN", "reference-missing-frozen",
                        "frozen evidence references a file that does not exist, "
                        "and cannot be corrected in place: %s" % cited, rel)
                else:
                    add("ERROR", "reference-missing",
                        "references a file that does not exist: %s" % cited, rel)


@lru_cache(maxsize=1)
def published_files():
    """Paths that exist in HEAD, and are therefore already public."""
    return frozenset(git("ls-tree", "-r", "HEAD", "--name-only"))


@lru_cache(maxsize=1)
def superseding_records():
    """Evidence files that replace an earlier file in the same exercise.

    `CONSIDERATIONS.md`, 2026-09-14, records the superseding file as the only
    remedy for defective frozen evidence. Such a file quotes the renderings it
    replaces, so it matches every capture-fidelity pattern by doing its job.
    The convention is a filename ending `-superseding-<NN>-<NN>.md`.
    """
    return frozenset(
        rel for rel in tracked_markdown()
        if "/evidence/" in rel and SUPERSEDING_NAME.search(rel)
    )


def code_regions(text):
    """(line number, text) for each fenced block and each inline code span.

    A shortened value is a defect wherever it is presented as machine output.
    A fenced block is the common case. An inline span that carries a
    double-quoted value is the same claim written into a sentence. Prose
    outside both is analysis, and three dots there are ordinary writing.
    """
    regions = []
    inside = False
    start = 0
    buffer = []
    for number, line in enumerate(text.split("\n"), 1):
        if CODE_FENCE.match(line):
            if inside:
                regions.append((start, "\n".join(buffer)))
                buffer = []
            else:
                start = number + 1
            inside = not inside
            continue
        if inside:
            buffer.append(line)
            continue
        for match in CODE_SPAN.finditer(line):
            if '"' in match.group(1):
                regions.append((number, match.group(1)))
    if inside and buffer:
        regions.append((start, "\n".join(buffer)))
    return regions


def shortened_values(text):
    """(line number, matched text) for every shortened value in a file.

    The three patterns overlap: a truncated identifier is also an ellipsis
    inside a quoted value. Report each place once, so the count is a count of
    defects and not a count of pattern hits.
    """
    out = []
    for number, region in code_regions(text):
        for line_offset, line in enumerate(region.split("\n")):
            taken = []
            for pattern in (TRUNCATED_ID, BRACKET_NOTE, ELLIPSIS_IN_VALUE):
                for match in pattern.finditer(line):
                    if pattern is BRACKET_NOTE:
                        note = match.group(1)
                        if REDACTION_NOTE.match(note) or " " not in note:
                            continue
                    start, end = match.span()
                    if any(start < b and a < end for a, b in taken):
                        continue
                    taken.append((start, end))
                    out.append((number + line_offset, match.group(0)))
    out.sort()
    return out


def abbreviated_paths(text):
    """(line number, matched text) for every backticked path that stops at -..."""
    out = []
    for number, line in enumerate(text.split("\n"), 1):
        for match in ABBREVIATED_PATH.finditer(line):
            out.append((number, match.group(0)))
    return out


def exercise_date(rel):
    """The date of the exercise holding a file, or None for a file outside one."""
    parts = rel.split("/")
    if len(parts) > 2 and parts[0] == "exercises":
        return parts[1][:10]
    return None


def check_capture_fidelity():
    """A capture block holds machine output, unedited except for named redactions.

    Decision 2026-09-14, Raymond. Three evidence files of
    `2026-09-14-device-code-detection` rendered captured API responses in a
    shortened form, and the defect reached a public push. Evidence 06 of that
    exercise itemises all seven shortenings and supersedes the three files.

    Severity is not lowered for frozen files as a class. `reference-missing`
    took that route earlier the same day, and it lowers severity for every
    future instance as well as every past one. This check uses the two devices
    the repository already relies on instead.

    First, a cutoff date. `CAPTURE_FIDELITY_DATE` marks when the rule was
    written down. Exercises before it are grandfathered at INFO, the same
    treatment `capture-header-grandfathered` and `evidence-log-grandfathered`
    already give their own conventions. Work from the cutoff forward is held
    at ERROR.

    Second, a registry. `SUPERSEDED_CAPTURES` lists acknowledged defects in
    published captures, one row per file, each citing the record that
    supersedes it. A listed path drops to INFO. Nothing else does, and a file
    absent from HEAD is never downgraded, because it can still be repaired by
    editing it. A row matching no finding is reported as stale, so the
    registry shrinks and never grows in silence.

    Owner action, by code. `capture-shortened` and `citation-abbreviated`:
    rewrite the capture before the commit, or write a superseding record and
    add a row here. `capture-registry-stale`: delete the row. The
    grandfathered and superseded codes carry no action, which is why they sit
    at INFO.

    The check reads marks, not meaning. It cannot see a property that was
    dropped without leaving one, which is four of the seven shortenings
    evidence 06 lists. It reduces the defect class; it does not close it.
    """
    published = published_files()
    exempt = superseding_records()
    matched = set()

    def report(rel, code, sentence, hits):
        line, sample = hits[0]
        detail = "%s, %d place(s), first at line %d: %s" % (
            sentence, len(hits), line, sample[:60])
        date = exercise_date(rel)
        if date is not None and date < CAPTURE_FIDELITY_DATE:
            add("INFO", code + "-grandfathered",
                "%s. The exercise predates the capture-fidelity rule." % detail, rel)
            return
        record = SUPERSEDED_CAPTURES.get(rel)
        if record and rel in published and os.path.exists(repo_path(record)):
            matched.add(rel)
            add("INFO", code + "-superseded",
                "%s. Superseded by %s." % (detail, record), rel)
            return
        add("ERROR", code, detail, rel)

    for rel in tracked_markdown():
        if rel in exempt:
            continue
        text = read(repo_path(rel))

        if "/evidence/" in rel and not rel.endswith("evidence-log.md"):
            hits = shortened_values(text)
            if hits:
                report(rel, "capture-shortened",
                       "capture holds a shortened value", hits)

        hits = abbreviated_paths(text)
        if hits:
            report(rel, "citation-abbreviated",
                   "citation abbreviates a path and cannot resolve", hits)

    for rel, record in sorted(SUPERSEDED_CAPTURES.items()):
        if not os.path.exists(repo_path(record)):
            add("ERROR", "capture-registry-broken",
                "registry row cites a record that does not exist: %s" % record, rel)
        elif rel not in matched:
            add("WARN", "capture-registry-stale",
                "registry row matches no finding, and is ready to delete", rel)


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
    """A closed exercise has a report. Its published evidence is a historical record.

    Compare against HEAD, not against the index. A file absent from HEAD has
    never been published, so it cannot have been altered, and adding evidence to
    a closed exercise is ordinary work. The earlier form unioned `git diff` with
    `git diff --cached`, which flagged every newly staged file and cleared the
    findings the moment the commit landed. Staging ADCS evidence 40 through 53
    on 2026-09-09 raised seventeen such errors, all of them artifacts.

    `--diff-filter=MDRT` keeps modification, deletion, rename and typechange.
    It drops addition, which is the case that produced the false errors.
    """
    closed = {
        name for name in exercises()
        if os.path.exists(repo_path("exercises", name, "report.md"))
    }
    altered = git("diff", "HEAD", "--diff-filter=MDRT", "--name-only")
    for rel in sorted(set(altered)):
        parts = rel.split("/")
        if len(parts) > 3 and parts[0] == "exercises" and parts[2] == "evidence":
            if parts[1] in closed:
                add("ERROR", "evidence-modified",
                    "published evidence of a closed exercise is altered", rel)


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
    check_capture_fidelity,
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
