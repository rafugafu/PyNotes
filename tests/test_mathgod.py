"""MathGod, the math notebook, which runs as a program of its own: its
module builds its window and runs the main loop as soon as it is run. These
tests load only the part of its source before that, which holds the math
engine, the translation of MathGod's syntax to Python and the rendering of
the results."""

import types
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pytest
import sympy

SOURCE = (Path(__file__).resolve().parent.parent / "Source" / "MathGod.py").read_text()
WINDOW_STARTS_AT = '\nplotlist = ""\ninnum = 1\n'


@pytest.fixture
def mathgod():
    """MathGod's module without its window."""
    assert WINDOW_STARTS_AT in SOURCE
    module = types.ModuleType("mathgod_under_test")
    module.__file__ = "MathGod.py"
    code = compile(SOURCE.split(WINDOW_STARTS_AT)[0], "MathGod.py", "exec")
    exec(code, module.__dict__)
    module.plotlist = ""
    module.id = 1
    module.outputboxes = {}
    module.root = types.SimpleNamespace(winfo_width=lambda: 1200)
    yield module
    module.plt.close("all")


x, y = sympy.symbols("x y")


# ---------------------------------------------------------------------------
# The math engine
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "argument", "expected"),
    [
        ("sin", 0, 0),
        ("cos", 0, 1),
        ("tan", 0, 0),
        ("asin", 1, sympy.pi / 2),
        ("acos", 1, 0),
        ("atan", 0, 0),
        ("sinh", 0, 0),
        ("cosh", 0, 1),
        ("tanh", 0, 0),
        ("asinh", 0, 0),
        ("acosh", 1, 0),
        ("atanh", 0, 0),
    ],
)
def test_trigonometric_functions(mathgod, name, argument, expected):
    assert getattr(mathgod.engine, name)(argument) == expected


def test_logarithms(mathgod):
    assert mathgod.engine.log(1) == 0
    assert mathgod.engine.log(8, 2) == 3
    assert mathgod.engine.log(sympy.E) == 1


def test_solving_an_equation(mathgod):
    assert sorted(mathgod.engine.solve(x**2 - 4, x)) == [-2, 2]


def test_derivatives(mathgod):
    assert mathgod.engine.derivative(x**3, x) == 3 * x**2
    assert mathgod.engine.derivative(x**3, x, 2) == 6 * x


def test_integrals(mathgod):
    assert mathgod.engine.integral(x**2, x) == x**3 / 3
    assert mathgod.engine.integral(x**2, x, 0, 3) == 9


def test_limits(mathgod):
    assert mathgod.engine.limit(sympy.sin(x) / x, x, 0) == 1


def test_sums_and_products(mathgod):
    assert mathgod.engine.summation(x, x, 1, 4) == 10
    assert mathgod.engine.product(x, x, 1, 4) == 24


def test_interpolation(mathgod):
    polynomial = mathgod.engine.interpolate([1, 4, 9, 16], x)

    assert sympy.simplify(polynomial.subs(x, 2) - 4) == 0


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------


def test_a_function_is_plotted_with_its_labels(mathgod):
    mathgod.engine.plotfunc(
        x**2,
        x,
        -1,
        1,
        title="Parabola",
        label="x squared",
        grid=True,
        x_label="x",
        y_label="y",
        xticks=[-1, 0, 1],
        yticks=[0, 1],
        linspace=11,
    )

    axes = mathgod.plt.gca()
    assert axes.get_title() == "Parabola"
    assert (axes.get_xlabel(), axes.get_ylabel()) == ("x", "y")
    (line,) = axes.get_lines()
    assert len(line.get_xdata()) == 11
    assert float(line.get_ydata()[0]) == 1 and float(line.get_ydata()[5]) == 0
    assert axes.get_legend() is not None


def test_a_constant_is_plotted_as_a_flat_line(mathgod):
    mathgod.engine.plotfunc(3, x, 0, 1, linspace=5)

    (line,) = mathgod.plt.gca().get_lines()
    assert list(line.get_ydata()) == [3] * 5


def test_coordinates_are_plotted(mathgod):
    mathgod.engine.plotlist2d([1, 2, 3], [4, 5, 6], title="Points", label="p")

    axes = mathgod.plt.gca()
    (line,) = axes.get_lines()
    assert list(line.get_xdata()) == [1, 2, 3]
    assert list(line.get_ydata()) == [4, 5, 6]
    assert axes.get_title() == "Points"


