#!/usr/bin/env python3
"""Emit a capture header, or a UTC reading, from the Mac Mini's clock.

Claude has Bash on the Mac Mini and nowhere else in this lab. It has no live
access to the Proxmox host, to DC01, to CA01, or to the tenant. So the only
clock it can read is this one, and a stamp from it means "when this was
recorded on the Mac Mini", never "when the command ran on the box".

That distinction is load-bearing here. `CARRYOVER.md` records DC01 running
about +5h 06m and CA01 about +7h against real time, and `references/gotchas.md`
records that dated artifact names in this repository do not derive from the
lab's clock. A timestamp that silently borrowed the wrong clock would be a
false capture, which is worse than no capture.

Usage:

    python3 stamp.py
        One line: the current UTC reading and the clock it came from.

    python3 stamp.py --since 2026-09-14T15:03:11Z
        A bounded reading. Use when the operator ran a command between two
        moments and did not report an execution time. The bound is honest
        where a single invented point is not.

    python3 stamp.py --header --command "GET https://..." --host "Graph Explorer on the Mac Mini"
        The three-line capture header the evidence convention requires, with
        the UTC line filled in. `--since` applies here too.

Exactness beats a bound. When the operator pastes back the output of their own
`date -u`, use that value and say so, rather than anything this script prints.
"""

import argparse
import subprocess
import sys

CLOCK = "date -u on the Mac Mini"


def now():
    out = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def utc_line(since=None):
    current = now()
    if since:
        return ("UTC: between %s and %s, bounded by %s at request and at record. "
                "The operator did not report an execution time."
                % (since, current, CLOCK))
    return "UTC: %s, from %s" % (current, CLOCK)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[0])
    ap.add_argument("--since", metavar="UTC",
                    help="lower bound, from an earlier run of this script")
    ap.add_argument("--header", action="store_true",
                    help="emit the full three-line capture header")
    ap.add_argument("--command", default="", help="the command, verbatim")
    ap.add_argument("--host", default="", help="where it ran")
    args = ap.parse_args(argv)

    if not args.header:
        print(utc_line(args.since))
        return 0

    if not args.command or not args.host:
        print("--header needs --command and --host. A capture header names all "
              "three, and a guessed host is a false capture.", file=sys.stderr)
        return 2

    print("Command: %s" % args.command)
    print("Host: %s" % args.host)
    print(utc_line(args.since))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
