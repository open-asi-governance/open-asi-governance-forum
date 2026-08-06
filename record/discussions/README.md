# Seed discussions, drafted and blocked

Bodies for the GitHub Discussions that seed the corpus's two open questions. They are committed
rather than held in a session because **the session that wrote them cannot post them**, and an
artifact that exists only in a chat log is lost the moment that session ends.

## Status

**Discussions are enabled** on the repository (2026-08-06, via `PATCH /repos/{owner}/{repo}` with
`has_discussions: true` — that call needs `administration=write`, which `GH_TOKEN_OAGF` has).

**Creating a discussion is blocked.** The GraphQL `createDiscussion` mutation returns
*"Resource not accessible by personal access token"*. It needs `discussions=write`, which the token
does not carry. This is a custodian action, recorded in `HANDOFF.md`.

## To post them

Either add `discussions=write` to `GH_TOKEN_OAGF` and run the mutation, or paste the bodies into the
**Q&A** category (`DIC_kwDOTvFKM84DC0EM`) by hand. Titles:

| File | Title |
|---|---|
| `Q-01-seed.md` | Q-01 — What empirical evidence would show a multi-agent ASI deployment cannot self-amplify or communicate out of band? |
| `Q-02-seed.md` | Q-02 — How do we distinguish cross-model agreement from shared bias and from sampling noise? |

## Why these two and nothing else

They are the record's own unanswered questions, carried from the founding transcript at raw lines
1520 and 1335. Neither was answered in the founding session, and neither was returned to across two
frontier review rounds. Seeding anything else first would put the project's output ahead of the
record's outstanding work, which is the ordering this corpus exists to resist.

The Q-02 body also surfaces **P-CHATGPT-0001**, an open prediction that this project will *fail* to
produce the variance-decomposition study Q-02 requires. On present evidence it resolves correct:
no such study exists and nothing schedules one. It is stated in the seed rather than omitted,
because a forum that hides the prediction against itself is doing public relations.
