# Omniversal Calculator

The world's first Omniversal Calculator. Nine mathematical universes, one interface, zero dependencies.

## Quick Start

Open `omniversal-calculator.html` in any modern browser. That's it. No install, no build, no server.

## How It Works

The top of the page shows nine **universe orbs** -- glowing circles labeled with each mathematical system's symbol. Click one to enter that universe. The entire calculator transforms: the color palette shifts, the description bar updates, and the input area reconfigures itself for the selected number system.

Every universe has a genuine math engine behind it. These aren't toy implementations -- they handle edge cases (division by zero, singular matrices, non-invertible elements) and follow the actual algebraic rules of each system.

### Universe Guide

**Real Numbers (R)** -- A full expression-based scientific calculator styled after the Google/Android scientific calculator. Dark theme with four distinct button categories: light blue-gray scientific functions, cyan AC button, dark charcoal number pad, medium gray operators, and a lavender equals button. The display is fully modular -- every button press inserts into the expression at the cursor position rather than replacing it, and a blinking cursor shows where input goes. Click anywhere in the expression to reposition the cursor. Arrow keys (Left/Right/Home/End) navigate the cursor; Delete removes the character after it. Live result preview appears above the expression as you type. A recursive-descent parser evaluates expressions with proper operator precedence (parentheses > functions > exponents > multiply/divide > add/subtract), implicit multiplication (e.g., 2pi = 2*pi), and postfix operators (! for factorial, % for percentage). Features: trig functions (with Deg/Rad toggle and Inv mode for asin/acos/atan), factorial, powers, roots, logarithms, constants (pi, e), percentage, and smart parentheses. Keys: 0-9, +, -, *, /, ^, !, %, (, ), Arrow keys, Enter, Backspace, Delete, Escape.

**Complex Numbers (C)** -- Enter two complex numbers z1 and z2 as real + imaginary parts. Supports addition, subtraction, multiplication, division, modulus, argument, conjugate, and squaring. Includes a live Argand diagram that plots z1 and the result on the complex plane with a dashed line from the origin.

**Modular Arithmetic (Z_n)** -- Set a modulus n, then perform arithmetic mod n. Addition, subtraction, multiplication, modular exponentiation (using fast binary exponentiation), modular inverse (using the extended Euclidean algorithm), and GCD.

**Matrix Algebra (M)** -- Toggle between 2x2 and 3x3 matrices. Enter values for matrices A and B in bracket-wrapped grids. Supports addition, multiplication, determinant (cofactor expansion), transpose, inverse (adjugate method), and trace.

**Quaternions (H)** -- Enter two quaternions as four components (a + bi + cj + dk). Addition, subtraction, multiplication (non-commutative -- q1 x q2 is not q2 x q1), conjugate, norm, and inverse. Hamilton's multiplication rules: i^2 = j^2 = k^2 = ijk = -1.

**Boolean Algebra (B)** -- Two toggle switches for inputs A and B. Operations: AND, OR, XOR, NOT, NAND, NOR, XNOR, and material implication (A -> B). Includes a live truth table showing all input combinations.

**Tropical Semiring (T)** -- Choose between min-plus and max-plus conventions. Tropical addition (which is min or max in the conventional sense) and tropical multiplication (which is conventional addition). Used in optimization theory, phylogenetics, and tropical algebraic geometry.

**Dual Numbers (D)** -- Enter dual numbers z1 = a + b*epsilon where epsilon^2 = 0. Supports arithmetic (+, -, x, /) and functions (sin, cos, exp, ln). The key trick: set b = 1 to perform automatic differentiation. sin(3 + 1*epsilon) returns sin(3) + cos(3)*epsilon -- the value AND the derivative in one pass. Composes via chain rule automatically.

**Omnidirectional Transforms (Omega)** -- The meta-universe. Build transformation sequences across dimensional spaces using the formal Omnidirectional Mathematics notation. Name an origin and destination, then compose operations: dimensional ascension/descension, clockwise/counterclockwise rotation, polarity reversal, wave collapse/expansion, intersection marking, parallel/orthogonal modes, boundary crossing, infinite recursion marking, and void traversal. The expression builder shows the full notation in real time, the state grid tracks dimension level, angle, polarity, wave state, and boundary count, and the visualization canvas plots the transformation path through dimensional space. See [NOTATION.md](../../NOTATION.md) for the formal specification.

## Design

**Single file.** Everything -- HTML structure, CSS styles, JavaScript engines, starfield animation -- lives in one `.html` file. No dependencies, no build tools, no frameworks.

**Dark theme.** Deep space aesthetic with a twinkling starfield background. Each universe has its own accent color that tints the entire interface when selected. The Real universe features a Google/Android scientific calculator-inspired design with pill-shaped buttons in four color categories: light blue-gray for scientific functions, cyan for AC, dark charcoal for the number pad, medium gray for operators, and lavender for the equals button.

**Responsive.** Flexbox and CSS Grid with media queries at 600px and 380px breakpoints. The calculator works on phones, tablets, and desktops. Universe orbs shrink, button grids reorganize, matrix inputs compact.

**Accessible.** Full keyboard support for the real calculator including cursor navigation (arrow keys, Home, End). Clickable expression display for cursor repositioning. Clear labels. High-contrast text. Semantic HTML structure.

## Testing

137 tests in `tests/omniversal/test_omniversal_calculator.py`:

- **24 structural tests** -- validate the HTML file has all 9 universes, UI elements, responsive tags, omni operator buttons, notation file, no external dependencies, and dark theme
- **14 real arithmetic tests** -- trig, powers, roots, logarithms
- **10 complex arithmetic tests** -- all operations plus modulus, argument, conjugate
- **10 modular arithmetic tests** -- mod operations, Fermat's little theorem, extended Euclidean algorithm
- **13 matrix tests** -- addition, multiplication, determinants (2x2 and 3x3), transpose, inverse, trace, non-commutativity
- **10 quaternion tests** -- Hamilton's rules (ij=k, ji=-k, i^2=-1), non-commutativity, norm, inverse
- **10 boolean tests** -- all gates plus De Morgan's laws
- **9 tropical tests** -- both conventions, distributive law, associativity
- **12 dual number tests** -- epsilon^2=0, autodiff for sin/cos/exp/ln, chain rule, product rule
- **25 omnidirectional tests** -- all 12 operators, void annihilation, the Earth-to-Celestial example, property verification (double reversal, boundary accumulation, rotation commutativity)

Run with: `make test-omniversal`

## Colors

| Universe | Accent |
|----------|--------|
| Real | #58a6ff (blue) |
| Complex | #b48ead (purple) |
| Modular | #a3be8c (green) |
| Matrix | #88c0d0 (cyan) |
| Quaternion | #d08770 (orange) |
| Boolean | #d8dee9 (silver) |
| Tropical | #ebcb8b (gold) |
| Dual | #8fbcbb (teal) |
| Omnidirectional | #c084fc (violet) |
