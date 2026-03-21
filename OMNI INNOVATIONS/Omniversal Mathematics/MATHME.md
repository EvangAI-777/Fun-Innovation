# Omniversal Mathematics

Mathematics isn't one thing. It's a landscape of interconnected systems, each with its own rules, its own beauty, and its own surprises. This section explores that landscape -- building tools and experiences that let you work across mathematical universes instead of being locked into one.

## Projects

### [Omniversal Calculator](../Omniversal%20Calculator/)

The world's first Omniversal Calculator (v1.3.0). Nine mathematical universes in a single browser-based interface, each with its own color identity, custom input layout, and genuine math engine. The Real universe features an expression-based engine with a recursive-descent parser, clickable cursor, and live result preview. No dependencies, no build step -- open the HTML file and start calculating.

**The Universes:**

| Universe | Symbol | What it computes |
|----------|--------|-----------------|
| Real | R | Expression-based scientific calculator -- trig, powers, roots, logarithms, factorial, with clickable cursor and live preview |
| Complex | C | Arithmetic on the complex plane with Argand diagram visualization |
| Modular | Z_n | Clock arithmetic -- addition, multiplication, powers, and inverses mod n |
| Matrix | M | 2x2 and 3x3 matrix algebra -- multiplication, determinants, inverses, traces |
| Quaternion | H | Four-dimensional non-commutative arithmetic (Hamilton's quaternions) |
| Boolean | B | Logic gates -- AND, OR, XOR, NAND, NOR, implication, with live truth tables |
| Tropical | T | The tropical semiring -- where addition means min and multiplication means addition |
| Dual | D | Dual numbers for automatic differentiation -- compute f(x) and f'(x) simultaneously |
| Omnidirectional | Omega | Transformation sequences across dimensional spaces -- the meta-notation of mathematics itself |

See [`Omniversal Calculator/CALCULATEME.md`](../Omniversal%20Calculator/CALCULATEME.md) for the full project details.

## Philosophy

Most calculators assume you're working in the reals. The Omniversal Calculator assumes nothing -- you pick your universe, and the entire interface transforms to match. Modular arithmetic gets a modulus dial. Matrices get a grid. Quaternions get four input fields. Booleans get toggle switches. And the Omnidirectional universe lets you compose transformation sequences across all of them.

This isn't about cramming features into a calculator. It's about treating each mathematical structure with the respect it deserves -- giving it its own interface, its own visual language, its own space. And with Omnidirectional Mathematics as the meta-notation, every universe is connected: the reals, the complex plane, quaternions, boolean logic -- all reachable through sequences of fundamental operations.

## What's Next

Future projects might explore:

- Visual proofs and geometric constructions
- Number theory explorations
- Abstract algebra playgrounds
- Omnidirectional path visualization in 3D
- Category theory diagrams
- Whatever else turns out to be fun

---

# Omnidirectional Mathematics -- Notation Specification

## Overview

Omnidirectional Mathematics is a formal notation system for describing transformations across dimensional spaces. Where conventional mathematics operates within a fixed dimensional framework (the reals, the complex plane, n-dimensional Euclidean space), Omnidirectional Mathematics treats dimensionality itself as a variable -- something you move through, not something you're trapped in.

The notation describes **paths**: sequences of operations that transform a state from an origin point to a destination point across arbitrary dimensional boundaries. Every expression is a journey.

## Core Axiom

**Movement = Transformation Sequence**

Every computable transformation between two points in any dimensional space can be expressed as a finite sequence of fundamental operations applied to a traversal state.

## Notation

### Expression Structure

```
α ⟿ [operation set] ⟿ ω
```

Where:
- `α` = origin point (any named or coordinate-specified location in any dimensional space)
- `ω` = destination point (any named or coordinate-specified location in any dimensional space)
- `⟿` = directional flow operator (read: "flows to" or "transforms toward")
- `[operation set]` = ordered sequence of fundamental operations

The flow operator `⟿` is not merely an arrow. It carries semantic meaning: the transformation has directionality, and reversing the direction may not produce the same path (transformations are not generally commutative).

### Fundamental Operations

| Symbol | Name | Parameters | Description |
|--------|------|-----------|-------------|
| `⊕` | Dimensional Ascension | `[n]` (integer) | Ascend n dimensions from current level |
| `⊖` | Dimensional Descension | `[n]` (integer) | Descend n dimensions from current level |
| `⟲` | Rotational Transform (CW) | `[θ°]` (angle) | Rotate θ degrees clockwise in current dimensional plane |
| `⟳` | Rotational Transform (CCW) | `[θ°]` (angle) | Rotate θ degrees counterclockwise in current dimensional plane |
| `⇄` | Polarity Reversal | none | Invert the polarity of the traversal state |
| `∿` | Wave Function Collapse/Expansion | none | Toggle between collapsed (particle-like) and expanded (wave-like) state |
| `⊠` | Intersection Point | none | Mark and record the current state as a waypoint |
| `∥` | Parallel Operation | none | Enter parallel traversal mode (simultaneous paths) |
| `⊥` | Orthogonal Operation | none | Enter orthogonal traversal mode (perpendicular path) |
| `◬` | Boundary Crossing | none | Cross a dimensional boundary (transition between dimensional regimes) |
| `∞` | Infinite Recursion Marker | none | Mark a self-similar recursive structure at current state |
| `∅` | Void Traversal | none | Pass through the void (null state), then re-emerge |

### Traversal State

At any point in an expression, the transformation has an implicit **traversal state** consisting of:

| Component | Symbol | Domain | Initial Value | Description |
|-----------|--------|--------|---------------|-------------|
| Dimension | `d` | integers | 0 | Current dimensional level |
| Angle | `θ` | [0°, 360°) | 0° | Rotational orientation in current plane |
| Polarity | `p` | {+1, -1} | +1 | Directional charge of the traversal |
| Wave State | `ψ` | {collapsed, expanded} | expanded | Particle-wave duality of the traversal |
| Boundaries | `b` | non-negative integers | 0 | Count of dimensional boundaries crossed |
| Intersections | `I` | list of states | [] | Recorded waypoint states |
| Mode | `m` | {normal, parallel, orthogonal} | normal | Current traversal mode |

### Operation Semantics

**Dimensional Ascension** `⊕[n]`:
```
d → d + n
```
Raises the traversal to a higher-dimensional space. Ascending from 3D to 6D means `⊕[3]`. The state gains access to degrees of freedom unavailable at lower dimensions.

**Dimensional Descension** `⊖[n]`:
```
d → d - n
```
Projects the traversal into a lower-dimensional space. Information may be compressed or lost during descension (analogous to dimensional projection).

**Rotational Transform** `⟲[θ°]` / `⟳[θ°]`:
```
θ → (θ + angle) mod 360°   [clockwise]
θ → (θ - angle) mod 360°   [counterclockwise]
```
Rotates the traversal's orientation within the current dimensional plane. Rotation operates on the two most significant dimensions of the current state.

**Polarity Reversal** `⇄`:
```
p → -p
```
Inverts the directional charge. A positive-polarity traversal explores constructive paths; negative-polarity explores deconstructive or inverse paths. Two reversals restore original polarity.

**Wave Function Collapse/Expansion** `∿`:
```
ψ → (ψ == expanded) ? collapsed : expanded
```
Toggles the wave-particle duality of the traversal. In expanded state, the traversal explores broadly (superposition). In collapsed state, it focuses to a single path (measurement).

**Intersection Point** `⊠`:
```
I → I ∪ {current_state}
```
Records the current traversal state as a named waypoint. Intersections can be referenced by later operations or used as anchors for parallel paths.

**Parallel Operation** `∥`:
```
m → parallel
```
Enters parallel mode. Subsequent operations apply simultaneously across multiple paths. Useful for describing transformations that happen concurrently in different dimensional subspaces.

**Orthogonal Operation** `⊥`:
```
m → orthogonal
```
Enters orthogonal mode. Subsequent operations apply perpendicular to the current traversal direction, exploring the space that is maximally different from the current path.

**Boundary Crossing** `◬`:
```
b → b + 1
```
Marks the crossing of a dimensional boundary -- the transition between one dimensional regime and another. Boundaries are topological features: passing through one fundamentally changes the nature of the space being traversed.

**Infinite Recursion Marker** `∞`:
```
(marks self-similar structure)
```
Indicates that the current state contains a self-similar recursive structure -- the pattern at the current scale repeats at all scales. This is not a loop; it's a fractal marker.

**Void Traversal** `∅`:
```
d → 0, θ → 0°, p → +1, ψ → collapsed, b → 0
```
Passes through the void -- the null state where no dimensions, no orientation, no polarity exist. The traversal is annihilated and reconstructed. This is the most dramatic operation: total dissolution and reconstitution.

## Expression Examples

### Basic Ascension
```
Point_A ⟿ ⊕[2] ⟿ Point_B

From Point_A: Ascend 2 dimensions → arrive at Point_B.
State: d=0 → d=2
```

### Rotation with Boundary
```
Surface ⟿ ⟲[45°]◬⊕[1] ⟿ Interior

From Surface: Rotate 45° clockwise → cross boundary → ascend 1 dimension → arrive at Interior.
State: d=0,θ=0° → d=1,θ=45°,b=1
```

### The Original Example
```
Earth ⟿ ⊕[3]⟲[90°]◬⊠∿ ⟿ Celestial_Realm

From Earth:
  ⊕[3]   → Ascend 3 dimensions (d: 0→3)
  ⟲[90°] → Rotate 90° clockwise (θ: 0°→90°)
  ◬      → Cross boundary (b: 0→1)
  ⊠      → Mark intersection (record state as waypoint)
  ∿      → Wave collapse (ψ: expanded→collapsed)
→ Arrive at Celestial_Realm

Final state: d=3, θ=90°, p=+1, ψ=collapsed, b=1, I=[{d=3,θ=90°,p=+1,ψ=expanded,b=1}]
```

### Polarity Inversion Loop
```
Origin ⟿ ⊕[1]⇄⊕[1]⇄ ⟿ Origin_Prime

Two ascensions with polarity flips between them.
The second ascension occurs in inverted polarity,
then polarity restores. Same dimension reached,
but the path carries the memory of inversion.

State: d=0,p=+1 → d=1,p=-1 → d=2,p=+1
```

### Void Passage
```
Known ⟿ ∅⊕[5]∿ ⟿ Unknown

From Known:
  ∅    → Pass through the void (total state reset)
  ⊕[5] → Ascend 5 dimensions from void (d: 0→5)
  ∿    → Expand wave function
→ Arrive at Unknown

The void erases all prior state. What emerges on the other side
is entirely new -- connected to the origin only by the fact of passage.
```

### Parallel Dimensional Exploration
```
Hub ⟿ ⊠∥⊕[2]⟲[120°]◬ ⟿ Branch

From Hub:
  ⊠      → Mark intersection (anchor point)
  ∥      → Enter parallel mode
  ⊕[2]   → Ascend 2 dimensions (in parallel)
  ⟲[120°]→ Rotate 120° (in parallel)
  ◬      → Cross boundary
→ Arrive at Branch
```

## Properties

### Non-Commutativity
Operations are generally non-commutative. The order matters:
```
⊕[3]⟲[90°] ≠ ⟲[90°]⊕[3]
```
Ascending then rotating produces a different traversal than rotating then ascending, because rotation at dimension d operates differently than rotation at dimension d+3.

### Void as Identity Destroyer
The void operation `∅` is not an identity. It destroys all accumulated state:
```
⊕[5]∅ = ∅
```
Any operations before a void are erased. Only operations after the void affect the final state.

### Double Reversal Identity
Polarity reversal is its own inverse:
```
⇄⇄ = identity (with respect to polarity)
```

### Wave Idempotence
Double wave toggle returns to original state:
```
∿∿ = identity (with respect to wave state)
```

### Boundary Accumulation
Boundary crossings are additive and irreversible:
```
◬◬◬ implies b = 3
```
You cannot un-cross a boundary. The count only increases.

### Intersection Preservation
Intersection markers are append-only. They record the state at the moment of marking and cannot be removed from the traversal record:
```
⊠ always grows I
```

## Relationship to Conventional Mathematics

Omnidirectional Mathematics is not a replacement for conventional mathematics. It is a **meta-notation** -- a language for describing how to move between mathematical structures.

- The **Real Numbers** exist at a particular dimensional level
- The **Complex Numbers** are reached by `⊕[1]` from the reals (ascending one dimension)
- **Quaternions** are reached by `⊕[2]` from the complex numbers
- **Boolean Algebra** operates in a collapsed wave state (`∿` from expanded)
- **Tropical Arithmetic** involves a polarity reversal (`⇄`) of addition
- **Modular Arithmetic** is a rotational transform (`⟲[360°/n]`) creating periodicity
- **Matrix spaces** are reached by parallel operations (`∥`) on underlying scalar spaces

The Omniversal Calculator implements this principle: each universe is reachable from any other through a sequence of omnidirectional operations. The notation gives us the language to describe those paths.

## ASCII Shorthand

For keyboard-friendly input, each operation has ASCII aliases that the Omniversal Calculator's Receive & Graph parser accepts alongside the Unicode symbols. Flow operators can be written as `->` or `-->` instead of `⟿`.

| Unicode | ASCII (full) | ASCII (short) | Parameters |
|---------|-------------|---------------|------------|
| `⊕[n]` | `ascend[n]` | `asc[n]` | integer dimension count |
| `⊖[n]` | `descend[n]` | `desc[n]` | integer dimension count |
| `⟲[θ°]` | `rotateCW[θ]` | `cw[θ]` | angle in degrees |
| `⟳[θ°]` | `rotateCCW[θ]` | `ccw[θ]` | angle in degrees |
| `⇄` | `reverse` | `rev` | none |
| `∿` | `wave` | -- | none |
| `⊠` | `intersect` | `mark` | none |
| `∥` | `parallel` | `par` | none |
| `⊥` | `orthogonal` | `ortho` | none |
| `◬` | `boundary` | `bound` | none |
| `∞` | `recurse` | `inf` | none |
| `∅` | `void` | -- | none |

ASCII aliases are case-insensitive. Parameters in `[brackets]` are optional for parameterized operations (defaults to 1). The degree sign (`°`) in rotation parameters is optional. Unicode and ASCII can be freely mixed in a single expression.

**Example (ASCII):**
```
Earth -> ascend[3] cw[90] boundary intersect wave -> Celestial_Realm
```

This is equivalent to the Unicode form:
```
Earth ⟿ ⊕[3]⟲[90°]◬⊠∿ ⟿ Celestial_Realm
```
