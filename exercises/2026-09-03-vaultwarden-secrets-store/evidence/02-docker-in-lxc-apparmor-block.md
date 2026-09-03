# Docker container init blocked by AppArmor in an unprivileged LXC

Host: Proxmox host shell, targeting container 103
Timestamp (UTC): 2026-09-03, after Docker installed cleanly

`docker version` had already returned a populated Server section. The first `docker run`:

```
docker: Error response from daemon: failed to create task for container: failed to create shim
task: OCI runtime create failed: runc create failed: unable to start container process: error
during container init: open sysctl net.ipv4.ip_unprivileged_port_start file: reopen fd 8:
permission denied
```

`docker ps` immediately after showed no running containers — a container object was created, its
process never started.

## Change applied

```
docker rm vaultwarden
pct stop 103
echo "lxc.apparmor.profile: unconfined" >> /etc/pve/lxc/103.conf
pct start 103
```

Proxmox's own warning on next start:

```
explicitly configured lxc.apparmor.profile overrides the following settings: features:nesting
```

## Result

```
CONTAINER ID   IMAGE                       COMMAND       STATUS                    PORTS                NAMES
a5eff0dadafb   vaultwarden/server:latest   "/start.sh"   Up (health: starting)     0.0.0.0:80->80/tcp   vaultwarden
```

```
/--------------------------------------------------------------------\
|                        Starting Vaultwarden                        |
|                           Version 1.37.2                           |
\--------------------------------------------------------------------/

[NOTICE] You are using a plain text `ADMIN_TOKEN` which is insecure.
[2026-09-03 15:53:16.584][vaultwarden::auth][INFO] Private key 'data/rsa_key.pem' created correctly
[2026-09-03 15:53:16.681][start][INFO] Rocket has launched from http://0.0.0.0:80
```

Container 103 remains `--unprivileged 1` (UID-mapped) after this change; what was removed is
AppArmor confinement, not the user-namespace mapping.
