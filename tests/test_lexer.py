"""Unit Tests for Phase 1: Lexical Analysis."""

import pytest
from compiler.tokens import TokenType
from compiler.lexer import Lexer
from compiler.diagnostics import DiagnosticBag, DiagnosticSeverity


def test_empty_source():
    """Verify empty input produces only EOF without crashing."""
    diag = DiagnosticBag()
    lexer = Lexer("", diag)
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert not diag.has_errors()


def test_whitespace_and_comments():
    """Verify whitespace and comments are parsed accurately."""
    source = """
    # Single line hash comment
    // Double slash comment
       
    RECIPE PANCAKE;
    """
    diag = DiagnosticBag()
    lexer = Lexer(source, diag)
    tokens = lexer.tokenize(include_comments=True)
    # Check that comments are captured
    comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
    assert len(comment_tokens) == 2
    assert "Single line hash comment" in comment_tokens[0].value
    assert "Double slash comment" in comment_tokens[1].value

    code_tokens = [t for t in tokens if t.type != TokenType.COMMENT and t.type != TokenType.EOF]
    assert len(code_tokens) == 3
    assert code_tokens[0].type == TokenType.RECIPE
    assert code_tokens[1].type == TokenType.IDENTIFIER
    assert code_tokens[2].type == TokenType.SEMICOLON


def test_token_coordinates():
    """Verify line and column tracking."""
    source = "RECIPE PANCAKE;\nADD(2, CUP, FLOUR);"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert tokens[0].type == TokenType.RECIPE
    assert tokens[0].line == 1
    assert tokens[0].column == 1

    # Line 2 token ADD
    add_tok = [t for t in tokens if t.type == TokenType.ADD][0]
    assert add_tok.line == 2
    assert add_tok.column == 1


def test_numeric_literals():
    """Verify integer and float scanning."""
    source = "10 2.5 0.75 100"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert tokens[0].type == TokenType.INTEGER_CONST
    assert tokens[0].value == 10
    assert tokens[1].type == TokenType.FLOAT_CONST
    assert tokens[1].value == 2.5
    assert tokens[2].type == TokenType.FLOAT_CONST
    assert tokens[2].value == 0.75
    assert tokens[3].type == TokenType.INTEGER_CONST
    assert tokens[3].value == 100


def test_malformed_numbers():
    """Verify malformed decimal format reports diagnostic error."""
    source = "ADD(2., CUP, FLOUR);"
    diag = DiagnosticBag()
    lexer = Lexer(source, diag)
    tokens = lexer.tokenize()
    assert diag.has_errors()
    errors = diag.errors()
    assert any("Malformed" in e.message for e in errors)


def test_unexpected_characters():
    """Verify illegal characters are tagged as UNKNOWN and reported."""
    source = "RECIPE @PANCAKE$;"
    diag = DiagnosticBag()
    lexer = Lexer(source, diag)
    tokens = lexer.tokenize()
    assert diag.has_errors()
    unknowns = [t for t in tokens if t.type == TokenType.UNKNOWN]
    assert len(unknowns) == 2  # '@' and '$'


def test_all_keywords_recognized():
    """Verify all defined keywords map to expected token types."""
    source = "RECIPE ADD MIX BOIL BAKE FRY SIMMER CHILL WHISK CHOP REST SERVE"
    lexer = Lexer(source)
    tokens = [t for t in lexer.tokenize() if t.type != TokenType.EOF]
    expected = [
        TokenType.RECIPE, TokenType.ADD, TokenType.MIX, TokenType.BOIL,
        TokenType.BAKE, TokenType.FRY, TokenType.SIMMER, TokenType.CHILL,
        TokenType.WHISK, TokenType.CHOP, TokenType.REST, TokenType.SERVE
    ]
    assert [t.type for t in tokens] == expected