def test_a_3d_surface_is_shown(mathgod, monkeypatch):
    shown = []
    monkeypatch.setattr(mathgod.plt, "show", lambda: shown.append(True))

    mathgod.engine.plotfunc3d(x * y, x, y, (0, 1), (0, 1), linspace=4)

    assert shown == [True]


def test_a_constant_3d_surface(mathgod, monkeypatch):
    monkeypatch.setattr(mathgod.plt, "show", lambda: None)

    mathgod.engine.plotfunc3d(2, x, y, (0, 1), (0, 1), linspace=4)

    assert len(mathgod.plt.gcf().axes) == 1


def test_charts_are_shown(mathgod, monkeypatch):
    shown = []
    monkeypatch.setattr(mathgod.plt, "show", lambda: shown.append(True))

    mathgod.engine.piechart([1, 2, 3])
    mathgod.engine.barchart([1, 2], [3, 4])

    assert shown == [True, True]


# ---------------------------------------------------------------------------
# The shared shell
# ---------------------------------------------------------------------------


def test_the_shell_returns_what_was_printed(mathgod):
    assert mathgod.shell.ragoae("print(1 + 1)") == "2\n"


def test_the_shell_returns_the_value_of_an_expression(mathgod):
    assert mathgod.shell.ragoae("2 * 21") == "42\n"


def test_the_shell_remembers_between_lines(mathgod):
    mathgod.shell.ragoae("shared_value = 5")

    assert mathgod.shell.ragoae("shared_value + 1") == "6\n"
    assert mathgod.shell.locals["shared_value"] == 5


def test_the_shell_returns_errors_as_text(mathgod):
    assert "ZeroDivisionError" in mathgod.shell.ragoae("1 / 0")


def test_the_shell_survives_a_statement_that_exits(mathgod):
    mathgod.shell.ragoae("raise SystemExit")

    assert mathgod.shell.ragoae("1") == "1\n"


def test_the_shell_does_not_leave_the_output_redirected(mathgod):
    import sys

    before = (sys.stdout, sys.stderr)

    mathgod.shell.ragoae("print('x')")

    assert (sys.stdout, sys.stderr) == before


# ---------------------------------------------------------------------------
# Symbols and curly braces
# ---------------------------------------------------------------------------


def test_unknown_names_become_math_symbols(mathgod):
    mathgod._auto_symbols("alpha_unknown + beta_unknown * 2")

    assert mathgod.alpha_unknown == sympy.Symbol("alpha_unknown")
    assert mathgod.beta_unknown == sympy.Symbol("beta_unknown")


def test_known_names_and_builtins_are_left_alone(mathgod):
    mathgod.defined_already = 5

    mathgod._auto_symbols("defined_already + len([1])")

    assert mathgod.defined_already == 5
    assert not hasattr(mathgod, "len") or mathgod.len is not sympy.Symbol("len")


def test_assigned_names_are_not_made_symbols(mathgod):
    mathgod._auto_symbols("assigned_name = 3")

    assert not hasattr(mathgod, "assigned_name")


def test_code_that_does_not_parse_is_left_to_fail_later(mathgod):
    mathgod._auto_symbols("1 +")


def test_executing_and_evaluating_with_automatic_symbols(mathgod):
    mathgod._gexec("auto_value = auto_symbol_one ** 2")

    assert mathgod._geval("auto_value") == sympy.Symbol("auto_symbol_one") ** 2


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("{integrate x**2, x}", "engine.integral(x**2, x)"),
        ("{derivative x**2, x}", "engine.derivative(x**2, x)"),
        ("{limit sin(x)/x, x, 0}", "engine.limit(sin(x)/x, x, 0)"),
        ("{solve x**2-4, x}", "engine.solve(x**2-4, x)"),
        ("{sum x, x, 1, 4}", "engine.summation(x, x, 1, 4)"),
        ("{prod x, x, 1, 4}", "engine.product(x, x, 1, 4)"),
        ("{interpolate [1, 4], x}", "engine.interpolate([1, 4], x)"),
        ("{plot x, x, 0, 1}", "{plot x, x, 0, 1}"),
        ("{notakeyword}", "{notakeyword}"),
        ("{}", "{}"),
        ("plain text", "plain text"),
        (
            "{derivative {integrate x, x}, x}",
            "engine.derivative(engine.integral(x, x), x)",
        ),
        (
            "1 + {sum x, x, 1, 2} + {prod x, x, 1, 2}",
            "1 + engine.summation(x, x, 1, 2) + engine.product(x, x, 1, 2)",
        ),
    ],
)
def test_expanding_braces(mathgod, line, expected):
    assert mathgod.expand_braces(line) == expected


