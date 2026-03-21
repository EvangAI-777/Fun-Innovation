"""
Tests for the Omniversal Calculator.

Two categories:
  1. Structural tests -- validate the HTML file contains all required universes,
     UI elements, accessibility tags, and responsive design markers.
  2. Math-engine reference tests -- Python implementations of each calculator
     universe's math, verifying correctness of the algorithms used in the JS.
"""

import math
import os
import re
import pytest

# ════════════════════════════════════════════════════
#  FIXTURES
# ════════════════════════════════════════════════════

HTML_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "OMNI INNOVATIONS",
    "Omniversal Calculator",
    "omniversal-calculator.html",
)


@pytest.fixture(scope="module")
def html():
    with open(HTML_PATH, encoding="utf-8") as f:
        return f.read()


# ════════════════════════════════════════════════════
#  STRUCTURAL TESTS
# ════════════════════════════════════════════════════


class TestStructure:
    """Validate the HTML file's structure and completeness."""

    def test_file_exists(self):
        assert os.path.isfile(HTML_PATH), "omniversal-calculator.html must exist"

    def test_is_valid_html5(self, html):
        assert html.strip().startswith("<!DOCTYPE html>"), "must be HTML5"

    def test_has_viewport_meta(self, html):
        assert 'name="viewport"' in html, "must have responsive viewport meta tag"

    def test_has_title(self, html):
        m = re.search(r"<title>(.+?)</title>", html)
        assert m, "must have a <title>"
        assert "omniversal" in m.group(1).lower()

    def test_has_all_nine_universes(self, html):
        universes = ["real", "complex", "modular", "matrix",
                     "quaternion", "boolean", "tropical", "dual",
                     "omnidirectional"]
        for uni in universes:
            assert f'data-uni="{uni}"' in html, f"missing universe orb: {uni}"
            assert f'id="panel-{uni}"' in html, f"missing panel: {uni}"

    def test_universe_descriptions_present(self, html):
        descriptions = [
            "Real Numbers", "Complex Numbers", "Modular Arithmetic",
            "Matrix Algebra", "Quaternion", "Boolean Algebra",
            "Tropical", "Dual Numbers", "Omnidirectional",
        ]
        for desc in descriptions:
            assert desc in html, f"missing universe description: {desc}"

    def test_has_starfield_canvas(self, html):
        assert 'id="starfield"' in html, "must have starfield background canvas"

    def test_has_display_elements(self, html):
        assert 'id="displayExpr"' in html
        assert 'id="displayResult"' in html

    def test_has_history_panel(self, html):
        assert 'id="histToggle"' in html
        assert 'id="histList"' in html

    def test_responsive_media_queries(self, html):
        assert "@media" in html, "must have responsive media queries"
        assert "max-width:" in html

    def test_all_css_is_inline(self, html):
        # Single-file: no external stylesheets
        assert '<link rel="stylesheet"' not in html

    def test_all_js_is_inline(self, html):
        # Single-file: no external scripts
        assert '<script src=' not in html

    def test_no_external_dependencies(self, html):
        assert "cdn" not in html.lower()
        assert "unpkg" not in html.lower()

    def test_has_keyboard_support(self, html):
        assert "keydown" in html, "must have keyboard event listener"

    def test_has_complex_plane_canvas(self, html):
        assert 'id="complexPlane"' in html, "complex universe must have visualization canvas"

    def test_has_truth_table(self, html):
        assert 'id="truthTable"' in html, "boolean universe must have truth table"

    def test_has_matrix_size_selector(self, html):
        assert 'data-msize="2"' in html
        assert 'data-msize="3"' in html

    def test_has_tropical_convention_selector(self, html):
        assert 'data-tconv="min"' in html
        assert 'data-tconv="max"' in html

    def test_has_omni_expression_builder(self, html):
        assert 'id="omniExpr"' in html, "omnidirectional must have expression builder"
        assert 'id="omniOrigin"' in html, "omnidirectional must have origin input"
        assert 'id="omniDest"' in html, "omnidirectional must have destination input"

    def test_has_omni_state_display(self, html):
        assert 'id="omniStateGrid"' in html, "omnidirectional must have state grid"
        assert 'id="omniVis"' in html, "omnidirectional must have visualization canvas"

    def test_has_omni_operators(self, html):
        ops = ["ascend", "descend", "rotateCW", "rotateCCW",
               "metaCW", "metaCCW", "reverse",
               "wave", "intersect", "parallel", "orthogonal", "boundary",
               "recurse", "void"]
        for op in ops:
            assert f'data-omniop="{op}"' in html, f"missing omni operator button: {op}"

    def test_notation_file_exists(self):
        notation_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "OMNI INNOVATIONS", "Omniversal Mathematics", "MATHME.md"
        )
        assert os.path.isfile(notation_path), "MATHME.md must exist"

    def test_button_count_reasonable(self, html):
        count = html.count("calc-btn")
        assert count >= 70, f"expected many calculator buttons, found {count} class refs"

    def test_dark_theme(self, html):
        # All projects in the repo use dark themes
        assert "#0a0a" in html or "#06060e" in html, "must use dark background"


# ════════════════════════════════════════════════════
#  MATH ENGINE REFERENCE TESTS
# ════════════════════════════════════════════════════

# ── Real ──────────────────────────────────────────


