"""PyCode's editing and navigation commands, which act on the active editor:
comments, indentation, marks, selections, the Python, LaTeX and Markdown
jumps, and the thin wrappers around the editor's own actions."""

from types import SimpleNamespace

import pytest

import pycode
import python_scope_build
import state
import utils
from test_editor import (
    cursor_at,
    editor,
    put,
    select,
    selected,
    shown,
    text_of,
    wait_for,
    wait_for_message,
)

pytestmark = pytest.mark.display


def lines_of(editor):
    return text_of(editor).split("\n")


def scan(editor):
    """Run the Python scope scan now, as the editor does in the background."""
    python_scope_build._python_scan_names(
        editor, editor.type_.get("1.0", "end"), editor._python_edit_generation[0]
    )


def python_editor(editor, code):
    editor.pchmode("python")
    put(editor, code)
    scan(editor)
    return editor


@pytest.fixture
def not_an_editor(app):
    """A buffer that is not an editor as the active one."""
    previous = state.active
    state.active = SimpleNamespace(hmode="normal", title="", unsaved=False)
    yield state.active
    state.active = previous


# ---------------------------------------------------------------------------
# Wrappers around the editor's actions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("function", "arguments"),
    [
        (pycode.pccopy, ()),
        (pycode.pccut, ()),
        (pycode.pcfindreplace, ()),
        (pycode.pcfindtext, ()),
        (pycode.pcget, ("1.0", "end")),
        (pycode.pcgotoline, (1,)),
        (pycode.pchmode, ("python",)),
        (pycode.pcinsert, ("1.0", "x")),
        (pycode.pcnewfile, ()),
        (pycode.pcopenfile, ()),
        (pycode.pcpageback, ()),
        (pycode.pcpageforw, ()),
        (pycode.pcpaste, ()),
        (pycode.pcredo, ()),
        (pycode.pcremoveselectionpoint, ()),
        (pycode.pcsaveasfile, ()),
        (pycode.pcsavefile, ()),
        (pycode.pcbackspace, ()),
        (pycode.pcleft, ()),
        (pycode.pcright, ()),
        (pycode.pcdeletekey, ()),
        (pycode.pcselall, ()),
        (pycode.pcsetselectionpoint, ()),
        (pycode.pcspeaktext, ()),
        (pycode.pctag, ("name", "1.0", "end")),
        (pycode.pctoggleselectionpoint, ()),
        (pycode.pcundo, ()),
        (pycode.pcuntag, ("name", "1.0", "end")),
        (pycode.pctkindex, ("1.0",)),
        (pycode.pcmovecursor, ("1.0",)),
        (pycode.pcgetselection, ()),
    ],
)
def test_wrappers_do_nothing_when_the_active_buffer_is_not_an_editor(
    not_an_editor, function, arguments
):
    assert function(*arguments) is None


def test_wrappers_act_on_the_active_editor(editor, tk_root):
    pycode.pcinsert("1.0", "hello world")
    assert pycode.pcget("1.0", "end-1c") == "hello world"

    pycode.pcselecttext("1.0", "1.5")
    pycode.pccopy()
    assert tk_root.clipboard_get() == "hello"
    pycode.pccut()
    assert text_of(editor) == " world"
    cursor_at(editor, "1.0")
    pycode.pcpaste()
    assert text_of(editor) == "hello world"
    pycode.pcundo()
    pycode.pcredo()


def test_wrappers_that_edit_use_the_editors_own_commands(editor):
    put(editor, "abc")
    cursor_at(editor, "1.3")
    pycode.pcbackspace()
    assert text_of(editor) == "ab"
    pycode.pcleft()
    assert editor.type_.index("insert") == "1.1"
    pycode.pcright()
    assert editor.type_.index("insert") == "1.2"
    pycode.pcleft()
    pycode.pcdeletekey()
    assert text_of(editor) == "a"


def test_selection_point_wrappers(editor):
    put(editor, "abc")
    cursor_at(editor, "1.1")

    pycode.pcsetselectionpoint()
    assert editor.selectionpoint == "1.1"
    pycode.pcremoveselectionpoint()
    assert editor.selectionpoint is None
    pycode.pctoggleselectionpoint()
    assert editor.selectionpoint == "1.1"


