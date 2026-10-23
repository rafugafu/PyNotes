"""PyCode: PyNotes' embedded scripting language. This module has two
halves: the language itself (pycodeparse(), the PyCode parser, which
translates PyCode source into plain Python that's then exec'd against
vars(state) by pcread()), and the pc* command functions PyCode code
calls into (each usually a thin wrapper around one editor/PyNotes
action, one per command documented in help.helppycode()).
"""

import ast
import inspect
import keyword
import os
import platform
import re
import warnings
import canvastk as ctk
import tkinter as tk
import state
from init import homedir, monospace
import editor
from utils import unbindrecur
import help
import terminal
import pythonshell
import pynotesemail
import utils
import window

PYCODE_BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}
PYCODE_CLOSING_BRACKETS = set(PYCODE_BRACKET_PAIRS.values())
PYCODE_CONTROL_PATTERN = re.compile(r"(if|elif|else|while)\b")
PYCODE_DECLARATION_PATTERN = re.compile(r"(global|nonlocal)\b")
PYCODE_RETURN_PATTERN = re.compile(r"return\b")
PYCODE_DELETE_PATTERN = re.compile(r"del\b")
PYCODE_SIMPLE_PATTERN = re.compile(r"(pass|break|continue)\b")
PYCODE_STRING_NEWLINE_PATTERN = re.compile(
    r"\\.|\n", re.DOTALL
)  # An escape, or a newline
PYCODE_NAME_PATTERN = re.compile(r"[^\W\d]\w*")
PYCODE_NUMBER_PATTERN = re.compile(r"\.?\d[\w.]*")
PYCODE_STRING_PREFIXES = {"r", "b", "u", "f", "br", "rb", "fr", "rf"}
# The keywords which are statements or values, unlike the other Python keywords
PYCODE_STATEMENT_WORDS = {
    "return",
    "global",
    "nonlocal",
    "pass",
    "break",
    "continue",
    "del",
    "while",
}
PYCODE_KEYWORD_ARGUMENT_PATTERN = re.compile(
    r"([^\W\d]\w*)\s*=(?!=)"
)  # Looks like name=, but not name==


# Maps each PyCode command name to the Python expression (usually just
# a function name in vars(state), since every module's globals end up
# there - see main.py) that the PyCode parser substitutes in when
# translating a call of the command. It is the parser's own table, so
# the plugins' PyCode commands added directly into it at startup (see
# main.py) are parsed as well.
pycode_commands = {
    "about_pynotes": "abt",
    "add_command": "pcaddcommand",
    "add_event_hook": "pcaddeventhook",
    "ask_dialog": "pcask",
    "backspace": "pcbackspace",
    "balance_buffers": "balance",
    "clear_editor": "pccleareditor",
    "close_buffer": "pcclosebuff",
    "close_pynotes": "ext",
    "comment_region": "pccommentregion",
    "comment_selection": "pccommentselection",
    "configure_fileinfo": "active.fileinfoconfig",
    "copy_selection": "pccopy",
    "copy_clipboard": "pccopytext",
    "cut_selection": "pccut",
    "delete_key": "pcdeletekey",
    "delete_text": "pcdelete",
    "dictate_text": "st",
    "download_plugins": "dp",
    "find_replace": "pcfindreplace",
    "find_text": "pcfindtext",
    "fullscreen_window": "pcfullscreen",
    "get_selection": "pcgetselection",
    "get_text": "pcget",
    "go_to_line": "pcgotoline",
    "indent_region": "pcindentregion",
    "indent_selection": "pcindentselection",
    "insert_text": "pcinsert",
    "key_bind": "pckeybind",
    "kill_pynotes": "pckillexit",
    "latex_go_to_end_of": "pclatexendof",
    "latex_go_to_start_of": "pclatexstartof",
    "mark_region": "pcmark",
    "mark_selection": "pcmarkselection",
    "markdown_go_to_end_of": "pcmarkdownendof",
    "markdown_go_to_start_of": "pcmarkdownstartof",
    "maximize_window": "pcmax",
    "minimize_window": "pcmin",
    "move_cursor": "pcmovecursor",
    "left": "pcleft",
    "right": "pcright",
    "new_editor": "neweditor",
    "new_file": "pcnewfile",
    "open_email_buffer": "pcopenemailbuf",
    "open_file": "pcopenfile",
    "open_file_new_editor": "pcneweditfile",
    "open_help": "pcopenhelp",
    "open_mathgod": "mathgod",
    "open_plugin_directory": "op",
    "open_preferences": "prf",
    "open_pycode": "pc",
    "open_python_shell": "pythonshell.openpythonshell",
    "open_terminal": "term",
    "page_back": "pcpageback",
    "page_forward": "pcpageforw",
    "paste_clipboard": "pcpaste",
    "prompt": "utils.prompt",
    "python_go_to_definition": "pcgodef",
    "python_go_to_end_of": "pcpyendof",
    "python_go_to_start_of": "pcpystartof",
    "redo_editor": "pcredo",
    "remove_selection_point": "pcremoveselectionpoint",
    "repeat_command": "pcrepeatx",
    "run_code": "pcruncode",
    "run_command": "cmdrun",
    "save_file": "pcsavefile",
    "save_file_as": "pcsaveasfile",
    "select_all": "pcselall",
    "select_text": "pcselecttext",
    "set_hmode": "pchmode",
    "set_selection_point": "pcsetselectionpoint",
    "set_variable": "pcsetvar",
    "set_window_geometry": "root.geometry",
    "set_window_title": "pcgosettitle",
    "show_message": "show",
    "show_popup": "say",
    "show_pynotes_source_code": "ss",
    "speak_selection": "pcspeaktext",
    "split_editor": "pcsplitedit",
    "switch_buffer": "setactive",
    "tag_add": "pctag",
    "tag_config": "pccolor",
    "tag_remove": "pcuntag",
    "run_shell": "pctermexec",
    "tk_index": "pctkindex",
    "toggle_selection_point": "pctoggleselectionpoint",
    "type_command": "cmd",
    "uncomment_region": "pcuncommentregion",
    "uncomment_selection": "pcuncommentselection",
    "undo_editor": "pcundo",
    "unfullscreen_window": "pcunfullscreen",
    "unindent_region": "pcunindentregion",
    "unindent_selection": "pcunindentselection",
    "unmark_all": "pcunmarkall",
    "unmark_region": "pcunmark",
    "unmaximize_window": "pcunmax",
    "sleep": "time.sleep",
    "write_editor": "pccmdwrite",
}


class PyCodeError(Exception):
    """A PyCode error in parsing."""


class PyCodeFunction:
    """A PyCode function container object used to hold and recognize
    PyCode functions in the defined dict. name is the Python name
    the function is called with.
    """

    def __init__(self, name):
        self.name = name


def pycode_error(text, index, inwhat, message):
    """Make a PyCodeError pointing at the character at index."""
    line = text.count("\n", 0, index) + 1
    column = index - text.rfind("\n", 0, index)  # rfind returns -1 if not found
    return PyCodeError(f"line {line} {inwhat}, column {column},\n{message}")


def pycode_string_ranges(text, inwhat="of code"):
    """Find the strings in the text, and return a dict
    {index of opening quote: index of closing quote}.
    """
    ranges = {}
    end = len(text)
    i = 0
    while i < end:
        quote = text[i]
        if quote in "\"'":
            j = i + 1
            while j < end and text[j] != quote:
                j += 2 if text[j] == "\\" else 1
            if j >= end:
                raise pycode_error(text, i, inwhat, f"SyntaxError: unmatched {quote!r}")
            ranges[i] = j
            i = j
        elif text[i] == "#":  # A comment; quotes in it don't count
            i = text.find("\n", i)
            if i == -1:
                break
        i += 1
    return ranges


def pycode_remove_comments(text, inwhat="of code"):
    """Replace the # comments in the text with spaces, so that
    all the indices in the text stay the same.
    """
    strings = pycode_string_ranges(text, inwhat)
    end = len(text)
    pieces = []
    last = 0
    i = 0
    while i < end:
        if i in strings:
            i = strings[i] + 1
        elif text[i] == "#":
            comment_end = text.find("\n", i)
            if comment_end == -1:
                comment_end = end
            pieces.append(text[last:i] + " " * (comment_end - i))
            last = i = comment_end
        else:
            i += 1
    pieces.append(text[last:])
    return "".join(pieces)


def pycode_bracket_match(text, inwhat="of code"):
    """Match every opening bracket of (), [], {} to its closing bracket
    tracking nesting, and return a dict {opening index: closing index}.
    """
    strings = pycode_string_ranges(text, inwhat)
    stack = []
    pairs = {}
    end = len(text)
    i = 0
    while i < end:
        if i in strings:
            i = strings[i] + 1
            continue
        c = text[i]
        if c in PYCODE_BRACKET_PAIRS:
            stack.append(i)
        elif c in PYCODE_CLOSING_BRACKETS:
            if not stack:
                raise pycode_error(text, i, inwhat, f"SyntaxError: unmatched {c!r}")
            opening = stack.pop()
            if PYCODE_BRACKET_PAIRS[text[opening]] != c:
                openingline = text.count("\n", 0, opening) + 1
                raise pycode_error(
                    text,
                    i,
                    inwhat,
                    f"SyntaxError: closing bracket {c!r} does not match opening bracket {text[opening]!r} on line {openingline}",
                )
            pairs[opening] = i
        i += 1

    if stack:  # If all brackets are not closed
        raise pycode_error(
            text,
            stack[-1],
            inwhat,
            f"SyntaxError: {text[stack[-1]]!r} was never closed",
        )
    return pairs


class PyCodeNameTranslator(ast.NodeTransformer):
    """Replace every reference to a PyCode function in a Python expression
    AST, called or not, with the Python expression it stands for. The names
    which are not PyCodeFunctions in defined (variables, parameters, and
    names Python knows) and the names bound inside the expression itself
    by a lambda or comprehension are left as they are.
    """

    def __init__(self, defined):
        self.defined = defined
        self.scopes = [set()]  # The names bound inside the expression

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and not any(
            node.id in scope for scope in self.scopes
        ):
            function = self.defined.get(node.id)
            if isinstance(function, PyCodeFunction):
                replacement = ast.parse(function.name, mode="eval").body
                return ast.copy_location(replacement, node)
        return node

    def visit_NamedExpr(self, node):
        node.value = self.visit(node.value)
        self.scopes[-1].add(node.target.id)
        return node

    def visit_Lambda(self, node):
        arguments = node.args
        arguments.defaults = [self.visit(default) for default in arguments.defaults]
        arguments.kw_defaults = [
            default and self.visit(default) for default in arguments.kw_defaults
        ]
        every_argument = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
        every_argument += [a for a in (arguments.vararg, arguments.kwarg) if a]
        self.scopes.append({argument.arg for argument in every_argument})
        node.body = self.visit(node.body)
        self.scopes.pop()
        return node

    def translate_comprehension(self, node, elements):
        generators = node.generators
        generators[0].iter = self.visit(generators[0].iter)  # Outside the scope
        self.scopes.append(
            {
                name.id
                for generator in generators
                for name in ast.walk(generator.target)
                if isinstance(name, ast.Name)
            }
        )
        for index, generator in enumerate(generators):
            generator.target = self.visit(generator.target)
            if index:
                generator.iter = self.visit(generator.iter)
            generator.ifs = [self.visit(condition) for condition in generator.ifs]
        for element in elements:
            setattr(node, element, self.visit(getattr(node, element)))
        self.scopes.pop()
        return node

    def visit_ListComp(self, node):
        return self.translate_comprehension(node, ["elt"])

    visit_SetComp = visit_GeneratorExp = visit_ListComp

    def visit_DictComp(self, node):
        return self.translate_comprehension(node, ["key", "value"])


