# Proxmox host had no route to the lab subnet

Host: Proxmox host shell
Timestamp (UTC): 2026-09-03, ~15:58

Vaultwarden was confirmed listening (`Rocket has launched from http://0.0.0.0:80`, `docker ps`
showing `0.0.0.0:80->80/tcp`). From the host:

```
# curl -v --max-time 5 http://10.0.0.20/
*   Trying 10.0.0.20:80...
* Connection timed out after 5002 milliseconds
curl: (28) Connection timed out after 5002 milliseconds
```

Bridge state, from this exercise's pre-flight capture:

```
vmbr0            UP             192.168.1.100/24 fe80::a229:19ff:fe60:4089/64
vmbr1            UP             fe80::cc29:12ff:fedd:89c7/64
```

`vmbr1` carries no host-side IPv4 address.

## Change applied

```
# ip addr add 10.0.0.5/24 dev vmbr1
# curl -v --max-time 5 http://10.0.0.20/
* Connected to 10.0.0.20 (10.0.0.20) port 80
< HTTP/1.1 200 OK
< server: Rocket
<!doctype html><html class="theme_light">...<title page-title>Vaultwarden Web</title>...
```

## Persistence

`/etc/network/interfaces` before, backed up to `/etc/network/interfaces.bak-<timestamp>`:

```
auto vmbr1
iface vmbr1 inet manual
        bridge-ports none
        bridge-stp off
        bridge-fd 0
#lab internal
```

Edited to `iface vmbr1 inet static` with `address 10.0.0.5/24`. **`ifreload` was not run** — VM 100
and pfSense were live and a network reload was judged not worth the risk mid-session. The runtime
address is proven; the persisted stanza is not.
