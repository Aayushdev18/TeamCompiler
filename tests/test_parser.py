"""Unit Tests for Phase 2: Syntax Analysis (Parser)."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import ProgramNode, AddNode, TimedOpNode, ChopNode, ServeNode
from compiler.diagnostics import DiagnosticBag


def parse_source(source: str):
    diag = DiagnosticBag()
    lexer = Lexer(source, diag)
    tokens = [t for t in lexer.tokenize() if t.category != "Comment"]
    parser = Parser(tokens, diag)
    ast = parser.parse()
    return ast, diag


def test_valid_recipe_parsing():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    MIX(3, MINUTES);
    CHOP(BUTTER);
    SERVE;
    """
    ast, diag = parse_source(source)
    assert not diag.has_errors()
    assert ast.recipe_decl is not None
    assert ast.recipe_decl.dish_name == "PANCAKE"
    assert len(ast.statements) == 3
    assert isinstance(ast.statements[0], AddNode)
    assert ast.statements[0].ingredient == "FLOUR"
    assert ast.statements[0].quantity == 2.0
    assert ast.statements[0].unit == "CUP"

    assert isinstance(ast.statements[1], TimedOpNode)
    assert ast.statements[1].operation == "MIX"
    assert ast.statements[1].duration == 3.0
    assert ast.statements[1].time_unit == "MINUTES"

    assert isinstance(ast.statements[2], ChopNode)
    assert ast.statements[2].ingredient == "BUTTER"

    assert isinstance(ast.serve_stmt, ServeNode)


def test_missing_recipe_header():
    source = """
    ADD(2, CUP, FLOUR);
    SERVE;
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Missing recipe declaration" in e.message for e in diag.errors())


def test_missing_semicolon():
    source = """
    RECIPE PANCAKE
    ADD(2, CUP, FLOUR);
    SERVE;
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Expected ';'" in e.message for e in diag.errors())


def test_missing_parentheses():
    source = """
    RECIPE PANCAKE;
    ADD 2, CUP, FLOUR;
    SERVE;
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Expected '('" in e.message for e in diag.errors())


def test_extra_arguments():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR, EXTRA);
    SERVE;
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Too many arguments" in e.message for e in diag.errors())


def test_missing_serve():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Missing mandatory terminating 'SERVE;'" in e.message for e in diag.errors())


def test_statement_after_serve():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    SERVE;
    ADD(1, CUP, MILK);
    """
    ast, diag = parse_source(source)
    assert diag.has_errors()
    assert any("Illegal statement" in e.message for e in diag.errors())
