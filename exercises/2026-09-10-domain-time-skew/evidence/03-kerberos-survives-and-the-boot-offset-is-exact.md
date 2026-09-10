# Kerberos survives the skew, DC01's boot offset is exactly the timezone offset, and its uptime does not reconcile

Command:

```
date -u
qm status 100 --verbose | egrep 'status|uptime'; qm status 107 --verbose | egrep 'status|uptime'
qm guest exec 100 --timeout 60 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; w32tm /query /peers; Get-WinEvent -FilterHashtable @{LogName="System"; ProviderName="Microsoft-Windows-Time-Service"} -MaxEvents 4 | Format-List TimeCreated,Id,Message'
qm guest exec 107 --timeout 90 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; klist get host/DC01.district.local; ([ADSI]"LDAP://DC01.district.local/rootDSE").ldapServiceName; nltest /sc_verify:district.local; certutil -view -out "RequestID,NotBefore,NotAfter,CommonName"'
date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) and CA01 (VM 107) through the QEMU guest
agent
UTC: 2026-09-10T21:53:12Z, returned 2026-09-10T21:53:16Z
Exit codes: both guest agent calls reported `"exitcode" : 0`, `"exited" : 1`.

`out-data` is reproduced below with `\r\n` and `\n` rendered as line breaks. No other alteration.

## Host

```
Thu Sep 10 09:53:12 PM UTC 2026
qmpstatus: running
status: running
uptime: 113621
qmpstatus: running
status: running
uptime: 113620
```

The first pair is VM 100, the second VM 107.

## DC01 (VM 100)

```
2026-09-10T19:59:24.9996233-07:00
#Peers: 1

Peer: time.windows.com
State: Pending
Time Remaining: 55686.4704711s
Mode: 0 (reserved)
Stratum: 0 (unspecified)
PeerPoll Interval: 0 (unspecified)
HostPoll Interval: 0 (unspecified)


TimeCreated : 9/9/2026 2:21:01 PM
Id          : 134
Message     : NtpClient was unable to set a manual peer to use as a time source because of DNS resolution error on
              'time.windows.com'. NtpClient will try again in 15 minutes and double the reattempt interval thereafter.
              The error was: This is usually a temporary error during hostname resolution and means that the local
              server did not receive a response from an authoritative server. (0x80072AFA)

TimeCreated : 9/9/2026 2:20:18 PM
Id          : 134
Message     : NtpClient was unable to set a manual peer to use as a time source because of DNS resolution error on
              'time.windows.com'. NtpClient will try again in 15 minutes and double the reattempt interval thereafter.
              The error was: No such host is known. (0x80072AF9)

TimeCreated : 9/9/2026 2:20:04 PM
Id          : 134
Message     : NtpClient was unable to set a manual peer to use as a time source because of DNS resolution error on
              'time.windows.com'. NtpClient will try again in 15 minutes and double the reattempt interval thereafter.
              The error was: No such host is known. (0x80072AF9)

TimeCreated : 9/9/2026 2:19:52 PM
Id          : 143
Message     : The time service has started advertising as a good time source.
```

## CA01 (VM 107)

```
2026-09-10T21:53:15.9599742-07:00

Current LogonId is 0:0x3e7
A ticket to host/DC01.district.local has been retrieved successfully.

Cached Tickets: (6)

#0>     Client: ca01$ @ DISTRICT.LOCAL
        Server: krbtgt/DISTRICT.LOCAL @ DISTRICT.LOCAL
        KerbTicket Encryption Type: AES-256-CTS-HMAC-SHA1-96
        Ticket Flags 0x40e10000 -> forwardable renewable initial pre_authent name_canonicalize
        Start Time: 9/10/2026 19:59:26 (local)
        End Time:   9/11/2026 5:59:26 (local)
        Renew Time: 9/17/2026 19:59:26 (local)
        Session Key Type: AES-256-CTS-HMAC-SHA1-96
        Cache Flags: 0x1 -> PRIMARY
        Kdc Called: DC01.district.local

#1>     Client: ca01$ @ DISTRICT.LOCAL
        Server: krbtgt/DISTRICT.LOCAL @ DISTRICT.LOCAL
        Ticket Flags 0x60a10000 -> forwardable forwarded renewable pre_authent name_canonicalize
        Start Time: 9/10/2026 3:12:41 (local)
        End Time:   9/10/2026 13:12:40 (local)
        Renew Time: 9/17/2026 0:43:41 (local)
        Cache Flags: 0x2 -> DELEGATION
        Kdc Called: DC01.district.local

#2>     Client: ca01$ @ DISTRICT.LOCAL
        Server: host/DC01.district.local @ DISTRICT.LOCAL
        Ticket Flags 0x40a50000 -> forwardable renewable pre_authent ok_as_delegate name_canonicalize
        Start Time: 9/10/2026 19:59:26 (local)
        End Time:   9/11/2026 5:59:26 (local)
        Renew Time: 9/17/2026 19:59:26 (local)
        Cache Flags: 0
        Kdc Called: DC01.district.local

#3>     Server: cifs/DC01.district.local/district.local @ DISTRICT.LOCAL
        Start Time: 9/10/2026 3:12:41 (local)
        End Time:   9/10/2026 13:12:40 (local)
        Renew Time: 9/17/2026 0:43:41 (local)