def test_tags_can_be_added_and_removed(editor):
    put(editor, "abc")
    editor.type_.tag_configure("mine")

    pycode.pctag("mine", "1.0", "1.2")
    assert editor.type_.tag_ranges("mine")
    pycode.pcuntag("mine", "1.0", "end")
    assert not editor.type_.tag_ranges("mine")


def test_the_hmode_and_go_to_line_wrappers(editor):
    put(editor, "one\ntwo")

    pycode.pchmode("latex")
    pycode.pcgotoline(2)

    assert editor.hmode == "latex"
    assert selected(editor) == "two"


def test_tk_index_resolves_references(editor):
    put(editor, "one\ntwo")
    cursor_at(editor, "2.1")

    assert pycode.pctkindex("insert") == "2.1"
    assert pycode.pctkindex("insert", "line") == "2"
    assert pycode.pctkindex("end-1c") == "2.3"


def test_move_cursor(editor):
    put(editor, "one\ntwo")

    pycode.pcmovecursor("2.2")

    assert editor.type_.index("insert") == "2.2"


def test_delete(editor):
    put(editor, "abcdef")

    pycode.pcdelete("1.1", "1.3")

    assert text_of(editor) == "adef"


def test_delete_in_another_buffer_says_so(not_an_editor, tk_root):
    pycode.pcdelete("1.0", "end")

    wait_for_message(tk_root, "not an editor")


def test_write_inserts_the_text_repeated(editor):
    pycode.pccmdwrite("ab", 3)

    assert text_of(editor) == "ababab"


def test_write_describes_newlines(editor, tk_root):
    pycode.pccmdwrite("a\nb", 1)

    assert text_of(editor) == "a\nb"
    wait_for_message(tk_root, "wrote 'a\\nb' 1 times")


def test_write_in_another_buffer_says_so(not_an_editor, tk_root):
    pycode.pccmdwrite("x", 1)

    wait_for_message(tk_root, "not an editor")


def test_the_run_command_runs_the_editors_code(editor, monkeypatch):
    calls = []
    monkeypatch.setattr(editor, "f5", lambda: calls.append(True))

    pycode.pcruncode()

    assert calls == [True]


def test_the_run_command_in_another_buffer_says_so(not_an_editor, tk_root):
    pycode.pcruncode()

    wait_for_message(tk_root, "not an editor")


# ---------------------------------------------------------------------------
# Selections, marks and clearing
# ---------------------------------------------------------------------------


def test_select_text(editor, tk_root):
    put(editor, "hello world")

    pycode.pcselecttext("1.6", "1.11")

    assert selected(editor) == "world"
    wait_for_message(tk_root, "selected text from 1.6 to 1.11")


def test_select_text_replaces_the_old_selection(editor):
    put(editor, "hello world")
    select(editor, "1.0", "1.5")

    pycode.pcselecttext("1.6", "1.11")

    assert selected(editor) == "world"


def test_get_selection(editor):
    put(editor, "hello world")
    assert pycode.pcgetselection() == ()

    select(editor, "1.0", "1.5")

    assert pycode.pcgetselection() == ("1.0", "1.5")


def test_mark_a_region_with_two_arguments_or_a_pair(editor):
    put(editor, "hello world")

    pycode.pcmark("1.0", "1.5")
    pycode.pcmark(("1.6", "1.11"))

    ranges = [str(i) for i in editor.type_.tag_ranges("marked")]
    assert ranges == ["1.0", "1.5", "1.6", "1.11"]


def test_mark_the_selection(editor):
    put(editor, "hello world")
    select(editor, "1.0", "1.5")

    pycode.pcmarkselection()

    assert [str(i) for i in editor.type_.tag_ranges("marked")] == ["1.0", "1.5"]


def test_mark_selection_without_a_selection_does_nothing(editor):
    put(editor, "hello")

    pycode.pcmarkselection()

    assert not editor.type_.tag_ranges("marked")


