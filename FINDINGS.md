# Findings log

How this skill's claims came to be true, and what the process keeps catching. Every finding below was produced by running things against **Macaulay2 1.26.06** (Homebrew, arm64) — never inferred from docs alone. Dates included because everything here is version-pinned and must be re-checked on a version bump.

## 2026-10-11 — Benchmark: skill × thinking level (wave 1, skill v1)

Three example prompts from the macaulay2-mcp README, executed by `nrp/qwen3` subagents with thinking levels off/false→xhigh; metric = `m2_evaluate` calls to a correct, matched answer (protocol footnotes at bottom).

| Configuration | Task 1 | Task 2 | Task 3 | Total | Errors |
|---|---|---|---|---|---|
| no skill, `#false` (baseline) | 11 | 5 | 6 | **22** | 8 error/retry events |
| skill, `#false` | 2 | 2 | 3 | **7** | 0 |
| skill, `#low` | 2 | 2 | 4 | **8** | 0 |
| skill, `#medium` | 2 | 3 | 2 | **7** | 1 (`height(Ideal)` — skill gap then) |
| skill, `#xhigh` | 2 | 2 | 2 | **6** | 0 |

**Headline:** with the skill, thinking level barely matters (6–8 calls at every level vs ~22 without it at the bottom). Knowledge substitutes for reasoning. Thinking showed up in style: `#xhigh` over-verified (independent UFD primality argument), `#medium` self-repaired its one error in a single retry, `#false`/`#low` just executed the ladder. All cells matched ground truth on all three tasks.

Caveats: (1) the skill contains the literal Task-1 ideal and the Task-3 twisted cubic (resolutions.md worked example) — that flatters these numbers; the honest post-push test is unseen tasks. (2) `#false`/`#low` used per-task kernel resets; `#medium`/`#xhigh` ran **concurrently** on the shared kernel with `med_`/`xh_`-namespaced definitions and no resets.

## 2026-10-11 — Rerun after skill v2 (default-loaded index + fixed ladder)

Same protocol, same four levels, skill at commit 005b009 + post-audit tweaks:

| Configuration | Task 1 | Task 2 | Task 3 | Total | Errors |
|---|---|---|---|---|---|
| skill v2, `#false` | 2 | 1 | 2 | **5** | 0 |
| skill v2, `#low` | 1 | 1 | 1 | **3** | 0 |
| skill v2, `#medium` (concurrent) | 2 | 1 | 2 | **5** | 0 |
| skill v2, `#xhigh` (concurrent) | 2 | 3 | 3 | **8** | 0 |

What changed and why it's attributable:

- **Grid-wide errors: 1 → 0.** `#medium`'s wave-1 failure (`height(Ideal)`) is now trap #12's verified row; it never fired.
- **The ladder got used, not just read.** `#low` grepped `isPrime` on rung 2, found only option-signature rows (`isPrime(Ideal,Strategy=>…)` from ⚡ MinimalPrimes), reasoned via traps #11/#12, and called `isPrime(J)` confidently. `#xhigh` prefix-grepped 14 names in ONE shell call before any kernel call, confirmed `reduceGb` absent and correctly interpreted `res`'s absence as documented alias behavior (rung 3 not even needed).
- **New cross-checks propagated:** `#false` ran the `hilbertSeries` closure added in v2 without being told to; `#xhigh` invented its own extra triangle (gb length = numgens; primaryDecomposition as an independent primality route) — the culture transferred, which is the point.
- `#xhigh`'s 8 vs `#low`'s 3 is deliberate verification breadth at equal correctness, not friction. Grid total 28 → 21 calls; no-skill baseline was 22 calls WITH 8 errors at the bottom level alone.

Agent-filed refinements applied post-run: full-row `expect` rendering in the trap demo (a truncated expect read as output truncation), `dim`/`degree` accepting ideals stated in trap #3, and a shared-kernel naming-hygiene bullet in §2 (the benchmark itself proved multi-session clobbering is real).

## 2026-10-11 — Wave 3: involved tasks (transfer test, zero overlap with skill examples)

Three harder tasks, none present in the skill: (T1) non-homogeneous affine quadric: primality, dim of coordinate ring, degree of projective closure + "can raw `degree J` be trusted?"; (T2) skew-planes union `I=(x,y)∩(z,w)`: generators, dim/degree, Betti table, depth, CM verdict; (T3) implicitize `(s, st, t²)` by elimination + primality/dimension/homogeneity. Four levels concurrent (prefix-namespaced, no resets).

