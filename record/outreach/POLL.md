# Polling for replies to the 2026-08-10 prior-art enquiry

**Any session can run this. It needs no scheduler, no background job and no state.**

The claude.ai Gmail connector must be connected (`/mcp`) on the `stephenlreed@gmail.com` mailbox.
`list_labels` is the cheapest liveness check: if it returns `insufficient authentication scopes`,
the OAuth grant lacks read permission and re-authorising is the fix — that is a *Google* scope,
not a Claude Code permission, and marking tools "always allow" does not affect it.

## The query

```
newer_than:14d -in:sent -in:draft {from:ryanph@umich.edu from:rjust@cs.washington.edu
from:gordon.fraser@uni-passau.de from:marinov@illinois.edu from:palvaro@ucsc.edu
from:haryadi@cs.uchicago.edu from:sbagchi@purdue.edu from:rushby@csl.sri.com
from:isa@york.ac.uk from:info@sei.cmu.edu from:mailer-daemon@googlemail.com
from:postmaster subject:"negative-control attestation"}
```

Scoped to the ten recipients, bounce senders, and the subject line. **Not general inbox
reading** — narrower is both better signal and less of the custodian's mail than a poll needs to
see.

## Negative-control the query before trusting a zero

**An empty result and a malformed query are indistinguishable.** Before reporting "no replies",
run the identical query with one sender known to have recent mail added to the brace group. If
that returns nothing, the query is broken, not the inbox empty.

Done 2026-08-10: the real query returned empty; the same query plus one known-good sender
returned 3. The zero was real.

## What counts

| observation | meaning |
|---|---|
| substantive reply | the result. Record it. |
| **a bounce** | **a result, not noise** — especially from `palvaro@ucsc.edu` (domain completed by the workbench, not read from any page) or `ryanph@umich.edu` (read over an unverified TLS connection) |
| out-of-office | not a result; note and ignore |
| nothing by **2026-10-05** | the pre-registered adverse outcome |

## Replies are private until their sender says otherwise

**The email as sent promised nothing about publication.** That promise appears on `CHALLENGE.md`,
which a recipient may never open. So a reply is private correspondence: record its *substance* in
the record without attribution, and ask the sender before publishing their words or name.

## Baseline

- Sent 2026-08-10, 19:58–20:07 UTC, all ten confirmed present in `SENT` with matching recipients.
- First poll 2026-08-10 ~20:25 UTC: **no replies, no bounces.** Roughly 20 minutes after sending,
  so this establishes only that nothing hard-failed immediately. Soft failures and greylisting can
  take hours; absence of a bounce is not evidence of delivery.
