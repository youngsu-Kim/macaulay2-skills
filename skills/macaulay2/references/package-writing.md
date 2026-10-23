# Writing M2 code and packages (Macaulay2 1.26)

Source: the official [Package Writing Style Guide](https://github.com/Macaulay2/M2/wiki/Package-Writing-Style-Guide) on the M2 wiki — a LIVING document. Unlike everything else in this skill, this page is conventions rather than version-pinned behavior; the guide is authoritative and this file is the agent-relevant distillation. Idioms marked with blocks below are kernel-verified on 1.26.06.

## Naming

- Packages: PascalCase, plural when named after a mathematical object type (`NormalToricVarieties` exports the `NormalToricVariety` type); the name string in `newPackage(...)` must match the filename for `loadPackage` to find it.
- Types: nouns in PascalCase (`CoherentSheaf`, `NormalToricVariety`).
- Methods: camelCase (`isPrime`, `groebnerBasis`); reuse existing method names for new types (`dim MyIdeal := ...`) — never embed the argument type in the name (`dim`, not `dimMyIdeal`).
- Booleans: `is` prefix (`isPrime`, `isPrimitive`). Exported names: no abbreviations (`formalDepth`, not `fD`).
- Optional arguments: PascalCase (`DebuggingMode =>`), reusing standard names (`Verify`, `Verbose`) when the meaning matches.

## Code behavior (the rules that break sessions)

- Packages should not print; signal errors by calling `error`.
- Set no variables in the User dictionary without an explicit request: create rings without user variables, never use `use` or `vars` inside a package, and audit yourself with `listUserSymbols` (all per the guide).

```m2
R1 = QQ(monoid[getSymbol "a"])
print (class R1, numgens R1)
-- expect: PolynomialRing
```

- Prefer `instance(x, T)` over `class x === T` — the latter disables inheritance:

```m2
S = QQ[a]
print (instance(a, RingElement), class a === RingElement)
-- expect: (true, false)
```

- Lists and matrices are IMMUTABLE: never append/prepend inside a loop — use `apply`, `for ... list ...`, or hash tables.
- Use `( ... ; ... ; ... )` for statement blocks that are not lists; avoid `return` (especially on the last line); never export single-character identifiers; minimize globals; no magic numbers.
- Return several values as a Sequence, so users can write `(a,b,c) = f(x,y,z)`; write `f x` rather than `f(x)`; never test booleans against `true`/`false` (`x === true` is just `x`).

## Argument order

Arguments in increasing order of complexity; the object the function mainly acts on goes LAST.

## Documentation nodes

- Every exported type, method, and function must have a documentation page, and every page an example; `check P` runs a package's examples (index: `_check.html`).
- Mathematics in TeX (`$R/I$`, `$x^2$`, `$\mathbb{Z}/p$`; macros `\OO \Hom \End \Ext \Tor` predefined), M2 syntax as code — and never the twain; use `ofClass` so identifiers become hyperlinked English words.
- Headlines: one brief noun phrase (they appear in menus) — no variables, no full sentences. Outputs sections: type AND mathematical description of each output. Don't assign to variables in Usage/Outputs samples; never reload the current package in example code.
- Start sentences with English words (not identifiers), end with a period (never a colon before examples); don't capitalize common nouns like "list" unless referring to the class `List`.

## Symbols without side effects

```m2
x1 = getSymbol "x"
print (class x1)
-- expect: Symbol
```

## JSAG article prose (selected)

No acronyms; "determine whether R is reduced" (not "whether or not"); "different from" (not "different than"); italicize *Macaulay2*; follow "e.g.", "i.e.", "resp." with a comma; watch the placement of "only"; choose "that" (restrictive, no commas) vs "which" (non-restrictive, commas).