def pycodeparse(code, defined, inwhat="of code"):
    """The new PyCode parser - take PyCode code and translate
    it to Python. Returns a list of blocks of executable Python
    code.
    """

    code = pycode_remove_comments(code, inwhat)
    brackets = pycode_bracket_match(code, inwhat)
    strings = pycode_string_ranges(code, inwhat)
    string_spans = sorted(strings.items())

    def error(index, message):
        return pycode_error(code, index, inwhat, message)

    def trim(start, end):
        """Narrow the span code[start:end] to exclude surrounding whitespace."""
        while start < end and code[start].isspace():
            start += 1
        while end > start and code[end - 1].isspace():
            end -= 1
        return start, end

    def split_code(start, end, on):
        """Split code[start:end] on top-level on into trimmed (start, end) spans."""
        spans = []
        last = start
        i = start
        while i < end:
            if i in strings:
                i = strings[i] + 1
                continue
            if i in brackets:
                i = brackets[i] + 1
                continue
            if code[i] == on:
                spans.append(trim(last, i))
                last = i + 1
            i += 1
        spans.append(trim(last, end))
        return spans

    def split_items(start, end):
        """Split comma separated arguments or parameters; one trailing comma is allowed."""
        items = split_code(start, end, ",")
        if items[-1][0] == items[-1][1]:
            items.pop()
        for s, e in items:
            if s == e:
                raise error(s, "SyntaxError: invalid syntax")
        return items

    def expression_text(start, end, newline):
        """The text of code[start:end] with every newline in a string
        replaced with the newline text.
        """
        pieces = []
        last = start
        for opening, closing in string_spans:
            if start <= opening and closing < end:
                pieces.append(code[last:opening])
                pieces.append(
                    PYCODE_STRING_NEWLINE_PATTERN.sub(
                        lambda match: (
                            newline if match.group() == "\n" else match.group()
                        ),
                        code[opening : closing + 1],
                    )
                )
                last = closing + 1
        pieces.append(code[last:end])
        return "".join(pieces)

    def check_expression(
        start, end, prefix="(", suffix=")", message="SyntaxError: invalid syntax"
    ):
        """Raise an error if the expression code[start:end] contains a function
        definition, or if it is not a valid Python expression. The { of a
        definition comes right after a ), which is never valid in a Python
        expression. The prefix is the Python code the expression goes after
        to be checked, like "_(" for an argument which can be *args or **kwargs.
        The suffix is the Python code it goes before. The message is the
        error if Python does not accept it.
        """
        for opening in brackets:
            if start <= opening < end and code[opening] == "{":
                before = opening - 1
                while before >= start and code[before].isspace():
                    before -= 1
                if before >= start and code[before] == ")":
                    raise error(
                        opening,
                        "SyntaxError: function definition inside function argument",
                    )

        text = expression_text(start, end, " ")  # A newline in a string is allowed
        wrapped = f"{prefix}{text}\n{suffix}"  # The brackets allow newlines
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ast.parse(wrapped)
        except SyntaxError as e:
            lines = wrapped.split("\n")
            index = sum(len(line) + 1 for line in lines[: e.lineno - 1])
            index += (e.offset or 1) - 1 - len(prefix)
            raise error(
                min(max(start + index, start), max(end - 1, start)),
                message,
            )

    def translate_expression(start, end, defined, kind="expression"):
        """Translate the expression code[start:end] to Python by replacing
        the references to PyCode functions in its AST. The kind is what it is:
        an "expression", an "argument" of a call (which can be *args or
        **kwargs), an assignment "target", or a "delete" target. Python
        formats the result, so whitespace and newlines in the code do not
        matter, and a newline in a string becomes \\n.
        """
        text = expression_text(start, end, "\\n")
        wrappers = {
            "expression": ("(", "\n)"),
            "argument": ("_(", "\n)"),
            "target": ("(", "\n) = 0"),
            "delete": ("del (", "\n)"),
        }
        prefix, suffix = wrappers[kind]
        statement = ast.parse(f"{prefix}{text}{suffix}").body[0]
        if kind == "expression":
            node = statement.value
        elif kind == "argument":
            node = (statement.value.args or statement.value.keywords)[0]
        else:
            node = statement.targets[0]
        try:
            return ast.unparse(PyCodeNameTranslator(defined).visit(node))
        except SyntaxError:  # A command whose Python expression is invalid
            raise error(start, "SyntaxError: invalid command in pycode_commands")

    def check_missing_semicolon(start, end):
        """Raise an error if the expression code[start:end] of a statement
        has an operand right after an operand, since then a ; is missing
        between two statements. Whitespace and newlines do not matter.
        """
        tokens = []  # (kind, start, end)
        i = start
        while i < end:
            if code[i].isspace():
                i += 1
            elif i in strings:
                tokens.append(("string", i, strings[i] + 1))
                i = strings[i] + 1
            elif i in brackets:
                tokens.append(("group", i, brackets[i] + 1))
                i = brackets[i] + 1
            elif name := PYCODE_NAME_PATTERN.match(code, i, end):
                after = name.end()
                if after in strings and name.group().lower() in PYCODE_STRING_PREFIXES:
                    tokens.append(("string", i, strings[after] + 1))
                    i = strings[after] + 1
                else:
                    tokens.append(("name", i, after))
                    i = after
            elif number := PYCODE_NUMBER_PATTERN.match(code, i, end):
                tokens.append(("number", i, number.end()))
                i = number.end()
            else:
                tokens.append(("operator", i, i + 1))
                i += 1

        def is_value_word(word):
            return not keyword.iskeyword(word) or word in ("True", "False", "None")

        def starts_control(token):
            """If the token is an if (condition) {, which a ternary never has."""
            opening = trim(token[2], end)[0]
            if opening >= end or code[opening] != "(":
                return False
            after = trim(brackets[opening] + 1, end)[0]
            return after < end and code[after] == "{"

        for before, token in zip(tokens, tokens[1:]):
            word = code[token[1] : token[2]]
            if token[0] == "name":
                starts = (
                    is_value_word(word)
                    or word in PYCODE_STATEMENT_WORDS
                    or (word == "if" and starts_control(token))
                )
            else:
                starts = token[0] == "number" or (
                    token[0] == "string" and before[0] != "string"
                )
            before_word = code[before[1] : before[2]]
            ends = before[0] in ("string", "number", "group") or (
                before[0] == "name" and is_value_word(before_word)
            )
            if starts and ends:
                raise error(token[1], "SyntaxError: invalid syntax")

    def parse_arguments(start, end, defined):
        """Translate the arguments of a function call."""
        translated = []
        keywords = set()
        has_varkeywords = False
        for s, e in split_items(start, end):
            stars = e - s - len(code[s:e].lstrip("*"))
            if stars > 2:
                raise error(s, "There can be at most two * before an argument")
            if stars:
                if stars == 1 and has_varkeywords:
                    raise error(s, "A * argument cannot come after a ** argument")
                if stars == 2:
                    has_varkeywords = True
                value_start, value_end = trim(s + stars, e)
                if value_start == value_end:
                    raise error(value_start, "Nothing follows the *")
                check_expression(value_start, value_end)
                translated.append(
                    "*" * stars + translate_expression(value_start, value_end, defined)
                )
                continue
            match = PYCODE_KEYWORD_ARGUMENT_PATTERN.match(code, s, e)
            if match:
                name = match.group(1)
                if keyword.iskeyword(name):
                    raise error(s, f"{name!r} cannot be used as an argument name")
                if name in keywords:
                    raise error(s, f"The argument {name!r} is given more than once")
                keywords.add(name)
                value_start, value_end = trim(match.end(), e)
                if value_start == value_end:
                    raise error(value_start, f"The argument {name!r} has no value")
                check_expression(value_start, value_end)
                translated.append(
                    f"{name}={translate_expression(value_start, value_end, defined)}"
                )
            else:
                if keywords or has_varkeywords:
                    raise error(
                        s,
                        "A plain argument must come before the named arguments and the ** argument",
                    )
                check_expression(s, e, "_(")
                translated.append(translate_expression(s, e, defined, "argument"))
        return ", ".join(translated)

    def parse_parameters(start, end, defined):
        """Translate the parameters of a function definition. Returns
        the translated parameters and the list of parameter names.
        """
        translated = []
        names = []
        has_default = False
        has_varargs = False
        has_varkeywords = False
        for s, e in split_items(start, end):
            if has_varkeywords:
                raise error(s, "SyntaxError: parameter follows ** parameter")
            stars = e - s - len(code[s:e].lstrip("*"))
            match = None
            if stars:  # *args or **kwargs
                name = code[s + stars : e].strip()
                if stars > 2 or not name.isidentifier():
                    raise error(s, f"SyntaxError: invalid parameter {code[s:e]!r}")
            else:
                match = PYCODE_KEYWORD_ARGUMENT_PATTERN.match(code, s, e)
                if match:
                    name = match.group(1)
                else:
                    name = code[s:e]
                    if not name.isidentifier():
                        raise error(s, f"SyntaxError: invalid parameter {name!r}")
            if keyword.iskeyword(name):
                raise error(s, f"SyntaxError: invalid parameter name {name!r}")
            if name in names:
                raise error(s, f"SyntaxError: duplicate parameter {name!r}")
            names.append(name)
            if stars == 1:
                if has_varargs:
                    raise error(s, "SyntaxError: more than one * parameter")
                has_varargs = True
                has_default = False  # The parameters after it are keyword-only
                translated.append(f"*{name}")
            elif stars == 2:
                has_varkeywords = True
                translated.append(f"**{name}")
            elif match:
                has_default = True
                value_start, value_end = trim(match.end(), e)
                if value_start == value_end:
                    raise error(value_start, "SyntaxError: invalid syntax")
                check_expression(value_start, value_end)
                translated.append(
                    f"{name}={translate_expression(value_start, value_end, defined)}"
                )
            else:
                if has_default:
                    raise error(
                        s,
                        "SyntaxError: parameter without a default follows parameter with a default",
                    )
                translated.append(name)
        return ", ".join(translated), names

    def indent(blocks):
        """Indent the blocks with one space to go inside a function, if, or loop."""
        return (
            "\n".join(" " + line for block in blocks for line in block.split("\n"))
            or " pass"
        )

    def parse_control(start, end, defined):
        """Translate an if (condition) {...} elif (condition) {...} else {...}
        statement or a while (condition) {...} statement.
        """
        branches = []
        pos = start
        while True:
            word = PYCODE_CONTROL_PATTERN.match(code, pos, end).group(1)
            if not branches and word not in ("if", "while"):
                raise error(pos, "SyntaxError: invalid syntax")
            pos = trim(pos + len(word), end)[0]
            header = word
            if word != "else":
                if pos >= end or code[pos] != "(":
                    raise error(pos, "SyntaxError: invalid syntax")
                condition_close = brackets[pos]
                condition_start, condition_end = trim(pos + 1, condition_close)
                if condition_start == condition_end:
                    raise error(condition_close, "SyntaxError: invalid syntax")
                check_expression(condition_start, condition_end)
                condition = translate_expression(
                    condition_start, condition_end, defined
                )
                header = f"{word} {condition}"
                pos = trim(condition_close + 1, end)[0]
            if pos >= end or code[pos] != "{":
                raise error(pos, "SyntaxError: invalid syntax")
            body_close = brackets[pos]
            body = parse_block(pos + 1, body_close, defined)
            branches.append(f"{header}:\n{indent(body)}")
            pos = trim(body_close + 1, end)[0]
            if pos >= end:
                return "\n".join(branches)
            following = PYCODE_CONTROL_PATTERN.match(code, pos, end)
            if (
                word in ("while", "else")
                or not following
                or following.group(1) not in ("elif", "else")
            ):
                raise error(pos, "SyntaxError: invalid syntax")

    def find_assignment(start, end):
        """Find the = of an assignment (not ==, !=, <=, >=) outside
        brackets and strings in code[start:end], or return -1.
        """
        i = start
        while i < end:
            if i in strings:
                i = strings[i] + 1
            elif i in brackets:
                i = brackets[i] + 1
            else:
                if (
                    code[i] == "="
                    and (i == start or code[i - 1] not in "=!<>")
                    and (i + 1 >= end or code[i + 1] != "=")
                ):
                    return i
                i += 1
        return -1

    def parse_assignment(start, end, equals, defined):
        """Translate target = value. The target is anything Python can assign
        to, like name, name.attr.attr..., name[index], or a, b. Assigning
        to a name makes it a variable in defined, so it is not a function.
        """
        target_start, target_end = trim(start, equals)
        if target_start == target_end:
            raise error(equals, "SyntaxError: invalid syntax")
        check_missing_semicolon(target_start, target_end)
        check_expression(target_start, target_end)
        check_expression(
            target_start,
            target_end,
            "(",
            ") = 0",
            "SyntaxError: invalid assignment target",
        )
        value_start, value_end = trim(equals + 1, end)
        if value_start == value_end:
            raise error(value_start, "SyntaxError: invalid syntax")
        check_missing_semicolon(value_start, value_end)
        check_expression(value_start, value_end)
        target = translate_expression(target_start, target_end, defined, "target")
        value = translate_expression(value_start, value_end, defined)
        for node in ast.walk(ast.parse(f"({code[target_start:target_end]}\n) = 0")):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined[node.id] = node.id
        return f"{target} = {value}"

    def parse_declaration(start, end, defined):
        """Translate global name, name, ... or nonlocal name, name, ...
        The names become variables in defined, so they are not functions.
        """
        word = PYCODE_DECLARATION_PATTERN.match(code, start, end).group(1)
        names = []
        for s, e in split_code(start + len(word), end, ","):
            name = code[s:e]
            if not name.isidentifier() or keyword.iskeyword(name):
                raise error(s, "SyntaxError: invalid syntax")
            names.append(name)
        for name in names:
            defined[name] = name
        return f"{word} {', '.join(names)}"

    def parse_return(start, end, defined):
        """Translate return or return value."""
        value_start, value_end = trim(start + len("return"), end)
        if value_start == value_end:
            return "return"
        check_missing_semicolon(value_start, value_end)
        check_expression(value_start, value_end)
        return f"return {translate_expression(value_start, value_end, defined)}"

    def parse_simple(start, end, defined):
        """Translate pass, break, or continue."""
        word = PYCODE_SIMPLE_PATTERN.match(code, start, end).group(1)
        rest = trim(start + len(word), end)[0]
        if rest < end:
            raise error(rest, "SyntaxError: invalid syntax")
        return word

    def parse_delete(start, end, defined):
        """Translate del target, target, ... The names deleted become
        undefined, so they are no longer functions or variables.
        """
        items = split_items(start + len("del"), end)
        if not items:
            raise error(start + len("del"), "SyntaxError: invalid syntax")
        targets = []
        for s, e in items:
            check_missing_semicolon(s, e)
            check_expression(s, e)
            check_expression(s, e, "del (", ")", "SyntaxError: invalid delete target")
            targets.append(translate_expression(s, e, defined, "delete"))
            if code[s:e].isidentifier():
                defined.pop(code[s:e], None)
        return f"del {', '.join(targets)}"

    def parse_expression_statement(start, end, defined):
        """Translate a statement which is just an expression. It must be
        valid Python; the errors from running it come on execution.
        """
        check_missing_semicolon(start, end)
        check_expression(start, end)
        return translate_expression(start, end, defined)

    def parse_statement(start, end, defined):
        """Translate a function call, function definition, if, while,
        assignment, global, nonlocal, return, pass, break, continue, del, or expression. A definition
        or assignment is added to defined.
        """
        if PYCODE_DECLARATION_PATTERN.match(code, start, end):
            return parse_declaration(start, end, defined)
        if PYCODE_RETURN_PATTERN.match(code, start, end):
            return parse_return(start, end, defined)
        if PYCODE_SIMPLE_PATTERN.match(code, start, end):
            return parse_simple(start, end, defined)
        if PYCODE_DELETE_PATTERN.match(code, start, end):
            return parse_delete(start, end, defined)
        if PYCODE_CONTROL_PATTERN.match(code, start, end):
            return parse_control(start, end, defined)
        equals = find_assignment(start, end)
        if equals != -1:
            return parse_assignment(start, end, equals, defined)
        paren = start
        while paren < end and code[paren] != "(":
            paren = strings.get(paren, paren) + 1  # Skip strings
        name = code[start:paren].strip()
        if paren >= end or not name.isidentifier():
            return parse_expression_statement(start, end, defined)

        close = brackets[paren]
        restart, restend = trim(close + 1, end)

        if restart == restend:  # Function call; looks like name(args)
            arguments = parse_arguments(paren + 1, close, defined)
            function = defined.get(name)
            if isinstance(function, PyCodeFunction):
                name = function.name
            return f"{name}({arguments})"  # Python raises NameError or TypeError on execution

        if code[restart] != "{":
            return parse_expression_statement(start, end, defined)

        # Function definition; looks like name (args) {...}
        bodyend = brackets[restart]
        afterstart, afterend = trim(bodyend + 1, end)
        if afterstart != afterend:
            raise error(afterstart, "SyntaxError: invalid syntax")

        if keyword.iskeyword(name):
            raise error(start, f"SyntaxError: invalid function name {name!r}")
        parameters, parameter_names = parse_parameters(paren + 1, close, defined)
        function_defined = defined.copy()
        function_defined[name] = PyCodeFunction(name)  # So the function can call itself
        for parameter in parameter_names:
            function_defined[parameter] = parameter
        body = parse_block(restart + 1, bodyend, function_defined)
        defined[name] = PyCodeFunction(name)
        return f"def {name}({parameters}):\n{indent(body)}"

    def parse_block(start, end, defined):
        """Translate the statements in code[start:end]."""
        defined = defined.copy()
        blocks = []
        for s, e in split_code(start, end, ";"):
            if s != e:
                blocks.append(parse_statement(s, e, defined))
        return blocks

    commands = {
        name: PyCodeFunction(python) for name, python in pycode_commands.items()
    }
    return parse_block(0, len(code), {**commands, **defined})


