"""Unit Tests for Phase 6: Target Code Generation (Virtual Kitchen Machine)."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ir import IRGenerator
from compiler.optimizer import IROptimizer
from compiler.codegen import CodeGenerator


def test_vkm_target_code_generation():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    MIX(3, MINUTES);
    FRY(5, MINUTES);
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()
    opt_ir, _, _ = IROptimizer(raw_ir).optimize()

    codegen = CodeGenerator(opt_ir)
    target_instructions = codegen.generate()
    asm_text = codegen.to_assembly_text()

    assert len(target_instructions) >= 5
    mnemonics = [t.mnemonic for t in target_instructions]
    assert mnemonics[0] == "LOAD_VESSEL"
    assert "DISPENSE" in mnemonics
    assert "STIR" in mnemonics
    assert "HEAT_FRY" in mnemonics
    assert "PLATING_SERVE" in mnemonics
    assert mnemonics[-1] == "HALT"

    assert ".text" in asm_text
    assert "_start:" in asm_text
    assert "HALT" in asm_text


def test_target_cycle_costs():
    source = """
    RECIPE TEA;
    ADD(250, ML, WATER);
    BOIL(2, MINUTES);
    SERVE;
    """
    ast = Parser([t for t in Lexer(source).tokenize() if t.category != "Comment"]).parse()
    raw_ir = IRGenerator(ast).generate()
    opt_ir, _, _ = IROptimizer(raw_ir).optimize()
    target_instructions = CodeGenerator(opt_ir).generate()

    # Total cycle cost must be positive
    total_cost = sum(t.cycle_cost for t in target_instructions)
    assert total_cost > 120  # Boiling for 2 minutes is 120 seconds
