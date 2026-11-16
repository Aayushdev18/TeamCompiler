"""Unit Tests for Full Compiler Pipeline."""

import pytest
from compiler.pipeline import CompilationPipeline


def test_full_pipeline_success_pancake():
    source = """
    RECIPE PANCAKE;
    ADD(2, CUP, FLOUR);
    ADD(1, PIECE, EGG);
    ADD(1, CUP, MILK);
    MIX(3, MINUTES);
    FRY(5, MINUTES);
    SERVE;
    """
    pipeline = CompilationPipeline(source)
    res = pipeline.compile()
    assert res["success"] is True
    assert res["summary"]["phases_succeeded"] == 6
    assert res["summary"]["phases_failed"] == 0
    assert res["summary"]["phases_skipped"] == 0

    # Verify each phase has real output
    phases_by_id = {p["id"]: p for p in res["phases"]}
    assert phases_by_id["lexer"]["output"]["total_tokens"] > 0
    assert phases_by_id["parser"]["output"]["ast"] is not None
    assert len(phases_by_id["semantic"]["output"]["symbol_table"]) >= 4
    assert phases_by_id["ir"]["output"]["count"] >= 6
    assert phases_by_id["optimizer"]["output"]["metrics"]["count_before"] > 0
    assert "HALT" in phases_by_id["codegen"]["output"]["assembly_text"]


def test_full_pipeline_syntax_failure_skips_downstream():
    source = "RECIPE PANCAKE; ADD(2, CUP, FLOUR) SERVE;"
    pipeline = CompilationPipeline(source)
    res = pipeline.compile()
    assert res["success"] is False
    phases_by_id = {p["id"]: p for p in res["phases"]}
    assert phases_by_id["lexer"]["status"] == "success"
    assert phases_by_id["parser"]["status"] == "error"
    assert phases_by_id["semantic"]["status"] == "skipped"
    assert phases_by_id["ir"]["status"] == "skipped"
    assert phases_by_id["optimizer"]["status"] == "skipped"
    assert phases_by_id["codegen"]["status"] == "skipped"


def test_full_pipeline_semantic_failure_skips_codegen():
    source = """
    RECIPE HERBAL_TEA;
    ADD(500, ML, WATER);
    ADD(5, GRAM, TEA_LEAVES);
    ADD(100, GRAM, BACON); // Invalid ingredient for tea
    BOIL(5, MINUTES);
    SERVE;
    """
    pipeline = CompilationPipeline(source)
    res = pipeline.compile()
    assert res["success"] is False
    phases_by_id = {p["id"]: p for p in res["phases"]}
    assert phases_by_id["lexer"]["status"] == "success"
    assert phases_by_id["parser"]["status"] == "success"
    assert phases_by_id["semantic"]["status"] == "error"
    assert phases_by_id["ir"]["status"] == "skipped"
    assert phases_by_id["optimizer"]["status"] == "skipped"
    assert phases_by_id["codegen"]["status"] == "skipped"
