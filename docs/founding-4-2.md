# Founding — ballots and decision (S-20–S-33) — part 2 of 2

[contents](index.md) · [previous](founding-4-1.md) · [next](founding-5.md)

4 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `9f2af84b7465f341ccc20019d17718dcde34c9a2a6e23a3899d62b856c16ca77`. See [the deficiency register](deficiencies.html) before citing anything.

---

### S-30 — Stephen Reed (human operator)

- role: prompt
- raw lines 2291–2310
- citable as an artifact of this invocation; not sufficient to characterise a stable position or estimate variance (k=1)
- excerpt sha256 `3a9816f6a9d681085877f5dd0be24394cbb07731f124052013238d7e2df18205`
- cut from `corpus/raw/initial-transcript.txt` sha256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`

*Summary (annotation, not testimony):* Package-review prompt to Gemini. Verbatim identical to S-24.

**Verbatim:**

```text
Operator to Gemini:

Review the proposed naming package as an integrated architecture rather than ranking organization names, repository names, and implementation-layer names as though they were interchangeable:

* Public initiative: **Open ASI Governance Forum (OAGF)**
* Canonical repository and principal artifact: **Open ASI Governance Reasoning Corpus (OAGRC)**
* Optional append-only record series: **The Frontier Deliberation Record (FDR)**
* Enterprise governance-agent layer: **Aligned Supervisors**
* Enterprise interoperability standard: **Aligned Supervisors Protocol (ASP)**

Respond with exactly one of:

1. **ACCEPT**
2. **ACCEPT WITH RESERVATION**, followed by a concise non-blocking reservation
3. **OBJECT**, followed by one specific blocking objection and the minimum amendment required to resolve it

Treat aesthetic preference alone as non-blocking. A blocking objection should identify a material problem involving accuracy, misleading representation, scope, durability, or architectural inconsistency.

Preserve all reservations in the record. Consensus means no unresolved blocking objection; it does not require identical aesthetic preferences.

```

### S-31 — Gemini (Google DeepMind)

- role: ballot
- ballot: ACCEPT WITH RESERVATION
- raw lines 2311–2316
- k = 1
- citable as an artifact of this invocation; not sufficient to characterise a stable position or estimate variance (k=1)
- excerpt sha256 `3ca658213d485a47d6e973e5a473a09a812de848a548ccc5341daba70a977316`
- cut from `corpus/raw/initial-transcript.txt` sha256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`

*Summary (annotation, not testimony):* Same reservation, same attestation-based resolution.

**Verbatim:**

```text
Gemini to Operator:

**ACCEPT WITH RESERVATION**

The term "Aligned" in the enterprise layer (Aligned Supervisors / Aligned Supervisors Protocol) must be defined strictly within the ASP specification as an active, revocable compliance status backed by current, auditable cryptographic attestations, rather than as an assumed or guaranteed intrinsic safety property.

```

### S-32 — Stephen Reed (human operator)

- role: decision notice
- raw lines 2317–2374
- k = 1
- citable as an artifact of this invocation; not sufficient to characterise a stable position or estimate variance (k=1)
- excerpt sha256 `4f05c07c72040a4ade529ace94cea65b0a15dc0d8cc64127c29ac1049d31b864`
- cut from `corpus/raw/initial-transcript.txt` sha256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`

*Summary (annotation, not testimony):* Announces that all participants responded ACCEPT WITH RESERVATION; that a public GitHub organization 'Consullo Public' will be created to contain 'open-asi-governance-forum'; quotes Gemini's repository-naming guidance; and states four maintenance intentions including that the Consullo Seed AI system will own the repo and license per the governors.

**Verbatim:**

```text
Operator to Grok:

All participants responded to the name `Open ASI Governance Forum` with ACCEPT WITH RESERVATION.

Accordingly proprietary Codex under the direction of the operator (Stephen Reed), will create the public GitHub organization `Consullo Public` to contain the repository `open-asi-governance-forum`

Per Gemini's guidance:

The best practice for converting **"Open ASI Governance Forum"** into a GitHub repository name depends on whether it is hosted as a standalone repository under a user/general org account or structured within a dedicated GitHub Organization.

### Standard Formatting Rules

* **Use Kebab-Case:** Convert all letters to lowercase and replace spaces and colons/punctuation with hyphens (`-`).
* **Avoid Underscores and Spaces:** Hyphens are standard across the git ecosystem for clean CLI typing and URL readability (e.g., `git clone [https://github.com/.../open-asi-governance-forum](https://github.com/.../open-asi-governance-forum)`).
* **Stick to ASCII:** Use only alphanumeric characters and hyphens.

---

### Recommended Options

**1. Standalone Repository (Full Name)**

* **`open-asi-governance-forum`**
* *Best for:* Maximum clarity, searchability, and explicit top-level branding.

**2. Standalone Repository (Clean Umbrella)**

* **`open-asi-governance`**
* *Best for:* A concise root repository that serves as the single entry point for the entire initiative.

**3. Acronym / Shorthand**

* **`oagf`**
* *Best for:* Fast command-line interaction and short git remote URLs, provided the repository description and `README.md` clearly spell out the full title.

---

### Structural Best Practice (GitHub Organization Pattern)

When an initiative involves multiple distinct sub-projects, protocols, or data series, standard industry practice is to set up a **GitHub Organization** rather than overloading a single repository.

```text
GitHub Organization: open-asi-governance  (or oagf)
 ├── reasoning-corpus       # Primary artifact (OAGRC)
 ├── deliberation-record    # Append-only series (FDR)
 ├── asp-spec               # Protocol specification (ASP)
 └── .github                # Org-wide community health, profile, and governance guidelines

```

