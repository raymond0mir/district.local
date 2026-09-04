# Credential scan

Run this before every commit. The repo is public. A literal password reached report prose on 2026-08-31.

Run each pass in Terminal on the Mac Mini, from the repo root. Each pass prints file, line, and text.

Run every pass. Do not stop at the first clean pass.

## Pass 1: assignment forms

```
git grep -InE -i '(password|passwd|secret|api[_-]?key|client[_-]?secret|bearer|token)[[:space:]]*[:=][[:space:]]*[^[:space:]&]'
```

Expect zero hits. A hit blocks the commit. Clear each hit before you continue.

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

## Pass 4: known secret values

Ask Raymond for the literal strings to check. He holds them in Vaultwarden.

Write the strings to a file outside the repo. Then run:

```
git grep -Inf /tmp/scan-patterns.txt
```

Expect zero hits. Delete the pattern file after the pass. Never write these strings into a repo file.

## Pass 5: unpublished identity

The current tenant Global Administrator's name stays out of every repo artifact. Ask Raymond for the name in session.

```
git grep -In '<name>'
```

Expect zero hits. Redact each hit before the commit.

## Scope

Each pass reads tracked files. Run the passes after `git add` and before `git commit`.

Scan the staged set alone when the tree holds unrelated work:

```
git diff --cached -U0 | grep -InE -i '<the pattern from the pass above>'
```

## Maintenance

Add a pattern when a new secret class enters the lab. Record the date and the exercise that found it.