def test_unmark_a_region_and_all(editor):
    put(editor, "hello world")
    pycode.pcmark("1.0", "1.11")

    pycode.pcunmark("1.0", "1.5")
    assert [str(i) for i in editor.type_.tag_ranges("marked")] == ["1.5", "1.11"]
    pycode.pcunmarkall()
    assert not editor.type_.tag_ranges("marked")


@pytest.mark.parametrize(
    "call",
    [
        lambda: pycode.pcmark("1.0", "1.1"),
        lambda: pycode.pcmarkselection(),
        lambda: pycode.pcunmark("1.0", "1.1"),
        lambda: pycode.pcunmarkall(),
        lambda: pycode.pcselecttext("1.0", "1.1"),
        lambda: pycode.pccleareditor(),
        lambda: pycode.pcindentregion(1, 1),
        lambda: pycode.pcindentselection(),
        lambda: pycode.pcunindentregion(1, 1),
        lambda: pycode.pcunindentselection(),
        lambda: pycode.pccommentregion(1, 1),
        lambda: pycode.pccommentselection(),
        lambda: pycode.pcuncommentregion(1, 1),
        lambda: pycode.pcuncommentselection(),
        lambda: pycode.pcpystartof("f"),
        lambda: pycode.pcpyendof("f"),
        lambda: pycode.pcgodef("f"),
        lambda: pycode.pclatexstartof("s"),
        lambda: pycode.pcmarkdownendof("s"),
    ],
)
def test_editor_commands_say_so_in_another_buffer(not_an_editor, tk_root, call):
    call()

    wait_for_message(tk_root, "not an editor")


def test_clearing_the_editor_asks_first(editor, app):
    put(editor, "text")
    app.dialogs.answer("ask", True)

    pycode.pccleareditor()

    assert text_of(editor) == ""
    assert app.dialogs.messages("ask") == ["Clear the active editor?"]


def test_clearing_the_editor_can_be_cancelled(editor, app):
    put(editor, "text")
    app.dialogs.answer("ask", False)

    pycode.pccleareditor()

    assert text_of(editor) == "text"


# ---------------------------------------------------------------------------
# Selected lines
# ---------------------------------------------------------------------------


def test_the_selected_lines(editor):
    put(editor, "a\nb\nc\nd")
    select(editor, "2.0", "3.1")

    assert pycode.pcselectionlines() == (2, 3)


def test_a_selection_that_only_reaches_the_start_of_a_line_leaves_it_out(editor):
    put(editor, "a\nb\nc\nd")
    select(editor, "2.0", "4.0")

    assert pycode.pcselectionlines() == (2, 3)


def test_a_selection_inside_one_line(editor):
    put(editor, "abc")
    select(editor, "1.0", "1.2")

    assert pycode.pcselectionlines() == (1, 1)


def test_no_selection_has_no_lines(editor, tk_root):
    put(editor, "abc")

    assert pycode.pcselectionlines() is None
    wait_for_message(tk_root, "nothing is selected")


# ---------------------------------------------------------------------------
# Indenting
# ---------------------------------------------------------------------------


def test_indent_region_indents_the_non_blank_lines_with_tabs(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", False)
    put(editor, "a\n\nb")

    pycode.pcindentregion(1, 3)

    assert lines_of(editor) == ["\ta", "", "\tb"]


def test_indent_region_indents_with_spaces_when_chosen(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", True)
    put(editor, "a\nb")

    pycode.pcindentregion(1, 1)

    assert lines_of(editor) == ["    a", "b"]


def test_indent_selection_indents_every_selected_line_even_blank_ones(
    editor, monkeypatch
):
    monkeypatch.setattr(state, "taborspace", False)
    put(editor, "a\n\nb\nc")
    select(editor, "1.0", "3.1")

    pycode.pcindentselection()

    assert lines_of(editor) == ["\ta", "\t", "\tb", "c"]


def test_indent_selection_without_a_selection_does_nothing(editor, tk_root):
    put(editor, "a")

    pycode.pcindentselection()

    assert text_of(editor) == "a"
    wait_for_message(tk_root, "nothing is selected")


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("\tx", "x"),
        ("\t\tx", "\tx"),
        ("    x", "x"),
        ("        x", "    x"),
        ("      x", "    x"),
        ("  x", "x"),
        ("x", "x"),
        ("", ""),
        ("   ", "   "),
    ],
)
def test_unindenting_a_line(editor, before, after):
    put(editor, before)

    pycode.pcunindentregion(1, 1)

    assert text_of(editor) == after


