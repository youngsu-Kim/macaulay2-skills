--- name: macaulay2 description: >- Write, fix, and verify Macaulay2 (M2) code and read its output: polynomial rings and ideals, Groebner bases, free resolutions, Betti tables, Hilbert series and polynomials, primary decomposition, packages. Use whenever a task involves Macaulay2 or an M2 kernel/MCP tool (m2_evaluate, iN:/oN= prompts, "no method for adjacent objects" errors, betti tables), even when the user only describes the algebra in words or LaTeX. ---

# Macaulay2 core skill

Version-pinned knowledge for **Macaulay2 1.26**. Every rule below was checked against a real kernel; `references/index.tsv`, `toc.md`, and `packages.md` are generated from the docs trees shipped inside the same pinned install — core plus the packages loaded by default (see the provenance headers). If your kernel reports a different version, prefer its own `m2_help`.

## 1. Lookup ladder — do this BEFORE guessing a function name

M2 errors from a wrong name are misleading; guessing burns many turns. In order:

1. Rules and references in this skill.
2. **Check the name exists**: `grep -E '^NAME' references/index.tsv` (columns: `symbol <TAB> blurb <TAB> page <TAB> source-package`). Use a PREFIX match, not exact: many symbols have only signature rows (`saturate(Ideal,Ideal)`, `factor(RingElement)`…) — 78+ bases on 1.26. The index covers core **plus the 21 default-loaded packages** (trap #11). A miss means the name is SUSPECT, not dead: pure aliases (`res`) and symbols inside multi-topic pages get no row.
3. **`m2_help topic`** (when available through the macaulay2-mcp server) — resolves real kernel bindings, aliases included, against the same pinned corpus (`m2_help "res"` → documents `freeResolution`).
4. Full page: `$PREFIX/share/doc/Macaulay2/<PKG>/html/<page>` — `<PKG>` is the 4th column; macaulay2.com serves the same paths.

Worked example of trap #2 below: `grep -E '^reduce' references/index.tsv` → no relevant rows, and `m2_help "reduceGb"` finds nothing ⇒ `reduceGb` does not exist ⇒ you already have the reduced basis from `generators gb I`. Contrast: `grep -E '^saturate' index.tsv` hits 21 signature rows (package: Saturation) ⇒ real, and no loadPackage needed — it is ⚡ default-loaded.

## 2. Statements and output discipline

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
print (I == ideal(x^3 - y, x^4 - z))
-- expect: true
```

- Separate statements with **newlines, not semicolons**. A trailing `;` SUPPRESSES that statement's displayed result (`x + 1;` computes, prints nothing). In batch/script runs, only some things print at all — prefer explicit `print`.
- `print` takes ONE expression: `print (a, b)` sequences them. `print a | b` parses as `(print a) | b`. Strings concatenate with `|`, and use **double quotes** (single quotes are invalid).
- `A; B` on one line shows only `B`.
- **Shared kernel hygiene:** the kernel is one global namespace. If other agents/sessions may share it, prefix YOUR definitions (`my_R = QQ[x,y,z]` — at most one underscore, see trap #18) AND your ring variable names (trap #15), and never call `session_reset`/`interrupt` — build each task self-contained in one call.
- **Syntax errors are kernel-fatal:** a parse error (e.g. using a reserved word like `in` as a variable) can restart the kernel with TOTAL state loss — unlike runtime errors (trap #6 survives). After any syntax error or if a name suddenly behaves like an unbound `IndexedVariable`, assume a fresh kernel and re-send the whole self-contained block.

## 3. The traps that cost models the most turns

*(Each demo block is self-contained — `verify.py` runs it in a fresh kernel. If you type them CONSECUTIVELY in one live session, remember trap #15: a later `QQ[w,x,y,z]` rebinds `x,y,z`; give each ring distinct variable names.)*

| # | Trap | Reality (verified on 1.26) |
|---|------|----------------------------|
| 1 | `gb I` | returns a **GroebnerBasis object**; to SEE the polynomials: `generators (gb I)` (synonym `gens`). They are **already sorted and auto-reduced** — there is NO `reduceGb`. |
| 2 | error `no method for adjacent objects: NAME (of class Symbol)` | means NAME itself is unknown/juxtaposed — the **name**, not the spacing, is wrong. Reformatting the call never fixes it; grep the index instead. |
| 3 | `dim S/I` | parses as `(dim S)/I` → error. Quotients need parens: `dim (S/I)`, `degree (S/I)`. Both `dim` and `degree` also accept the **ideal directly**: `degree I` ✓ (verified). |
| 4 | `res (R/I)` | classic mistake — `res` (freeResolution) takes **ideals/modules/maps**, not quotient rings: use `res I`. (`hilbertPolynomial (S/I)` however DOES take the quotient.) |
| 5 | assigning to `gb`, `res`, `betti`, `ideal`, … | `error: assignment to protected global variable` — pick another name. |
| 6 | a line failed halfway | the kernel is a REPL: **no rollback**. Earlier statements already took effect (`x = 2` on a failing line still leaves `x = 2`). Fix forward; `:=` scopes per-iteration locals in loops: `for k from 1 to 5 list (J := ideal(...); <expr>)`. |
| 7 | name now holds a value | `x = symbol x` restores the bare symbol. Note expressions captured values at assignment time. |
| 8 | graded invariants (`betti` degrees, `hilbertSeries`) | require a **homogeneous** ideal; non-homogeneous input gives misleading or failed output. |
| 9 | `loadPackage "P"` answers "not reloaded; try Reload => true" | P is **already loaded** — just use it. Force-reloading is fragile (breaks on packages with `needsPackage` dependencies). |
| 10 | batch scripts: one unresolved symbol | poisons the whole script's `User` package: you ALSO get `mutable unexported unset symbol(s) in package User: 'T'` noise. The FIRST error line is the real signal. |
| 11 | "I must loadPackage first" | **21 packages are loaded at startup** (⚡ in `packages.md`): PrimaryDecomposition, Saturation, Elimination, IntegralClosure, MinimalPrimes, TangentCone, ReesAlgebra, InverseSystems, LLLBases, Polyhedra, Varieties, Truncations, Complexes, PushForward, Classic, ConwayPolynomials, Isomorphism, SimpleDoc, OnlineLookup, PackageCitations (+Core). `primaryDecomposition`, `saturate`, `integralClosure`, `tangentCone`, `minimalPrimes` … work in a FRESH session — do not load them. Introspect: `#loadedPackages` (it's a List — NO parens). |
| 12 | trusting a doc blurb/signature | signatures UNDER-describe: `isPrime` blurbs "integer or polynomial" but `isPrime(Ideal)` works (verified `true`). They also OVER-imply: `height` is indexed yet `height(Ideal)` has NO method (verified error) — compute `dim R - dim (R/I)`. Docs describe titles, not dispatch tables; the kernel is the arbiter. |
| 13 | `degree` on a NON-homogeneous ideal | does NOT fail — it silently returns `degree S/(in I)`, so the MONOMIAL ORDER changes the answer: `ideal(v+u^2)` has degree **1 under Lex**, **2 under GRevLex** (both verified). Only degree-compatible orders (the default GRevLex) make that equal the projective-closure degree. `hilbertPolynomial`/`hilbertSeries` hard-reject instead (`expected a homogeneous module`). Honest closure degree: homogenize first (trap #14). |
| 14 | `homogenize(f, w)` errors | "homogenization requires variable in the same ring" — `sub` the element/ideal into the bigger ring FIRST: `homogenize(sub(f, S), w)` (verified). `sub(Ideal, Ring)` also works; RingMap forms failed in benchmarks — prefer `sub(_, Ring)` or `{var => expr}` substitution lists. |
| 15 | building a second ring `QQ[w,x,y,z]` | **rebinds the global symbols x,y,z** into the new ring — objects created earlier still live in the old ring, so later mixed expressions fail confusingly (though `==` on corresponding elements works, verified). Use distinct variable names per ring (`QQ[my_x, my_y]`), especially on shared kernels. Related parse trap: `sub(f, w => 1) == g` swallows `==` into the options pair — assign the `sub` result first. |
| 16 | `depth`/`isCM` for commutative algebra | core `depth` is about Net/String RENDERING — `depth(Ideal)`, `depth(Module)`, and quotient-ring forms have NO method until **`loadPackage "Depth"`** (NOT default-loaded; both states verified). `pdim` IS core. Package-free CM certificate: Auslander–Buchsbaum — see resolutions.md worked block. |
| 17 | bare `hilbertPolynomial (S/I)` prints `- 2*P_0 + 3*P_1` | that is the **class form** (ProjectiveHilbertPolynomial): `P_j` = class of a codimension-`j` linear subspace; for a curve substitute `P_0=1`, `P_1=i+1` ⇒ `3i+1`. Don't hand-parse — for numbers use `hilbertPolynomial(S/I, Projective => false)` or `reduceHilbert hilbertSeries (S/I)` (both verified): |

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (hilbertPolynomial (S/C))
print (reduceHilbert hilbertSeries (S/C))
-- expect: + 3*P
-- expect: 1 + 2T
```

| 18 | underscore in names (shared-kernel prefixes!) | `_` is M2's SUBSCRIPT operator: `med_R` is a legal indexed assignment, but chained `sg_ds_S` parses as a subscript/juxtaposition mess → `error: no method for assignment to binary operator _`. Prefix rule: ONE underscore max, plain segments (`kb_R`, `mmS`), and never embed reserved words as segments (`xh_in`). |

```m2
sg_ds_S = QQ[a,b]
-- expect-error: binary operator _
```

Demo of traps 1–3 (note the exact error shapes):

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
print (generators gb I)
-- expect: | xy-z x2z-y2 y3-xz2 x3-y |
```

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
print (reduceGb I)
-- expect-error: no method for adjacent objects
```

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (dim S/C)
-- expect-error: no method for binary operator /
```

Demo of traps 11–12 — default-loaded power, and blurbs that lie both ways:

```m2
print (#loadedPackages)
R = QQ[x,y,z]
print (isPrime ideal(x^2 + y^2 - z^2))
-- expect: 21
-- expect: true
```

Trap #13's order-sensitivity, in four lines (note how defining `RG` rebinds `v,u` mid-script — trap #15 in action; each ideal was created under the intended order):

```m2
RL = QQ[v,u, MonomialOrder => Lex]
IL = ideal(v + u^2)
RG = QQ[v,u]
IG = ideal(v + u^2)
print (degree IL, degree IG)
-- expect: (1, 2)
```

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
height I
-- expect-error: applying height
```

## 4. Cross-check culture (cheap and high-value)

A second, independent route beats trusting one command:

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
J = ideal apply(flatten entries gens gb I, p -> p)
print (J == I)
-- expect: true
```

For a resolution: the Betti totals must agree with `(dim, degree)` and the Hilbert polynomial — see `references/resolutions.md` (worked twisted-cubic example with all three cross-checked).

## 5. Map of this skill

| File | Content |
|------|---------|
| `references/index.tsv` | 5.7k rows: core + ⚡ default-loaded packages → blurb → page → package (**prefix-grep `^NAME`**) |
| `references/toc.md` | thematic outline of the whole 1.26 core docs |
| `references/packages.md` | all 299 bundled packages by theme, ⚡ = default-loaded, ⭐ = refereed |
| `references/groebner.md` | bases, orders, elimination, membership |
| `references/resolutions.md` | `res`/`betti` reading, Hilbert series/polynomial |
| `references/debugging.md` | error-message taxonomy with repro blocks |

Per-package deep-dives live in sibling skills (`macaulay2-<name>`) generated from each package's own pinned docs.

## 6. Companion server

This skill pairs with the **macaulay2-mcp** MCP server (persistent 1.26 kernel, `m2_help`, memory line after every evaluation, OS-call gate). The skill is useful with any M2 access path; the lookup ladder's rung 3 only exists there.