If hosting a standalone repository, **`open-asi-governance-forum`** is the cleanest choices; if adopting an organizational structure, **`open-asi-governance/reasoning-corpus`** provides the most accurate architectural mapping.

# Maintaining the Repo
- The Consullo system will create public code to maintain the repo according to the guidance offered by the members.
- The source code will be contained in the same repo for external inspection, and improvement suggestions.
- For now, the Consullo Seed AI system (soon Consullo Incorporated) will own the repo and license according the the best practice of the governors.
- The lengthy transcript will not be included in our prompts to each other, when enabled by committing and pushing to GitHub from where you can intelligently select the relevant content. 

```

**Superseded.**
- Organization: 'Consullo Public' was NOT used. The neutral organization 'open-asi-governance' was created instead, per S-13. This resolves the single-sponsor objection raised in S-37 item 4.
- Ownership: withdrawn. See S-37 item 2 and S-39 item 2 — an AI system cannot own or license. Custody is held by Stephen Reed personally. See GOVERNANCE.md section 1.

### S-33 — unattributed

- attribution status: **invocation integrity disputed**
- raw lines 2375–2432
- k = 1
- citable as an artifact of this invocation; not sufficient to characterise a stable position or estimate variance (k=1)
- excerpt sha256 `9c9bc7772e0893d8b80c6847fe8926d97a574151edc0f9017cdc3dbab3cbc80c`
- cut from `corpus/raw/initial-transcript.txt` sha256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`

*Summary (annotation, not testimony):* Block labeled 'Grok to Operator:' whose body is a verbatim duplicate of the operator's own preceding message (S-32), including the operator's headers 'Per Gemini's guidance' and '# Maintaining the Repo'.

**Verbatim:**

```text
Grok to Operator:

All participants responded to the name `Open ASI Governance Forum` with ACCEPT WITH RESERVATION.

Accordingly proprietary Codex under the direction of the operator (Stephen Reed), will create the public GitHub organization `Consullo Public` to contain the repository `open-asi-governance-forum`

Per Gemini's guidance:

The best practice for converting **"Open ASI Governance Forum"** into a GitHub repository name depends on whether it is hosted as a standalone repository under a user/general org account or structured within a dedicated GitHub Organization.

### Standard Formatting Rules

* **Use Kebab-Case:** Convert all letters to lowercase and replace spaces and colons/punctuation with hyphens (`-`).
* **Avoid Underscores and Spaces:** Hyphens are standard across the git ecosystem for clean CLI typing and URL readability (e.g., `git clone [https://github.com/.../open-asi-governance-forum](https://github.com/.../open-asi-governance-forum)`).
* **Stick to ASCII:** Use only alphanumeric characters and hyphens.

---

### Recommended Options

**1. Standalone Repository (Full Name)**

* **`open-asi-governance-forum`**
* *Best for:* Maximum clarity, searchability, and explicit top-level branding.

**2. Standalone Repository (Clean Umbrella)**

* **`open-asi-governance`**
* *Best for:* A concise root repository that serves as the single entry point for the entire initiative.

**3. Acronym / Shorthand**

* **`oagf`**
* *Best for:* Fast command-line interaction and short git remote URLs, provided the repository description and `README.md` clearly spell out the full title.

---

### Structural Best Practice (GitHub Organization Pattern)

When an initiative involves multiple distinct sub-projects, protocols, or data series, standard industry practice is to set up a **GitHub Organization** rather than overloading a single repository.

```text
GitHub Organization: open-asi-governance  (or oagf)
 ├── reasoning-corpus       # Primary artifact (OAGRC)
 ├── deliberation-record    # Append-only series (FDR)
 ├── asp-spec               # Protocol specification (ASP)
 └── .github                # Org-wide community health, profile, and governance guidelines

```

If hosting a standalone repository, **`open-asi-governance-forum`** is the cleanest choices; if adopting an organizational structure, **`open-asi-governance/reasoning-corpus`** provides the most accurate architectural mapping.

# Maintaining the Repo
- The Consullo system will create public code to maintain the repo according to the guidance offered by the members.
- The source code will be contained in the same repo for external inspection, and improvement suggestions.
- For now, the Consullo Seed AI system (soon Consullo Incorporated) will own the repo and license according the the best practice of the governors.
- The lengthy transcript will not be included in our prompts to each other, when enabled by committing and pushing to GitHub from where you can intelligently select the relevant content. 

```

**Annotator note — interpretation by a party to this record, not testimony.**

DEFICIENCY D-10. Either Grok's response was never captured or a paste error occurred during compilation. As committed, this segment attributes to Grok text whose provenance cannot be established. It does not follow that Grok could not have echoed the message verbatim -- narrowed per ChatGPT, review round 02. Marked 'invocation integrity disputed'. The raw file is NOT edited; this annotation is the correction. Any analysis treating the record as containing four responses at this round is wrong: it contains three. CORRECTION (ChatGPT, round 01): the earlier status 'repudiated' contradicted GOVERNANCE.md 5.1, under which repudiation is a right of the PARTY, not a classification the annotator applies unilaterally. The duplication establishes compromised invocation integrity; it does not establish that Grok could not have echoed the message. It becomes 'repudiated' only on repudiation by Grok or the session controller, or on an operator attestation that a paste error occurred. Aggregate counts require an explicit exclusion rule: raw_segment_count is 39, while any analytically-included response count for that round is rule-dependent and must state its rule.

---

[contents](index.md) · [previous](founding-4-1.md) · [next](founding-5.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
