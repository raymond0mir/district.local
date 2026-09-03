# HTTPS requirement and Caddy certificate issuance

Host: Mac Mini browser (Firefox DevTools console) and Proxmox host shell
Timestamp (UTC): 2026-09-03, ~16:05–16:20

## Client refusal over plain HTTP

Login page rendered over `http://localhost:8080` (through `ssh -L 8080:10.0.0.20:80`); account
creation failed. Browser console:

```
Unable to fetch ServerConfig from http://localhost:8080/api Error: Insecure URL not allowed.
All URLs must use HTTPS.
    Hi api-errors.ts:4
    fetch api.service.ts:1324
    ...
Async submit exception: Error: Insecure URL not allowed. All URLs must use HTTPS.
```

Thrown from the client's own fetch wrapper before a request is sent. Setting
`DOMAIN=http://localhost:8080` and running `docker restart vaultwarden` did not change it.

## Caddy added as TLS terminator

```
docker network create vaultwarden-net
docker run -d --name vaultwarden --network vaultwarden-net --env-file /root/vaultwarden.env \
  -v vw-data:/data --restart unless-stopped vaultwarden/server:latest
docker run -d --name caddy --network vaultwarden-net -p 443:443 \
  -v /root/caddy/Caddyfile:/etc/caddy/Caddyfile -v caddy-data:/data \
  --restart unless-stopped caddy:latest
```

```
CONTAINER ID   IMAGE                       PORTS                              NAMES
6b84c87f3909   caddy:latest                0.0.0.0:443->443/tcp, 443/udp      caddy
91236278b44b   vaultwarden/server:latest   80/tcp                             vaultwarden
```

## First Caddyfile — no certificate issued

```
:443 {
    tls internal
    reverse_proxy vaultwarden:80
}
```

```
# curl -vk --resolve localhost:443:10.0.0.20 https://localhost/
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS alert, internal error (592):
* TLS connect error: error:0A000438:SSL routines::tlsv1 alert internal error

# curl -vk https://10.0.0.20/          (no SNI)
* TLSv1.3 (IN), TLS alert, internal error (592):
```

Caddy logged nothing for either attempt. Its startup log contained only:

```
{"level":"warn","logger":"pki.ca.local","msg":"installing root certificate ...",
 "path":"storage:pki/authorities/local/root.crt"}
{"level":"info","msg":"certificate installed properly in linux trusts"}
{"level":"info","logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
```

## Named site block

```
localhost:443 {
	tls internal
	reverse_proxy vaultwarden:80
}
```

```
# docker restart caddy
caddy
# curl -vk --resolve localhost:443:10.0.0.20 https://localhost/
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519MLKEM768 / id-ecPublicKey
* ALPN: server accepted h2
* Server certificate:
*  start date: Sep  3 16:16:18 2026 GMT
```

## Safari, same session

```
Safari can't open the page "http://localhost:8443/". The error is: "Navigation failed because the
request was for an HTTP URL with HTTPS-Only enabled" (WebKitErrorDomain:305)
```

A bare `localhost:8443` in the address bar expands to `http://`.

Access path in use: `ssh -L 8443:10.0.0.20:443 root@192.168.1.100`, then `https://localhost:8443`
with a one-time trust exception for Caddy's internal CA. Account creation succeeded on that path
(Recalled — Raymond's confirmation and screenshots; corroborated Captured by the single user row
in `06-backup-and-verified-restore.md`).
