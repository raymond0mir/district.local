# Evidence log — Vaultwarden secrets store

## What was captured

Real command output from the Proxmox host shell and container 103, plus one block of browser
DevTools console text. Six threads, one file each: pre-flight and container build; the AppArmor
block on Docker-in-LXC; the registry diagnosis behind a wrong image name; the host's missing route
to `10.0.0.0/24`; the HTTPS requirement and Caddy certificate issuance; backup, restore
verification, and schedule.

## What was not captured, and why

- **The admin token and master password** were never displayed or transmitted. The token was
  generated and written to a file in a single shell step so it never appeared in copyable form;
  the master password is Raymond's alone.
- **The vault account's email** and **the home network's public IP** (echoed back by Docker Hub in
  a `docker-ratelimit-source` header) are redacted — this repo is public.
- **Account creation succeeding in the browser is Recalled**, not Captured — confirmed in session
  and by screenshot, which the capture contract classes as Recalled. Corroborated Captured by the
  restored database containing exactly one user row.
- **The persisted `/etc/network/interfaces` change is untested** — `ifreload` was deliberately not
  run with VMs live, so the static `vmbr1` address is proven at runtime only.
- **The cron job has never been observed firing** — the crontab entry is captured; a 03:00 run is
  not.

## Deviations from the plan going in

Two design assumptions failed outright and were replaced mid-exercise: that a plain-HTTP tunnel to
localhost would satisfy Vaultwarden (it does not — a Caddy TLS reverse proxy was added, landing on
the "TLS termination" goal named when this work was proposed), and that `ssh -L` to `10.0.0.20`
would work (the host had no layer-3 presence on its own lab bridge). Scope also grew by one
unplanned item: the AppArmor relaxation on container 103, accepted as the lesser cost versus
making the container privileged.