def pcdone(nc):
    """Save nc (raw PyCode source) as the user's ~/.pynotes startup
    config and translate+run it immediately.
    """
    open(f"{homedir}/.pynotes", "w+", encoding="utf-8").write(nc)
    pcread(nc)


def say(string):
    """PyCode's `say` command: show string in a popup."""
    state.root.info("Print PyCode", string)


def pcrun(code):
    """Run a list of already-translated Python code blocks (one PyCode
    statement each, as the PyCode parser produces) against vars(state),
    reporting each block's error separately rather than aborting the
    rest.
    """
    for block in code:
        try:
            exec(block, vars(state))
        except tk.TclError:
            pass
        except Exception as error:
            error = str(error)
            state.root.error(
                "Error",
                f'Error in running the translated PyCode block\n"{block}":\n{error}',
            )


def pcexecaction(index):
    """Run the function of the key binding state.pckeyactions[index],
    reporting any error.
    """
    try:
        state.pckeyactions[index]()
    except tk.TclError:
        pass
    except Exception as error:
        error = str(error)
        state.root.error("Error", f"Error in running the PyCode key binding:\n{error}")


def pccallwithinput(function, commandinput):
    """Call a function PyCode registered for an Alt-X command or event
    hook: it gets commandinput as its argument if it takes one, and the
    `commandinput` variable is set to it for the ones which do not.
    """
    vars(state)["commandinput"] = commandinput
    try:
        parameters = inspect.signature(function).parameters.values()
    except (TypeError, ValueError):
        parameters = ()
    if any(
        parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
        for parameter in parameters
    ):
        return function(commandinput)
    return function()


def pcopenhelp(thing):
    """PyCode's `openhelp` command: open the named Help topic
    (commands/email/pycode/mathgod/plugins).
    """
    if thing == "commands":
        utils.show("open alt-x commands help")
        help.hx()
    elif thing == "email":
        utils.show("open email help")
        help.hemail()
    elif thing == "pycode":
        utils.show("open pycode help")
        help.helppycode()
    elif thing == "mathgod":
        utils.show("open mathgod help")
        help.helpmathgod()
    elif thing == "plugins":
        utils.show("open plugin help")
        help.ap()


def pctermexec(command):
    utils.show("output: " + terminal.termexec(command))


def pcrepeatx(command, n):
    """PyCode's `repeatxcommand` command: run the given Alt-X command
    string n times. (Imports command.py lazily to avoid a circular
    import, since command.py itself imports pycode.)
    """
    import command as _command_module

    for i in range(n):
        _command_module.cmdrun(command)


def pcfullscreen():
    pcrunhook("before", "fullscreen")
    state.root.update()
    state.root.attributes("-fullscreen", True)
    state.root.update()
    utils.show("fullscreen mode")
    pcrunhook("after", "fullscreen")


def pcunfullscreen():
    pcrunhook("before", "un-fullscreen")
    state.root.update()
    state.root.attributes("-fullscreen", False)
    state.root.update()
    utils.show("windowed mode")
    pcrunhook("after", "un-fullscreen")


def pcmax():
    pcrunhook("before", "maximize-window")
    state.root.update()
    if platform.system() == "Linux":
        state.root.attributes("-zoomed", True)
    else:
        state.root.state("zoomed")
    state.root.update()
    utils.show("maximized window")
    pcrunhook("after", "maximize-window")


def pcunmax():
    pcrunhook("before", "unmaximize-window")
    state.root.update()
    if platform.system() == "Linux":
        state.root.attributes("-zoomed", False)
    else:
        state.root.state("normal")
    state.root.update()
    utils.show("unmaximize window")
    pcrunhook("after", "unmaximize-window")


def pcmin():
    pcrunhook("before", "minimize-window")
    state.root.iconify()
    pcrunhook("after", "minimize-window")


def pcrunhook(when, event, commandinput=None):
    """Run every PyCode event hook registered for event at time when
    ("before"/"after"), see pccallwithinput(). event may be
    "kind:detail" (e.g. "alt-x-command:save"); hooks registered for
    just "kind" (e.g. "alt-x-command") run for every detail too. Errors
    in one hook are reported without stopping the others.
    """
    try:
        state.root.update()
    except Exception:
        pass
    hooks = state.pcbeforehooks if when == "before" else state.pcafterhooks
    for key in dict.fromkeys((event, event.split(":", 1)[0])):
        for function in hooks.get(key, []):
            try:
                pccallwithinput(function, commandinput)
            except Exception as error:
                error = str(error)
                state.root.error(
                    "Error in PyCode",
                    f"There was an error in running the '{when}:{event}' hook:\n{error}",
                )


def pcask(askstring):
    return state.root.askstring("PyCode Input", askstring)


def pccopytext(text):
    state.root.clipboard_clear()
    state.root.clipboard_append(text)
    utils.show(f"copied '{text}'")
    state.root.update()


