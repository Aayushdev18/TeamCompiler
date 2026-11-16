"""Unit Tests for Phase 5: Code Optimization."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ir import IRGenerator
from compiler.optimizer import IROptimizer


def test_unit_normalization_pass():
    source = """
    RECIPE PANCAKE;
    ADD(1, CUP, MILK);
    ADD(1, KG, FLOUR);
    MIX(2, MINUTES);
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()

    optimizer = IROptimizer(raw_ir)
    opt_ir, transformations, metrics = optimizer.optimize()

    # MILK should be converted from 1 CUP to 240 ML
    milk_inst = [i for i in opt_ir if i.op == "DISPENSE" and i.arg1 == "MILK"][0]
    assert milk_inst.arg3 == "ML"
    assert milk_inst.arg2 == 240.0

    # FLOUR should be converted from 1 KG to 1000 GRAM
    flour_inst = [i for i in opt_ir if i.op == "DISPENSE" and i.arg1 == "FLOUR"][0]
    assert flour_inst.arg3 == "GRAM"
    assert flour_inst.arg2 == 1000.0

    # MIX should be converted from 2 MINUTES to 120 SECONDS
    mix_inst = [i for i in opt_ir if i.op == "COOK" and i.arg1 == "MIX"][0]
    assert mix_inst.arg3 == "SECONDS"
    assert mix_inst.arg2 == 120.0


def test_adjacent_dispense_merging():
    """Verify consecutive additions of the same ingredient are merged into 1 instruction."""
    source = """
    RECIPE PANCAKE;
    ADD(100, GRAM, FLOUR);
    ADD(150, GRAM, FLOUR); // Adjacent addition of same ingredient!
    ADD(1, PIECE, EGG);
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()
    initial_count = len(raw_ir)

    optimizer = IROptimizer(raw_ir)
    opt_ir, transformations, metrics = optimizer.optimize()

    assert len(opt_ir) == initial_count - 1
    flour_insts = [i for i in opt_ir if i.op == "DISPENSE" and i.arg1 == "FLOUR"]
    assert len(flour_insts) == 1
    assert flour_insts[0].arg2 == 250.0  # 100 + 150
    assert metrics["reduction_percentage"] > 0


def test_adjacent_cook_merging():
    """Verify consecutive identical timed operations are merged."""
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    MIX(1, MINUTES);
    MIX(2, MINUTES); // Consecutive mixing steps!
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()

    optimizer = IROptimizer(raw_ir)
    opt_ir, transformations, metrics = optimizer.optimize()

    # 1 min (60s) + 2 min (120s) = 180s
    mix_insts = [i for i in opt_ir if i.op == "COOK" and i.arg1 == "MIX"]
    assert len(mix_insts) == 1
    assert mix_insts[0].arg2 == 180.0
    assert mix_insts[0].arg3 == "SECONDS"


def test_dead_code_elimination():
    """Verify 0-quantity additions are eliminated."""
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    ADD(0, GRAM, FLOUR); // Zero quantity!
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()

    optimizer = IROptimizer(raw_ir)
    opt_ir, transformations, metrics = optimizer.optimize()

    rules_applied = [t.rule_name for t in transformations]
    assert "RULE_PRUNE_ZERO_QUANTITY" in rules_applied