# ---------------------------------------------------------------------------
# Translating a cell
# ---------------------------------------------------------------------------


def run(mathgod, code):
    return mathgod.translate(code)


def test_an_expression_is_shown_as_latex(mathgod):
    assert run(mathgod, "x**2 + 1") == [("latex", "x^{2} + 1")]


def test_the_caret_means_a_power(mathgod):
    assert run(mathgod, "x^2") == [("latex", "x^{2}")]


def test_a_number_followed_by_a_name_is_a_product(mathgod):
    assert run(mathgod, "2x") == [("latex", "2 x")]


def test_curly_braces_run_math_operations(mathgod):
    assert run(mathgod, "{integrate x**2, x}") == [("latex", "\\frac{x^{3}}{3}")]
    assert run(mathgod, "{derivative x**3, x}") == [("latex", "3 x^{2}")]


def test_nested_braces(mathgod):
    assert run(mathgod, "{derivative {integrate x**2, x}, x}") == [("latex", "x^{2}")]


def test_an_assignment_defines_the_name_and_shows_the_value(mathgod):
    assert run(mathgod, "value_a = 3 + 4") == [("latex", "7")]
    assert run(mathgod, "value_a * 2") == [("latex", "14")]


def test_names_defined_in_one_cell_are_seen_by_the_next(mathgod):
    run(mathgod, "shared_name = 10")

    assert run(mathgod, "shared_name + 1") == [("latex", "11")]


def test_a_function_can_be_defined_and_called(mathgod):
    shown = run(mathgod, "{func double, n, n*2}")

    assert shown == [("latex", "2 n")]
    assert run(mathgod, "double(21)") == [("latex", "42")]


def test_a_function_with_several_parameters(mathgod):
    run(mathgod, "{func addup, a b, a + b}")

    assert run(mathgod, "addup(1, 2)") == [("latex", "3")]


def test_an_equation_can_be_defined_and_shown(mathgod):
    shown = run(mathgod, "{eq line1, y=2*x}")

    assert shown == [("latex", "y = 2 x")]
    assert mathgod.line1 == sympy.Eq(y, 2 * x)


def test_variables_are_symbols_until_assigned(mathgod):
    assert run(mathgod, "unassignedsymbol + 1") == [("latex", "unassignedsymbol + 1")]


def test_several_lines_in_one_cell(mathgod):
    shown = run(mathgod, "line_a = 2\nline_b = 3\nline_a * line_b")

    assert [item[1] for item in shown] == ["2", "3", "6"]


def test_blank_lines_are_ignored(mathgod):
    assert run(mathgod, "\n\n1 + 1\n\n") == [("latex", "2")]


def test_a_cell_error_is_shown_as_text(mathgod):
    shown = run(mathgod, "1 / 0")

    assert shown[0][0] == "text"
    assert "ZeroDivisionError" in shown[0][1] or "zoo" in shown[0][1]


def test_a_syntax_error_is_shown_as_text(mathgod):
    shown = run(mathgod, "1 +")

    assert shown and shown[0][0] == "text"


def test_plotting_adds_to_the_plot_and_clearplot_starts_over(mathgod, monkeypatch):
    monkeypatch.setattr(mathgod.plt, "show", lambda: None)

    run(mathgod, "{plot x, x, 0, 1}")
    assert mathgod.plotlist.count("engine.plotfunc(") == 1
    run(mathgod, "{plot x**2, x, 0, 1}")
    assert mathgod.plotlist.count("engine.plotfunc(") == 1  # each cell starts clear
    run(mathgod, "{plot x, x, 0, 1}\n{plot x**2, x, 0, 1}")
    assert mathgod.plotlist.count("engine.plotfunc(") == 2
    run(mathgod, "clearplot")
    assert mathgod.plotlist == ""


