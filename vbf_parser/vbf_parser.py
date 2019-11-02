import re
from typing import List, Tuple, Union

VBF_SYNTAX = "={};,"
WHITESPACE = "\r\n\t\f\v "


def _lex_quoted(header: str) -> Tuple[str, str]:
    """
    >>> _lex_quoted('"abc";a=10')
    ('"abc"', ';a=10')
    >>> _lex_quoted('a=10')
    ('', 'a=10')
    """
    if header[0] != '"':
        return "", header
    end_quote_pos = header.find('"', 1)
    return header[: end_quote_pos + 1], header[end_quote_pos + 1 :]


def _lex_unquoted_value(header: str) -> Tuple[str, str]:
    """
    >>> _lex_unquoted_value("abc=10")
    ('abc', '=10')
    >>> _lex_unquoted_value(" a")
    ('', ' a')
    >>> _lex_unquoted_value("abc")
    ('abc', '')
    """
    if header[0] in VBF_SYNTAX + WHITESPACE:
        return "", header
    match = re.search(rf"[\s{VBF_SYNTAX}]", header)
    if not match:
        return header, ""
    return header[: match.start()], header[match.start() :]


def _lex_syntax(header: str) -> Tuple[str, str]:
    """
    >>> _lex_syntax("=123")
    ('=', '123')
    """
    if header[0] not in VBF_SYNTAX:
        return "", header
    return header[0], header[1:]


def _lex_whitespace(header: str) -> Tuple[str, str]:
    """
    >>> _lex_whitespace(" \\n  a")
    ('', 'a')
    >>> _lex_whitespace(" abc")
    ('', 'abc')
    >>> _lex_whitespace("a ")
    ('', 'a ')
    """
    whitespace_match = re.match(r"\s+", header)
    if not whitespace_match:
        return "", header
    return "", header[whitespace_match.end() :]


def _lex_single_line_comment(header: str) -> Tuple[str, str]:
    """
    >>> _lex_single_line_comment("a=10")
    ('', 'a=10')
    >>> _lex_single_line_comment("//comment\\nb=20")
    ('', 'b=20')
    """
    if header[:2] != "//":
        return "", header
    line_end_pos = header.find("\n")
    return "", header[line_end_pos + 1 :]


def _lex_multi_line_comment(header: str) -> Tuple[str, str]:
    """
    >>> _lex_multi_line_comment("a=10")
    ('', 'a=10')
    >>> _lex_multi_line_comment("/*multiline\\ncomment*/b=20")
    ('', 'b=20')
    """
    if header[:2] != "/*":
        return "", header
    end_comment_pos = header.find("*/")
    return "", header[end_comment_pos + 2 :]


def lex_vbf_header(header: str) -> List[str]:
    """
    >>> lex_vbf_header('x = "ab"')
    ['x', '=', '"ab"']
    >>> lex_vbf_header('y={1,  2,3}')
    ['y', '=', '{', '1', ',', '2', ',', '3', '}']
    >>> lex_vbf_header('y={{1,2},3};  abc=   0x12;')
    ['y', '=', '{', '{', '1', ',', '2', '}', ',', '3', '}', ';', 'abc', '=', '0x12', ';']
    >>> lex_vbf_header('x=1; //comment \\ny=2; /* multiline \\n comment */z=3')
    ['x', '=', '1', ';', 'y', '=', '2', ';', 'z', '=', '3']
    """
    tokens = []
    lexing_functions = [
        _lex_quoted,
        _lex_unquoted_value,
        _lex_syntax,
        _lex_whitespace,
        _lex_single_line_comment,
        _lex_multi_line_comment,
    ]
    while header:
        for lex_func in lexing_functions:
            token, header = lex_func(header)
            if token:
                tokens.append(token)
                break
    return tokens


def _parse_array(tokens: List[str]) -> Tuple[Union[list, str], List[str]]:
    """
    >>> _parse_array(list("1,{2,3}};abc"))
    (['1', ['2', '3']], [';', 'a', 'b', 'c'])
    >>> _parse_array(list("1}"))
    (['1'], [])
    >>> _parse_array(list(""))
    ([], [])
    """
    array: List[Union[list, str]] = []
    while tokens:
        token, *tokens = tokens
        if token == "}":
            return array, tokens
        elif token == "{":
            sub_array, tokens = _parse_array(tokens)
            array.append(sub_array)
        elif token != ",":
            array.append(token)
            assert tokens[0] == "}" or tokens[0] == ","
    return array, tokens


def parse_vbf_tokens(tokens: List[str]):
    """
    >>> tokens = lex_vbf_header('x = 10; yz={1,{2,3}};')
    >>> parse_vbf_tokens(tokens)
    {'x': '10', 'yz': ['1', ['2', '3']]}

    >>> tokens = lex_vbf_header('x = 0xff;')
    >>> parse_vbf_tokens(tokens)
    {'x': 255}

    >>> tokens = lex_vbf_header('abc = 0xff; //comment \\n z = "a b"; /* multi\\nline*/ y = {1,{2,3}  };')
    >>> parse_vbf_tokens(tokens)
    {'abc': 255, 'z': 'a b', 'y': ['1', ['2', '3']]}
    """
    result = {}
    value: Union[int, list, str]
    while tokens:
        name, equal_sign, *tokens = tokens
        assert equal_sign == "=", f"Syntax error: expected '=' got {equal_sign}; before: {''.join(tokens)}"
        if tokens[0] == "{":
            value, (semicolon, *tokens) = _parse_array(tokens[1:])
        else:
            value, semicolon, *tokens = tokens
            if value.startswith("0x"):
                value = int(value, base=16)
            elif re.match(r'"[^"]*"', value):
                value = value[1:-1]
        assert semicolon == ";", f"Syntax error: expected ';' got {semicolon}; before: {''.join(tokens)}"
        result[name] = value
    return result
