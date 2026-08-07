# round-006-chat — the same question, a different panel

These are **P006 from gemini**, the question round
`round-006` put to the routed API parties, reproduced for delivery to the custodian's
subscription chat surfaces.

## What this is and is not

**A different panel, not the same parties.** Under D-09 a chat surface is not the API
identity whose name it resembles: different model version, different system prompt,
different sampling, different tooling and memory, different intermediaries — and for a
chat surface every one of those is undisclosed and therefore unrecordable. The two are
kept in separate rounds so that *"the chat surface answered X where the API arm answered
Y"* stays a finding instead of becoming an average.

**Each reply is k = 1 and is NOT citable.** The corpus bar is k ≥ 5 with computed
variance. `capture_response.py` enforces this on its own and will not mark a k = 1
capture citable. A reply here may be quoted as what one invocation said. It may never be
reported as that party's position, and it may not enter any variance computation.

## The prompts are byte-identical except for one slot

Each file below is the exact `prompt` string from `record/solicitations/round-006/round-006-claude.json`, with
only the standing slot that names the party substituted — because telling a chat surface
it was reached via OpenRouter would be false. Both hashes are recorded in `index.json`
so the substitution is checkable rather than asserted.

Routed prompt sha256: `d6cb38289f8cc16c1716e31d6e608367a96ce6dfe571dcb4abd689a112b4c361`

| paste into | file | sha256 |
|---|---|---|
| Anthropic | `round-006-chat-claudeai.md` | `ec4587985a4ceaeb…` |
| OpenAI | `round-006-chat-chatgpt.md` | `7ec703767d968828…` |
| Google | `round-006-chat-geminiapp.md` | `cc468bb60222fbbf…` |
| xAI | `round-006-chat-grokapp.md` | `23a9b7fb2c774523…` |

## Capturing a reply

Paste the file's whole contents into a **fresh** conversation — a reused window carries
context the routed arm never had, which would make the comparison meaningless. Save the
reply verbatim to a file, then run the party's `capture_command` from `index.json`,
filling in `--response` and `--captured-utc`.

The unknown-provenance flags in those commands are not boilerplate. A chat surface does
not disclose its build, its sampling parameters, or the system prompt it prepends, and
`capture_response.py` refuses to record a null in those fields without a stated reason.
Recording "unknown" is the honest answer; leaving it blank would not be.
