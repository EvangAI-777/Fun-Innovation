# Omniversal Calculator

The world's first Omniversal Calculator. Nine mathematical universes, one interface, zero dependencies.

## Why This Exists

Most calculators assume you're working in one number system. This one assumes nothing—you pick your universe and the entire interface transforms to match. But the real point is the Omnidirectional universe.

Omnidirectional Mathematics is a notation system for describing movement between points in any dimensional space. Dimensionality isn't a box you're trapped in—it's a variable you move through. The expression `⊕[3]⟲[90°]◬⊠∿` isn't abstract. It's five operations producing a real traversal state: dimension 3, rotated 90°, one boundary crossed, one intersection marked, wave collapsed. A path from Earth to Celestial_Realm.

The Receive & Graph mode is the original idea made real: give the calculator coordinates of an omniversal place, and it shows you the path there. Type the formal Unicode notation, or plain ASCII, or any mix—the parser understands all of it. This is a coordinate system for places that don't have coordinate systems yet.

Built by a human and an AI pushing into territory neither would reach alone.

## Quick Start

Open `omniversal-calculator.html` in any modern browser. That's it. No install, no build, no server.

## How It Works

The top of the page shows nine **universe orbs** -- glowing circles labeled with each mathematical system's symbol. Click one to enter that universe. The entire calculator transforms: the color palette shifts, the description bar updates, and the input area reconfigures itself for the selected number system.

Every universe has a genuine math engine behind it. These aren't toy implementations -- they handle edge cases (division by zero, singular matrices, non-invertible elements) and follow the actual algebraic rules of each system.

### Universe Guide

**Real Numbers (R)** -- A full expression-based scientific calculator with pill-shaped buttons in the unified site-wide palette. Five button categories: deep purple scientific functions, purple-glow AC button, void-dark number pad, surface-dark operators, and a bright purple equals button. The display is fully modular -- every button press inserts into the expression at the cursor position rather than replacing it, and a blinking cursor shows where input goes. Click anywhere in the expression to reposition the cursor. Arrow keys (Left/Right/Home/End) navigate the cursor; Delete removes the character after it. Live result preview appears above the expression as you type. A recursive-descent parser evaluates expressions with proper operator precedence (parentheses > functions > exponents > multiply/divide > add/subtract), implicit multiplication (e.g., 2pi = 2*pi), and postfix operators (! for factorial, % for percentage). Features: trig functions (with Deg/Rad toggle and Inv mode for asin/acos/atan), factorial, powers, roots, logarithms, constants (pi, e), percentage, and smart parentheses. Keys: 0-9, +, -, *, /, ^, !, %, (, ), Arrow keys, Enter, Backspace, Delete, Escape.

**Complex Numbers (C)** -- Enter two complex numbers z1 and z2 as real + imaginary parts. Supports addition, subtraction, multiplication, division, modulus, argument, conjugate, and squaring. Includes a live Argand diagram that plots z1 and the result on the complex plane with a dashed line from the origin.

**Modular Arithmetic (Z_n)** -- Set a modulus n, then perform arithmetic mod n. Addition, subtraction, multiplication, modular exponentiation (using fast binary exponentiation), modular inverse (using the extended Euclidean algorithm), and GCD.

**Matrix Algebra (M)** -- Toggle between 2x2 and 3x3 matrices. Enter values for matrices A and B in bracket-wrapped grids. Supports addition, multiplication, determinant (cofactor expansion), transpose, inverse (adjugate method), and trace.

**Quaternions (H)** -- Enter two quaternions as four components (a + bi + cj + dk). Addition, subtraction, multiplication (non-commutative -- q1 x q2 is not q2 x q1), conjugate, norm, and inverse. Hamilton's multiplication rules: i^2 = j^2 = k^2 = ijk = -1.

