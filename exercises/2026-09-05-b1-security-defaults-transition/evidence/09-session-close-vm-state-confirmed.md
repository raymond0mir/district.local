Command (verbatim):
```
qm status 100
qm status 101
qm status 102
qm status 104
date -u
```
Host: Proxmox host console.
UTC timestamp: 2026-09-05T19:16:42Z.

```
status: stopped
status: stopped
status: stopped
status: running
```

Finding: VM 100, 101, 102 stopped. VM 104 (pfSense) running. Matches the lab's standard
opening state. VM 100 shut down via `qm shutdown 100` through its working guest agent. VM 101
shut down manually from inside Windows, avoiding `qm stop`/`--forceStop` per the standing
gotcha against forcing a stop on a VM with no working guest agent.
