# Credential scan

Run this before every commit. The repo is public. A literal password reached report prose on 2026-08-31.

Rotating a leaked lab credential is cheap. Unpublishing it is not. A pushed object stays
retrievable by its SHA after a force-push until GitHub garbage-collects it, and public repositories
are copied by forks and code-search indexes within minutes. The scan is portfolio hygiene as much
as a security control: a literal secret in the public history of a repository written to
demonstrate identity engineering is read as a judgment signal.

## The hook

`.githooks/pre-commit` runs the scan automatically. Enable it once per clone:

```
git config core.hooksPath .githooks
```

The hook blocks a commit on passes 1, 1b, 3, 4 and 5. Pass 2 prints its hits and does not block,
because hits are expected there and need a human read.

Run the whole tracked tree instead of the staged diff for a periodic sweep:

```
.githooks/pre-commit --all
```

Two exclusions keep the hook quiet without hiding anything. This file is excluded, because it
matches the patterns by documenting them. A value written as `"[REDACTED...]"` is dropped from
pass 1b, because that marker is what the procedure asks for.

Bypass with `git commit --no-verify` only after reading every hit.

## Pass 1: assignment forms

```
git grep -InE -i '(password|passwd|secret|api[_-]?key|client[_-]?secret|bearer|token)[[:space:]]*[:=][[:space:]]*[^[:space:]&]'
```

Expect zero hits. A hit blocks the commit. Clear each hit before you continue.

## Pass 1b: JSON-quoted keys

```
git grep -InE -i '"(password|passwd|secret|api[_-]?key|client[_-]?secret|bearer|token)"[[:space:]]*:[[:space:]]*"[^"]'
```

Expect hits only where the value is a redaction marker. Read every hit. A literal value blocks
the commit.

Pass 1 matches a bare key, as in `password: value`. It does not match a quoted key, as in
`"password": "value"`, because the closing quote sits between the key and the colon. Graph
evidence is JSON, so pass 1 alone does not cover it. Added 2026-09-06, found during
`exercises/2026-09-06-b4-pim-eligible-role` while scanning a `passwordProfile` request body.

## Pass 2: PowerShell plaintext idioms

```
git grep -InE -i '(AsPlainText|ConvertTo-SecureString|--password|net user )'
```

Expect hits. This lab rotates passwords with inline random generation. Read each hit. Confirm the line prints no literal secret.

## Pass 3: key material

```
git grep -InE 'BEGIN ([A-Z]+ )?PRIVATE KEY'
```

Expect zero hits. A hit blocks the commit.

## Passes 4 and 5: literal strings

Pass 4 is the known secret values Raymond holds in Vaultwarden. Pass 5 is the current tenant
Global Administrator's name, which stays out of every repo artifact. A name cannot be rotated, so
pass 5 is the one string here whose publication is genuinely irreversible.

Both read from one file of literal strings, one per line, held outside the repository:

```
~/.config/district-local/scan-patterns.txt
```

Override the path with `DISTRICT_SCAN_PATTERNS`. The hook refuses to run if the file sits inside
the working tree. It searches the whole tracked tree, not the staged diff, because a string may
already sit in an earlier commit. It prints file and line only, never the matched text, so the
value does not reach the terminal or its scrollback.

Expect zero hits. Redact each hit before the commit. Never write these strings into a repo file.

## Scope

The hook reads the staged diff for passes 1, 1b, 2 and 3, and the whole tracked tree for passes 4
and 5. `--all` puts every pass on the whole tree.

Run the passes by hand only when the hook is unavailable. Then scan the staged set:

```
git diff --cached -U0 | grep -InE -i '<the pattern from the pass above>'
```

## Maintenance

Add a pattern when a new secret class enters the lab. Record the date and the exercise that found it.