def test_unindent_selection(editor):
    put(editor, "\ta\n\tb\n\tc")
    select(editor, "1.0", "2.2")

    pycode.pcunindentselection()

    assert lines_of(editor) == ["a", "b", "\tc"]


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


def test_comment_python_at_the_shared_indent(editor):
    python_editor(editor, "def f():\n    x = 1\n\n    y = 2")

    pycode.pccommentregion(2, 4)

    assert lines_of(editor) == ["def f():", "    # x = 1", "", "    # y = 2"]


def test_comment_python_uses_the_least_indented_line(editor):
    python_editor(editor, "if a:\n        deep\n    shallow")

    pycode.pccommentregion(2, 3)

    assert lines_of(editor) == ["if a:", "    #     deep", "    # shallow"]


def test_comment_latex_adds_a_percent_sign(editor):
    editor.pchmode("latex")
    put(editor, "a\nb")

    pycode.pccommentregion(1, 2)

    assert lines_of(editor) == ["%a", "%b"]


@pytest.mark.parametrize("mode", ["html", "markdown"])
def test_comment_html_and_markdown_wrap_the_line(editor, mode):
    editor.pchmode(mode)
    put(editor, "text")

    pycode.pccommentregion(1, 1)

    assert text_of(editor) == "<!--text-->"


def test_commenting_does_nothing_in_other_hmodes(editor):
    put(editor, "text")

    pycode.pccommentregion(1, 1)

    assert text_of(editor) == "text"


def test_uncomment_python(editor):
    python_editor(editor, "def f():\n    # x = 1\n    #y\n    z")

    pycode.pcuncommentregion(2, 4)

    assert lines_of(editor) == ["def f():", "    x = 1", "    y", "    z"]


def test_uncomment_latex(editor):
    editor.pchmode("latex")
    put(editor, "%a\nb")

    pycode.pcuncommentregion(1, 2)

    assert lines_of(editor) == ["a", "b"]


def test_uncomment_html(editor):
    editor.pchmode("html")
    put(editor, "<!--text-->")

    pycode.pcuncommentregion(1, 1)

    assert text_of(editor) == "text"


def test_commenting_and_uncommenting_are_inverses(editor):
    python_editor(editor, "a = 1\n    b = 2\n\nc = 3")
    original = text_of(editor)

    pycode.pccommentregion(1, 4)
    pycode.pcuncommentregion(1, 4)

    assert text_of(editor) == original


def test_comment_selection_uses_the_selected_lines(editor):
    python_editor(editor, "a\nb\nc")
    select(editor, "2.0", "3.1")

    pycode.pccommentselection()

    assert lines_of(editor) == ["a", "# b", "# c"]


def test_uncomment_selection_uses_the_selected_lines(editor):
    python_editor(editor, "# a\n# b\n# c")
    select(editor, "1.0", "2.3")

    pycode.pcuncommentselection()

    assert lines_of(editor) == ["a", "b", "# c"]


def test_comment_selection_without_a_selection_says_so(editor, tk_root):
    python_editor(editor, "a")

    pycode.pccommentselection()

    assert text_of(editor) == "a"
    wait_for_message(tk_root, "nothing is selected")


def test_comment_markers(editor):
    editor.hmode = "python"
    assert pycode.pccommentmarkers() == ("# ", "")
    editor.hmode = "latex"
    assert pycode.pccommentmarkers() == ("%", "")
    editor.hmode = "html"
    assert pycode.pccommentmarkers() == ("<!--", "-->")


def test_commenting_runs_the_hooks(editor):
    python_editor(editor, "a")
    seen = []
    state.pcbeforehooks["comment-region"] = [lambda value: seen.append(("b", value))]
    state.pcafterhooks["comment-region"] = [lambda value: seen.append(("a", value))]

    pycode.pccommentregion(1, 1)

    assert seen == [("b", (1, 1)), ("a", (1, 1))]


