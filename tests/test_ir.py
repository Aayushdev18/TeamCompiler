"""Unit Tests for Phase 4: Intermediate Representation (IR)."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ir import IRGenerator


def test_ir_generation_structure():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    ADD(1, PIECE, EGG);
    MIX(3, MINUTES);
    SERVE;
    """
    lexer = Lexer(source)
    tokens = [t for t in lexer.tokenize() if t.category != "Comment"]
    parser = Parser(tokens)
    ast = parser.parse()

    ir_gen = IRGenerator(ast)
    instructions = ir_gen.generate()

    assert len(instructions) == 5
    assert instructions[0].op == "DECLARE_RECIPE"
    assert instructions[0].arg1 == "PANCAKE"

    assert instructions[1].op == "DISPENSE"
    assert instructions[1].arg1 == "FLOUR"
    assert instructions[1].arg2 == 2.0
    assert instructions[1].arg3 == "CUP"

    assert instructions[2].op == "DISPENSE"
    assert instructions[2].arg1 == "EGG"

    assert instructions[3].op == "COOK"
    assert instructions[3].arg1 == "MIX"
    assert instructions[3].arg2 == 3.0
    assert instructions[3].arg3 == "MINUTES"

    assert instructions[4].op == "SERVE"


def test_readable_3ac_formatting():
    source = """
    RECIPE TEA;
    ADD(250, ML, WATER);
    BOIL(3, MINUTES);
    SERVE;
    """
    lexer = Lexer(source)
    tokens = [t for t in lexer.tokenize() if t.category != "Comment"]
    ast = Parser(tokens).parse()
    instructions = IRGenerator(ast).generate()

    readable = [inst.to_readable() for inst in instructions]
    assert any("RECIPE TEA" in r for r in readable)
    assert any("ADD WATER, 250 ML" in r for r in readable)
    assert any("BOIL 3 MINUTES" in r for r in readable)
    assert any("SERVE" in r for r in readable)
