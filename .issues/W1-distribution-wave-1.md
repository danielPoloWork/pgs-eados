# W1 — Distribution, Wave 1

Tracking issue: **#382** (carries the seven-step publish checklist).

Wave 0 (#380 / #381, merged 2026-07-28) fixed the landing surface. Wave 1 is the first traffic
ever pointed at it. Wave 2 (Show HN, Reddit) stays closed until the demo recording exists — see
*The gate on Wave 2* at the bottom.

**Nothing in this document has been published.** Every item is a draft awaiting the owner's
explicit go, because each one publishes public content or sends a message under his name.

---

## 1. The awesome-list lane is narrower than the plan assumed

Researched 2026-07-28. Two of the highest-value targets are **closed**, and finding that out now
is worth more than the entries themselves.

| Target | Status | Why |
|---|---|---|
| [`tairov/awesome-agents.md`](https://github.com/tairov/awesome-agents.md) | ❌ **CLOSED** | **Archived 2026-01-26, read-only.** Was the single best fit — EADOS *generates* AGENTS.md contracts. No PR is possible. |
| [`subinium/awesome-claude-code`](https://github.com/subinium/awesome-claude-code) | ❌ **CLOSED** | Lists only repositories with **1,000+ stars**. EADOS has 2. Revisit at ~1k, not before. |
| [`Engineering4AI/awesome-spec-driven-development`](https://github.com/engineering4ai/awesome-spec-driven-development) | ✅ **OPEN — primary** | *"Contributions are welcome! Please feel free to submit a pull request."* No threshold. Best remaining fit: EADOS is RFC-first by construction. |
| [`hesreallyhim/awesome-claude-code`](https://github.com/hesreallyhim/awesome-claude-code) | ⚠️ **OPEN, issue form only** | *"Do not open a PR. Just fill out the form."* Opening a PR risks repository restrictions. No star threshold, but selective. |
| [`jqueryscript/awesome-claude-code`](https://github.com/jqueryscript/awesome-claude-code) | ✅ OPEN — secondary | PR-based, loose criteria. Category fit: *Agents & Orchestration* or *Tools & Utilities*. |
| [`bradAGI/awesome-cli-coding-agents`](https://github.com/bradagi/awesome-cli-coding-agents) | ⚠️ Partial fit | Scope is agents and harnesses. EADOS is neither — it governs the repo an agent works in. Only if a governance category exists. |

**Read this before submitting anywhere.** The `hesreallyhim` maintainer states plainly that the
point of an awesome list is to be selective, and advises building an audience first rather than
treating the list as a marketing strategy. That is a fair warning and it applies to us: submit to
the two lists where EADOS genuinely belongs, do not carpet-bomb the category. A rejected entry
costs nothing; a reputation for spraying costs the next three submissions.

### 1a. Entry — `awesome-spec-driven-development` (PR)

Section: **Development Frameworks** (fallback: *Specification Tools*). Their format is
`*   [Name](url) [![](star-badge)](star-badge) - Description.`

```markdown
*   [EADOS](https://github.com/danielPoloWork/pgs-eados) - Renders a governed repository from a manifest and an RFC — agent contract, ADRs, CI gates and SemVer rules — for any of 19 language toolchains, then enforces the rules with lint on every commit.
```

### 1b. Entry — `hesreallyhim/awesome-claude-code` (issue form, **never a PR**)

Their style rules: single line, no emoji, objective statement, do not address the reader, do not
write a sales pitch.

> Generates a governed repository — agent contract, ADRs, CI gates, and SemVer rules — from a
> single manifest for 19 language toolchains, and ships slash commands for a six-phase delivery
> pipeline from RFC to release.

Submit via the *Recommend a resource* issue template. License (MIT) is discovered automatically.

### 1c. Entry — `jqueryscript/awesome-claude-code` (PR)

Category: *Agents & Orchestration*.

```markdown
- [EADOS](https://github.com/danielPoloWork/pgs-eados) - Language-agnostic delivery OS that generates a governed repo (agent contract, ADRs, CI gates, SemVer) for 19 toolchains and enforces it with 16 lint gates.
```

---

## 2. The article — dev.to / Hashnode

This is the highest-leverage asset in Wave 1: evergreen, indexable, and it is the only one that
demonstrates competence rather than asserting it. **Publish the article before the list
submissions**, so a curator following the link finds a project with a story attached.

**Title:** *My AI agent filed an issue. Then it proved itself wrong.*

---

Six weeks ago I started an experiment: could an AI coding agent run a real delivery pipeline — not
autocomplete, not "write me a function," but the whole thing? RFCs, architecture decision records,
CI gates, semantic versioning, release notes.

Eighteen releases later, here is the moment that convinced me the contract matters more than the
model.

### The issue

The agent filed issue #372 against my own project. The summary: a generated repository tracks its
`.claude/commands/` adapter files in git, but ignores the rest of the factory tooling, and nothing
documents why. The recommendation was to write down the reasoning and keep tracking the adapters.

Reasonable. I would have merged that.

### What the gate found

Before the fix shipped, the render smoke test ran against a real generated repository — not a
fixture, the actual rendered output. The tracked adapter turned out to be a **dangling pointer**:
the committed file names a path that the same `.gitignore` excludes.

Anyone cloning that repository would get slash commands resolving to a missing file. That is worse
than absence. An absent command is obviously absent; a dangling one fails at the point of use and
reads as a broken repo.

The pull request that shipped **reversed the recommendation the issue had been filed with**.

### Why that is the interesting part

The agent was not wrong because it was a weak model. It was wrong because it reasoned from the
repository *as documented*, and the repository *as rendered* disagreed.

No amount of prompt engineering finds that. A test that renders the real thing finds it in eight
seconds.

That is the whole thesis. **An agent's failure mode is confident, internally consistent, and
locally reasonable.** You do not catch it by asking it to be more careful. You catch it by making
the ground truth executable.

### What "a contract" actually means

Not a longer system prompt. A set of rules that fail a build:

- **version-lockstep** — the release badge in the README must equal the latest release in the
  CHANGELOG. Three READMEs, three languages. It has caught drift more than once.
- **i18n-freshness** — every translation pins the SHA-256 content hash of the English source it was
  made from. Edit the English, both translations go stale and CI goes red. Content-based rather
  than commit-based, so a squash merge cannot orphan the record.
- **gate-coverage** — a meta-gate. Every externally-modifiable class of file must be claimed by
  some gate, and the build fails if one is not.

That last one is load-bearing, and it is the idea I would keep if I had to throw the rest away:
**the honest failure mode of a gate system is not a gate that fails — it is a class of file that
nobody gated.** A gate that fails is loud. A hole is silent, and it stays silent for months.

### The part people ask about

The agent drafts. A human merges. Always. Not because the agent cannot be trusted with a merge
button, but because someone has to be accountable, and accountability does not survive being
delegated to a process that cannot be called into a meeting.

### If you want to try it

EADOS is MIT, standard-library Python, and installs into an existing repository additively — it
never overwrites a file you already have.

<!-- link to the repo here -->

---

## 3. LinkedIn

Post the article first, then link it. Italian first (the existing network), English a few days
later.

### 3a. Italian

> Sei settimane fa mi sono chiesto una cosa: un agente AI può reggere una pipeline di delivery
> vera? Non l'autocomplete — RFC, ADR, gate di CI, versionamento semantico, note di rilascio.
>
> Diciotto release dopo, il momento che mi ha convinto non è stato uno in cui l'agente ha fatto
> qualcosa di brillante. È stato quello in cui si è smentito da solo.
>
> Aveva aperto una issue sul mio progetto e proposto una soluzione. Ragionevole: l'avrei mergiata.
> Poi un test ha girato contro un repository realmente generato, e ha mostrato che quella soluzione
> produceva un puntatore rotto. La PR che è arrivata in fondo **ha ribaltato la raccomandazione con
> cui la issue era stata aperta.**
>
> Il punto non è che il modello fosse debole. È che aveva ragionato sul repository *come
> documentato*, mentre il repository *come generato* diceva un'altra cosa. Nessun prompt migliore
> trova quella differenza. Un test che genera la cosa vera la trova in otto secondi.
>
> La modalità di errore di un agente è sicura di sé, internamente coerente e localmente sensata.
> Non la correggi chiedendogli di stare più attento. La correggi rendendo eseguibile la verità.
>
> Ho scritto qui cosa significa in pratica dare un contratto a un agente invece di un prompt 👇

### 3b. English

> Six weeks ago I asked whether an AI coding agent could run a real delivery pipeline — RFCs, ADRs,
> CI gates, SemVer, release notes. Not autocomplete.
>
> Eighteen releases later, the moment that convinced me wasn't the agent doing something clever. It
> was the agent proving itself wrong.
>
> It filed an issue on my project and proposed a fix. Reasonable — I'd have merged it. Then a test
> ran against a really-generated repository and showed the fix produced a dangling pointer. The PR
> that shipped reversed the recommendation the issue was filed with.
>
> The model wasn't weak. It reasoned from the repo *as documented*, while the repo *as rendered*
> disagreed. No prompt finds that gap. A test that renders the real thing finds it in eight seconds.
>
> An agent's failure mode is confident, internally consistent, and locally reasonable. You don't fix
> that by asking it to be more careful. You fix it by making ground truth executable.
>
> Wrote up what giving an agent a contract instead of a prompt actually looks like 👇

---

## 4. The warm list — three people, all of them real

This is the entire set of humans who have ever engaged. It is small enough to write to
individually, which is exactly why it should be.

| Who | Relationship | Note |
|---|---|---|
| [@AlexMnrs](https://github.com/AlexMnrs) | Forked 2026-06-27. Authored the closed PR #96 that inspired M9's installer; accepted the co-author credit. | Warmest contact we have. |
| [@gxuxhxm](https://github.com/gxuxhxm) | Forked 2026-06-27, still pushing 2026-06-28. Co-author on the in-house re-implementation behind #101. | Second warmest. |
| [@cedendahlkim](https://github.com/cedendahlkim) | **The only stranger who has ever starred the repo.** No other interaction. | Unknown; treat gently. |

**Channel:** a comment on the issue/PR they already participated in, not a cold DM. For
@cedendahlkim there is no such thread — either leave them alone or wait until there is a release
worth announcing. Recommendation: **leave them alone.** One star is not consent to be contacted.

### Draft — @AlexMnrs (comment on #96)

> Hi Alex — following up on this one. The installer you proposed shipped in M9 and has been in
> every release since, with your co-author credit on it. EADOS has moved a fair way past that
> point: six phases now, 19 language profiles, 16 lint gates.
>
> No ask attached. You are one of the few people who has actually looked at this thing, so if you
> ever run it on something real I would genuinely want to hear where it broke. That is worth more
> to me right now than a star.

### Draft — @gxuxhxm (comment on the #101 thread)

> Hi — the manifest-template check you co-authored is still in the lint, and it has grown neighbours:
> 16 gates now, including a meta-gate that fails the build when a class of file is not covered by
> any gate at all.
>
> If you still have that fork lying around and ever point it at a real project, I would like to know
> what broke. Field reports are the thing this project is short of, not features.

---

## 5. Sequencing

| # | Action | Depends on | Owner's click needed |
|---|---|---|---|
| 1 | Publish the dev.to article | — | Yes — publishes public content |
| 2 | LinkedIn IT, linking the article | 1 | Yes |
| 3 | PR to `awesome-spec-driven-development` | 1 | Yes — PR under his identity on a third-party repo |
| 4 | Issue form to `hesreallyhim/awesome-claude-code` | 1 | Yes |
| 5 | Comments to @AlexMnrs and @gxuxhxm | — | Yes — messages on his behalf |
| 6 | LinkedIn EN | 2 (+3 days) | Yes |
| 7 | PR to `jqueryscript/awesome-claude-code` | 3 | Yes |

Spread over ~2 weeks. Do not do 3 and 4 on the same day as 1 — a curator who arrives at a repo whose
article went live an hour ago sees a marketing push, not a project.

**Measure at day 14, not day 2.** The only numbers that matter: unique visitors, count of distinct
external referrers, and how many humans ran it and said something. Ignore the download counter — it
still includes our own release verification.

## 6. The gate on Wave 2

Show HN and Reddit are effectively one-shot per project, and both are currently **blocked on the
demo recording**. The README headline now promises that something is *prevented*; the 90-second
recording ending on a deliberate violation and the gate firing red is what turns that from a claim
into a demonstration. Front-paging the claim without the proof spends the one shot on the weakest
version of the pitch.