# ---------------------------------------------------------------------------
# Python navigation
# ---------------------------------------------------------------------------

PYTHON_CODE = """\
import os

class Outer:
    def method(self):
        if self:
            return 1
        else:
            return 2

    class Inner:
        def deep(self):
            pass

def top(a):
    x = a
    return x

value = 3
"""


def test_scope_chains_are_the_def_names_from_the_module_down(editor):
    python_editor(editor, PYTHON_CODE)

    chains = set(pycode.pcpyscopechains().values())

    assert chains == {
        (),
        ("Outer",),
        ("Outer", "method"),
        ("Outer", "Inner"),
        ("Outer", "Inner", "deep"),
        ("top",),
    }


def test_names_are_attribute_chains(editor):
    python_editor(editor, PYTHON_CODE)

    names = pycode.pcpynames()

    assert {
        "Outer",
        "Outer.method",
        "Outer.Inner",
        "Outer.Inner.deep",
        "top",
        "top.x",
        "top.a",
        "value",
        "os",
    } <= names


def test_jump_to_the_start_of_a_function_by_name(editor, tk_root):
    python_editor(editor, PYTHON_CODE)

    pycode.pcpystartof("Outer.method")

    assert editor.type_.index("insert") == editor.type_.index("4.end")
    wait_for_message(tk_root, "jumped to start of function 'Outer.method'")


def test_jump_to_the_end_of_a_function_by_name(editor):
    python_editor(editor, PYTHON_CODE)

    pycode.pcpyendof("top")

    assert editor.type_.index("insert") == editor.type_.index("16.end")


def test_jump_to_the_start_and_end_of_a_class(editor, tk_root):
    python_editor(editor, PYTHON_CODE)

    pycode.pcpystartof("Outer.Inner")
    assert editor.type_.index("insert") == editor.type_.index("10.end")
    wait_for_message(tk_root, "jumped to start of class 'Outer.Inner'")
    pycode.pcpyendof("Outer")
    assert editor.type_.index("insert") == editor.type_.index("12.end")


def test_jump_to_the_function_around_the_cursor(editor):
    python_editor(editor, PYTHON_CODE)
    cursor_at(editor, "6.10")

    pycode.pcpystartof("function")
    assert editor.type_.index("insert") == editor.type_.index("4.end")
    cursor_at(editor, "6.10")
    pycode.pcpyendof("f")
    assert editor.type_.index("insert") == editor.type_.index("8.end")


def test_jump_to_the_class_around_the_cursor(editor):
    python_editor(editor, PYTHON_CODE)
    cursor_at(editor, "12.12")

    pycode.pcpystartof("class")

    assert editor.type_.index("insert") == editor.type_.index("10.end")


def test_jump_to_the_innermost_function_not_the_outer_one(editor):
    python_editor(editor, PYTHON_CODE)
    cursor_at(editor, "12.12")

    pycode.pcpystartof("func")

    assert editor.type_.index("insert") == editor.type_.index("11.end")


def test_jump_to_the_block_around_the_cursor(editor, tk_root):
    python_editor(editor, PYTHON_CODE)
    cursor_at(editor, "6.12")

    pycode.pcpystartof("block")
    assert editor.type_.index("insert") == editor.type_.index("5.end")
    wait_for_message(tk_root, "jumped to start of block 'if'")
    cursor_at(editor, "6.12")
    pycode.pcpyendof("b")
    assert editor.type_.index("insert") == editor.type_.index("6.end")


@pytest.mark.parametrize(
    ("command", "line", "message"),
    [
        ("function", 1, "error: currently in no function"),
        ("class", 1, "error: currently in no class"),
        ("block", 1, "error: not in block"),
        (
            "Missing",
            1,
            "error: function or class 'Missing' does not exist in current editor",
        ),
    ],
)
def test_jumps_that_find_nothing_say_so(editor, tk_root, command, line, message):
    python_editor(editor, PYTHON_CODE)
    cursor_at(editor, f"{line}.0")

    pycode.pcpystartof(command)

    wait_for_message(tk_root, message)
    assert editor.type_.index("insert") == f"{line}.0"


