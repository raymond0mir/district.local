# The paired control did not hold: the session never switched accounts

This capture is a failed control. It is kept because the failure is the evidence.

```
Command: GET https://graph.microsoft.com/v1.0/users?$top=3
Host:    Graph Explorer, browser on the Mac Mini
UTC:     between 2026-09-13T01:07:51Z and the token read below
Intended signing identity: adm-jsmith
Actual signing identity:   the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8
```

The read returned `200` with three users: `adm-jsmith`, `ajones` and `bhound`, plus an
`@odata.nextLink`. `adm-jsmith` appearing first is alphabetical ordering by `userPrincipalName`. It
is not evidence about the caller.

## The token that made the call

```
Command: python3 <scratchpad>/decode-token.py, reading the clipboard
Host:    Terminal on the Mac Mini
UTC:     token iat 2026-09-13T01:11:38Z, exp 2026-09-14T01:16:38Z
```

```json
{
  "aud": "00000003-0000-0000-c000-000000000000",
  "appid": "de8bc8b5-d9f9-48b1-a8ad-b748da725064",
  "app_displayname": "Graph Explorer",
  "scp": "... Application.Read.All ... Directory.Read.All ... User.Read User.Read.All User.ReadBasic.All User.ReadWrite.All ...",
  "roles": null,
  "wids": [
    "62e90394-69f5-4237-9190-012177145e10",
    "b79fbf4d-3ef9-4689-8143-76b194e85509"
  ],
  "oid": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
  "tid": "e0b13496-83d1-4721-8bf9-f965f676106f",
  "ver": "1.0",
  "iat": 1789261898,
  "exp": 1789348598
}
```

The `scp` list is abbreviated here to the entries the comparison turns on. The full list is the same
one recorded in `evidence/03-graph-explorer-token-decoded.md`, with `Application.Read.All` added by
this exercise's consent.

---

## What went wrong

The instruction said to sign out of Graph Explorer, sign in as `adm-jsmith`, and read the account
chip. The token proves the account did not change. A sign-out followed by a sign-in re-authenticates
through the browser's existing session, and the same account returns without a prompt. Reading a
chip would have caught it; so did the token, which is why the token read was added before the write-up
rather than after.

**Claude built the sequence with a chip-reading step for the second time in this exercise.** The same
gap was corrected earlier the same day, in captures 01 and 02. The lesson did not reach the next
sequence design. Establish the signing identity from the token, before the read that depends on it.

## What the capture is still worth

It compares two tokens rather than two clients. A token holding `User.Read.All` read `/users` at
`200`. A token holding `User.Read` alone was refused at `403`, in
`evidence/07-device-code-token-bounds-the-signed-in-user.md`. That comparison changes two variables
at once, the scope and the human, so it supports the finding and does not close it.

## The control that would close it

Request a second token for the **same client and the same user**, with one different scope. The scope
must be one that `adm-jsmith` can consent to without an administrator, or the run stops at consent
rather than at authorization. `User.ReadBasic.All` is the candidate. That run changes exactly one
variable.

It also tests something the exercise has assumed and never checked: whether the application's
declared permission list bounds what the client may request at runtime. `Lab-AI-Agent-CLI` declares
one scope. If a request for a second scope succeeds, the declared list is not the boundary, and the
exercise's own hypothesis needs restating.