**Boolean Algebra (B)** -- Two toggle switches for inputs A and B. Operations: AND, OR, XOR, NOT, NAND, NOR, XNOR, and material implication (A -> B). Includes a live truth table showing all input combinations.

**Tropical Semiring (T)** -- Choose between min-plus and max-plus conventions. Tropical addition (which is min or max in the conventional sense) and tropical multiplication (which is conventional addition). Used in optimization theory, phylogenetics, and tropical algebraic geometry.

**Dual Numbers (D)** -- Enter dual numbers z1 = a + b*epsilon where epsilon^2 = 0. Supports arithmetic (+, -, x, /) and functions (sin, cos, exp, ln). The key trick: set b = 1 to perform automatic differentiation. sin(3 + 1*epsilon) returns sin(3) + cos(3)*epsilon -- the value AND the derivative in one pass. Composes via chain rule automatically.

**Omnidirectional Transforms (Omega)** -- The meta-universe. Two modes: **Build** and **Receive & Graph**.

In **Build** mode, construct transformation sequences step by step. Name an origin and destination, then compose operations: dimensional ascension/descension, clockwise/counterclockwise rotation, polarity reversal, wave collapse/expansion, intersection marking, parallel/orthogonal modes, boundary crossing, infinite recursion marking, and void traversal. The expression builder shows the full notation in real time.

In **Receive & Graph** mode, type or paste an omnidirectional expression and the calculator parses it and graphs the transformation path. Accepts both the formal Unicode notation (`Earth ⟿ ⊕[3]⟲[90°]◬⊠∿ ⟿ Celestial_Realm`) and ASCII shorthand (`Earth -> ascend[3] cw[90] boundary intersect wave -> Celestial_Realm`). Mixed Unicode and ASCII in the same expression is supported. Contextual autocomplete suggests operations as you type -- arrow keys to navigate, Enter/Tab to insert. Ctrl+Enter parses the expression.

Both modes share the state grid (dimension level, angle, polarity, wave state, boundary count) and the visualization canvas that plots the transformation path through dimensional space. See [MATHME.md](../Omniversal%20Mathematics/MATHME.md) for the formal specification.

## Design

**Single file.** Everything -- HTML structure, CSS styles, JavaScript engines, starfield animation -- lives in one `.html` file. No dependencies, no build tools, no frameworks.

**Dark theme.** Deep space aesthetic with a twinkling starfield background. Each universe has its own accent color that tints the entire interface when selected. The Real universe features pill-shaped buttons in the unified site-wide palette: deep purple for scientific functions, purple-glow for AC, void-dark for the number pad, surface-dark for operators, and bright purple for the equals button.

**Responsive.** Flexbox and CSS Grid with media queries at 600px and 380px breakpoints. The calculator works on phones, tablets, and desktops. Universe orbs shrink, button grids reorganize, matrix inputs compact.

**Accessible.** Full keyboard support for the real calculator including cursor navigation (arrow keys, Home, End). Clickable expression display for cursor repositioning. Clear labels. High-contrast text. Semantic HTML structure.

## Testing

171 tests in `tests/omniversal/test_omniversal_calculator.py`:

- **24 structural tests** -- validate the HTML file has all 9 universes, UI elements, responsive tags, omni operator buttons (including metaCW/metaCCW), notation file, no external dependencies, and dark theme
- **14 real arithmetic tests** -- trig, powers, roots, logarithms
- **10 complex arithmetic tests** -- all operations plus modulus, argument, conjugate
- **10 modular arithmetic tests** -- mod operations, Fermat's little theorem, extended Euclidean algorithm
- **13 matrix tests** -- addition, multiplication, determinants (2x2 and 3x3), transpose, inverse, trace, non-commutativity
- **10 quaternion tests** -- Hamilton's rules (ij=k, ji=-k, i^2=-1), non-commutativity, norm, inverse
- **10 boolean tests** -- all gates plus De Morgan's laws
- **9 tropical tests** -- both conventions, distributive law, associativity
- **12 dual number tests** -- epsilon^2=0, autodiff for sin/cos/exp/ln, chain rule, product rule
- **31 omnidirectional tests** -- all 14 operators (including metaCW/metaCCW), metadegrees wrapping, meta-angle independence from entity angle, void annihilation (including metaAngle reset), the Earth-to-Celestial example, property verification (double reversal, boundary accumulation, rotation commutativity)
- **11 receive & graph structural tests** -- tab bar, textarea, parse button, autocomplete, parser function, token definitions
- **17 expression parser tests** -- Unicode parsing, ASCII parsing, mixed notation, operations-only, void sequences, all parameterless ops, metadegrees (Unicode and ASCII), error handling, case insensitivity, default parameters

