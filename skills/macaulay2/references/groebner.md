# Groebner bases (Macaulay2 1.26)

## The one object model you need

`gb I` computes and returns a **GroebnerBasis object** — printing the object shows status metadata, not the basis. Extract the polynomials with `generators` (or `gens`), which yields a matrix:

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
G = gb I
print (class G)
-- expect: GroebnerBasis
```

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
print (generators gb I)
-- expect: | xy-z x2z-y2 y3-xz2 x3-y |
```

**The generators are already sorted and auto-reduced** — the docs guarantee it; there is no `reduceGb`/`reducedGroebnerBasis` in core 1.26 (verify against `references/index.tsv`). If you feel the urge to "reduce again", you already have the reduced basis.

Sanity property: a reduced basis for `ideal(x^3 - y, x^4 - z)` in `QQ[x,y,z]` (default graded reverse lex) has 4 elements and contains the leading terms `x^3, y^3`-side structure — but the honest check is ideal equality:

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
J = ideal apply(flatten entries generators gb I, p -> p)
print (J == I)
-- expect: true
```

## Monomial orders

Set the order at **ring construction** (not on `gb` itself):

```m2
R = QQ[x,y,z, MonomialOrder => Lex]
I = ideal(x^2 + y^2, x*y - z)
print (generators gb I)
```

```m2
R = QQ[x,y,z, MonomialOrder => Eliminate 1]
I = ideal(x*y - z, x^2 - z)
print (generators gb I)
```

- Default (no option) = graded reverse lexicographic (`GRevLex`): fastest for most tasks; elimination properties come for free in variable order.
- `Lex`: good for elimination/parametrization, slower.
- `Eliminate k`: first `k` variables are eliminated — the resulting basis contains a basis of `I ∩ QQ[last variables]`.
- `monomialOrder R` is NOT a core method in 1.26 (index says: not found) — to inspect the order, look at how you built the ring or `describe R` (needs no package: see debugging.md).

## Membership and reduction idioms

```m2
R = QQ[x,y,z]
I = ideal(x^3 - y, x^4 - z)
f = x^3*y - y^2        -- = y*(x^3 - y), hence in I
print (f % I == 0)
print (member(f, I))
-- expect: true
```

- `f % I` = normal form of `f` modulo `I` (reduced by `gb I`).
- `member(f, I)` is the boolean form, but **over rings with nontrivial coefficients `% I == 0` is the general idiom**; for QQ[x,..] either works. Careful: `x^5 % (ideal(x^3 - y, x^4 - z))` is NOT 0 — powers of x reduce via `x^3 ≡ y`, so `x^5 ≡ x^2 y`: let the kernel, not mental arithmetic, decide membership.
- `trim I` gives a reduced set of GENERATORS of I (as an ideal) — this is NOT the same thing as a Groebner basis (it doesn't compute one), but it is the shortest path to "simplify my generating set":

```m2
R = QQ[x,y]
I = ideal(x^2 + y*x, x)
print (trim I)
-- expect: ideal x
```

## Intersections, quotients, saturations (core, no package)

```m2
R = QQ[x,y,z]
I = ideal(x, y)
J = ideal(y, z)
print (I + J, I * J, intersect(I, J))
```

- `intersect(I, J, ...)` — ideal intersection (via GB machinery).
- `quotient(I, J)` — colon ideal `I : J`; `saturate(I, J)` for `I : J^∞` (⚡ default-loaded from the Saturation package — 21 signature rows in `index.tsv`, no `loadPackage`; verified: `saturate(ideal(x*y, x^2), ideal(x))` in `QQ[x,y,z]` returns `ideal 1`, correct since `x ∈ (x,y)` kills saturation).
- Primary decomposition: `primaryDecomposition` is **already available** (⚡ PrimaryDecomposition package, default-loaded — no loadPackage!) and handles general ideals:

```m2
R = QQ[x,y]
print (primaryDecomposition ideal(x^2, x*y))
-- expect: ideal x
```

Result `{ideal x, ideal (y, x^2)}` — an irredundant decomposition; for minimal primes of non-prime ideals use `minimalPrimes` (⚡ MinimalPrimes).

## Elimination and implicitization (⚡ Elimination, verified)

Implicitize the parametrization `(s,t) ↦ (s, st, t²)`: build the graph ideal in ONE big ring, then `eliminate` the parameters:

```m2
T = QQ[s,t,x,y,z]
K = ideal(x - s, y - s*t, z - t^2)
E = trim eliminate({s,t}, K)
print (numgens E, degree E)
print (isHomogeneous E, isPrime E)
-- expect: (1, 3)
-- expect: (false, true)
```

E = (x²z − y²): one generator, prime, **not homogeneous** — yet `degree E` = 3 still equals its projective-closure degree because default GRevLex is degree-compatible (trap #13: under Lex even this can change). Alternative route (same answer, verified): `kernel map(QQ[s,t], QQ[x,y,z], {s, s*t, t^2})` — then `sub` into the target ring for comparisons (trap #15).
