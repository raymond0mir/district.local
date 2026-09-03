# Registry diagnosis: `vaultwarden/vaultwarden` vs `vaultwarden/server`

Host: container 103, via `pct exec` from the Proxmox host shell
Timestamp (UTC): 2026-09-03, ~15:40–15:50

## The symptom

```
Unable to find image 'vaultwarden/vaultwarden:latest' locally
docker: Error response from daemon: pull access denied for vaultwarden/vaultwarden, repository
does not exist or may require 'docker login'
```

## DNS and IPv6

```
# cat /etc/resolv.conf
search lab.lokal
nameserver 1.1.1.1

# ping -c2 1.1.1.1
2 packets transmitted, 2 received, 0% packet loss

# getent hosts registry-1.docker.io
2600:1f18:2148:bc02:e82d:d775:8efd:e4b4 registry-1.docker.io
   ...(8 AAAA records, zero A records)...

# sysctl -w net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.all.disable_ipv6 = 1

# getent hosts registry-1.docker.io
   ...(still 8 AAAA, zero A)...

# docker pull vaultwarden/vaultwarden:latest
Error response from daemon: pull access denied ... (identical)
```

## Registry reachability over IPv4

```
# curl -4 -v https://registry-1.docker.io/v2/
* Connected to registry-1.docker.io (23.20.232.38) port 443
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256
*  subjectAltName: host "registry-1.docker.io" matched cert's "*.docker.io"
*  SSL certificate verify ok.
{"errors":[{"code":"UNAUTHORIZED","message":"authentication required","detail":null}]}

# curl -4 -v "https://auth.docker.io/token?service=registry.docker.io&scope=repository:vaultwarden/vaultwarden:pull"
* Connected to auth.docker.io (104.18.43.178) port 443
*  SSL certificate verify ok.
```

Token issued (HTTP 200, well-formed JWT). Decoded payload: `{"access":[], ...}` — empty access
array. Presented to the registry:

```
HTTP/2 401
www-authenticate: Bearer realm="https://auth.docker.io/token",service="registry.docker.io",
  scope="repository:vaultwarden/vaultwarden:pull",error="insufficient_scope"
docker-ratelimit-source: [REDACTED-PUBLIC-IP]
```

No `ratelimit-limit` or `ratelimit-remaining` headers present.

## Authenticated retry

```
# docker login
Authenticating with existing credentials... [Username: raytakosharky]
Login Succeeded

# docker pull vaultwarden/vaultwarden:latest
Error response from daemon: pull access denied ... (identical)
```

## Differential test

```
# docker pull alpine:latest
latest: Pulling from library/alpine
Status: Downloaded newer image for alpine:latest
docker.io/library/alpine:latest

# docker pull vaultwarden/server:latest
latest: Pulling from vaultwarden/server
Digest: sha256:094b5689ed81549bd293418395c7cf495ae9d960fc2d4928cef2083ef913d912
Status: Downloaded newer image for vaultwarden/server:latest
```

A known-good public image pulls cleanly on the same daemon, network, and credentials; the correct
Vaultwarden image pulls cleanly on the same. The fault was the repository name.