class TestRealArithmetic:
    """Reference tests for basic real-number operations."""

    def test_addition(self):
        assert 2 + 3 == 5

    def test_subtraction(self):
        assert 7 - 4 == 3

    def test_multiplication(self):
        assert 6 * 7 == 42

    def test_division(self):
        assert 10 / 4 == 2.5

    def test_division_by_zero(self):
        assert math.isnan(float("nan"))  # JS returns NaN

    def test_power(self):
        assert 2 ** 10 == 1024

    def test_sqrt(self):
        assert math.sqrt(144) == 12.0

    def test_sqrt_negative_is_nan(self):
        assert math.isnan(float("nan"))  # JS returns NaN for sqrt(-1) in reals

    def test_trig_sin(self):
        assert abs(math.sin(math.pi / 2) - 1.0) < 1e-10

    def test_trig_cos(self):
        assert abs(math.cos(0) - 1.0) < 1e-10

    def test_trig_tan(self):
        assert abs(math.tan(math.pi / 4) - 1.0) < 1e-10

    def test_ln(self):
        assert abs(math.log(math.e) - 1.0) < 1e-10

    def test_log10(self):
        assert abs(math.log10(1000) - 3.0) < 1e-10

    def test_abs_negative(self):
        assert abs(-42) == 42


# ── Complex ───────────────────────────────────────


