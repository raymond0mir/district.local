# Backup, restore verification, and schedule

Host: Proxmox host shell
Timestamp (UTC): 2026-09-03, ~16:26–16:35

## Hardening applied before backup

```
# pct exec 103 -- bash -c '... sed SIGNUPS_ALLOWED=false ... vaultwarden hash ...'
RESULT: signups closed; token hash did not run non-interactively (left as plain text)
```

Container recreated (not restarted) so the env change applied. Post-recreate startup log:

```
[NOTICE] You are using a plain text `ADMIN_TOKEN` which is insecure.
[2026-09-03 16:26:40.924][start][INFO] Rocket has launched from http://0.0.0.0:80
```

`SIGNUPS_ALLOWED=false` applied; `ADMIN_TOKEN` still plain text.

## Backup script

`/usr/local/bin/vaultwarden-backup.sh`:

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
DEST=/var/lib/vz/dump/vaultwarden
pct exec 103 -- docker stop vaultwarden
pct exec 103 -- tar czf /tmp/vw-$STAMP.tar.gz -C /var/lib/docker/volumes/vw-data/_data .
pct exec 103 -- docker start vaultwarden
pct pull 103 /tmp/vw-$STAMP.tar.gz "$DEST/vaultwarden-$STAMP.tar.gz"
pct exec 103 -- rm -f /tmp/vw-$STAMP.tar.gz
ls -1t "$DEST"/vaultwarden-*.tar.gz | tail -n +15 | xargs -r rm -f
```

First run:

```
backup complete: /var/lib/vz/dump/vaultwarden/vaultwarden-20260903T162752Z.tar.gz
=== archive contents ===
drwxr-xr-x root/root         0 2026-09-03 09:26 ./
-rw-r--r-- root/root     16512 2026-09-03 09:27 ./db.sqlite3-wal
-rw-r--r-- root/root     32768 2026-09-03 09:27 ./db.sqlite3-shm
-rw-r--r-- root/root    278528 2026-09-03 09:26 ./db.sqlite3
drwxr-xr-x root/root         0 2026-09-03 08:53 ./tmp/
-rw-r--r-- root/root      1675 2026-09-03 08:53 ./rsa_key.pem
```

## Restore verification

```
# pct push 103 "$ARCHIVE" /tmp/restore-test.tar.gz
# tar xzf /tmp/restore-test.tar.gz -C /tmp/restore-data
--- integrity check ---
ok
--- user rows in restored DB ---
1
--- booting throwaway instance on restored data ---
HTTP status from restored instance: 200
--- cleaned up ---
```

`PRAGMA integrity_check` on the restored database, its user row count, and a throwaway Vaultwarden
container mounted on the restored data serving `/api/config`. Test instance and extracted data
removed afterward.

## Schedule

```
# crontab -l
0 3 * * * /usr/local/bin/vaultwarden-backup.sh >> /var/log/vaultwarden-backup.log 2>&1
```

Daily 03:00 host-local (`America/Los_Angeles`). No unattended run observed yet.