#4>     Server: CA01$ @ DISTRICT.LOCAL
        Start Time: 9/10/2026 3:12:40 (local)
        End Time:   9/10/2026 13:12:40 (local)
        Renew Time: 9/17/2026 0:43:41 (local)

#5>     Server: LDAP/DC01.district.local/district.local @ DISTRICT.LOCAL
        Start Time: 9/10/2026 3:12:40 (local)
        End Time:   9/10/2026 13:12:40 (local)
        Renew Time: 9/17/2026 0:43:41 (local)

district.local:dc01$@DISTRICT.LOCAL
Flags: b0 HAS_IP  HAS_TIMESERV
Trusted DC Name \\DC01.district.local
Trusted DC Connection Status Status = 0 0x0 NERR_Success
Trust Verification Status = 0 0x0 NERR_Success
The command completed successfully
Schema:
  Column Name                   Localized Name                Type    MaxLength
  ----------------------------  ----------------------------  ------  ---------
  RequestID                     Issued Request ID             Long    4 -- Indexed
  NotBefore                     Certificate Effective Date    Date    8
  NotAfter                      Certificate Expiration Date   Date    8 -- Indexed
  CommonName                    Issued Common Name            String  8192 -- Indexed

Row 1:  Issued Request ID: 0x1  Effective: 9/5/2026 3:14 PM   Expiration: 9/4/2031 3:14 PM   CN: "district.local Issuing CA"
Row 2:  Issued Request ID: 0x2  Effective: 9/5/2026 2:16 PM   Expiration: 9/2/2036 2:16 PM   CN: "district.local Root CA"
Row 3:  Issued Request ID: 0x3  Effective: 9/7/2026 1:34 PM   Expiration: 9/7/2027 1:34 PM   CN: "DC01.district.local"
Row 4:  Issued Request ID: 0x4  Effective: 9/8/2026 12:13 AM  Expiration: 9/8/2028 12:23 AM  CN: "John Smith"
Row 5:  Issued Request ID: 0x5  Effective: 9/8/2026 2:24 PM   Expiration: 9/8/2027 2:24 PM   CN: "John Smith"
Row 6:  Issued Request ID: 0x6  Effective: 9/8/2026 7:21 AM   Expiration: 9/7/2031 7:21 AM   CN: "district.local Issuing CA"
Row 7:  Issued Request ID: 0x7  Effective: 9/8/2026 11:16 PM  Expiration: 9/8/2027 11:16 PM  CN: "John Smith"
Row 8:  Issued Request ID: 0x8  Effective: 9/9/2026 7:58 PM   Expiration: 9/9/2028 8:08 PM   CN: "jsmith"
Row 9:  Issued Request ID: 0x9  Effective: 9/9/2026 10:10 PM  Expiration: 9/9/2027 10:10 PM  CN: "DC01.district.local"

Maximum Row Index: 9
9 Rows
CertUtil: -view command completed successfully.
```

Rows 1 to 9 are reflowed onto one line each from the original block layout. No value is altered.

## Trailing host reading

```
Thu Sep 10 09:53:16 PM UTC 2026
```

## Derived values

**Both guests booted at the same instant.** Host uptime 113621 s for VM 100 and 113620 s for
VM 107 at 2026-09-10T21:53:12Z gives a boot at 2026-09-09T14:19:31Z and 14:19:32Z, which is
07:19:31 PDT.

**DC01 booted at exactly the timezone offset.** Its `Id 143` event, "The time service has started
advertising as a good time source", is stamped 9/9/2026 2:19:52 PM in DC01's local time, 21 seconds
after the real boot at 14:19:31Z. DC01's local clock therefore read 14:19:52 when real UTC was
14:19:52. Its base error at boot was 7h 00m 00s, which is the host's UTC offset exactly.

**DC01 has lost time since boot.** From +7h 00m 00s at 2026-09-09T14:19:31Z to +5h 06m 11.0s at
2026-09-10T21:45:56.5Z, a loss of 1h 53m 49s across 113,545 s of host time.

**CA01 booted correct.** Its two `Id 129` events are stamped 7:19:59 AM and 7:20:00 AM local, 28
and 29 seconds after the real boot at 07:19:31 PDT.

**DC01's uptime does not reconcile and CA01's does.** CA01 reports `LastBootUpTime`
9/9/2026 2:19:41 PM against its own current reading of 9/10 21:53:15.96 and the host's 113620 s;
now minus uptime gives 9/9 14:19:35, a 6-second difference. DC01 reports `LastBootUpTime`
9/10/2026 3:39:58 AM against its own current reading of 9/10 19:59:25; now minus that value implies
an uptime of 58,767 s against the host's 113,621 s, a ratio of 0.517. DC01's actual boot in its own
frame was 9/9 2:19:31 PM, so the reported value is also 13h 20m 27s later than the machine's own
boot. Whether `LastBootUpTime` is stored or computed is not established here, and neither reading
of it fits.

**The Kerberos ticket carries the KDC's clock.** The TGT's Start Time is 9/10/2026 19:59:26 local,
issued to a client whose own clock read 21:53:15.96 in the same command. DC01's `Get-Date` in the
same block read 19:59:24.99. Both machines report the same timezone, so this is not a rendering
difference.
