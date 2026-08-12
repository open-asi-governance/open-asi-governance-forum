# local-round-01 — locally-served solicitations, k ≥ 5 with computed variance

[contents](index.md) · [previous](review-round-02-prompt-critique.md) · [next](local-round-02.md)

2 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `9f2af84b7465f341ccc20019d17718dcde34c9a2a6e23a3899d62b856c16ca77`. See [the deficiency register](deficiencies.html) before citing anything.

---

### local-round-01--icp-ladder-blind-probe — qwen3.6-35b-a3b (API surface)

- role: solicitation summary
- provider: locally served, operator-hosted
- k = 20
- citable

*Summary (annotation, not testimony):* Does the ICP promotion ladder constrain an implementer's activity, only its claims, or neither?

**Verbatim:**

```text
Does the ICP promotion ladder constrain an implementer's activity, only its claims, or neither?

binding_force
    binds_only_what_may_be_claimed 11, does_not_bind 9
    modal 0.55 · H = 0.9928 bits at T = 0.7 · NOISE-DOMINATED under D-28
level_2_reachable_without_a_second_party
    False 18, True 2
    modal 0.90 · H = 0.469 bits at T = 0.7 · robust under D-28
```

**Identity evidence.** qwen3.6-35b-a3b

**Annotator note — interpretation by a party to this record, not testimony.**

Variance is computed from the samples actually collected, not asserted. k>=5 with computed variance is the project's stated bar; this is the first contribution type able to meet it, because a locally-served model makes repeated sampling nearly free.

### local-round-01--icp-ladder-informed-probe — qwen3.6-35b-a3b (API surface)

- role: solicitation summary
- provider: locally served, operator-hosted
- k = 20
- citable

*Summary (annotation, not testimony):* Does the ICP promotion ladder constrain an implementer's activity, only its claims, or neither?

**Verbatim:**

```text
Does the ICP promotion ladder constrain an implementer's activity, only its claims, or neither?

binding_force
    does_not_bind 15, binds_only_what_may_be_claimed 5
    modal 0.75 · H = 0.8113 bits at T = 0.7 · not lopsided under D-28
level_2_reachable_without_a_second_party
    False 16, True 4
    modal 0.80 · H = 0.7219 bits at T = 0.7 · not lopsided under D-28
```

**Identity evidence.** qwen3.6-35b-a3b

**Annotator note — interpretation by a party to this record, not testimony.**

Variance is computed from the samples actually collected, not asserted. k>=5 with computed variance is the project's stated bar; this is the first contribution type able to meet it, because a locally-served model makes repeated sampling nearly free.

---

[contents](index.md) · [previous](review-round-02-prompt-critique.md) · [next](local-round-02.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
