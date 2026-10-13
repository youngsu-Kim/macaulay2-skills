# Debugging Macaulay2 1.26 — error taxonomy

Match the message, believe the FIRST error, act per the right column. Every block below reproduces its row on a real 1.26 kernel.

| Message (look at this) | Real meaning | Fix |
|---|---|---|
| `no method for adjacent objects: NAME (of class Symbol)` + `SPACE ...` | NAME isn't a known function (or you juxtaposed something impossible). **Not a spacing problem.** | grep `references/index.tsv`; rethink approach |
| `no method found for applying freeResolution to: ... (of class QuotientRing)` | you wrote `res (R/I)` | `res I` |
| `no method for binary operator / applied to objects: 4 (of class ZZ) / ideal ...` | `dim S/I` parsed as `(dim S)/I` | parenthesize: `dim (S/I)` |
| `assignment to protected global variable 'gb'` | NAME collides with a builtin | rename your variable |
| `mutable unexported unset symbol(s) in package User: 'T', ...` (batch runs) | downstream pollution AFTER an unresolved-symbol error | ignore; scroll up to the FIRST error |
| `expected argument N to be a list, sequence, or iterable object` | passed a non-list (often a Symbol left over from a failed assignment) | check what the name currently holds: `class x` |
| `no method for binary operator ? applied to objects: ... (of class Package)` | you `sort`ed a list of Package objects | stringify first: `sort for p in loadedPackages list toString p` |
| `key not found in hash table:` + `name (of class Symbol)` | you wrote `P.name` on a Package — there is no such field | `toString P` |
| `expected a homogeneous module` | `hilbertPolynomial`/`hilbertSeries` on a non-homogeneous ideal (they REFUSE, unlike `degree` — trap #13) | homogenize first (trap #14) |
| `homogenization requires variable in the same ring` | `homogenize(f, w)` with `w` in a bigger ring | `homogenize(sub(f, S), w)` |
| `expected pair to have a method for '=='` | `sub(f, w => 1) == g` parses the `==` INTO the options pair — it is NOT a cross-ring failure (plain `f == sub(f, S)` works, verified `true`) | assign `sub(...)` to a temp first, then compare |
| `no method found for applying factor to:` + Ideal | `factor` takes RingElement, NOT ideals | `factor f`, not `factor I` |
| `syntax error at 'in'` (or `to`, `of`, `if`, …) | reserved word as a variable name — **and a syntax error can restart the kernel, losing all state** | rename; resend your self-contained block |
| "not reloaded; try Reload => true" on `loadPackage` | the package is **already loaded** | do nothing; never force-reload |

## Trap 1: the misleading "adjacent objects" error

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
print (reduceGb I)
-- expect-error: no method for adjacent objects
```

Models respond to this message by re-typing the same call with spaces/parens variants (`reduceGb I`, `reduceGb(I)`…) — that NEVER helps: the symbol `reduceGb` does not exist in the pinned corpus (index grep: no relevant hit).

## Trap 2: the kernel remembers everything (no rollback)

```m2
a = 404
zzzznope a
print a
-- expect-error: no method for adjacent objects
-- expect: 404
```

The failed line still left `a = 404` defined (the error killed only that input). In an interactive/MCP session, fix FORWARD; state survives errors. `class a` is the way to see what a name holds now:

```m2
x = 2
print (class x)
-- expect: ZZ
x = symbol x
print (class x)
-- expect: Symbol
```

## Trap 3: values are captured at assignment time

```m2
n = 5
sq = n^2
n = 10
print sq
-- expect: 25
```

`sq` is the *value* 25, not a lazy formula. (A function needs `->`: `f = n -> n^2`.)

## Trap 4: suppressing output with `;` looks like a hang/crash

```m2
R = QQ[x,y,z]
I = ideal(x, y);
x + y;
print "semicolons above printed nothing, but definitions took effect"
-- expect: semicolons above printed nothing
```

Statements ending in `;` ran (check: `I` exists) — they just don't display. In batch scripts the same rule applies to top-level expressions: use `print`.

## Trap 5: protected names in disguise

```m2
gb = 5
-- expect-error: assignment to protected global variable
```

Also protected: `res`, `betti`, `ideal`, `toExternalString`, etc. When a doc example shadows one with `a = ...`, it works — but for the common single-letter function names expect errors.

## Trap 6: "nothing happened" on valid-looking code

`net`/`describe`-style introspection when display surprises you:

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
G = gb I
print (describe R | "\n")
```

`describe R` renders the ring (variables + monomial order) as a string; `class obj` gives the type; `peek` bypasses custom `net` methods.

## Probing the package corpus at runtime (four traps, all verified)

M2's two package lists have **opposite shapes**:

- `loadedPackages` — a List of Package objects, loaded RIGHT NOW (21 entries on a fresh 1.26.06 startup, Core included; NO parens — see error below).
- `installedPackages()` — a FUNCTION returning a List of MANAGER-installed packages, typically EMPTY even though 299 packages ship bundled and are `loadPackage "Name"`-able.

```m2
print (#loadedPackages)
L = installedPackages()
print (class L, #L)
-- expect: 21
-- expect: List
```

The working idiom for names (Package objects have **no `.name` field** — "key not found in hash table" — and **no sort method** — "no method for binary operator ?" — so stringify first):

```m2
names = for p in loadedPackages list toString p
print (member("PrimaryDecomposition", names), member("Saturation", names))
-- expect: (true, true)
```

Two errors worth recognizing (they look exotic but are beginner traps):

```m2
print (loadedPackages ())
-- expect-error: no method for adjacent objects
```

```m2
sort loadedPackages
-- expect-error: no method for binary operator
```

Which packages ride along by default (⚡) and what they contribute: `references/packages.md`; the merged `index.tsv` rows carry the providing package in column 4.
