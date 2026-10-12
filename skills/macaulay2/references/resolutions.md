# Free resolutions, Betti tables, Hilbert functions (Macaulay2 1.26)

## The two calls that answer "tell me about S/I"

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (betti res C)
-- expect: total: 1 3 2
```

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (hilbertPolynomial(S/C, Projective => false))
-- expect: 3i + 1
```

- `res I` takes the **ideal** (also a module or map). `res (S/C)` is the
  classic mistake: no method applies `freeResolution` to a QuotientRing.
- `betti`'s `total:` row sums generators/syzygies per homological degree.
- `hilbertPolynomial` DOES take the quotient ring `S/C`. With
  `Projective => false` it returns the polynomial in `i` (degree and Euler
  characteristic readable off it: here `3·i + 1` ⇒ degree 3, genus 0 — the
  twisted cubic).

## Reading the table (twisted cubic, from the run above)

```
       0 1 2
total: 1 3 2
    0: 1 . .
    1: . 3 2
```

- Columns = homological degree `i`; **rows are labelled `j − i`, not the raw
  internal degree**: `β_{i,j}` prints in row `j−i`. The three quadrics
  `β_{1,2}` therefore sit under row `1:` (not `2:`), and the twisted-cubic
  table above reads: row 1 = quadratic generators (col 1) and linear syzygies
  `β_{2,3}` (col 2, row `3−2=1`). Misreading this label is the #1 way to
  "see" degrees that aren't there.
- Resolution: `0 → S(-3)² → S(-2)³ → S → S/C → 0` (three quadrics, two
  linear first syzygies — the hallmark of an arithmetically Cohen–Macaulay
  curve of degree 3).
- Sanity checks that should all pass (and do, on 1.26):

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (dim (S/C), degree C)
-- expect: (2, 3)
```

  - number of generators (3) = length of any gb for this ideal,
  - `dim (S/C) = 2` (curve in ℙ³ ⇒ projective dimension 1 + 1),
  - `degree C = 3` = leading coefficient × 1! of `3i + 1`,
  - `sum(−1)^k totals_k = 1 − 3 + 2 = 0` = the rank of `S/C` as an S-module
    (0 because C is nonzero of positive dimension — never expect 1 here!).

## Hilbert series

```m2
S = QQ[w,x,y,z]
C = ideal(x*z - y^2, y*w - z^2, x*w - y*z)
print (hilbertSeries(S/C, Reduce => true))
-- expect: 1 + 2T
```

- `Reduce => true` returns the REDUCED rational form — rendered multi-line
  ASCII (expect `1 + 2T` over `(1 - T)2`, i.e. `(1+2T)/(1−T)²`); without it
  you get the raw alternating sum from the resolution.
- The two forms must agree, and this is a real cross-check:
  `(1 − 3T² + 2T³)/(1 − T)⁴ = (1+2T)/(1−T)²` because
  `1 − 3T² + 2T³ = (1−T)²(1+2T)` — numerator coefficients come from the
  Betti totals `1, 3, 2`, denominator `(1−T)⁴` from the four variables.
- Expanding `(1+2T)/(1−T)²` gives coefficients `3n + 1` — exactly the
  Hilbert polynomial above. Series ↔ polynomial ↔ Betti table all close.
- For NON-homogeneous ideals the graded machinery is wrong — see trap #8 in
  SKILL.md.

## Modules and maps

```m2
S = QQ[x,y]
M = coker matrix {{x, y}, {0, x}}
print (betti res M)
```

- `betti res M` works directly on modules; matrices are presented as
  `coker matrix {{...}}` (rows = relations on generators).
- Length of the resolution is the projective dimension; for `S/I` with
  `I` perfect (like the twisted cubic: pd 2 = codim 2) it equals the height.

## Depth and Cohen–Macaulay (verified: two skew planes in A^4)

`I = (x,y) ∩ (z,w)` in `A = QQ[x,y,z,w]` — union of two planes meeting only
at the origin. This is THE canonical non-CM example, and the API has a
package gate (trap #16):

```m2
A = QQ[x,y,z,w]
I = intersect(ideal(x,y), ideal(z,w))
print (betti res I)
print (pdim (A^1/I), dim (A/I), degree I)
-- expect: total: 1 4 4 1
-- expect: (3, 2, 2)
```

- `betti` row check: all four generators/syzygies on row `1:` → 2-linear
  resolution; `total: 1 4 4 1`.
- `pdim` is core; `depth`/`isCM` need `loadPackage "Depth"`:

```m2
A = QQ[x,y,z,w]
I = intersect(ideal(x,y), ideal(z,w))
loadPackage "Depth"
print (depth (A^1/I), isCM (A^1/I))
-- expect: (1, false)
```

- Package-free CM certificate (Auslander–Buchsbaum):
  `depth (A/I) = numgens vars A - pdim (A/I) = 4 - 3 = 1 < dim = 2` ⇒
  **not Cohen–Macaulay**; equivalently `pdim ≠ height` (3 ≠ 2) ⇒ not perfect.
  Geometry echo: `primaryDecomposition I` returns exactly `{ideal(x,y),
  ideal(z,w)}` — two components, degree 1+1 = 2 ✓.