def test_python_jumps_need_the_python_hmode(editor, tk_root):
    put(editor, "def f(): pass")

    pycode.pcpystartof("f")

    wait_for_message(tk_root, "not in python hmode")


def test_a_block_jump_in_code_that_does_not_parse(editor, tk_root):
    python_editor(editor, "def (:\n")

    pycode.pcpystartof("block")

    wait_for_message(tk_root, "error: cannot parse python code")


def test_go_to_definition_finds_the_nearest_binding_before_the_cursor(editor, tk_root):
    python_editor(editor, "x = 1\nprint(x)\nx = 2\nprint(x)\n")
    cursor_at(editor, "4.0")

    pycode.pcgodef("x")

    assert editor.type_.index("insert") == editor.type_.index("3.end")
    wait_for_message(tk_root, "jumped to definition of 'x'")


def test_go_to_definition_falls_back_to_the_first_binding_after_the_cursor(editor):
    python_editor(editor, "print(x)\nx = 2\n")
    cursor_at(editor, "1.0")

    pycode.pcgodef("x")

    assert editor.type_.index("insert") == editor.type_.index("2.end")


def test_go_to_definition_of_a_name_in_a_function(editor):
    python_editor(editor, PYTHON_CODE)

    pycode.pcgodef("top.x")

    assert editor.type_.index("insert") == editor.type_.index("15.end")


def test_go_to_definition_of_a_missing_name(editor, tk_root):
    python_editor(editor, "x = 1\n")

    pycode.pcgodef("nothing")

    wait_for_message(tk_root, "error: name 'nothing' does not exist in current editor")


def test_go_to_definition_needs_the_python_hmode(editor, tk_root):
    put(editor, "x = 1")

    pycode.pcgodef("x")

    wait_for_message(tk_root, "not in python hmode")


# ---------------------------------------------------------------------------
# LaTeX and Markdown navigation
# ---------------------------------------------------------------------------

LATEX = r"""\documentclass{article}
\begin{document}
\section{Intro}
Hello.

\subsection{Details}
More text. % \section{commented}

\subsubsection{Deep}
Deepest.

\section{Second}
End.
\end{document}
"""

MARKDOWN = """\
# Title
intro

## Part A
text

```
# not a heading
```

### Detail
deep

## Part B
last
"""


def test_latex_sections_have_spans_and_levels():
    spans = pycode._pclatexsections(LATEX)

    assert [(s, e, level, title) for s, e, level, title, _ in spans] == [
        (3, 10, 1, "Intro"),
        (6, 10, 2, "Details"),
        (9, 10, 3, "Deep"),
        (12, 13, 1, "Second"),
    ]


def test_latex_commented_sections_are_ignored():
    titles = [title for _, _, _, title, _ in pycode._pclatexsections(LATEX)]

    assert "commented" not in titles


def test_latex_sections_stop_at_the_end_of_the_document():
    spans = pycode._pclatexsections("\\section{A}\ntext\n\\end{document}\nafter")

    assert [(s, e) for s, e, *_ in spans] == [(1, 2)]


def test_latex_starred_and_optional_titles_are_found():
    spans = pycode._pclatexsections("\\section*{Starred}\n\\section[Short]{Long}\n")

    assert [title for _, _, _, title, _ in spans] == ["Starred", "Long"]


def test_markdown_sections_ignore_fenced_code():
    spans = pycode._pcmarkdownsections(MARKDOWN)

    assert [(s, e, level, title) for s, e, level, title, _ in spans] == [
        (1, 15, 1, "Title"),
        (4, 12, 2, "Part A"),
        (11, 12, 3, "Detail"),
        (14, 15, 2, "Part B"),
    ]


def test_markdown_headings_with_closing_hashes_and_no_title():
    spans = pycode._pcmarkdownsections("## Closed ##\n#\n")

    assert [(level, title) for _, _, level, title, _ in spans] == [
        (2, "Closed"),
        (1, ""),
    ]


