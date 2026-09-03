# Evidence log

## Captured

- `evidence/01-preflight-host-health.txt` — container 103 status, thin pool Data%/Meta%, host RAM.
  Command, host, and UTC timestamp precede the raw output.
- `evidence/02-cipher-count-verification.txt` — cipher count query (result: 3) and the failed
  type-breakdown follow-up query, both with exit-relevant output kept verbatim.

## Not captured, and why

- The contents of the three vault items. Raymond entered them directly in the browser. Claude
  never had access to the plaintext values and did not ask for them. This is a deliberate scope
  boundary, not a missed capture.
- The vault item titles. Not queryable without decrypting the database; left as an Open question
  in `report.md`.
- Whether `ADMIN_TOKEN` in `/root/vaultwarden.env` was rotated or cleared after being copied into
  the vault. It was read, not changed, this session. The file's plain-text state is unchanged from
  before this exercise.

## Errors kept, per the capture contract

- `SELECT type, COUNT(*) FROM ciphers GROUP BY type` failed with `no such column: type` against
  this Vaultwarden 1.37.2 schema. Kept in `evidence/02-cipher-count-verification.txt` rather than
  silently dropped or retried until it worked.