def test_a_plot_prints_its_function_as_the_output(mathgod, monkeypatch):
    monkeypatch.setattr(mathgod.plt, "show", lambda: None)

    shown = run(mathgod, "{plot x**2, x, 0, 1}")

    assert shown == [("latex", "x^{2}")]


def test_a_plot_that_fails_is_not_kept(mathgod, monkeypatch):
    monkeypatch.setattr(mathgod.plt, "show", lambda: None)

    run(mathgod, "{plot x, x, 0}")

    assert mathgod.plotlist == ""


def test_a_coordinate_plot_has_no_output(mathgod, monkeypatch):
    monkeypatch.setattr(mathgod.plt, "show", lambda: None)

    shown = run(mathgod, "{plotlist [1, 2], [3, 4]}")

    assert shown == []
    assert "engine.plotlist2d(" in mathgod.plotlist


def test_pie_and_bar_charts_are_drawn_at_once(mathgod, monkeypatch):
    shown = []
    monkeypatch.setattr(mathgod.plt, "show", lambda: shown.append(True))

    run(mathgod, "{pie [1, 2, 3]}")
    run(mathgod, "{bar [1, 2], [3, 4]}")

    assert shown == [True, True]


def test_a_3d_plot_is_drawn_at_once(mathgod, monkeypatch):
    shown = []
    monkeypatch.setattr(mathgod.plt, "show", lambda: shown.append(True))

    shown_items = run(mathgod, "{plot3 x*y, x, y, (0, 1), (0, 1)}")

    assert shown == [True]
    assert shown_items == [("latex", "x y")]


# ---------------------------------------------------------------------------
# Drawing the results
# ---------------------------------------------------------------------------


def test_latex_is_drawn_as_an_image(mathgod):
    image = mathgod._render_latex_img("x^{2} + 1")

    assert image.mode == "RGB"
    assert image.width > 5 and image.height > 5


def test_a_larger_size_or_scale_makes_a_larger_image(mathgod):
    small = mathgod._render_latex_img("x^{2}", size=12)
    large = mathgod._render_latex_img("x^{2}", size=24)
    scaled = mathgod._render_latex_img("x^{2}", size=24, scale=2.0)

    assert large.width > small.width
    assert scaled.width > large.width


def test_text_is_drawn_as_an_image(mathgod):
    one = mathgod._render_text_img("hello")
    two = mathgod._render_text_img("hello\nworld")

    assert one.mode == "RGB"
    assert two.height > one.height


def test_longer_text_is_a_wider_image(mathgod):
    assert (
        mathgod._render_text_img("a" * 40).width
        > mathgod._render_text_img("a" * 4).width
    )


class Label:
    def __init__(self):
        self.options = {}

    def config(self, **options):
        self.options.update(options)


def test_no_output_clears_the_label(mathgod):
    label = Label()

    mathgod.render_output(label, [])

    assert label.options == {"image": "", "text": ""}


def test_output_is_stacked_into_one_image(mathgod, tk_root):
    label = Label()

    mathgod.render_output(label, [("latex", "x^{2}"), ("text", "plain")])

    assert label.options["text"] == ""
    photo = label.options["image"]
    assert photo.height() > 20


def test_latex_that_cannot_be_drawn_falls_back_to_text(mathgod, tk_root, monkeypatch):
    def broken(latex):
        raise RuntimeError("no render")

    monkeypatch.setattr(mathgod, "_render_latex_img", broken)
    label = Label()

    mathgod.render_output(label, [("latex", "x")])

    assert label.options["image"].height() > 5


def test_wide_output_is_shrunk_to_the_window(mathgod, tk_root):
    mathgod.root = types.SimpleNamespace(winfo_width=lambda: 520)
    label = Label()

    mathgod.render_output(label, [("text", "w" * 200)])

    assert label.options["image"].width() <= 520 - 420 + 1


def test_the_outputs_of_a_cell_are_cached_and_drawn(mathgod, tk_root):
    label = Label()
    mathgod.outputboxes[1] = label

    result = mathgod.retranslateandprint([("latex", "x"), ("text", "y")])

    assert result == "break"
    assert mathgod.output_cache[1] == "latex\x1fx\x1etext\x1fy"
    assert "image" in label.options


def test_printing_no_output_caches_nothing_useful(mathgod, tk_root):
    mathgod.outputboxes[1] = Label()

    mathgod.retranslateandprint(None)

    assert mathgod.output_cache[1] == ""
