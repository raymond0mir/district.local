# Vaultwarden Credential Migration

## What I set out to do

Three real secrets lived outside Vaultwarden: the new break-glass Global Administrator's
password, `svc-entraconnect`'s password, and Vaultwarden's own `ADMIN_TOKEN`. This exercise moves
all three into the vault and confirms the move without exposing any plaintext value to Claude or
to this repo.

## The setup

Container 103 (Vaultwarden) running. Thin pool Data% 72.11, under the 85% gate. Host RAM available
3.5Gi. The SSH tunnel and vault from the 2026-09-03 Vaultwarden build were already in place; no new
infrastructure needed.

## What I did

- Ran a pre-flight check in the Proxmox console: container status, thin pool usage, host RAM.
- Raymond opened the SSH tunnel on the Mac Mini and logged into the vault in his browser.
- Raymond read the plain-text `ADMIN_TOKEN` from `/root/vaultwarden.env` via `pct exec`, on his own
  screen, and typed it into a new vault item.
- Raymond added two more vault items: the break-glass Global Administrator's password and
  `svc-entraconnect`'s password. Values entered directly in the browser; never sent to this chat.
- Queried the live cipher count in the vault's SQLite database through `pct exec`, without
  decrypting or reading any item content.

## Where Raymond was consulted

Whether to include the break-glass account's UPN in the vault item's title, given the UPN is kept
out of every other repo artifact by his 2026-09-03 decision. He made the call inside the vault UI.
Claude has no visibility into vault item titles and does not know which way he decided — see Open
questions.

## What the box said

```
Command: date -u; pct exec 103 -- sqlite3 /var/lib/docker/volumes/vw-data/_data/db.sqlite3
  "SELECT COUNT(*) FROM ciphers;"
Thu Sep  3 11:39:10 PM UTC 2026
3
```

Three ciphers exist in the database, matching the three items added. Full output, including the
failed follow-up query, in `evidence/02-cipher-count-verification.txt`.

## What broke, and why

A follow-up query, `SELECT type, COUNT(*) FROM ciphers GROUP BY type`, failed: `no such column:
type`. This Vaultwarden 1.37.2 schema names the column differently. Non-blocking: `COUNT(*)` alone
proves item count, which was the only claim this exercise needed. The real column name was not
looked up.

## What I'd do differently

Run `PRAGMA table_info(ciphers)` before guessing a column name. Cheap, and would have avoided one
failed query.

## Open questions

- The break-glass vault item's title, and whether it includes the UPN — Claude cannot read vault
  contents beyond the encrypted row count, so this stays genuinely unknown to Claude.
- The real name of the `ciphers` table's type column in Vaultwarden 1.37.2 — never queried.
- Whether `/root/vaultwarden.env` still holds the `ADMIN_TOKEN` in plain text on disk. It was only
  read this exercise, not changed. Storing a copy in the vault does not resolve the exposure
  `EXPOSURES.md` already flags for that file — hashing or removing the token is still open, and was
  not attempted this session.
- Whether the break-glass password and `svc-entraconnect`'s password now exist anywhere else
  outside the vault (a password manager, a note, memory) — not audited, out of scope here.
