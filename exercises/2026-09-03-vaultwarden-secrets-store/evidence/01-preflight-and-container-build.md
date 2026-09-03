# Pre-flight readings and LXC container build

Command: `pct list` / `qm list` / `free -h` / `lvs -a -o+data_percent,metadata_percent` / `pveam list local` / `ip -br a`
Host: Proxmox host shell
Timestamp (UTC): 2026-09-03, before the first state change of this exercise

```
      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID
       100 winserver2022        running    10000             60.00 1946
       101 win11-client01       stopped    4096              64.00 0
       102 entraconnect01       stopped    3072              60.00 0
       104 pfsense-fw           running    2048              20.00 1464
               total        used        free      shared  buff/cache   available
Mem:            15Gi        11Gi       3.8Gi        49Mi       415Mi       3.9Gi
Swap:          8.0Gi          0B       8.0Gi
  LV    VG  Attr       LSize    Pool Origin   Data%  Meta%
  data  pve twi-aotz-- <155.23g                72.00  3.62

vmbr0            UP             192.168.1.100/24 fe80::a229:19ff:fe60:4089/64
vmbr1            UP             fe80::cc29:12ff:fedd:89c7/64
```

`pct list` returned no rows — no LXC container existed on this host before this exercise.
`pveam list local` returned a header with zero rows — no templates cached.

## Storage content type

`local` was configured `content iso,vztmpl,backup` — no `rootdir`, so it could not hold a
container filesystem:

```
pvesm set local --content iso,vztmpl,backup,rootdir
```

## Template and container

```
pveam update
pveam available | grep -i debian-12
```

Selected `system  debian-12-standard_12.12-1_amd64.tar.zst` (the remaining matches were TurnKey
appliance images).

```
pveam download local debian-12-standard_12.12-1_amd64.tar.zst
pct create 103 local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst \
  --hostname vaultwarden \
  --memory 1024 --swap 512 --cores 1 \
  --rootfs local:8 \
  --net0 name=eth0,bridge=vmbr1,ip=10.0.0.20/24,gw=10.0.0.1 \
  --unprivileged 1 \
  --features nesting=1,keyctl=1 \
  --onboot 1
pct start 103
```

```
calculating checksum...OK, checksum verified          (123731847 bytes)
VMID       Status     Lock         Name
103        running                 vaultwarden
lo               UNKNOWN        127.0.0.1/8 ::1/128
eth0@if19        UP             10.0.0.20/24 fe80::be24:11ff:fefe:d131/64
```

## Docker install

From Docker's apt repository with a pinned signing key:

```
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
docker version
```

```
Client: Docker Engine - Community
 Version:           29.7.2
Server: Docker Engine - Community
 Engine:
  Version:          29.7.2
 containerd:
  Version:          v2.3.4
 runc:
  Version:          1.4.3
```
