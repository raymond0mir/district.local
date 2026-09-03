# Standing up a self-hosted secrets store for the lab

## What I set out to do

The break-glass rotation earlier the same day produced a credential with nowhere good to live.
This exercise closes that gap: a self-hosted Vaultwarden instance for lab secrets — service
account credentials, break-glass passwords, API keys. Hypothesis going in: a lightweight
container, mostly mechanical work.

It was not mechanical. Five things failed, and three of them came from assumptions I asserted
confidently without verifying.

## The setup

Pre-flight: thin pool **72.00% Data% / 3.62% Meta%** (under the 85% gate), **3.8Gi available** RAM
with VM 100 and VM 104 running, and `pct list` returning nothing — **no LXC container had ever
existed on this host.** Every prior guest is a full VM, so this is also the lab's first container
workload.

Two decisions taken with Raymond before building:

- **Lab secrets only**, not a general daily password manager — which set the network placement
  (`vmbr1`, the isolated lab segment) and bounds what a compromise costs.
- **Manual LXC + Docker + official image**, explicitly rejecting the community Proxmox helper
  scripts. Those are one root-run `curl`-to-shell on the hypervisor; the manual path is more steps
  but each is readable before it runs.

## What I did

1. Added `rootdir` to `local` storage so the container's filesystem could sit on `pve-root` rather
   than the constrained thin pool.
2. Created container 103 (`vaultwarden`) — Debian 12, unprivileged, `nesting=1,keyctl=1`, 1GB RAM,
   `10.0.0.20/24` on `vmbr1`.
3. Installed Docker from Docker's own apt repository with a pinned signing key.
4. Ran Vaultwarden behind Caddy as a TLS-terminating reverse proxy on a private Docker network,
   with Vaultwarden publishing no port of its own.
5. Closed signups; attempted to hash the admin token (failed — see Open questions).
6. Wrote a backup script, verified a restore three ways, scheduled it daily.

## Where Raymond was consulted

- **Vault scope** — lab secrets only, versus becoming his real daily password manager.
- **Build method** — manual, versus the community helper script.
- **Reachability** — SSH tunnel versus a pfSense port-forward. He chose the tunnel: no standing
  inbound exposure at the lab's edge, at the cost of opening a tunnel per session. More
  consequential than it looked, since it later forced the TLS question rather than deferring it.
- **Documentation** — whether Vaultwarden belongs in `district.local` given it is not AD or Entra
  work. He decided it does.

## What the box said

Full captures in `evidence/`.

- Docker daemon running inside an unprivileged LXC: Engine 29.7.2, containerd 2.3.4, runc 1.4.3.
- Vaultwarden 1.37.2 behind Caddy, TLS 1.3, ALPN `h2`, reachable at `https://localhost:8443`
  through an SSH tunnel and nowhere else. `SIGNUPS_ALLOWED=false` applied.
- Backup archive: `db.sqlite3` (278528 bytes) with its `-wal`/`-shm` companions, plus
  `rsa_key.pem`.
- Restore verified: `PRAGMA integrity_check` → `ok`; user rows → `1`; throwaway Vaultwarden booted
  on the restored data → HTTP `200`.
- `crontab -l` confirms the daily 03:00 job.

## What broke, and why

**A wrong image name that survived four wrong diagnoses.** `vaultwarden/vaultwarden` does not
exist; the image is `vaultwarden/server`. That was my error, asserted confidently and carried from
the first command. Before catching it, the session disproved four hypotheses in turn: IPv6-only
DNS answers (disabling IPv6 changed nothing), a broken network path (TLS handshakes to both
registry hosts were clean), Docker Hub rate limiting (no rate-limit headers present), and required
authentication (logging in changed nothing). What settled it was one command — `docker pull
alpine:latest` — proving pulls worked at all and isolating the fault to the requested repository.
**That differential test should have been first, not fifth.** Docker's error message contributed:
"pull access denied ... repository does not exist or may require 'docker login'" leads with the
auth reading and buries the correct one, and Docker Hub's auth service returns HTTP 200 with a
well-formed token whose `access` array is empty — issued-looking, granting nothing.

**Nesting is not enough for Docker in an unprivileged LXC.** `runc` writes
`net.ipv4.ip_unprivileged_port_start` during container init; Proxmox's default AppArmor profile
blocks it, surfacing as an OCI runtime error with no visible connection to AppArmor. Fixed with
`lxc.apparmor.profile: unconfined`, which Proxmox warns *overrides* the nesting feature rather
than supplementing it. The container stays unprivileged and UID-mapped — this is a
defense-in-depth reduction, not a grant of host root, and the alternative (a privileged container)
would have been worse. It is still the only guest in the lab running without AppArmor, and it is
the one holding the secrets store.

**The host could not reach the subnet it hosts.** `vmbr1` has no host-side IPv4 address — it is a
pure layer-2 bridge — so `ssh -L 8080:10.0.0.20:80` had nowhere to go at its far end, because the
forward originates from the host's own network stack. The evidence was sitting in the pre-flight
capture I had already taken and not read. Fixed by giving the host `10.0.0.5/24` on `vmbr1`, which
is a topology change worth carrying forward: pfSense is no longer the sole path between host side
and lab side.

**"localhost is a secure context" is true of browsers and irrelevant here.** Vaultwarden's client
bundle throws `Insecure URL not allowed. All URLs must use HTTPS.` from its own fetch wrapper,
before sending anything, with no localhost exemption. I asserted the opposite as the reason no
certificate would be needed. Two further fixes were attempted on that wrong theory before I opened
the browser console, which named the throwing module immediately.

**Two smaller behaviours, each costing a cycle.** `docker restart` does not re-read `--env-file` —
env files are parsed once at creation and baked in, while a bind-mounted Caddyfile *is* re-read,
so the two behave oppositely. And a Caddy site block written as bare `:443` has no hostname to
provision a certificate for, so it aborts handshakes with a fatal `internal_error` and logs
nothing about the attempts; its startup line about installing a root certificate refers to its own
CA, not a site cert, and reads as reassurance it should not.

## What I'd do differently

Run the cheap differential test first — one known-good pull would have collapsed four hypotheses
into one fact in a single command. Read the pre-flight capture before building a plan that depends
on what it says. Open the browser console before theorising about a browser-side error. The
pattern underneath all three: I stated things confidently that I had not checked, and the checks
were all one command away.

## Open questions

- **`ADMIN_TOKEN` is still plain text** — `vaultwarden hash` will not read a piped password.
  Either hash it interactively or remove the token and disable the admin panel entirely, which for
  a single-user instance may be the better answer.
- **The persisted `vmbr1` address is unproven** — `ifreload` was deliberately skipped with VMs
  live. If the stanza is wrong, the first symptom is Vaultwarden unreachable after a host reboot.
- **The cron job has never been seen firing** — the entry exists; an unattended run has not been
  observed. `/var/log/vaultwarden-backup.log` is the check.
- **Backups share a disk with what they protect** — `/var/lib/vz` is on the same NVMe as the thin
  pool, so this is a rollback point, not disaster recovery.
- **Whether a narrower AppArmor profile would work** was never investigated; the standard
  workaround was taken at face value.
- **Nothing is stored in the vault yet.** The new break-glass password, `svc-entraconnect`'s, and
  the admin token itself all still live outside it. Until they move in, this is infrastructure
  without a tenant.