| level | T1 | T2 | T3 | Total | All correct? |
|---|---|---|---|---|---|
| `#false` | 13 | 15 | 6 | **36** | ✅ — found the Lex counterexample unaided |
| `#low` | 7 | 1* | 9 | **17** | ✅ |
| `#medium` | 8 | 1 | 2 | **11** | ✅ |
| `#xhigh` | 5 | 5 | 1 | **11** | ✅ |

*`#low`'s one-call T2 rode on a concurrent neighbor's `loadPackage "Depth"` — shared-kernel side effect, flagged as a protocol artifact.

Difficulty scaled 3–4× and correctness held at every level; costs concentrated in a NEW gap cluster, all independently reported by ≥2 agents and all verified by author probes in fresh processes before shipping as skill content:

1. **`degree` on non-homogeneous ideals = degree of `S/(in I)`** — order- sensitive: `ideal(v+u²)` → **1 (Lex) vs 2 (GRevLex)**. GRevLex (default) happens to equal the closure degree; Lex breaks it. → trap #13 + demo block.
2. **`depth`/`isCM` gated behind `loadPackage "Depth"`** (core `depth` is the Net/String rendering depth!); `pdim` is core (fresh process → 3). → trap #16 + resolutions.md worked CM block.
3. **Ring construction rebinds variable symbols globally**; `homogenize` needs `sub(f, S)` first ("homogenization requires variable in the same ring"). → traps #14/#15 + demo block.
4. **Syntax errors are kernel-fatal** (restart, total state loss) vs runtime errors (trap #6 survives); reserved words (`in`) can't be variables ("syntax error at 'in'"); post-restart ghosts read as `IndexedVariable`. → §2 bullet.
5. **Betti rows are labelled j−i**, not raw internal degree (the skew-planes quadrics print on row `1:`). → resolutions.md fix.
6. **`sub(f, w => 1) == g` parse trap**: `==` is absorbed into the options pair ("expected pair to have a method for '=='") — NOT a cross-ring failure; plain `f == sub(f, S)` returns `true` (author probe corrected the agent's over-claim). → debugging row.
7. `factor(Ideal)` has no method (RingElement only). → debugging row.

Process note: two agent claims were WRONG and caught by verification-before- writing (cross-ring `==` fatalism; `#medium`'s single-call `depth (A/I)` only worked thanks to neighbor contamination). The discipline — reproduce in a fresh process before it becomes skill text — is load-bearing.

## 2026-10-12 — Wave 5: cross-model generalization + Segre re-run

Correction first: a session summary before this wave claimed a "wave 4" (4 thinking levels + Segre task) whose results were "recorded in FINDINGS.md and pushed." Git and the file disprove both — no such record or commit ever existed. Lesson logged: session-summarized results are NOT data; only in-message transcripts + commits are. The wave-4 tasks were re-run fresh below; nothing unverifiable is recorded.

Setup: skill installed PRODUCTION-PATH via `npx skills add youngsu-Kim/macaulay2-skills -g` (lands in ~/.agents/skills/macaulay2). Tasks = the three Introduction prompts; cells = 6 models across 5 families.

| Cell | Model | Skill access | Calls | Kernel errors | Subanswers |
|---|---|---|---|---|---|
| ref | qwen3#false | pointer | 5 | 0 | 3/3 |
| A | qwen3-small#false | pointer | 3 | 0 | 3/3 |
| B | deepseek-v4-flash#false | pointer | 3 | 0 | 3/3 |
| C | gpt-oss#low | pointer | 3 | 0 | 2/3 + 1 partial |
| D | glm-5#low | pointer | 3 | 0 | 3/3 |
| E | minimax-m2 | pointer | — | — | infra: agent died twice, no data |
| G | kimi | AUTO (no pointer) | 4 | 0 | 3/3 |
| F | qwen3-small#false | AUTO (accidental) | 3 | 0 | 3/3 |

Segre re-run (never-in-skill task; 2×2 minors of a generic 2×3 matrix — ground truth from fresh probes: betti 1 3 2, dim 4, degree 3, CM via Depth-package depth=4=dim AND package-free AB, prime):

| Cell | Model | Calls | All four subanswers |
|---|---|---|---|
| — | deepseek-v4-flash#false | 5 | ✅ incl. CM double-certificate |
| — | qwen3-small#false | 3 | ✅ |
| — | kimi (auto-discovered skill) | 2 | ✅ |

**True no-skill control (F2), after temporarily removing the global install:** `qwen3-small#false`, identical prompt to the original wave-1 baseline: **21 calls** (T1: 2, T2: 2, T3: **17**) with 6+ error events, five failed strategies to decode the `-2*P₀ + 3*P₁` class form (the exact trap-#17 display) until `m2_help` found `HP(k)`, one syntax error that forced a kernel restart, and a full self-contained re-run — yet all three answers eventually correct. Two conclusions: (1) the with-skill 3–5 calls figure is real, not a control artifact — F2's 21 nearly reproduces qwen3#false's baseline 22 across a model swap; (2) the removal/reinstall round-trip confirmed the harness's skill listing updates live, so earlier F-cell contamination was genuine auto-discovery, not cache. Bonus harvest from F2's marathon (recorded for a future patch, NOT yet in the skill): `HP(k)` evaluates the class form at integer k; `list entries HP` is a SYNTAX error (unbalanced `list` usage) — kernel-fatal per §2.

Findings:

1. **Generalization holds:** 3–5 calls, zero kernel errors on every model/family that produced data — vs 22 calls / 8 errors for the no-skill baseline. The "knowledge substitutes for reasoning" claim is no longer qwen3-specific.
2. **Auto-discovery works (twice):** kimi (cell G, deliberate) and qwen3-small (cell F, accidental — my "control" leaked because the globally installed skill enters every fresh session's listing). The frontmatter description is a functioning trigger. True no-skill controls on this machine now require removing the install first.
3. **C's partial = new trap #17:** gpt-oss#low read bare `hilbertPolynomial(S/C)` class-form output `-2*P_0 + 3*P_1` as "does not match 3i+1" and gave up; kimi decoded the same display correctly and deepseek avoided it via Projective=>false. Trap #17 (class-form reading + the two number-producing idioms) added with verified blocks.
4. **My OWN concurrency convention was a trap (new trap #18):** prompts prescribed prefixes like `sg_ds_`; in M2 `_` is the SUBSCRIPT operator — `med_R` (single underscore) is a legal indexed assignment, chained `sg_ds_S` dies with `no method for assignment to binary operator _`. Two of three Segre agents burned a call on it (their transcripts also show self-recovery in one retry, which is the intended ladder behavior). Skill now prescribes ONE-underscore prefixes and flags reserved-word segments.
5. One agent (qwen3-small) proposed that trap #15 is wrong because "rings are per-connection" — REJECTED: that contradicts wave-3's reproduced rebind/cross-ring errors and this harness's documented shared kernel. Recorded here as an agent over-claim caught by the reproduce-before-recording rule (third instance of that rule paying for itself).

## 2026-10-22 — Announcement-day spot checks + trap #19 + style guide

Zulip announcement posted (Package stream, topic "mcp"). Four live checks the same evening, all green: `uvx macaulay2-mcp --version` → 0.1.4; the URL-only skill prompt (README "Or Input", deepseek-v4-flash#false) → correct basis + J == I cross-check; server smoke test reproducing the README's pinned Example-1 values; and a pure-LaTeX prompt — a NEW problem, not in the skill:

Let I = (x^2 + y^2 - 1, xy - 1) in Q[x,y]. Compute a Groebner basis, decide whether I is radical, and determine the number of solutions over C.

Ground truth (author-pinned before the run): basis {xy-1, x^2+y^2-1, y^3+x-y}, dim 0 degree 4, and the subtlety — I is PRIME over Q (x^4-x^2+1 = Φ12 is irreducible, so the quotient is a field) while its variety splits into 4 conjugate C-points. The deepseek#false agent got all three answers correct, used the right radicality idiom unprompted, and identified Φ12. One micro-inaccuracy: claimed "lex order" for a default-GRevLex computation (the bases coincide here) — models may embellish method while the math holds.

Harvest from that test → **trap #19**: `isRadical` does not exist in M2 (0 index rows); the working idiom is `radical I == I`. Shipped with verified blocks (the Φ12 example doubles as the prime-over-Q lesson).

Also added: `references/package-writing.md` — the official M2 wiki Package-Writing-Style-Guide distilled for agents (naming, package code behavior, doc nodes, JSAG prose) with three kernel-verified idiom blocks (`QQ(monoid[getSymbol "a"])`, `instance` vs `class ===` inheritance demo, `getSymbol`). The skill's FIRST non-pinned source, labeled as such: the wiki is a living document, so that page is conventions, not version-pinned behavior. Per the author's new policy, both repos now carry a Sources section and only publicly available material is incorporated.

## 2026-10-11 — The documentation is authoritative but gappy (five classes)

Discovered by benchmark agents + author probing. Ordered by how badly they mislead a model that trusts them.

1. **The index keys on PAGE TITLES, not symbols.** `master.html` has no row for `res` (an alias), `freeResolution` (documented inside the multi-topic page "Hilbert functions and free resolutions"), or `monomialOrder`. ⇒ A "not in index ⇒ doesn't exist" rule is WRONG; a miss means *suspect*. `m2_help "res"` resolves it (kernel-level alias → freeResolution docs).
2. **Blurbs/signatures UNDER-describe.** `isPrime` blurbs "integer or polynomial", yet `isPrime(Ideal)` → `true` (three agents proved it live). The 1.26 docs also simply omit the existence of `isPrime(Ideal)`.
3. **Blurbs OVER-imply.** `height` is indexed ("height of an object") but `height(Ideal)` has no method — compute `dim R - dim (R/I)`.
4. **The core index has the WRONG SCOPE (the big one).** Macaulay2 loads 21   packages at startup (runtime-detected): Core, Classic, Complexes, ConwayPolynomials, Elimination, IntegralClosure, InverseSystems, Isomorphism, LLLBases, MinimalPrimes, OnlineLookup, PackageCitations, Polyhedra, PrimaryDecomposition, PushForward, ReesAlgebra, Saturation, SimpleDoc, TangentCone, Truncations, Varieties. `primaryDecomposition`, `saturate`, `integralClosure`, `minimalPrimes`, `tangentCone` all **work in a fresh session** yet had **zero rows** in a core-only index. ⇒ `index.tsv` now merges core + all default-loaded package trees (4,424 → 5,704 rows, column 4 = providing package). Related: 78+ symbols have ONLY signature rows (`saturate(Ideal,Ideal)`, `factor(RingElement)`…) ⇒ **prefix-grep `^name`, never exact-match**.
5. *(added after wave 3)* **MECHANISM gaps** — the function exists and succeeds, but returns something other than what its name promises: non-homogeneous `degree` = initial-ideal degree (order-sensitive), core `depth` = rendering depth, `homogenize` scope, Betti row = j−i. Docs describe these only in mid-page prose unreachable by title-indexing. See the wave-3 section; traps #13–#16 carry the fixes.

## 2026-10-11 — Kernel-vs-docs truths (Tier B: no doc states these)

- `gb = 5` → `assignment to protected global variable 'gb'` (exact text).
- Batch (script) mode **halts after unresolved-symbol errors** and adds confusing `mutable unexported unset symbol(s) in package User: 'T'` noise; piped-REPL mode **continues** (verified both). First error = real signal.
- `generators (gb I)` = *sorted, auto-reduced* basis (docs: `gb` page) — but the misleading part is that `print (gb I)` shows only `GroebnerBasis[status: done; ...]`, no polynomials.
- `loadedPackages` (List, parenless) vs `installedPackages()` (function, usually `{}`) — opposite shapes; Package objects have no `.name` and no sort method (`?` operator error). Idiom: `for p in loadedPackages list toString p`.
- `print sort (...)` is a dangling-operator continuation — keep `print (…)` parenthesized (author tripped; SKILL.md §2 rule).
- `dim S/I` parses as `(dim S)/I` → `no method for binary operator /` (reproduced verbatim in three independent runs).
- `x = 2` on a line that later fails still leaves `x = 2` (no rollback — REPL semantics that every error-recovery strategy depends on).

## Verification caught the skill author, too

During first authoring `verify.py` failed 3/26 blocks:
- `x^5 % (ideal(x^3-y, x^4-z)) == 0` — FALSE (x^5 ≡ x²y). Author algebra bug.
- `keys installedPackages()` — installedPackages() is a List, not HashTable.
- `hilbertSeries(S/C, Reduce=>true)` renders `(1+2T)/(1−T)²` multi-line ASCII, not the raw resolution numerator — the reduction identity `1−3T²+2T³ = (1−T)²(1+2T)` became a better cross-check lesson.

## Known residual gaps (deliberate, documented)

- Alias-only symbols (`res`) still have no index row by construction (master.html limitation; fixed upstream would be better). Ladder rung 3 (`m2_help`) is the designed backstop, and its wording now says so.
- Per-package `toc.md`s not merged (core toc only); wave-2 per-package skills carry their own.
- "21 default-loaded" is pinned to this build (header provenance records the runtime-detected list). CI on other builds should regenerate first.

## Reproduction

```sh
python3 tools/mk_skill.py   # regenerates artifacts incl. runtime default-load list
python3 tools/verify.py     # executes every ```m2 block (26 → 32 → 36 blocks across the three waves, 36/36 passing)
```
The four-way benchmark protocol: subagent (model variant `nrp/qwen3#<level>`)
+ skill-first prompt + the three README prompts + per-task reset (or namespaced concurrency), counting `m2_evaluate` calls. See git history of this file for each wave's numbers.
