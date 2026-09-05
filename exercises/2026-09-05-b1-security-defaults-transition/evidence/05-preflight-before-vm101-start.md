Command (verbatim):
```
date -u
qm status 100
lvs -a -o+data_percent,metadata_percent
free -h
```
Host: Proxmox host console.
UTC timestamp: 2026-09-05T18:45:01Z.

```
status: running
data pool: Data% 66.28, Meta% 3.41.
Mem: total 15Gi, used 10Gi, free 4.5Gi, available 4.6Gi.
```

Finding: pool Data% 66.28, under the 85% gate. Available memory rose to 4.6Gi from 1.2Gi at
the 18:25:14Z reading, with no host action taken between the two reads. Cause not
investigated. Sufficient headroom exists to start VM 101 (3072 MB) without stopping VM 100
first.