def pcgosettitle(title=None):
    """PyCode's `set_window_title` command: with no title, unset it."""
    if title is None:
        pcunsettitle()
        return
    state.root.title(title)
    utils.show(f"set window title to '{title}'")
    state.pcsettitle = True


def pcunsettitle():
    utils.show("unset window title")
    state.pcsettitle = False
    if getattr(state.active, "title", False):
        state.root.title(
            ("PyNotes - " + os.path.basename(state.active.title))
            if not getattr(state.active, "unsaved", False)
            else "PyNotes - " + os.path.basename(state.active.title) + " *"
        )
    else:
        state.root.title("PyNotes - Untitled")
    if hasattr(state.active, "keypress"):
        state.active.keypress()


def pckillexit():
    """PyCode's `killquit` command: kill PyNotes immediately, with no
    save/cleanup.
    """
    os._exit(0)


def pcsetvar(var, val):
    """PyCode's `set_variable` command: set a state variable by name, for
    where an assignment cannot be written, like in a lambda.
    """
    vars(state)[var] = val


def pccolor(name, *args, **kwargs):
    """PyCode's `color` command: define a reusable tag named name with
    the given tkinter tag_config options, usable later via the `tag`
    command and preserved across syntax-highlighting redraws (which
    otherwise clear tags not owned by the highlighter).
    """
    theme_key = f"pccolor:{name}"
    state.theme[theme_key] = ", ".join(
        [repr(arg) for arg in args]
        + [f"{kw} = {repr(val)}" for kw, val in kwargs.items()]
    )
    state.plugin_hl[theme_key] = {name: (None, theme_key)}
    state._EDITOR_HL_SKIP_REMOVE_TAGS.add(name)
    for buffer in state.all_buffers:
        if isinstance(buffer, editor.Editor):
            buffer.type_.tag_config(name, *args, **kwargs)


def pcneweditfile(orient="horizontal"):
    window.neweditor(True, orient)


def pcsplitedit(n=None, orient="horizontal"):
    if n is None:
        n = state.buffindex
    else:
        n = int(n)
    buffer = state.all_buffers[n]
    if not isinstance(buffer, editor.Editor):
        utils.show("not an editor")
        return
    if buffer.title:
        window.neweditor(buffer.title, orient)
        utils.show(
            "split editor horizontally"
            if orient == "horizontal"
            else "split editor vertically"
        )
    else:
        utils.show("no file open to split editor")


def pcruncode():
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    state.active.f5()


# pccopy through pcuntag below are thin, no-op-if-not-an-editor wrappers
# around the active Editor's matching method; each is one PyCode command
# (see help.helppycode()) named after the tkinter/PyNotes action it
# forwards to.
def pccopy(*args, **kwargs):
    if not hasattr(state.active, "cp"):
        return
    return state.active.cp(*args, **kwargs)


def pccut(*args, **kwargs):
    if not hasattr(state.active, "cut"):
        return
    return state.active.cut(*args, **kwargs)