Run with: `make test-omniversal`

## Colors

| Universe | Accent |
|----------|--------|
| Real | #c084fc (purple) |
| Complex | #b48ead (purple) |
| Modular | #a3be8c (green) |
| Matrix | #88c0d0 (cyan) |
| Quaternion | #d08770 (orange) |
| Boolean | #d8dee9 (silver) |
| Tropical | #ebcb8b (gold) |
| Dual | #8fbcbb (teal) |
| Omnidirectional | #c084fc (violet) |

---

# Changelog

All notable changes to the Omniversal Calculator are documented here.

## [v1.4.1] - 2026-03-30

### Changed
- **Unified default accent** -- Default and Real universe accent color changed from #58a6ff (blue) to #c084fc (purple) to match the site-wide unified palette. Per-universe accent colors for the other 8 mathematical universes are preserved.
- **Unified Real universe button panel** -- Real calculator button colors replaced from Google/Android Material Design palette to the site-wide unified palette. Number pad (#161640), scientific functions (#252550), operators (#10102a), AC (purple glow), and equals (#c084fc) now match the rest of the site.

## [v1.4.0] - 2026-03-21

### Added
- **Receive & Graph mode** -- The original vision for the Omnidirectional universe. Type or paste omniversal coordinates as text and the calculator parses the expression and graphs the transformation path. Accepts formal Unicode notation (`⊕[3]⟲[90°]◬⊠∿`), ASCII shorthand (`ascend[3] cw[90] boundary intersect wave`), or any mix of both. Flow operators support both `⟿` and `->` / `-->`.
- **Tab toggle** -- The Omega universe now has Build and Receive & Graph tabs. Both share the state grid and visualization canvas.
- **Expression parser** -- Tokenizes omnidirectional expressions supporting all 14 operations with Unicode symbols, full-name ASCII aliases, and short aliases. Parameters in `[n]` brackets, with degree signs optional. Parameterized ops without brackets default to 1.
- **Contextual autocomplete** -- As you type in the Receive & Graph textarea, matching operations appear in a dropdown. Arrow keys navigate, Enter/Tab inserts the Unicode symbol. Works for both Unicode and ASCII input.
- **Metadegrees** -- Two new fundamental operations: Metarotation CW (`⥁`) and Metarotation CCW (`⥀`). Metadegrees measure the rotation of space around an entity, not the entity itself. The entity's own angle `θ` is unchanged -- the frame of reference shifts. ASCII aliases: `metaCW`/`mcw`, `metaCCW`/`mccw`. Adds Meta-Angle (`φ`) to the traversal state grid.
- **34 new tests** -- 11 structural tests for the new UI elements, 17 parser reference tests covering Unicode, ASCII, mixed notation, metadegrees, error handling, and edge cases, 6 metadegrees engine tests.

## [v1.3.0] - 2026-02-10

### Changed
- **Expression-based engine** -- Complete rewrite of the Real calculator from accumulator model to expression-based. Every button press now inserts into a visible expression string at the cursor position. Constants like `e` and `pi` no longer overwrite the current operation.
- **Recursive-descent parser** -- Proper operator precedence (parentheses > functions > exponents > multiply/divide > add/subtract), right-associative exponentiation, and implicit multiplication (e.g., `2pi` = `2 * pi`).
- **Clickable cursor** -- Blinking cursor in the expression display. Click any character to reposition. Arrow keys (Left/Right/Home/End) navigate; Delete removes the character after the cursor; Backspace deletes multi-character tokens (like `sin(`) as a unit.
- **Live result preview** -- The evaluated result appears above the expression in real time as you type.
- **Smart continuation** -- After pressing `=`, typing a digit starts fresh; typing an operator continues from the result.

## [v1.2.0] - 2026-02-10

### Changed
- **Google/Android calculator style** -- Redesigned the Real universe with a 4-column layout, pill-shaped buttons, and five color categories: light blue-gray scientific functions, cyan AC, dark charcoal numbers, medium gray operators, and lavender equals.

### Added
- **Factorial** (`!`) -- Computes n! for non-negative integers up to 170.
- **Deg/Rad toggle** -- Switches trig functions between degree and radian input.
- **Inverse trig mode** (Inv) -- Toggles sin/cos/tan to asin/acos/atan with dynamic button labels.
- **Percentage** (`%`) -- Postfix operator dividing by 100.
- **Smart parentheses** (`( )`) -- Auto-detects whether to insert `(` or `)` based on nesting depth.
- **Extended keyboard** -- `^`, `!`, `%`, `(`, `)` keys now mapped.

## [v1.1.0] - 2026-02-10

### Added
- **Omnidirectional Transforms** -- Ninth mathematical universe implementing the formal Omnidirectional Mathematics notation. Fourteen fundamental operators (ascend, descend, rotate CW/CCW, metarotate CW/CCW, polarity reversal, wave collapse/expansion, intersection, parallel, orthogonal, boundary crossing, infinite recursion, void traversal). Expression builder with real-time notation display, traversal state grid, and dimensional path visualization canvas.
- **Formal notation specification** -- `MATHME.md` defines the Omnidirectional Mathematics system: core axiom, operation semantics, state model, and examples.
- **25 omnidirectional tests** -- Covering all 14 operators (including metaCW/metaCCW), void annihilation, the Earth-to-Celestial example, and property verification.

## [v1.0.0] - 2026-02-10

### Added
- **Eight mathematical universes** -- Real, Complex, Modular, Matrix, Quaternion, Boolean, Tropical, and Dual numbers, each with dedicated input layout, math engine, and accent color.
- **Real Numbers** -- Scientific calculator with trig, powers, roots, logarithms, constants (pi, e), keyboard support.
- **Complex Numbers** -- Full complex arithmetic with live Argand diagram visualization.
- **Modular Arithmetic** -- Clock arithmetic with fast binary modular exponentiation and extended Euclidean algorithm for inverses.
- **Matrix Algebra** -- 2x2 and 3x3 matrix operations (add, multiply, determinant via cofactor expansion, adjugate inverse, transpose, trace).
- **Quaternions** -- Non-commutative 4D algebra following Hamilton's rules (i^2 = j^2 = k^2 = ijk = -1).
- **Boolean Algebra** -- Logic gates (AND, OR, XOR, NOT, NAND, NOR, XNOR, implication) with live truth table.
- **Tropical Semiring** -- Min-plus and max-plus conventions with tropical addition and multiplication.
- **Dual Numbers** -- Automatic differentiation via epsilon-based dual numbers (epsilon^2 = 0) with chain rule composition.
- **Dark space theme** -- Animated twinkling starfield, per-universe accent colors, smooth transitions.
- **Responsive design** -- Breakpoints at 600px and 380px for phones, tablets, and desktops.
- **History panel** -- Tracks up to 50 recent calculations across all universes.
- **Zero dependencies** -- Single HTML file, no build tools, no frameworks, no CDN imports.
- **112 tests** -- Structural validation + math engine reference tests for all 8 universes.
