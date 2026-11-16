"""Unit Tests for Phase 3: Semantic Analysis."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.diagnostics import DiagnosticBag


def analyze_source(source: str):
    diag = DiagnosticBag()
    lexer = Lexer(source, diag)
    tokens = [t for t in lexer.tokenize() if t.category != "Comment"]
    parser = Parser(tokens, diag)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(ast, diag)
    symbol_table = analyzer.analyze()
    return analyzer, symbol_table, diag


def test_valid_pancake_semantics():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    ADD(1, PIECE, EGG);
    ADD(1, CUP, MILK);
    MIX(3, MINUTES);
    FRY(5, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert not diag.has_errors()
    assert sym_tab.lookup("FLOUR") is not None
    assert sym_tab.lookup("EGG") is not None
    assert sym_tab.lookup("MILK") is not None


def test_incompatible_ingredient_for_dish():
    source = """
    RECIPE HERBAL_TEA;
    ADD(500, ML, WATER);
    ADD(5, GRAM, TEA_LEAVES);
    ADD(100, GRAM, BACON); // Bacon in herbal tea!
    BOIL(5, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    errors = diag.errors()
    assert any("not compatible with dish 'HERBAL_TEA'" in e.message for e in errors)


def test_incompatible_measurement_unit():
    source = """
    RECIPE PANCAKE;
    ADD(2, PIECE, FLOUR); // Flour measured in pieces!
    ADD(1, PIECE, EGG);
    ADD(1, CUP, MILK);
    MIX(2, MINUTES);
    FRY(4, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    errors = diag.errors()
    assert any("Invalid measurement unit 'PIECE' for ingredient 'FLOUR'" in e.message for e in errors)


def test_non_positive_quantity():
    source = """
    RECIPE PANCAKE;
    ADD(0, CUP, FLOUR);
    ADD(1, PIECE, EGG);
    ADD(1, CUP, MILK);
    MIX(2, MINUTES);
    FRY(4, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    assert any("must be strictly positive" in e.message for e in diag.errors())


def test_empty_vessel_operation():
    source = """
    RECIPE PANCAKE;
    MIX(5, MINUTES); // Mixing empty bowl before adding any ingredients
    ADD(2, CUP, FLOUR);
    ADD(1, PIECE, EGG);
    ADD(1, CUP, MILK);
    FRY(4, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    assert any("Cannot execute 'MIX' operation before adding any ingredients" in e.message for e in diag.errors())


def test_forbidden_operation_for_raw_dish():
    source = """
    RECIPE FRESH_SALAD;
    ADD(200, GRAM, LETTUCE);
    ADD(2, PIECE, TOMATO);
    ADD(2, TBSP, OIL);
    BAKE(20, MINUTES); // Cannot bake a fresh salad!
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    assert any("Operation 'BAKE' is forbidden for dish 'FRESH_SALAD'" in e.message for e in diag.errors())


def test_missing_required_ingredients():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    // Missing EGG and MILK!
    MIX(2, MINUTES);
    FRY(4, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    assert diag.has_errors()
    assert any("Missing essential ingredients" in e.message for e in diag.errors())


def test_multiple_independent_semantic_errors():
    source = """
    RECIPE PANCAKE;
    ADD(-5, CUP, FLOUR);       // Error 1: negative quantity
    ADD(500, ML, EGG);         // Error 2: egg cannot be measured in ML
    ADD(1, CUP, UNKNOWN_MAGIC);// Error 3: unknown ingredient
    FRY(5, MINUTES);
    SERVE;
    """
    analyzer, sym_tab, diag = analyze_source(source)
    errors = diag.errors()
    assert len(errors) >= 3
