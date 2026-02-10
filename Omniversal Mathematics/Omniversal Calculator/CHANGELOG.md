# Omniversal Calculator Changelog

All notable changes to the Omniversal Calculator are documented here.

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
- **Omnidirectional Transforms** -- Ninth mathematical universe implementing the formal Omnidirectional Mathematics notation. Twelve fundamental operators (ascend, descend, rotate CW/CCW, polarity reversal, wave collapse/expansion, intersection, parallel, orthogonal, boundary crossing, infinite recursion, void traversal). Expression builder with real-time notation display, traversal state grid, and dimensional path visualization canvas.
- **Formal notation specification** -- `NOTATION.md` defines the Omnidirectional Mathematics system: core axiom, operation semantics, state model, and examples.
- **25 omnidirectional tests** -- Covering all 12 operators, void annihilation, the Earth-to-Celestial example, and property verification.

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
