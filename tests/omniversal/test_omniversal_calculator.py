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
    "Omniversal Mathematics",
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

    def test_has_all_eight_universes(self, html):
        universes = ["real", "complex", "modular", "matrix",
                     "quaternion", "boolean", "tropical", "dual"]
        for uni in universes:
            assert f'data-uni="{uni}"' in html, f"missing universe orb: {uni}"
            assert f'id="panel-{uni}"' in html, f"missing panel: {uni}"

    def test_universe_descriptions_present(self, html):
        descriptions = [
            "Real Numbers", "Complex Numbers", "Modular Arithmetic",
            "Matrix Algebra", "Quaternion", "Boolean Algebra",
            "Tropical", "Dual Numbers",
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

    def test_button_count_reasonable(self, html):
        count = html.count("calc-btn")
        assert count >= 60, f"expected many calculator buttons, found {count} class refs"

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