def pcfindreplace(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.fr(*args, **kwargs)


def pcfindtext(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.f(*args, **kwargs)


def pcget(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.type_.get(*args, **kwargs)


def pcgotoline(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.gl(*args, **kwargs)


def pchmode(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.pchmode(*args, **kwargs)


def pcinsert(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.type_.insert(*args, **kwargs)


def pcnewfile(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.nw(*args, **kwargs)


def pcopenfile(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.llld(*args, **kwargs)


def pcpageback(*args, **kwargs):
    if not hasattr(state.active, "ptb"):
        return
    return state.active.ptb(*args, **kwargs)


def pcpageforw(*args, **kwargs):
    if not hasattr(state.active, "ptf"):
        return
    return state.active.ptf(*args, **kwargs)


def pcpaste(*args, **kwargs):
    if not hasattr(state.active, "pst"):
        return
    return state.active.pst(*args, **kwargs)


def pcredo(*args, **kwargs):
    if not hasattr(state.active, "redo"):
        return
    return state.active.redo(*args, **kwargs)


def pcremoveselectionpoint(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.removeselpoint(*args, **kwargs)


def pcsaveasfile(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.ssv(*args, **kwargs)


def pcsavefile(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.sssv(*args, **kwargs)


def pcbackspace():
    """PyCode's `backspace` command: what pressing BackSpace does in
    the active editor (see Editor.backspace()).
    """
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.backspace()


def pcleft():
    """PyCode's `left` command: what pressing Left does in the active
    editor (see Editor.left()).
    """
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.left()


def pcright():
    """PyCode's `right` command: what pressing Right does in the active
    editor (see Editor.right()).
    """
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.right()


def pcdeletekey():
    """PyCode's `deletekey` command: what pressing Delete does in the
    active editor (see Editor.delete_key()).
    """
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.delete_key()


def pcselall(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.selall(*args, **kwargs)


def pcsetselectionpoint(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.setselpoint(*args, **kwargs)


def pcspeaktext(*args, **kwargs):
    if not hasattr(state.active, "spk"):
        return
    return state.active.spk(*args, **kwargs)


def pctag(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.type_.tag_add(*args, **kwargs)


def pctoggleselectionpoint(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.toggleselpoint(*args, **kwargs)


def pcundo(*args, **kwargs):
    if not hasattr(state.active, "undo"):
        return
    return state.active.undo(*args, **kwargs)


def pcuntag(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        return
    return state.active.type_.tag_remove(*args, **kwargs)


def pcselectionlines():
    """The (start, end) line numbers covered by the active editor's
    selection, leaving out a last line the selection only reaches the
    very start of (e.g. after selecting whole lines by triple-click or
    Shift-Down). Shows a message and returns None if nothing is
    selected.
    """
    try:
        first = state.active.type_.index("sel.first")
        last = state.active.type_.index("sel.last")
    except Exception:
        utils.show("nothing is selected")
        return None
    start = int(first.split(".")[0])
    end, end_column = (int(x) for x in last.split("."))
    if end_column == 0 and end > start:
        end -= 1
    return start, end


def pccommentmarkers():
    """The (prefix, suffix) that commenting a line adds in the active
    editor's HMode (which must be Python / LaTeX / HTML / Markdown).
    """
    if state.active.hmode == "python":
        return "# ", ""
    if state.active.hmode == "latex":
        return "%", ""
    return "<!--", "-->"


def pccommentlines(start, end):
    """Comment every non-blank line from start to end. In the Python
    HMode, the '# ' goes at the indentation shared by all the lines
    (so the comment marks line up with the least indented line, as in
    other editors) instead of at the start of each line.
    """
    prefix, suffix = pccommentmarkers()
    type_ = state.active.type_
    lines = {l: type_.get(f"{l}.0", f"{l}.end") for l in range(start, end + 1)}
    nonblank_lines = [l for l in lines if lines[l].strip()]
    column = 0
    if state.active.hmode == "python" and nonblank_lines:
        column = len(
            os.path.commonprefix(
                [
                    lines[l][: len(lines[l]) - len(lines[l].lstrip())]
                    for l in nonblank_lines
                ]
            )
        )
    type_.edit_separator()
    for l in nonblank_lines:
        if suffix:
            type_.insert(f"{l}.end", suffix)
        type_.insert(f"{l}.{column}", prefix)
    type_.edit_separator()


def pcuncommentlines(start, end):
    """Undo pccommentlines() on every line from start to end that has
    the comment marker (a Python '#' loses one following space too).
    """
    prefix, suffix = pccommentmarkers()
    type_ = state.active.type_
    type_.edit_separator()
    for l in range(start, end + 1):
        line = type_.get(f"{l}.0", f"{l}.end")
        stripped = line.lstrip()
        if stripped.startswith(prefix.strip()):
            a = len(line) - len(stripped)
            b = a + len(prefix.strip())
            if prefix.endswith(" ") and line[b : b + 1] == " ":
                b += 1
            type_.delete(f"{l}.{a}", f"{l}.{b}")
        if suffix:
            line = type_.get(f"{l}.0", f"{l}.end").rstrip()
            if line.endswith(suffix):
                type_.delete(f"{l}.{len(line) - len(suffix)}", f"{l}.{len(line)}")
    type_.edit_separator()


def pccommentregion(start, end):
    """PyCode's `commentregion` command: prefix every non-blank line
    from start to end with the active HMode's comment marker (HTML/
    Markdown also get a closing '-->').
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode not in ("python", "latex", "html", "markdown"):
        return
    pcrunhook("before", "comment-region", (start, end))
    pccommentlines(start, end)
    utils.show("comment region")
    state.active.keypress()
    pcrunhook("after", "comment-region", (start, end))


def pccommentselection():
    """PyCode's `commentselection` command: pccommentregion() over the
    line range of the current selection.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode not in ("python", "latex", "html", "markdown"):
        return
    if (lines := pcselectionlines()) is None:
        return
    start, end = lines
    pcrunhook("before", "comment-region", (start, end))
    pccommentlines(start, end)
    utils.show("comment selection")
    state.active.keypress()
    pcrunhook("after", "comment-region", (start, end))


def pcuncommentregion(start, end):
    """PyCode's `uncommentregion` command: undo pccommentregion()'s
    prefix/suffix on every line from start to end that has them.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode not in ("python", "latex", "html", "markdown"):
        return
    pcrunhook("before", "uncomment-region", (start, end))
    pcuncommentlines(start, end)
    utils.show("uncomment region")
    state.active.keypress()
    pcrunhook("after", "uncomment-region", (start, end))


def pcuncommentselection():
    """PyCode's `uncommentselection` command: pcuncommentregion() over
    the line range of the current selection.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode not in ("python", "latex", "html", "markdown"):
        return
    if (lines := pcselectionlines()) is None:
        return
    start, end = lines
    pcrunhook("before", "uncomment-region", (start, end))
    pcuncommentlines(start, end)
    utils.show("uncomment selection")
    state.active.keypress()
    pcrunhook("after", "uncomment-region", (start, end))


def pccleareditor():
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.root.ask("Warning", "Clear the active editor?", options=("ok", "cancel")):
        pcrunhook("before", "clear-editor")
        state.active.type_.edit_separator()
        state.active.type_.delete("1.0", "end")
        state.active.type_.edit_separator()
        utils.show("cleared editor")
        pcrunhook("after", "clear-editor")


def pcselecttext(a, b):
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    state.active.type_.tag_remove("sel", "1.0", "end")
    state.active.type_.tag_add("sel", a, b)
    utils.show(f"selected text from {a} to {b}")


def pcgetselection():
    if not isinstance(state.active, editor.Editor):
        return
    try:
        start = state.active.type_.index("sel.first")
        end = state.active.type_.index("sel.last")
        ans = (str(start), str(end))
    except Exception:
        ans = tuple()
    return ans


def pcmark(a, b=None):
    """PyCode's `mark` command: visually tag the range a..b as
    "marked" (a separate, persistent highlight from the selection),
    accepting either two args (a, b) or one (a, b) tuple/list.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if not b:
        a, b = a[0], a[1]
    pcrunhook("before", "mark-region", (a, b))
    state.active.type_.tag_add("marked", a, b)
    utils.show(f"marked text from {a} to {b}")
    pcrunhook("after", "mark-region", (a, b))


def pcmarkselection():
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    try:
        start = state.active.type_.index("sel.first")
        end = state.active.type_.index("sel.last")
    except Exception:
        return
    pcrunhook("before", "mark-region", (start, end))
    state.active.type_.tag_add("marked", start, end)
    utils.show(f"marked text from {start} to {end}")
    pcrunhook("after", "mark-region", (start, end))


def pcunmark(a, b=None):
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if not b:
        a, b = a[0], a[1]
    pcrunhook("before", "unmark-region", (a, b))
    state.active.type_.tag_remove("marked", a, b)
    utils.show(f"unmarked text from {a} to {b}")
    pcrunhook("after", "unmark-region", (a, b))


def pcunmarkall():
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    state.active.type_.tag_remove("marked", "1.0", "end")
    utils.show(f"unmarked all text")


def pctkindex(toindex, line=False):
    """PyCode's `tkindex` command: resolve a tkinter-style index (or
    reference like "end", "sel.first") to its normalized "line.col"
    form, or just the line number if line == "line".
    """
    if not isinstance(state.active, editor.Editor):
        return
    ans = state.active.type_.index(toindex)
    if line == "line":
        ans = ans.split(".")[0]
    return ans


def pcdelete(*args, **kwargs):
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    state.active.type_.delete(*args, **kwargs)


def _pcmovecursor(index):
    """Move the active editor's cursor to index and scroll to it,
    without the isinstance(Editor) guard pcmovecursor() has (used by
    callers, like the Python-navigation commands below, that already
    know it's an Editor).
    """
    state.active.type_.mark_set("insert", index)
    state.active.type_.see(index)


def pcmovecursor(index):
    """PyCode's `movecursor` command."""
    if not isinstance(state.active, editor.Editor):
        return
    _pcmovecursor(index)


def pcopenemailbuf():
    """PyCode's `openemailbuf` command."""
    pynotesemail.openemailbuf()


def pcpyscopechains():
    """Map every function/class scope index of the active (Python-HMode)
    editor to its full attribute chain, a tuple of the def names from
    the module level down to it (e.g. ("Outer", "Inner", "method")).
    The module scope (index 0) maps to the empty chain; a scope that is
    not a named function/class (lambda, comprehension) or sits inside
    one is left out.
    """
    defs_by_start = {}
    for dl, dc, dname, dkind in state.active._python_def_names:
        defs_by_start.setdefault(dl, []).append((dname, dkind))
    chains = {0: ()}
    for idx, sc in enumerate(state.active._python_scopes):
        if idx == 0 or sc.get("parent") not in chains:
            continue
        want_def_kind = "class" if sc.get("kind") == "class" else "func"
        if sc.get("kind") not in ("class", "function"):
            continue
        for dname, dkind in defs_by_start.get(sc["start"], []):
            if dkind == want_def_kind:
                chains[idx] = chains[sc["parent"]] + (dname,)
                break
    return chains


def pcpynames():
    """Every attribute chain ("Outer.Inner.name" strings) the Python
    navigation commands accept in the active (Python-HMode) editor:
    the chain of every function/class, and of every name bound directly
    inside one (or at the module level).
    """
    chains = pcpyscopechains()
    out = set()
    for idx, chain in chains.items():
        if chain:
            out.add(".".join(chain))
        for name in state.active._python_scopes[idx]["names"]:
            out.add(".".join(chain + (name,)))
    return out


def _pcpyblocks(text):
    """Every block (suite of a compound statement: def/class/if/elif/
    else/for/while/try/except/finally/with/case...) in text, as
    (start_line, end_line, keyword) where start_line is the block's
    header line. Returns None if text can't be parsed.
    """
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    lines = text.split("\n")
    blocks = []

    def add(headerline, suite, keyword=None):
        if keyword is None:
            words = lines[headerline - 1].split()
            keyword = words[0].rstrip(":") if words else "block"
            if keyword == "async" and len(words) > 1:
                keyword += " " + words[1].rstrip(":")
        blocks.append((headerline, suite[-1].end_lineno, keyword))

    def findkeywordline(suite, keyword):
        for ln in range(suite[0].lineno, 0, -1):
            if re.match(rf"\s*{keyword}\s*:", lines[ln - 1]):
                return ln
        return suite[0].lineno

    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            continue
        if isinstance(node, ast.match_case):
            add(node.pattern.lineno, node.body, "case")
            continue
        for attr in ("body", "orelse", "finalbody"):
            suite = getattr(node, attr, None)
            if not (
                isinstance(suite, list)
                and suite
                and all(isinstance(s, ast.stmt) for s in suite)
            ):
                continue
            if attr == "body":
                add(node.lineno, suite)
            elif attr == "finalbody":
                add(findkeywordline(suite, "finally"), suite, "finally")
            elif not (
                isinstance(suite[0], ast.If)
                and lines[suite[0].lineno - 1].lstrip().startswith("elif")
            ):
                add(findkeywordline(suite, "else"), suite, "else")
    return blocks


def _pcpyresolve(commandinput):
    """Shared logic for pcpystartof()/pcpyendof(): resolve
    commandinput to a target line in the active (Python-HMode) editor.
    If it names a kind (f/fun/func/function/c/class/b/block), find the
    innermost enclosing function/class/block of that kind around the
    cursor; otherwise treat commandinput as a function/class attribute
    chain (Outer.Inner.name, starting at the module level) and find its
    definition. Returns None (after showing an error) if nothing
    matches.
    """
    if state.active.hmode != "python":
        utils.show("not in python hmode")
        return None
    raw = commandinput.strip()
    word = raw.lower()
    line = int(state.active.type_.index("insert").split(".")[0])
    if word in ("b", "block"):
        blocks = _pcpyblocks(state.active.type_.get("1.0", "end-1c"))
        if blocks is None:
            utils.show("error: cannot parse python code")
            return None
        best = None
        for bstart, bend, bkeyword in blocks:
            if not (bstart <= line <= bend):
                continue
            if (
                best is None
                or bstart > best[0]
                or (bstart == best[0] and bend < best[1])
            ):
                best = (bstart, bend, bkeyword)
        if best is None:
            utils.show("error: not in block")
            return None
        return best[0], best[1], best[2], "block"
    if word in ("f", "fun", "func", "function", "c", "class"):
        wantclass = word in ("c", "class")
        want_scope_kind = "class" if wantclass else "function"
        want_def_kind = "class" if wantclass else "func"
        best = None
        for idx, scchain in pcpyscopechains().items():
            sc = state.active._python_scopes[idx]
            if not scchain or sc.get("kind") != want_scope_kind:
                continue
            if not (sc["start"] <= line <= sc["end"]):
                continue
            if best is None or sc["start"] > best[0]:
                best = (sc["start"], sc["end"], ".".join(scchain))
        if best is None:
            utils.show(
                "error: currently in no class"
                if wantclass
                else "error: currently in no function"
            )
            return None
        startline, endline, name = best
        return startline, endline, name, want_def_kind
    chain = tuple(raw.split("."))
    defkinds = {
        (dl, dname): dkind for dl, dc, dname, dkind in state.active._python_def_names
    }
    for idx, scchain in pcpyscopechains().items():
        if scchain == chain:
            sc = state.active._python_scopes[idx]
            return (
                sc["start"],
                sc["end"],
                raw,
                defkinds.get((sc["start"], chain[-1]), "func"),
            )
    utils.show(f"error: function or class '{raw}' does not exist in current editor")
    return None


def pcpystartof(commandinput):
    """PyCode's `pythongostartof` command: jump to the start of the
    resolved function/class (see _pcpyresolve()).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    result = _pcpyresolve(commandinput)
    if result is None:
        return
    startline, endline, name, kind = result
    label = {"class": "class", "block": "block"}.get(kind, "function")
    _pcmovecursor(f"{startline}.end")
    state.active.keypress()
    utils.show(f"jumped to start of {label} '{name}'")


def pcpyendof(commandinput):
    """PyCode's `pythongoendof` command: jump to the end of the
    resolved function/class (see _pcpyresolve()).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    result = _pcpyresolve(commandinput)
    if result is None:
        return
    startline, endline, name, kind = result
    label = {"class": "class", "block": "block"}.get(kind, "function")
    _pcmovecursor(f"{endline}.end")
    state.active.keypress()
    utils.show(f"jumped to end of {label} '{name}'")


def pcgodef(commandinput):
    """PyCode's `pythongodef` command: jump to the definition of the
    name given as an attribute chain (Outer.Inner.name, starting at the
    module level): its nearest binding at or before the cursor in the
    scope the chain leads to; if that scope has no binding at or before
    the cursor, falls back to its earliest binding (which may be after
    the cursor).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode != "python":
        utils.show("not in python hmode")
        return
    raw = commandinput.strip()
    chain = tuple(raw.split("."))
    line = int(state.active.type_.index("insert").split(".")[0])
    target_line = None
    for idx, scchain in pcpyscopechains().items():
        if scchain == chain[:-1]:
            bindings = state.active._python_scopes[idx]["names"].get(chain[-1])
            if bindings:
                candidates = [ln for ln, kd in bindings if ln <= line]
                target_line = (
                    max(candidates) if candidates else min(ln for ln, kd in bindings)
                )
                break
    if target_line is None:
        utils.show(f"error: name '{raw}' does not exist in current editor")
        return
    _pcmovecursor(f"{target_line}.end")
    state.active.keypress()
    utils.show(f"jumped to definition of '{raw}'")


_LATEX_SECTION_NAMES = ("chapter", "section", "subsection", "subsubsection")
_LATEX_SECTION_PAT = re.compile(
    r"^\s*\\(chapter|section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\s*\{(.*)\}"
)
_LATEX_SECTION_KINDWORDS = {
    "c": 0,
    "chapter": 0,
    "s": 1,
    "sec": 1,
    "section": 1,
    "ss": 2,
    "subsec": 2,
    "subsection": 2,
    "sss": 3,
    "subsubsec": 3,
    "subsubsection": 3,
}
_MARKDOWN_SECTION_PAT = re.compile(r"^(#{1,6})(?:[ \t]+(.*?))?[ \t]*#*[ \t]*$")
_MARKDOWN_SECTION_KINDWORDS = {
    "h1": 1,
    "h2": 2,
    "h3": 3,
    "h4": 4,
    "h5": 5,
    "h6": 6,
    "s": None,
    "sec": None,
    "section": None,
}


def _pclatexsections(text):
    """Every \\chapter/\\section/\\subsection/\\subsubsection in text,
    as (start_line, end_line, level, title, label): level indexes
    _LATEX_SECTION_NAMES, and end_line is the last non-blank line before
    the next heading of the same or a higher level (or before
    \\end{document}, or the end of the text).
    """
    lines = text.split("\n")
    lastline = len(lines)
    headings = []
    for ln, content in enumerate(lines, 1):
        content = re.split(r"(?<!\\)%", content, maxsplit=1)[0]
        if re.match(r"\s*\\end\{document\}", content):
            lastline = ln - 1
            break
        m = _LATEX_SECTION_PAT.match(content)
        if m:
            level = _LATEX_SECTION_NAMES.index(m.group(1))
            headings.append((ln, level, m.group(2).strip(), m.group(1)))
    return _pcsectionspans(lines, headings, lastline)


def _pcmarkdownsections(text):
    """Every ATX heading (# to ######, outside fenced code blocks) in
    text, as (start_line, end_line, level, title, label): level is the
    number of #s, and end_line is the last non-blank line before the
    next heading of the same or a higher level (or the end of the
    text).
    """
    lines = text.split("\n")
    headings = []
    fence = None
    for ln, content in enumerate(lines, 1):
        fencematch = re.match(r"\s{0,3}(`{3,}|~{3,})", content)
        if fencematch:
            if fence is None:
                fence = fencematch.group(1)[0]
            elif fencematch.group(1)[0] == fence:
                fence = None
            continue
        if fence is not None:
            continue
        m = _MARKDOWN_SECTION_PAT.match(content)
        if m:
            level = len(m.group(1))
            headings.append(
                (ln, level, (m.group(2) or "").strip(), f"h{level} section")
            )
    return _pcsectionspans(lines, headings, len(lines))


def _pcsectionspans(lines, headings, lastline):
    """Shared by _pclatexsections()/_pcmarkdownsections(): turn
    headings ((line, level, title, label), in order) into spans by
    ending each one before the next heading of the same or a higher
    level (or at lastline), minus trailing blank lines.
    """
    spans = []
    for i, (ln, level, title, label) in enumerate(headings):
        end = lastline
        for nln, nlevel, ntitle, nlabel in headings[i + 1 :]:
            if nlevel <= level:
                end = nln - 1
                break
        while end > ln and not lines[end - 1].strip():
            end -= 1
        spans.append((ln, max(end, ln), level, title, label))
    return spans


def _pcsectionresolve(commandinput, spans, kindwords, kindnouns, anynoun):
    """Shared logic for the LaTeX/Markdown navigation commands: resolve
    commandinput to (start_line, end_line, title, label). If it is one
    of kindwords (mapping keyword -> heading level, or None for any
    level), find the innermost enclosing heading of that level around
    the cursor; otherwise treat it as a heading title and find the
    first such heading. kindnouns maps level -> noun used in the
    "currently in no ..." error; anynoun is used for a None level.
    Returns None (after showing an error) if nothing matches.
    """
    raw = commandinput.strip()
    word = raw.lower()
    line = int(state.active.type_.index("insert").split(".")[0])
    if word in kindwords:
        wantlevel = kindwords[word]
        best = None
        for sstart, send, level, title, label in spans:
            if wantlevel is not None and level != wantlevel:
                continue
            if not (sstart <= line <= send):
                continue
            if best is None or sstart > best[0]:
                best = (sstart, send, title, label)
        if best is None:
            noun = anynoun if wantlevel is None else kindnouns[wantlevel]
            utils.show(f"error: currently in no {noun}")
            return None
        return best
    for sstart, send, level, title, label in spans:
        if title == raw:
            return sstart, send, title, label
    utils.show(f"error: {anynoun} '{raw}' does not exist in current editor")
    return None


def _pcsectionjump(
    commandinput, atend, hmode, spansfunc, kindwords, kindnouns, anynoun
):
    """Shared by pclatexstartof()/pclatexendof()/pcmarkdownstartof()/
    pcmarkdownendof(): jump to the start (or end, if atend) of the
    section commandinput resolves to.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if state.active.hmode != hmode:
        utils.show(f"not in {hmode} hmode")
        return
    result = _pcsectionresolve(
        commandinput,
        spansfunc(state.active.type_.get("1.0", "end-1c")),
        kindwords,
        kindnouns,
        anynoun,
    )
    if result is None:
        return
    startline, endline, title, label = result
    _pcmovecursor(f"{endline if atend else startline}.end")
    state.active.keypress()
    utils.show(f"jumped to {'end' if atend else 'start'} of {label} '{title}'")


def pclatexstartof(commandinput):
    """PyCode's `latexgostartof` command: jump to the start of the
    resolved chapter/section/subsection/subsubsection (see
    _pcsectionresolve()).
    """
    _pcsectionjump(
        commandinput,
        False,
        "latex",
        _pclatexsections,
        _LATEX_SECTION_KINDWORDS,
        _LATEX_SECTION_NAMES,
        "section",
    )


def pclatexendof(commandinput):
    """PyCode's `latexgoendof` command: jump to the end of the resolved
    chapter/section/subsection/subsubsection (see
    _pcsectionresolve()).
    """
    _pcsectionjump(
        commandinput,
        True,
        "latex",
        _pclatexsections,
        _LATEX_SECTION_KINDWORDS,
        _LATEX_SECTION_NAMES,
        "section",
    )


def pcmarkdownstartof(commandinput):
    """PyCode's `markdowngostartof` command: jump to the start of the
    resolved Markdown section (see _pcsectionresolve()).
    """
    _pcsectionjump(
        commandinput,
        False,
        "markdown",
        _pcmarkdownsections,
        _MARKDOWN_SECTION_KINDWORDS,
        {level: f"h{level} section" for level in range(1, 7)},
        "section",
    )


def pcmarkdownendof(commandinput):
    """PyCode's `markdowngoendof` command: jump to the end of the
    resolved Markdown section (see _pcsectionresolve()).
    """
    _pcsectionjump(
        commandinput,
        True,
        "markdown",
        _pcmarkdownsections,
        _MARKDOWN_SECTION_KINDWORDS,
        {level: f"h{level} section" for level in range(1, 7)},
        "section",
    )


def pclatexsectiontitles():
    """Every section title in the active (LaTeX-HMode) editor, for the
    LaTeX navigation commands' autocomplete.
    """
    return [
        title
        for s, e, l, title, label in _pclatexsections(
            state.active.type_.get("1.0", "end-1c")
        )
    ]


def pcmarkdownsectiontitles():
    """Every section title in the active (Markdown-HMode) editor, for
    the Markdown navigation commands' autocomplete.
    """
    return [
        title
        for s, e, l, title, label in _pcmarkdownsections(
            state.active.type_.get("1.0", "end-1c")
        )
    ]


def pccmdwrite(text, n):
    """PyCode's `write` command: insert text repeated n times at the
    cursor.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    state.active.type_.edit_separator()
    state.active.type_.insert(state.active.type_.index("insert"), text * n)
    utils.show(f'wrote \'{text.replace("\n", "\\n")}\' {n} times')
    state.active.type_.edit_separator()
    state.active.keypress()


def pcindentregion(start, end):
    """PyCode's `indentregion` command: indent every non-blank line
    from start to end by one tab or 4 spaces (per state.taborspace).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    pcrunhook("before", "indent-region", (start, end))
    if state.taborspace:
        whitespace = "    "
    else:
        whitespace = "	"
    l = start
    state.active.type_.edit_separator()
    while not l > end:
        if not state.active.type_.get(f"{l}.0", f"{l}.end").strip():
            l += 1
            continue
        state.active.type_.insert(f"{l}.0", whitespace)
        l += 1
    state.active.type_.edit_separator()
    utils.show("indent region")
    state.active.keypress()
    pcrunhook("after", "indent-region", (start, end))


def pcindentselection():
    """PyCode's `indentselection` command: pcindentregion() over the
    line range of the current selection (including blank lines,
    unlike pcindentregion()).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if (lines := pcselectionlines()) is None:
        return
    start, end = lines
    pcrunhook("before", "indent-region", (start, end))
    if state.taborspace:
        whitespace = "    "
    else:
        whitespace = "	"
    state.active.type_.edit_separator()
    for l in range(start, end + 1):
        state.active.type_.insert(f"{l}.0", whitespace)
    state.active.type_.edit_separator()
    utils.show("indent selection")
    state.active.keypress()
    pcrunhook("after", "indent-region", (start, end))


def pcunindentlines(start, end):
    """Unindent every non-blank indented line from start to end by one
    indentation level, each line on its own (like backspace() does):
    a tab, or the spaces back to the previous multiple of 4 columns, so
    at most 4 spaces are removed from a line.
    """
    type_ = state.active.type_
    type_.edit_separator()
    for l in range(start, end + 1):
        line = type_.get(f"{l}.0", f"{l}.end")
        old = line[: len(line) - len(line.lstrip())]
        if not line.strip() or not old:
            continue
        trailing_spaces = len(old) - len(old.rstrip(" "))
        if trailing_spaces:
            remove = min(trailing_spaces, len(old.expandtabs(8)) % 4 or 4)
        else:
            remove = 1
        type_.delete(f"{l}.{len(old) - remove}", f"{l}.{len(old)}")
    type_.edit_separator()


def pcunindentregion(start, end):
    """PyCode's `unindentregion` command: remove one level of leading
    indentation from every non-blank line from start to end (see
    pcunindentlines()).
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    pcrunhook("before", "unindent-region", (start, end))
    pcunindentlines(start, end)
    utils.show("unindent region")
    state.active.keypress()
    pcrunhook("after", "unindent-region", (start, end))


def pcunindentselection():
    """PyCode's `unindentselection` command: pcunindentregion() over
    the line range of the current selection.
    """
    if not isinstance(state.active, editor.Editor):
        utils.show("not an editor")
        return
    if (lines := pcselectionlines()) is None:
        return
    start, end = lines
    pcrunhook("before", "unindent-region", (start, end))
    pcunindentlines(start, end)
    utils.show("unindent selection")
    state.active.keypress()
    pcrunhook("after", "unindent-region", (start, end))


def pcparse(code, inwhat="of code"):
    """Translate PyCode source to a list of blocks of Python code with
    the PyCode parser. Shows the error and returns None if the source
    is not valid PyCode.
    """
    try:
        return pycodeparse(code, {}, inwhat)
    except Exception as error:
        state.root.error("Error in PyCode", str(error))
        return None


def pcevaluate(code):
    """Translate and run PyCode source (the `pccmd` Alt-X command, and
    the console's pycode-eval command).
    """
    blocks = pcparse(code, "of the PyCode expression")
    if blocks is None:
        utils.show("invalid pycode expression")
        return
    pcrun(blocks)
    utils.show("evaluated pycode expression")


def pcread(code):
    """Forget everything the previous PyCode source registered (Alt-X
    commands, event hooks, key bindings), translate code with the PyCode
    parser and run it, then bind the keys it asked for with key_bind().
    Called whenever PyCode source needs to be (re-)run: on startup, and
    by pcdone() (which the PyCode editor's Done button calls with its
    edited source).
    """
    state.pcwrittencommands = {}
    state.pcbeforehooks = {}
    state.pcafterhooks = {}
    state.pckeybindings = []
    state.pcdeferkeybindings = True
    try:
        blocks = pcparse(code)
        if blocks is not None:
            pcrun(blocks)
    finally:
        state.pcdeferkeybindings = False
        pcapplykeybindings()


def pckeybind(key, function, where=None):
    """PyCode's `key_bind` command: run function when key (like
    '<Control-x>', or a chord like '<Control-x & Control-s>') is
    pressed. where is None for any buffer, or 'editor' for only the
    editors (which also replaces their default binding of the key).
    """
    if not isinstance(key, str) or not re.match(r"^<.+>$", key):
        raise ValueError(f"invalid key {key!r}, it must look like '<Control-x>'")
    if not callable(function):
        raise TypeError("a key binding needs a function to run")
    if where not in (None, "editor"):
        raise ValueError(f"invalid binding place {where!r}, it can be 'editor'")
    state.pckeybindings.append((key, function, where))
    if not state.pcdeferkeybindings:
        pcapplykeybindings()


def pcaddcommand(name, function):
    """PyCode's `add_command` command: make function the Alt-X command
    name. If function takes a parameter, it gets the command's input.
    """
    if not callable(function):
        raise TypeError("an Alt-X command needs a function to run")
    state.pcwrittencommands[name] = function


def pcaddeventhook(event, function):
    """PyCode's `add_event_hook` command: run function before or after
    an event, where event is 'before:event' or 'after:event' (see
    pchookevents). If function takes a parameter, it gets the event's
    input.
    """
    when, _, name = event.partition(":")
    if when not in ("before", "after"):
        raise ValueError(
            f"invalid event {event!r}, it must start with before: or after:"
        )
    if name.split(":", 1)[0] not in pchookevents:
        raise ValueError(f"invalid event {name!r}")
    if not callable(function):
        raise TypeError("an event hook needs a function to run")
    (state.pcbeforehooks if when == "before" else state.pcafterhooks).setdefault(
        name, []
    ).append(function)


def pcapplykeybindings():
    """Bind the default keys and every key_bind() of state.pckeybindings,
    first removing the keys bound by the previous call. A key binding
    runs state.pckeyactions[its index in state.pckeybindings]. A binding
    with where None works in every buffer, one with where 'editor' only
    in the editors. Chords like '<Control-x & Control-s>' are compiled
    into a small key-sequence state machine.
    """
    for binded in state.wholenewwords:
        state.root.unbind(binded)
        for buffer in state.all_buffers:
            unbindrecur(buffer, binded)
    state.wholenewwords.clear()
    vars(state).setdefault("_pychord_state", [None])[0] = None
    state.pckeyactions = [function for _, function, _ in state.pckeybindings]
    simple_global = {}
    simple_editor = {}
    chords_global = []
    chords_editor = []
    for action, (key_part, _, where) in enumerate(state.pckeybindings):
        if re.match(r"^<.+&.+>$", key_part):
            chord_keys = ["<" + k.strip() + ">" for k in key_part[1:-1].split("&")]
            state.wholenewwords.extend(chord_keys)
            (chords_global if where is None else chords_editor).append(
                (action, chord_keys)
            )
        else:
            state.wholenewwords.append(key_part)
            (simple_global if where is None else simple_editor)[key_part] = action
    cdt = []
    type_bind_cdt = []
    for key_part, action in simple_global.items():
        type_bind_cdt.append(
            f"for buffer in all_buffers: bindrecur(buffer, '{key_part}', lambda event: pcexecaction({action}))"
        )
        cdt.append(
            f"root.bind('{key_part}', lambda event: pcexecaction({action}) or 'break')"
        )
    for key_part, action in simple_editor.items():
        type_bind_cdt.append(
            f"for buffer in all_buffers: bindtype_(buffer, '{key_part}', lambda event: pcexecaction({action}))"
        )
    default_root_bindings = [
        ("<Alt-x>", "cmd()"),
        ("<Control-N>", "neweditor()"),
        ("<Control-O>", "neweditor(True)"),
        ("<Control-q>", "ext()"),
    ]
    default_type_bindings = [
        ("<Control-a>", "editor.selall()"),
        ("<Control-n>", "editor.nw()"),
        ("<Control-o>", "editor.llld()"),
        ("<Control-c>", "editor.cp()"),
        ("<Control-v>", "editor.pst()"),
        ("<Control-w>", "pcclosebuff(all_buffers.index(editor))"),
        ("<Control-x>", "editor.cut()"),
        ("<Tab>", "editor.tab()"),
        ("<BackSpace>", "editor.backspace()"),
        ("<Left>", "editor.left()"),
        ("<Right>", "editor.right()"),
        ("<Delete>", "editor.delete_key()"),
        ("<Alt-l>", "editor.gl()"),
        ("<Control-p>", "editor.ptf()"),
        ("<Control-P>", "editor.ptb()"),
        ("<Control-f>", "editor.f()"),
        ("<Control-F>", "editor.fr()"),
        ("<Control-h>", "editor.fr()"),
        ("<Control-z>", "editor.undo()"),
        ("<Control-Z>", "editor.redo()"),
        ("<Control-s>", "editor.sssv()"),
        ("<Control-S>", "editor.ssv()"),
        ("<F5>", "editor.f5()"),
        ("<Control-space>", "editor.toggleselpoint()"),
    ]
    defaults_cdt_root = [
        f"bindrecur(root, '{key}', lambda event: {action})"
        for key, action in default_root_bindings
    ]
    defaults_cdt_type_ = [
        f"for buffer in all_buffers: bindtype_(buffer, '{key}', lambda event, editor = buffer: {action})"
        for key, action in default_type_bindings
    ]
    defaults_cdt_type_ += [
        "for buffer in all_buffers: bindtype_(buffer, '<KeyRelease>', lambda event, editor = buffer: editor.keypress(), break_ = False)",
        "for buffer in all_buffers: bindtype_(buffer, '<Return>', lambda event, editor = buffer: editor.indent(), break_ = False)",
        "for buffer in all_buffers: bindtype_(buffer, '<KeyPress>', lambda event, editor = buffer: editor.selkeypress(event), False, '+')",
    ]
    pycode_default_type_actions = dict(default_type_bindings)
    pycode_default_root_actions = dict(default_root_bindings)

    def pycodechordhandler(transitions, completions, standalone, guard):
        """Build the expression a chord-involved key's handler runs. A
        completion runs only its chord's action; a later chord step
        runs nothing else; any other press restarts: it begins a chord
        (also running the key's own standalone binding, if any) or
        just runs its standalone binding and clears the chord.
        """
        reset = "_pychord_state.__setitem__(0, None)"
        handler = f"({standalone} or {reset})" if standalone else reset
        for from_s, to_s in reversed(transitions):
            if from_s is not None:
                continue
            advance = f"_pychord_state.__setitem__(0, '{to_s}')"
            if standalone:
                advance = f"({standalone} or {advance})"
            handler = f"({advance} if True{guard} else {handler})"
        for from_s, to_s in reversed(transitions):
            if from_s is None:
                continue
            advance = f"_pychord_state.__setitem__(0, '{to_s}')"
            handler = f"({advance} if _pychord_state[0] in ('{from_s}',){guard} else {handler})"
        for es, ap in reversed(completions):
            handler = f"((pcexecaction({ap}) or {reset}) if _pychord_state[0] in ('{es}',){guard} else {handler})"
        return handler

    def pycodechordcode(chords, simple_actions, editors):
        """Compile the chords (a list of (action, chord keys)) into
        (root bindings, buffer bindings, the <KeyPress> handler's
        expression). simple_actions maps the keys with a standalone
        binding to its action. With editors the bindings are only for
        the editors and there are no root bindings; otherwise they are
        for the root and every buffer which is not an editor.
        """
        cdt = []
        type_bind_cdt = []
        nonmod_completions = []
        nonmod_transitions = []
        mod_key_transitions = {}
        mod_key_completions = {}
        for action, chord_keys in chords:
            last_key = chord_keys[-1]
            expected_state = "+".join(chord_keys[:-1])
            prefix_positions = {}
            for i in range(len(chord_keys) - 1):
                prefix_positions.setdefault(chord_keys[i], []).append(i)
            for ck, positions in prefix_positions.items():
                if ck == last_key:
                    continue
                if re.match(r"^<(Control|Shift|Alt|Meta|Super)-", ck):
                    for pos in sorted(positions):
                        from_s = "+".join(chord_keys[:pos]) if pos > 0 else None
                        to_s = "+".join(chord_keys[: pos + 1])
                        mod_key_transitions.setdefault(ck, []).append((from_s, to_s))
                else:
                    ck_inner = ck[1:-1]
                    for pos in sorted(positions):
                        from_s = "+".join(chord_keys[:pos]) if pos > 0 else None
                        to_s = "+".join(chord_keys[: pos + 1])
                        nonmod_transitions.append((from_s, ck_inner, to_s))
            last_key_inner = last_key[1:-1]
            last_key_is_mod = bool(
                re.match(r"^(Control|Shift|Alt|Meta|Super)-", last_key_inner)
            )
            overlap_positions = sorted(
                [i for i, k in enumerate(chord_keys[:-1]) if k == last_key],
                reverse=True,
            )
            if last_key_is_mod:
                mod_key_completions.setdefault(last_key, []).append(
                    (expected_state, action)
                )
                for pos in overlap_positions:
                    from_s = "+".join(chord_keys[:pos]) if pos > 0 else None
                    to_s = "+".join(chord_keys[: pos + 1])
                    mod_key_transitions.setdefault(last_key, []).append((from_s, to_s))
            else:
                nonmod_completions.append((expected_state, last_key_inner, action))
                for pos in overlap_positions:
                    from_s = "+".join(chord_keys[:pos]) if pos > 0 else None
                    to_s = "+".join(chord_keys[: pos + 1])
                    nonmod_transitions.append((from_s, last_key_inner, to_s))
        buffer_test = "" if editors else "not "

        def bindhandler(key_part, handler_t, handler_r, standalone_r):
            type_bind_cdt.append(
                f"for editor in all_buffers: (bindrecur(editor, '{key_part}', lambda event, editor = editor: {handler_t}) if {buffer_test}isinstance(editor, Editor) else None)"
            )
            if not editors:
                cdt.append(
                    f"root.bind('{key_part}', lambda event: {handler_r}{" or 'break'" if standalone_r else ''})"
                )

        for mod_key in set(list(mod_key_transitions) + list(mod_key_completions)):
            if mod_key in simple_actions:
                standalone_t = standalone_r = f"pcexecaction({simple_actions[mod_key]})"
            else:
                standalone_t = (
                    f"({pycode_default_type_actions[mod_key]} if isinstance(editor, Editor) else None)"
                    if mod_key in pycode_default_type_actions
                    else None
                )
                standalone_r = pycode_default_root_actions.get(mod_key)
            transitions = mod_key_transitions.get(mod_key, [])
            completions = mod_key_completions.get(mod_key, [])
            bindhandler(
                mod_key,
                pycodechordhandler(transitions, completions, standalone_t, ""),
                pycodechordhandler(transitions, completions, standalone_r, ""),
                standalone_r,
            )
        for key_part in dict.fromkeys(
            list(simple_actions) + list(pycode_default_type_actions)
        ):
            simple_match = re.match(r"^<([^<>\-]+)>$", key_part)
            if not simple_match:
                continue
            simple_inner = simple_match.group(1)
            simple_transitions = [
                (from_s, to_s)
                for from_s, ks_, to_s in nonmod_transitions
                if ks_ == simple_inner
            ]
            simple_completions = [
                (es, ap) for es, ks_, ap in nonmod_completions if ks_ == simple_inner
            ]
            if not simple_transitions and not simple_completions:
                continue
            if key_part in simple_actions:
                standalone_t = standalone_r = (
                    f"pcexecaction({simple_actions[key_part]})"
                )
            else:
                standalone_t = f"({pycode_default_type_actions[key_part]} if isinstance(editor, Editor) else None)"
                standalone_r = None
            guard = " and not (event.state & 12)"
            bindhandler(
                key_part,
                pycodechordhandler(
                    simple_transitions, simple_completions, standalone_t, guard
                ),
                pycodechordhandler(
                    simple_transitions, simple_completions, standalone_r, guard
                ),
                standalone_r,
            )
        MODS = "('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Meta_L', 'Meta_R', 'Super_L', 'Super_R', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'ISO_Level3_Shift')"
        kp_body = (
            f"None if event.keysym in {MODS} else _pychord_state.__setitem__(0, None)"
        )
        for restart in (True, False):
            for from_s, ks_, to_s in reversed(nonmod_transitions):
                if (from_s is None) != restart:
                    continue
                state_check = (
                    "True" if from_s is None else f"_pychord_state[0] in ('{from_s}',)"
                )
                kp_body = f"((_pychord_state.__setitem__(0, '{to_s}') or 'break') if {state_check} and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
        for es, ks_, ap in reversed(nonmod_completions):
            kp_body = f"((pcexecaction({ap}) or _pychord_state.__setitem__(0, None) or 'break') if _pychord_state[0] in ('{es}',) and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
        return cdt, type_bind_cdt, kp_body

    cdt = defaults_cdt_root + cdt
    type_bind_cdt = defaults_cdt_type_ + type_bind_cdt
    if chords_global or chords_editor:
        global_cdt, global_type, global_kp_body = pycodechordcode(
            chords_global, simple_global, False
        )
        _, editor_type, editor_kp_body = pycodechordcode(
            sorted(chords_global + chords_editor),
            {**simple_global, **simple_editor},
            True,
        )
        cdt = (
            [f"root.bind('<KeyPress>', lambda event: {global_kp_body})"]
            + cdt
            + global_cdt
        )
        type_bind_cdt = (
            [
                f"for editor in all_buffers: bindtype_(editor, '<KeyPress>', lambda event: {editor_kp_body}, False, '+')"
            ]
            + type_bind_cdt
            + global_type
            + editor_type
        )
        state.wholenewwords.append("<KeyPress>")
    state.pycode_keybindings_cdt = type_bind_cdt
    pcrun(cdt)
    pcrun(type_bind_cdt)


def edit(widget, editfrom):
    """The PyCode editor's special-key handler, bound to the opening
    brackets/quotes so it can auto-close them with the cursor left in
    between, and to ; so it can start a new line after it.
    """
    if editfrom == ";":
        widget.insert("insert", ";\n")
        return "break"
    widget.insert("insert", {"(": ")", "[": "]", "{": "}"}.get(editfrom, editfrom))
    widget.mark_set("insert", "insert-1c")


# Every event name a PyCode "[before/after:event] :→ [commands]" hook
# can attach to (see pcrunhook() and help.helppycode()'s Event Hooks tab).
pchookevents = [
    "new-file-current-editor",
    "new-file-new-editor",
    "open-file-current-editor",
    "open-file-new-editor",
    "save-file",
    "save-as-file",
    "exit-pynotes",
    "close-buffer",
    "switch-buffer",
    "run-code",
    "mark-region",
    "unmark-region",
    "comment-region",
    "uncomment-region",
    "indent-region",
    "unindent-region",
    "open-mathgod",
    "term-exec",
    "alt-x-command",
    "pycode-command",
    "undo",
    "redo",
    "show-pynotes-source-code",
    "open-terminal",
    "open-preferences",
    "next-page",
    "previous-page",
    "copy-text",
    "paste-text",
    "cut-text",
    "fullscreen",
    "un-fullscreen",
    "maximize-window",
    "unmaximize-window",
    "minimize-window",
    "clear-editor",
    "open-pycode",
    "change-hmode",
    "open-python-shell",
    "open-email-buffer",
    "resize-window",
]


def pcgraphicalstatements(commands, indent=""):
    """The PyCode statements calling the given commands, one per line."""
    return "".join(f"{indent}{command}();\n" for command in commands)


def pcgraphicallambda(commands):
    """A PyCode lambda calling the given commands, for key_bind(),
    add_command(), and add_event_hook().
    """
    if not commands:
        return "lambda: None"
    return "lambda: [\n" + "".join(f"    {command}(),\n" for command in commands) + "]"


def pc():
    """Open the PyCode editor window: a text editor (codeedit,
    pre-loaded from and, on Done, saved back to ~/.pynotes via
    pcdone()) plus a "Define" sidebar for graphical coding - picking a
    construct (Function, Variable, Startup Code, Keyboard Shortcut,
    Alt-X Command, or Event Hook) walks through prompts and/or a button
    list of every available command, then inserts the corresponding
    PyCode into codeedit.
    """
    pcrunhook("before", "open-pycode")
    utils.show("open pycode")
    pcwin = state.root.subwin()
    pcwin.title("PyCode - PyNotes")
    gcframe = ctk.Frame(pcwin)
    buttonframe = ctk.ScrolledFrame(gcframe)
    buttonframe.pack(side="top", fill="y", expand=True)
    buttonframe.bind(
        "<Configure>",
        lambda event: buttonframe.viewport.configure(
            width=buttonframe.winfo_reqwidth()
        ),
        add="+",
    )
    pccmddonebutton = ctk.Button(
        gcframe, text="Done", command=lambda: [setcommand("Done"), gcframe.update()]
    )
    gcframe.pack(side="left", fill="y", expand=True, padx=10, pady=10)
    ctk.Label(buttonframe, text="Define:").grid(column=0)
    todefine = tk.StringVar(pcwin)

    def pickcommands():
        """Show the command buttons until Done is pressed, and return
        the commands pressed.
        """
        prompttext = ctk.Label(buttonframe, text="Commands:")
        prompttext.grid(column=0, row=0)
        row = 0
        for button in buttons:
            row += 1
            button.grid(column=0, row=row, sticky="ew", pady=2)
        pccmddonebutton.pack(side="bottom", fill="x")
        while not commanddone:
            pcwin.update()
        prompttext.grid_forget()
        picked = commandtodo.copy()
        commandtodo.clear()
        commanddone.clear()
        return picked

    def askname(title, prompt):
        """Ask for a name which is a valid PyCode identifier, or return
        None if it was cancelled or is not valid.
        """
        name = state.root.askstring(title, prompt, parent=pcwin)
        if not name:
            return None
        if not name.isidentifier() or keyword.iskeyword(name):
            state.root.error("Error", f"'{name}' is not a valid name.")
            return None
        return name

    def define(todefine):
        def shortcutselected():
            shortcut.append(showkey.cget("text"))

        def keypressforshortcut(event):
            state = event.state
            key = event.keysym
            keycombination = []
            if state & 0x0001:
                keycombination.append("Shift")
            if state & 0x0004:
                keycombination.append("Control")
            if state & 0x0008:
                keycombination.append("Alt")
            keycombination.append(key)
            showkey.config(text="+".join(keycombination))

        if todefine == "Function":
            funcname = askname("Name", "Name of the Function:")
            if not funcname:
                return
            statements = pcgraphicalstatements(pickcommands(), "    ")
            codeedit.insert("insert", f"\n{funcname} () {{\n{statements}}};\n")
        elif todefine == "Variable":
            varname = askname("Name", "Name of the Variable:")
            if not varname:
                return
            value = state.root.askstring(
                "Value", "Value of the Variable:", parent=pcwin
            )
            if not value:
                return
            codeedit.insert("insert", f"\n{varname} = {value};\n")
        elif todefine == "Startup Code":
            codeedit.insert("insert", f"\n{pcgraphicalstatements(pickcommands())}")
        elif todefine == "Keyboard Shortcut":
            keygetting = state.root.subwin()
            keygetting.title("Keyboard Shortcut")
            ctk.Label(keygetting, text="Press a key:").grid(
                padx=10, pady=10, column=0, row=0
            )
            showkey = ctk.Label(
                keygetting,
                text="",
                bg="white",
                fg="black",
                padx=7,
                pady=7,
                bd=2,
                relief="sunken",
            )
            showkey.grid(column=0, row=1, padx=10, pady=10)
            keygetting.bind(
                "<KeyPress>",
                lambda event: [
                    utils.unlock_window_size(keygetting),
                    keypressforshortcut(event),
                    keygetting.update(),
                    utils.lock_window_size(keygetting),
                ],
            )
            keygetting.protocol("WM_DELETE_WINDOW", "break")
            ctk.Button(keygetting, text="Done", command=shortcutselected).grid(
                column=0, row=2, padx=10, pady=10
            )
            shortcut = []
            keygetting.update()
            utils.lock_window_size(keygetting)
            while not shortcut:
                keygetting.update()
            keygetting.destroy()
            shortcut = "".join(shortcut).replace("+", "-")
            codeedit.insert(
                "insert",
                f"\nkey_bind({f'<{shortcut}>'!r}, {pcgraphicallambda(pickcommands())});\n",
            )
        elif todefine == "Alt-X Command":
            cmdname = state.root.askstring(
                "Name", "Name of the Alt-X Command:", parent=pcwin
            )
            if not cmdname:
                return
            codeedit.insert(
                "insert",
                f"\nadd_command({cmdname!r}, {pcgraphicallambda(pickcommands())});\n",
            )
        elif todefine == "Event Hook":
            hookwin = state.root.subwin()
            hookwin.title("PyCode Event Hook Definition")
            ctk.Label(hookwin, text="When:").grid(
                column=0, row=0, padx=10, pady=10, sticky="e"
            )
            whenvar = tk.StringVar(hookwin)
            ctk.OptionMenu(hookwin, whenvar, "before", "after").grid(
                column=1, row=0, padx=10, pady=10, sticky="ew"
            )
            ctk.Label(hookwin, text="Event:").grid(
                column=0, row=1, padx=10, pady=10, sticky="e"
            )
            eventtype = ctk.Combobox(hookwin, values=pchookevents, state="readonly")
            eventtype.set(pchookevents[0])
            eventtype.grid(column=1, row=1, padx=10, pady=10, sticky="ew")
            hookdone = []
            ctk.Button(
                hookwin,
                text="Done",
                command=lambda: [
                    hookdone.append((whenvar.get(), eventtype.get())),
                    hookwin.destroy(),
                ],
            ).grid(column=1, row=2, columnspan=2, padx=10, pady=10, sticky="ew")
            hookwin.update()
            utils.lock_window_size(hookwin)
            hookwin.wait_window()
            if not hookdone:
                return
            when, event = hookdone[0]
            if event in ("alt-x-command", "pycode-command"):
                subcmd = state.root.askstring(
                    "Command Name",
                    f'{"Alt-X" if event == "alt-x-command" else "PyCode"} command (leave blank for all):',
                    parent=pcwin,
                )
                if subcmd:
                    event = f"{event}:{subcmd.strip()}"
            codeedit.insert(
                "insert",
                f"\nadd_event_hook({f'{when}:{event}'!r}, {pcgraphicallambda(pickcommands())});\n",
            )
        optionsdropdown.config(state="normal")

    optionsdropdown = ctk.OptionMenu(
        buttonframe,
        todefine,
        "Function",
        "Variable",
        "Startup Code",
        "Keyboard Shortcut",
        "Alt-X Command",
        "Event Hook",
        command=lambda inpt: [
            optionsdropdown.config(state="disabled"),
            define(inpt),
            optionsdropdown.config(state="normal"),
        ],
    )
    optionsdropdown.grid(column=0)
    commands = sorted(pycode_commands)
    buttons = []
    commandtodo = []
    commanddone = []

    def setcommand(command):
        if command == "Done":
            hidebuttons()
            commanddone.append("True")
        else:
            commandtodo.append(command)

    def hidebuttons():
        for button in buttons:
            button.grid_forget()
        pccmddonebutton.pack_forget()

    for command in commands:
        button = ctk.Button(
            buttonframe,
            text=command,
            command=lambda command=command: setcommand(command),
        )
        buttons.append(button)
    done = ctk.Button(
        pcwin,
        text="Done",
        command=lambda: [pcdone(codeedit.get("1.0", "end-1c")), pcwin.destroy()],
    )
    done.pack(side="bottom", fill="x", expand=True)
    codeedit = ctk.Textbox(pcwin, scrolled=True, font=monospace, wrap="word")
    codeedit.pack(side="left", fill="both")
    codeedit.focus_set()
    codeedit.bind("<semicolon>", lambda event: edit(codeedit, ";"))
    codeedit.bind("(", lambda event: edit(codeedit, "("))
    codeedit.bind("[", lambda event: edit(codeedit, "["))
    codeedit.bind("<braceleft>", lambda event: edit(codeedit, "{"))
    codeedit.bind("<quoteright>", lambda event: edit(codeedit, "'"))
    codeedit.bind("<quotedbl>", lambda event: edit(codeedit, '"'))
    try:
        open(f"{homedir}/.pynotes", "r", encoding="utf-8")
    except Exception:
        open(f"{homedir}/.pynotes", "w+", encoding="utf-8")
    codeedit.insert("end", open(f"{homedir}/.pynotes", "r", encoding="utf-8").read())
    pcwin.update()
    utils.lock_window_size(pcwin)
    pcrunhook("after", "open-pycode")