def test_trailing_blank_lines_are_not_part_of_a_section():
    spans = pycode._pcsectionspans(
        ["# a", "text", "", "", "# b"], [(1, 1, "a", "x"), (5, 1, "b", "x")], 5
    )

    assert [(s, e) for s, e, *_ in spans] == [(1, 2), (5, 5)]


def test_jump_to_a_latex_section_by_title(editor, tk_root):
    editor.pchmode("latex")
    put(editor, LATEX)

    pycode.pclatexstartof("Details")
    assert editor.type_.index("insert") == editor.type_.index("6.end")
    wait_for_message(tk_root, "jumped to start of subsection 'Details'")
    pycode.pclatexendof("Details")
    assert editor.type_.index("insert") == editor.type_.index("10.end")


def test_jump_to_the_latex_section_around_the_cursor(editor):
    editor.pchmode("latex")
    put(editor, LATEX)
    cursor_at(editor, "9.0")

    pycode.pclatexstartof("section")
    assert editor.type_.index("insert") == editor.type_.index("3.end")
    cursor_at(editor, "9.0")
    pycode.pclatexstartof("subsubsection")
    assert editor.type_.index("insert") == editor.type_.index("9.end")
    cursor_at(editor, "9.0")
    pycode.pclatexstartof("ss")
    assert editor.type_.index("insert") == editor.type_.index("6.end")


def test_latex_jump_that_finds_nothing_says_so(editor, tk_root):
    editor.pchmode("latex")
    put(editor, LATEX)
    cursor_at(editor, "1.0")

    pycode.pclatexstartof("section")
    wait_for_message(tk_root, "error: currently in no section")
    pycode.pclatexstartof("Missing")
    wait_for_message(
        tk_root, "error: section 'Missing' does not exist in current editor"
    )
    pycode.pclatexstartof("chapter")
    wait_for_message(tk_root, "error: currently in no chapter")


def test_latex_jumps_need_the_latex_hmode(editor, tk_root):
    put(editor, "text")

    pycode.pclatexstartof("section")

    wait_for_message(tk_root, "not in latex hmode")


def test_jump_to_a_markdown_section(editor, tk_root):
    editor.pchmode("markdown")
    put(editor, MARKDOWN)

    pycode.pcmarkdownstartof("Part B")
    assert editor.type_.index("insert") == editor.type_.index("14.end")
    pycode.pcmarkdownendof("Title")
    assert editor.type_.index("insert") == editor.type_.index("15.end")
    pycode.pcmarkdownendof("Part A")
    assert editor.type_.index("insert") == editor.type_.index("12.end")


def test_jump_to_the_markdown_heading_of_a_level_around_the_cursor(editor, tk_root):
    editor.pchmode("markdown")
    put(editor, MARKDOWN)
    cursor_at(editor, "12.0")

    pycode.pcmarkdownstartof("h3")
    assert editor.type_.index("insert") == editor.type_.index("11.end")
    wait_for_message(tk_root, "jumped to start of h3 section 'Detail'")
    cursor_at(editor, "12.0")
    pycode.pcmarkdownstartof("section")
    assert editor.type_.index("insert") == editor.type_.index("11.end")
    cursor_at(editor, "12.0")
    pycode.pcmarkdownstartof("h1")
    assert editor.type_.index("insert") == editor.type_.index("1.end")


def test_markdown_jump_that_finds_nothing_says_so(editor, tk_root):
    editor.pchmode("markdown")
    put(editor, MARKDOWN)
    cursor_at(editor, "1.0")

    pycode.pcmarkdownstartof("h2")

    wait_for_message(tk_root, "error: currently in no h2 section")


def test_section_titles_for_autocomplete(editor):
    editor.pchmode("latex")
    put(editor, LATEX)
    assert pycode.pclatexsectiontitles() == ["Intro", "Details", "Deep", "Second"]

    editor.pchmode("markdown")
    editor.type_.delete("1.0", "end")
    put(editor, MARKDOWN)
    assert pycode.pcmarkdownsectiontitles() == ["Title", "Part A", "Detail", "Part B"]