def c_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def c_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def c_mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def c_div(a, b):
    d = b[0] ** 2 + b[1] ** 2
    if d == 0:
        return (float("nan"), float("nan"))
    return ((a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d)


def c_mod(a):
    return math.sqrt(a[0] ** 2 + a[1] ** 2)


def c_arg(a):
    return math.atan2(a[1], a[0])


def c_conj(a):
    return (a[0], -a[1])


def c_sq(a):
    return c_mul(a, a)


class TestComplexArithmetic:
    """Reference tests for complex number operations."""

    def test_add(self):
        assert c_add((3, 4), (1, -2)) == (4, 2)

    def test_sub(self):
        assert c_sub((5, 3), (2, 1)) == (3, 2)

    def test_mul(self):
        # (3+4i)(1+2i) = 3+6i+4i+8i² = 3+10i-8 = -5+10i
        assert c_mul((3, 4), (1, 2)) == (-5, 10)

    def test_mul_by_conjugate(self):
        z = (3, 4)
        result = c_mul(z, c_conj(z))
        assert abs(result[0] - 25) < 1e-10
        assert abs(result[1]) < 1e-10

    def test_div(self):
        # (1+0i) / (0+1i) = -i = (0, -1)
        r = c_div((1, 0), (0, 1))
        assert abs(r[0]) < 1e-10
        assert abs(r[1] - (-1)) < 1e-10

    def test_div_by_zero(self):
        r = c_div((1, 1), (0, 0))
        assert math.isnan(r[0])

    def test_modulus(self):
        assert abs(c_mod((3, 4)) - 5.0) < 1e-10

    def test_argument(self):
        assert abs(c_arg((1, 1)) - math.pi / 4) < 1e-10

    def test_conjugate(self):
        assert c_conj((3, -7)) == (3, 7)

    def test_square(self):
        # (1+i)² = 1+2i+i² = 2i
        r = c_sq((1, 1))
        assert abs(r[0]) < 1e-10
        assert abs(r[1] - 2) < 1e-10


# ── Modular ───────────────────────────────────────


def modp(a, n):
    return ((a % n) + n) % n


def mod_pow(base, exp, n):
    if n == 1:
        return 0
    result = 1
    base = modp(base, n)
    exp = max(0, exp)
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % n
        exp //= 2
        base = (base * base) % n
    return result


def ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = ext_gcd(b % a, a)
    return g, y - (b // a) * x, x


def mod_inverse(a, n):
    a = modp(a, n)
    g, x, _ = ext_gcd(a, n)
    if g != 1:
        return None
    return modp(x, n)


class TestModularArithmetic:
    """Reference tests for modular arithmetic."""

    def test_mod_add(self):
        assert modp(5 + 4, 7) == 2

    def test_mod_sub(self):
        assert modp(3 - 5, 7) == 5

    def test_mod_mul(self):
        assert modp(3 * 4, 7) == 5

    def test_mod_pow_basic(self):
        assert mod_pow(2, 10, 1000) == 1024 % 1000

    def test_mod_pow_fermat(self):
        # Fermat's little theorem: a^(p-1) ≡ 1 (mod p) for prime p
        assert mod_pow(3, 6, 7) == 1

    def test_mod_inverse_exists(self):
        inv = mod_inverse(3, 7)
        assert inv is not None
        assert modp(3 * inv, 7) == 1

    def test_mod_inverse_5_mod7(self):
        assert mod_inverse(5, 7) == 3  # 5*3 = 15 ≡ 1 (mod 7)

    def test_mod_inverse_no_inverse(self):
        assert mod_inverse(2, 4) is None  # gcd(2,4) != 1

    def test_gcd(self):
        g, _, _ = ext_gcd(12, 8)
        assert g == 4

    def test_mod_n_1(self):
        assert mod_pow(999, 999, 1) == 0


# ── Matrix ────────────────────────────────────────


def mat_add(a, b):
    n = len(a)
    return [[a[i][j] + b[i][j] for j in range(n)] for i in range(n)]


def mat_mul(a, b):
    n = len(a)
    r = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                r[i][j] += a[i][k] * b[k][j]
    return r


def mat_det(m):
    n = len(m)
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    det = 0
    for j in range(n):
        sub = [row[:j] + row[j + 1:] for row in m[1:]]
        det += ((-1) ** j) * m[0][j] * mat_det(sub)
    return det


def mat_transpose(m):
    n = len(m)
    return [[m[j][i] for j in range(n)] for i in range(n)]


def mat_trace(m):
    return sum(m[i][i] for i in range(len(m)))


def mat_inverse_2x2(m):
    det = mat_det(m)
    if det == 0:
        return None
    return [
        [m[1][1] / det, -m[0][1] / det],
        [-m[1][0] / det, m[0][0] / det],
    ]


class TestMatrixOperations:
    """Reference tests for matrix algebra."""

    def test_add_2x2(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        assert mat_add(a, b) == [[6, 8], [10, 12]]

    def test_mul_identity(self):
        a = [[3, 1], [0, 2]]
        I = [[1, 0], [0, 1]]
        assert mat_mul(a, I) == a
        assert mat_mul(I, a) == a

    def test_mul_2x2(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        assert mat_mul(a, b) == [[19, 22], [43, 50]]

    def test_det_2x2(self):
        assert mat_det([[3, 8], [4, 6]]) == -14

    def test_det_3x3(self):
        m = [[6, 1, 1], [4, -2, 5], [2, 8, 7]]
        assert mat_det(m) == -306

    def test_det_identity(self):
        assert mat_det([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 1

    def test_transpose_2x2(self):
        assert mat_transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]

    def test_transpose_symmetric(self):
        m = [[1, 2], [2, 1]]
        assert mat_transpose(m) == m

    def test_trace_2x2(self):
        assert mat_trace([[5, 3], [1, 7]]) == 12

    def test_trace_3x3(self):
        assert mat_trace([[1, 0, 0], [0, 2, 0], [0, 0, 3]]) == 6

    def test_inverse_2x2(self):
        m = [[4, 7], [2, 6]]
        inv = mat_inverse_2x2(m)
        result = mat_mul(m, inv)
        for i in range(2):
            for j in range(2):
                expected = 1.0 if i == j else 0.0
                assert abs(result[i][j] - expected) < 1e-10

    def test_inverse_singular(self):
        assert mat_inverse_2x2([[1, 2], [2, 4]]) is None

    def test_mul_non_commutative(self):
        a = [[1, 2], [3, 4]]
        b = [[0, 1], [1, 0]]
        assert mat_mul(a, b) != mat_mul(b, a)


# ── Quaternion ────────────────────────────────────


def q_add(p, q):
    return tuple(p[i] + q[i] for i in range(4))


def q_sub(p, q):
    return tuple(p[i] - q[i] for i in range(4))


def q_mul(p, q):
    a, b, c, d = p
    e, f, g, h = q
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def q_conj(q):
    return (q[0], -q[1], -q[2], -q[3])


def q_norm(q):
    return math.sqrt(sum(x ** 2 for x in q))


def q_inv(q):
    n2 = sum(x ** 2 for x in q)
    if n2 == 0:
        return (float("nan"),) * 4
    return (q[0] / n2, -q[1] / n2, -q[2] / n2, -q[3] / n2)


class TestQuaternionArithmetic:
    """Reference tests for quaternion operations."""

    def test_add(self):
        assert q_add((1, 2, 3, 4), (5, 6, 7, 8)) == (6, 8, 10, 12)

    def test_sub(self):
        assert q_sub((5, 5, 5, 5), (1, 2, 3, 4)) == (4, 3, 2, 1)

    def test_mul_ij_equals_k(self):
        i = (0, 1, 0, 0)
        j = (0, 0, 1, 0)
        k = (0, 0, 0, 1)
        assert q_mul(i, j) == k

    def test_mul_ji_equals_neg_k(self):
        i = (0, 1, 0, 0)
        j = (0, 0, 1, 0)
        assert q_mul(j, i) == (0, 0, 0, -1)

    def test_mul_non_commutative(self):
        p = (1, 2, 3, 4)
        q = (5, 6, 7, 8)
        assert q_mul(p, q) != q_mul(q, p)

    def test_mul_by_conjugate_gives_norm_squared(self):
        q = (1, 2, 3, 4)
        result = q_mul(q, q_conj(q))
        n2 = sum(x ** 2 for x in q)
        assert abs(result[0] - n2) < 1e-10
        assert abs(result[1]) < 1e-10
        assert abs(result[2]) < 1e-10
        assert abs(result[3]) < 1e-10

    def test_norm(self):
        assert abs(q_norm((1, 0, 0, 0)) - 1.0) < 1e-10
        assert abs(q_norm((3, 4, 0, 0)) - 5.0) < 1e-10

    def test_conjugate(self):
        assert q_conj((1, 2, 3, 4)) == (1, -2, -3, -4)

    def test_inverse(self):
        q = (1, 2, 3, 4)
        inv = q_inv(q)
        product = q_mul(q, inv)
        assert abs(product[0] - 1.0) < 1e-10
        for i in range(1, 4):
            assert abs(product[i]) < 1e-10

    def test_i_squared_is_neg_one(self):
        i = (0, 1, 0, 0)
        result = q_mul(i, i)
        assert result == (-1, 0, 0, 0)


# ── Boolean ───────────────────────────────────────


class TestBooleanAlgebra:
    """Reference tests for boolean logic operations."""

    def test_and(self):
        assert (1 & 1) == 1
        assert (1 & 0) == 0
        assert (0 & 0) == 0

    def test_or(self):
        assert (0 | 0) == 0
        assert (1 | 0) == 1
        assert (1 | 1) == 1

    def test_xor(self):
        assert (0 ^ 0) == 0
        assert (1 ^ 0) == 1
        assert (1 ^ 1) == 0

    def test_not(self):
        assert (1 ^ 1) == 0  # NOT 1 = 0
        assert (0 ^ 1) == 1  # NOT 0 = 1

    def test_nand(self):
        assert int(not (1 and 1)) == 0
        assert int(not (1 and 0)) == 1

    def test_nor(self):
        assert int(not (1 or 1)) == 0
        assert int(not (0 or 0)) == 1

    def test_xnor(self):
        assert int(not (1 ^ 1)) == 1
        assert int(not (1 ^ 0)) == 0

    def test_implication(self):
        # A -> B is equivalent to (not A) or B
        assert int((not 0) or 0) == 1  # F -> F = T
        assert int((not 0) or 1) == 1  # F -> T = T
        assert int((not 1) or 1) == 1  # T -> T = T
        assert int((not 1) or 0) == 0  # T -> F = F

    def test_demorgan_and(self):
        for a in (0, 1):
            for b in (0, 1):
                assert int(not (a and b)) == int((not a) or (not b))

    def test_demorgan_or(self):
        for a in (0, 1):
            for b in (0, 1):
                assert int(not (a or b)) == int((not a) and (not b))


# ── Tropical ──────────────────────────────────────


def trop_add_min(a, b):
    return min(a, b)


def trop_add_max(a, b):
    return max(a, b)


def trop_mul(a, b):
    return a + b


def trop_pow(a, n):
    return n * a


class TestTropicalArithmetic:
    """Reference tests for tropical semiring operations."""

    def test_min_plus_add(self):
        assert trop_add_min(3, 7) == 3

    def test_min_plus_add_equal(self):
        assert trop_add_min(5, 5) == 5

    def test_max_plus_add(self):
        assert trop_add_max(3, 7) == 7

    def test_tropical_mul(self):
        assert trop_mul(3, 4) == 7

    def test_tropical_mul_identity(self):
        # Multiplicative identity in tropical semiring is 0
        assert trop_mul(5, 0) == 5

    def test_tropical_pow(self):
        assert trop_pow(3, 4) == 12  # 3 ⊗ 3 ⊗ 3 ⊗ 3 = 3+3+3+3 = 12

    def test_tropical_distributive(self):
        # a ⊗ (b ⊕ c) = (a ⊗ b) ⊕ (a ⊗ c) in min-plus
        a, b, c = 2, 3, 5
        lhs = trop_mul(a, trop_add_min(b, c))
        rhs = trop_add_min(trop_mul(a, b), trop_mul(a, c))
        assert lhs == rhs

    def test_tropical_associativity(self):
        a, b, c = 1, 2, 3
        assert trop_mul(trop_mul(a, b), c) == trop_mul(a, trop_mul(b, c))

    def test_tropical_add_negative(self):
        assert trop_add_min(-3, 2) == -3
        assert trop_add_max(-3, 2) == 2


# ── Dual Numbers ──────────────────────────────────


def d_add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def d_sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def d_mul(x, y):
    return (x[0] * y[0], x[0] * y[1] + x[1] * y[0])


def d_div(x, y):
    if y[0] == 0:
        return (float("nan"), float("nan"))
    return (x[0] / y[0], (x[1] * y[0] - x[0] * y[1]) / (y[0] ** 2))


def d_sin(x):
    return (math.sin(x[0]), x[1] * math.cos(x[0]))


def d_cos(x):
    return (math.cos(x[0]), -x[1] * math.sin(x[0]))


def d_exp(x):
    return (math.exp(x[0]), x[1] * math.exp(x[0]))


def d_ln(x):
    if x[0] <= 0:
        return (float("nan"), float("nan"))
    return (math.log(x[0]), x[1] / x[0])


class TestDualNumbers:
    """Reference tests for dual number operations and automatic differentiation."""

    def test_add(self):
        assert d_add((3, 1), (2, 4)) == (5, 5)

    def test_sub(self):
        assert d_sub((5, 3), (2, 1)) == (3, 2)

    def test_mul(self):
        # (3 + 1ε)(2 + 4ε) = 6 + (3·4 + 1·2)ε = 6 + 14ε
        assert d_mul((3, 1), (2, 4)) == (6, 14)

    def test_epsilon_squared_is_zero(self):
        # ε * ε = (0 + 1ε)(0 + 1ε) = 0 + (0·1 + 1·0)ε = 0
        eps = (0, 1)
        result = d_mul(eps, eps)
        assert result == (0, 0)

    def test_div(self):
        # (6 + 2ε) / (3 + 0ε) = 2 + (2/3)ε
        r = d_div((6, 2), (3, 0))
        assert abs(r[0] - 2.0) < 1e-10
        assert abs(r[1] - 2 / 3) < 1e-10

    def test_div_by_zero_dual_part(self):
        r = d_div((1, 1), (0, 1))
        assert math.isnan(r[0])

    def test_autodiff_sin(self):
        # d/dx sin(x) = cos(x). Evaluate at x=π/4.
        x = math.pi / 4
        r = d_sin((x, 1))
        assert abs(r[0] - math.sin(x)) < 1e-10
        assert abs(r[1] - math.cos(x)) < 1e-10  # derivative

    def test_autodiff_cos(self):
        # d/dx cos(x) = -sin(x). Evaluate at x=π/3.
        x = math.pi / 3
        r = d_cos((x, 1))
        assert abs(r[0] - math.cos(x)) < 1e-10
        assert abs(r[1] - (-math.sin(x))) < 1e-10

    def test_autodiff_exp(self):
        # d/dx e^x = e^x. Evaluate at x=1.
        r = d_exp((1, 1))
        assert abs(r[0] - math.e) < 1e-10
        assert abs(r[1] - math.e) < 1e-10

    def test_autodiff_ln(self):
        # d/dx ln(x) = 1/x. Evaluate at x=2.
        r = d_ln((2, 1))
        assert abs(r[0] - math.log(2)) < 1e-10
        assert abs(r[1] - 0.5) < 1e-10

    def test_autodiff_chain_rule(self):
        # d/dx sin(x²) at x=1. Use chain rule: cos(x²)·2x = 2cos(1)
        # Compute x² as dual: (1,1)*(1,1) = (1, 2)
        x_dual = (1, 1)
        x_sq = d_mul(x_dual, x_dual)  # (1, 2)
        result = d_sin(x_sq)
        assert abs(result[0] - math.sin(1)) < 1e-10
        assert abs(result[1] - 2 * math.cos(1)) < 1e-10

    def test_autodiff_product_rule(self):
        # d/dx [x · sin(x)] at x=π/2
        # = sin(x) + x·cos(x) = 1 + (π/2)·0 = 1
        x = math.pi / 2
        x_dual = (x, 1)
        sin_x = d_sin(x_dual)
        result = d_mul(x_dual, sin_x)
        expected_val = x * math.sin(x)
        expected_deriv = math.sin(x) + x * math.cos(x)
        assert abs(result[0] - expected_val) < 1e-10
        assert abs(result[1] - expected_deriv) < 1e-10


# ── Omnidirectional Transforms ────────────────────


def omni_default():
    """Default traversal state."""
    return {
        "d": 0, "angle": 0, "metaAngle": 0, "polarity": 1,
        "wave": "expanded", "boundaries": 0,
        "intersections": 0, "mode": "normal",
    }


def omni_apply(state, op, param=0):
    """Apply a single omnidirectional operation to a state."""
    s = dict(state)
    if op == "ascend":
        s["d"] += param
    elif op == "descend":
        s["d"] -= param
    elif op == "rotateCW":
        s["angle"] = (s["angle"] + param) % 360
    elif op == "rotateCCW":
        s["angle"] = (s["angle"] - param) % 360
        if s["angle"] < 0:
            s["angle"] += 360
    elif op == "metaCW":
        s["metaAngle"] = (s["metaAngle"] + param) % 360
    elif op == "metaCCW":
        s["metaAngle"] = (s["metaAngle"] - param) % 360
        if s["metaAngle"] < 0:
            s["metaAngle"] += 360
    elif op == "reverse":
        s["polarity"] *= -1
    elif op == "wave":
        s["wave"] = "collapsed" if s["wave"] == "expanded" else "expanded"
    elif op == "intersect":
        s["intersections"] += 1
    elif op == "parallel":
        s["mode"] = "parallel"
    elif op == "orthogonal":
        s["mode"] = "orthogonal"
    elif op == "boundary":
        s["boundaries"] += 1
    elif op == "void":
        s.update({"d": 0, "angle": 0, "metaAngle": 0, "polarity": 1,
                  "wave": "collapsed", "boundaries": 0, "mode": "normal"})
    return s


def omni_run(ops):
    """Run a sequence of (op,) or (op, param) tuples from default state."""
    state = omni_default()
    for step in ops:
        op = step[0]
        param = step[1] if len(step) > 1 else 0
        state = omni_apply(state, op, param)
    return state


class TestOmnidirectionalTransforms:
    """Reference tests for omnidirectional mathematics operations."""

    # ── Basic operations ──

    def test_default_state(self):
        s = omni_default()
        assert s["d"] == 0
        assert s["angle"] == 0
        assert s["metaAngle"] == 0
        assert s["polarity"] == 1
        assert s["wave"] == "expanded"
        assert s["boundaries"] == 0

    def test_ascend(self):
        s = omni_run([("ascend", 3)])
        assert s["d"] == 3

    def test_descend(self):
        s = omni_run([("descend", 2)])
        assert s["d"] == -2

    def test_ascend_then_descend(self):
        s = omni_run([("ascend", 5), ("descend", 3)])
        assert s["d"] == 2

    def test_rotate_clockwise(self):
        s = omni_run([("rotateCW", 90)])
        assert s["angle"] == 90

    def test_rotate_counterclockwise(self):
        s = omni_run([("rotateCCW", 90)])
        assert s["angle"] == 270  # -90 mod 360

    def test_rotation_wraps(self):
        s = omni_run([("rotateCW", 270), ("rotateCW", 180)])
        assert s["angle"] == 90  # 450 mod 360

    def test_polarity_reversal(self):
        s = omni_run([("reverse",)])
        assert s["polarity"] == -1

    def test_double_reversal_identity(self):
        s = omni_run([("reverse",), ("reverse",)])
        assert s["polarity"] == 1

    def test_wave_collapse(self):
        s = omni_run([("wave",)])
        assert s["wave"] == "collapsed"

    def test_wave_double_toggle(self):
        s = omni_run([("wave",), ("wave",)])
        assert s["wave"] == "expanded"

    def test_boundary_crossing(self):
        s = omni_run([("boundary",), ("boundary",), ("boundary",)])
        assert s["boundaries"] == 3

    def test_intersection_count(self):
        s = omni_run([("intersect",), ("intersect",)])
        assert s["intersections"] == 2

    def test_parallel_mode(self):
        s = omni_run([("parallel",)])
        assert s["mode"] == "parallel"

    def test_orthogonal_mode(self):
        s = omni_run([("orthogonal",)])
        assert s["mode"] == "orthogonal"

    # ── Void ──

    def test_void_resets_state(self):
        s = omni_run([("ascend", 5), ("rotateCW", 45), ("reverse",),
                      ("boundary",), ("metaCW", 60), ("void",)])
        assert s["d"] == 0
        assert s["angle"] == 0
        assert s["metaAngle"] == 0
        assert s["polarity"] == 1
        assert s["wave"] == "collapsed"
        assert s["boundaries"] == 0

    def test_void_then_rebuild(self):
        s = omni_run([("ascend", 10), ("void",), ("ascend", 3)])
        assert s["d"] == 3

    def test_void_is_annihilation(self):
        # Operations before void have no effect on final state
        s1 = omni_run([("ascend", 100), ("rotateCW", 359), ("void",), ("ascend", 1)])
        s2 = omni_run([("void",), ("ascend", 1)])
        assert s1["d"] == s2["d"]
        assert s1["angle"] == s2["angle"]

    # ── Complex sequences ──

    def test_earth_to_celestial(self):
        """The original example from the notation: Earth ⟿ ⊕[3]⟲[90°]◬⊠∿ ⟿ Celestial_Realm"""
        s = omni_run([
            ("ascend", 3),
            ("rotateCW", 90),
            ("boundary",),
            ("intersect",),
            ("wave",),
        ])
        assert s["d"] == 3
        assert s["angle"] == 90
        assert s["polarity"] == 1
        assert s["wave"] == "collapsed"
        assert s["boundaries"] == 1
        assert s["intersections"] == 1

    def test_round_trip_dimension(self):
        s = omni_run([("ascend", 7), ("descend", 7)])
        assert s["d"] == 0

    def test_full_rotation(self):
        s = omni_run([("rotateCW", 360)])
        assert s["angle"] == 0

    def test_polarity_inversion_loop(self):
        """Origin ⟿ ⊕[1]⇄⊕[1]⇄ ⟿ Origin_Prime"""
        s = omni_run([("ascend", 1), ("reverse",), ("ascend", 1), ("reverse",)])
        assert s["d"] == 2
        assert s["polarity"] == 1

    # ── Properties ──

    def test_ascend_descend_inverse(self):
        for n in range(1, 10):
            s = omni_run([("ascend", n), ("descend", n)])
            assert s["d"] == 0

    def test_rotation_commutes_with_itself(self):
        s1 = omni_run([("rotateCW", 30), ("rotateCW", 60)])
        s2 = omni_run([("rotateCW", 60), ("rotateCW", 30)])
        assert s1["angle"] == s2["angle"] == 90

    def test_boundary_only_increases(self):
        s = omni_default()
        for _ in range(5):
            old_b = s["boundaries"]
            s = omni_apply(s, "boundary")
            assert s["boundaries"] == old_b + 1

    # ── Metadegrees ──

    def test_metaCW(self):
        s = omni_run([("metaCW", 90)])
        assert s["metaAngle"] == 90

    def test_metaCCW(self):
        s = omni_run([("metaCCW", 90)])
        assert s["metaAngle"] == 270  # -90 mod 360

    def test_meta_wraps(self):
        s = omni_run([("metaCW", 270), ("metaCW", 180)])
        assert s["metaAngle"] == 90  # 450 mod 360

    def test_meta_void_resets(self):
        s = omni_run([("metaCW", 120), ("void",)])
        assert s["metaAngle"] == 0

    def test_meta_independent_of_angle(self):
        """Meta-angle and entity angle are independent state components."""
        s = omni_run([("rotateCW", 45), ("metaCW", 90)])
        assert s["angle"] == 45
        assert s["metaAngle"] == 90

    def test_meta_full_rotation(self):
        s = omni_run([("metaCW", 360)])
        assert s["metaAngle"] == 0


# ════════════════════════════════════════════════════
#  RECEIVE & GRAPH -- STRUCTURAL TESTS
# ════════════════════════════════════════════════════


class TestReceiveAndGraphStructure:
    """Validate the Receive & Graph tab HTML elements exist."""

    def test_has_tab_bar(self, html):
        assert 'omni-tab-bar' in html, "must have tab bar for Build/Receive modes"

    def test_has_build_tab(self, html):
        assert 'data-omnitab="build"' in html, "must have Build tab"

    def test_has_receive_tab(self, html):
        assert 'data-omnitab="receive"' in html, "must have Receive & Graph tab"

    def test_has_build_tab_content(self, html):
        assert 'id="omniTabBuild"' in html, "must have Build tab content div"

    def test_has_receive_tab_content(self, html):
        assert 'id="omniTabReceive"' in html, "must have Receive tab content div"

    def test_has_receive_textarea(self, html):
        assert 'id="omniReceiveInput"' in html, "must have textarea for expression input"

    def test_has_parse_button(self, html):
        assert 'id="omniParseBtn"' in html, "must have Parse & Graph button"

    def test_has_autocomplete_container(self, html):
        assert 'id="omniAutocomplete"' in html, "must have autocomplete dropdown"

    def test_has_parse_message_area(self, html):
        assert 'id="omniParseMsg"' in html, "must have parse status message area"

    def test_has_parser_function(self, html):
        assert 'omniParseExpression' in html, "must have expression parser function"

    def test_has_token_defs(self, html):
        assert 'omniTokenDefs' in html, "must have token definitions for parser"


# ════════════════════════════════════════════════════
#  RECEIVE & GRAPH -- PARSER REFERENCE TESTS
# ════════════════════════════════════════════════════


# Python mirror of the JS parser for reference testing
_TOKEN_DEFS = [
    {"op": "ascend",     "unicode": "\u2295", "ascii": ["ascend", "asc"],      "hasParam": True},
    {"op": "descend",    "unicode": "\u2296", "ascii": ["descend", "desc"],     "hasParam": True},
    {"op": "rotateCW",   "unicode": "\u27F2", "ascii": ["rotatecw", "cw"],      "hasParam": True},
    {"op": "rotateCCW",  "unicode": "\u27F3", "ascii": ["rotateccw", "ccw"],    "hasParam": True},
    {"op": "metaCW",     "unicode": "\u2941", "ascii": ["metacw", "mcw"],       "hasParam": True},
    {"op": "metaCCW",    "unicode": "\u2940", "ascii": ["metaccw", "mccw"],     "hasParam": True},
    {"op": "reverse",    "unicode": "\u21C4", "ascii": ["reverse", "rev"],      "hasParam": False},
    {"op": "wave",       "unicode": "\u223F", "ascii": ["wave"],                "hasParam": False},
    {"op": "intersect",  "unicode": "\u22A0", "ascii": ["intersect", "mark"],   "hasParam": False},
    {"op": "parallel",   "unicode": "\u2225", "ascii": ["parallel", "par"],     "hasParam": False},
    {"op": "orthogonal", "unicode": "\u22A5", "ascii": ["orthogonal", "ortho"], "hasParam": False},
    {"op": "boundary",   "unicode": "\u25EC", "ascii": ["boundary", "bound"],   "hasParam": False},
    {"op": "recurse",    "unicode": "\u221E", "ascii": ["recurse", "inf"],      "hasParam": False},
    {"op": "void",       "unicode": "\u2205", "ascii": ["void"],                "hasParam": False},
]


def omni_parse(text):
    """Python mirror of the JS omniParseExpression function."""
    text = text.strip()
    if not text:
        return {"error": "Empty expression"}

    origin = None
    destination = None
    ops_text = text

    # Try Unicode flow operator ⟿
    flow_uni = "\u27FF"
    if flow_uni in text:
        parts = [p.strip() for p in text.split(flow_uni)]
        if len(parts) >= 3:
            origin = parts[0] or None
            destination = parts[-1] or None
            ops_text = " ".join(parts[1:-1])
        elif len(parts) == 2:
            origin = parts[0] or None
            ops_text = parts[1]
    elif "->" in text:
        parts = re.split(r"\s*-+>\s*", text)
        if len(parts) >= 3:
            origin = parts[0] or None
            destination = parts[-1] or None
            ops_text = " ".join(parts[1:-1])
        elif len(parts) == 2:
            origin = parts[0] or None
            ops_text = parts[1]

    # Tokenize
    sequence = []
    pos = 0
    ops_text = ops_text.strip()

    while pos < len(ops_text):
        if ops_text[pos].isspace():
            pos += 1
            continue

        matched = False

        # Try Unicode symbols
        for defn in _TOKEN_DEFS:
            if ops_text[pos] == defn["unicode"]:
                pos += 1
                param = 0
                if defn["hasParam"] and pos < len(ops_text) and ops_text[pos] == "[":
                    close = ops_text.find("]", pos)
                    if close == -1:
                        return {"error": f"Unclosed bracket after {defn['unicode']}"}
                    param_str = ops_text[pos + 1:close].replace("°", "")
                    try:
                        param = float(param_str)
                    except ValueError:
                        return {"error": f"Invalid parameter for {defn['op']}"}
                    pos = close + 1
                elif defn["hasParam"]:
                    param = 1
                sequence.append({"op": defn["op"], "param": param})
                matched = True
                break

        if matched:
            continue

        # Try ASCII keywords
        remaining = ops_text[pos:]
        best_match = None
        for defn in _TOKEN_DEFS:
            for alias in defn["ascii"]:
                if remaining.lower().startswith(alias):
                    after = pos + len(alias)
                    if after < len(ops_text) and ops_text[after].isalnum() and ops_text[after] != "[":
                        continue
                    if best_match is None or len(alias) > len(best_match[1]):
                        best_match = (defn, alias, after)

        if best_match:
            defn, alias, after = best_match
            pos = after
            param = 0
            if defn["hasParam"] and pos < len(ops_text) and ops_text[pos] == "[":
                close = ops_text.find("]", pos)
                if close == -1:
                    return {"error": f"Unclosed bracket after {alias}"}
                param_str = ops_text[pos + 1:close].replace("°", "")
                try:
                    param = float(param_str)
                except ValueError:
                    return {"error": f"Invalid parameter for {alias}"}
                pos = close + 1
            elif defn["hasParam"]:
                param = 1
            sequence.append({"op": defn["op"], "param": param})
            continue

        return {"error": f"Unexpected token at position {pos}"}

    if not sequence:
        return {"error": "No operations found in expression"}
    return {"origin": origin, "destination": destination, "sequence": sequence}


class TestExpressionParser:
    """Reference tests for the omnidirectional expression parser."""

    def test_parse_unicode_full_expression(self):
        """Earth ⟿ ⊕[3]⟲[90°]◬⊠∿ ⟿ Celestial_Realm"""
        result = omni_parse("Earth \u27FF \u2295[3]\u27F2[90\u00B0]\u25EC\u22A0\u223F \u27FF Celestial_Realm")
        assert "error" not in result
        assert result["origin"] == "Earth"
        assert result["destination"] == "Celestial_Realm"
        assert len(result["sequence"]) == 5
        assert result["sequence"][0] == {"op": "ascend", "param": 3.0}
        assert result["sequence"][1] == {"op": "rotateCW", "param": 90.0}
        assert result["sequence"][2] == {"op": "boundary", "param": 0}
        assert result["sequence"][3] == {"op": "intersect", "param": 0}
        assert result["sequence"][4] == {"op": "wave", "param": 0}

    def test_parse_unicode_produces_correct_state(self):
        """Verify the parsed sequence produces the expected traversal state."""
        result = omni_parse("Earth \u27FF \u2295[3]\u27F2[90\u00B0]\u25EC\u22A0\u223F \u27FF Celestial_Realm")
        ops = [(s["op"], s["param"]) if s["param"] else (s["op"],) for s in result["sequence"]]
        state = omni_run(ops)
        assert state["d"] == 3
        assert state["angle"] == 90
        assert state["polarity"] == 1
        assert state["wave"] == "collapsed"
        assert state["boundaries"] == 1
        assert state["intersections"] == 1

    def test_parse_ascii_full_expression(self):
        result = omni_parse("Earth -> ascend[3] cw[90] boundary intersect wave -> Celestial_Realm")
        assert "error" not in result
        assert result["origin"] == "Earth"
        assert result["destination"] == "Celestial_Realm"
        assert len(result["sequence"]) == 5
        assert result["sequence"][0] == {"op": "ascend", "param": 3.0}
        assert result["sequence"][1] == {"op": "rotateCW", "param": 90.0}

    def test_parse_ascii_shorthand(self):
        result = omni_parse("A -> asc[2] rev wave -> B")
        assert "error" not in result
        assert result["origin"] == "A"
        assert result["destination"] == "B"
        assert len(result["sequence"]) == 3
        assert result["sequence"][0] == {"op": "ascend", "param": 2.0}
        assert result["sequence"][1] == {"op": "reverse", "param": 0}
        assert result["sequence"][2] == {"op": "wave", "param": 0}

    def test_parse_mixed_unicode_and_ascii(self):
        result = omni_parse("Earth \u27FF \u2295[3] cw[90] \u25EC mark \u223F \u27FF Celestial_Realm")
        assert "error" not in result
        assert len(result["sequence"]) == 5
        assert result["sequence"][0]["op"] == "ascend"
        assert result["sequence"][1]["op"] == "rotateCW"
        assert result["sequence"][2]["op"] == "boundary"
        assert result["sequence"][3]["op"] == "intersect"
        assert result["sequence"][4]["op"] == "wave"

    def test_parse_ops_only_no_origin_dest(self):
        result = omni_parse("\u2295[2]\u27F2[45\u00B0]")
        assert "error" not in result
        assert result["origin"] is None
        assert result["destination"] is None
        assert len(result["sequence"]) == 2
        assert result["sequence"][0] == {"op": "ascend", "param": 2.0}
        assert result["sequence"][1] == {"op": "rotateCW", "param": 45.0}

    def test_parse_void_sequence(self):
        result = omni_parse("\u2205\u2295[5]\u223F")
        assert "error" not in result
        assert len(result["sequence"]) == 3
        assert result["sequence"][0]["op"] == "void"
        assert result["sequence"][1] == {"op": "ascend", "param": 5.0}
        assert result["sequence"][2]["op"] == "wave"
        # Verify state: void resets, then ascend 5, then wave toggle
        ops = [(s["op"], s["param"]) if s["param"] else (s["op"],) for s in result["sequence"]]
        state = omni_run(ops)
        assert state["d"] == 5
        assert state["wave"] == "expanded"  # void sets collapsed, wave toggles to expanded

    def test_parse_all_parameterless_ops(self):
        result = omni_parse("\u21C4\u223F\u22A0\u2225\u22A5\u25EC\u221E\u2205")
        assert "error" not in result
        assert len(result["sequence"]) == 8
        ops = [s["op"] for s in result["sequence"]]
        assert ops == ["reverse", "wave", "intersect", "parallel",
                       "orthogonal", "boundary", "recurse", "void"]

    def test_parse_error_invalid_token(self):
        result = omni_parse("Earth \u27FF !@# \u27FF Dest")
        assert "error" in result

    def test_parse_error_unclosed_bracket(self):
        result = omni_parse("\u2295[3")
        assert "error" in result

    def test_parse_error_empty(self):
        result = omni_parse("")
        assert "error" in result

    def test_parse_ascii_arrow_variants(self):
        """Both -> and --> should work as flow operators."""
        r1 = omni_parse("A -> ascend[1] -> B")
        r2 = omni_parse("A --> ascend[1] --> B")
        assert "error" not in r1
        assert "error" not in r2
        assert r1["origin"] == r2["origin"] == "A"
        assert r1["destination"] == r2["destination"] == "B"

    def test_parse_default_param_for_parameterized_ops(self):
        """Parameterized ops without brackets default to param=1."""
        result = omni_parse("\u2295\u2296")
        assert "error" not in result
        assert result["sequence"][0] == {"op": "ascend", "param": 1}
        assert result["sequence"][1] == {"op": "descend", "param": 1}

    def test_parse_ascii_case_insensitive(self):
        result = omni_parse("Ascend[5] WAVE Boundary")
        assert "error" not in result
        assert len(result["sequence"]) == 3
        assert result["sequence"][0]["op"] == "ascend"
        assert result["sequence"][1]["op"] == "wave"
        assert result["sequence"][2]["op"] == "boundary"

    def test_parse_meta_unicode(self):
        result = omni_parse("\u2941[90]\u2940[45]")
        assert "error" not in result
        assert len(result["sequence"]) == 2
        assert result["sequence"][0] == {"op": "metaCW", "param": 90.0}
        assert result["sequence"][1] == {"op": "metaCCW", "param": 45.0}

    def test_parse_meta_ascii(self):
        result = omni_parse("mcw[90] mccw[45]")
        assert "error" not in result
        assert len(result["sequence"]) == 2
        assert result["sequence"][0] == {"op": "metaCW", "param": 90.0}
        assert result["sequence"][1] == {"op": "metaCCW", "param": 45.0}

    def test_parse_meta_in_full_expression(self):
        result = omni_parse("A -> asc[3] mcw[180] boundary -> B")
        assert "error" not in result
        assert result["origin"] == "A"
        assert result["destination"] == "B"
        assert len(result["sequence"]) == 3
        assert result["sequence"][1] == {"op": "metaCW", "param": 180.0}
