"""Phase Orchestrator: Central Compilation Pipeline.

Coordinates the 6-phase compiler lifecycle (Lexer, Parser, Semantic Analyzer,
IR Generator, Optimizer, Code Generator) and returns a structured JSON payload.
"""

import time
from typing import Dict, Any, List, Optional
from .diagnostics import DiagnosticBag, DiagnosticPhase
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .ir import IRGenerator
from .optimizer import IROptimizer
from .codegen import CodeGenerator


class CompilationPipeline:
    """End-to-End Compiler Pipeline for Digital Cookbook DSL."""

    def __init__(self, source_code: str) -> None:
        self.source: str = source_code
        self.diagnostics: DiagnosticBag = DiagnosticBag()

    def compile(self) -> Dict[str, Any]:
        """Execute the compilation pipeline across all six phases."""
        start_time = time.perf_counter()

        phases: List[Dict[str, Any]] = [
            {"id": "lexer", "name": "Lexical Analysis", "phase_number": 1, "status": "pending", "output": {}},
            {"id": "parser", "name": "Syntax Analysis", "phase_number": 2, "status": "pending", "output": {}},
            {"id": "semantic", "name": "Semantic Analysis", "phase_number": 3, "status": "pending", "output": {}},
            {"id": "ir", "name": "Intermediate Code Generation", "phase_number": 4, "status": "pending", "output": {}},
            {"id": "optimizer", "name": "Code Optimization", "phase_number": 5, "status": "pending", "output": {}},
            {"id": "codegen", "name": "Target Code Generation", "phase_number": 6, "status": "pending", "output": {}},
        ]

        def get_phase_record(phase_id: str) -> Dict[str, Any]:
            for p in phases:
                if p["id"] == phase_id:
                    return p
            raise KeyError(phase_id)

        try:
            # -------------------------------------------------------------
            # PHASE 1: LEXICAL ANALYSIS
            # -------------------------------------------------------------
            lexer_rec = get_phase_record("lexer")
            p1_start = time.perf_counter()
            lexer = Lexer(self.source, self.diagnostics)
            tokens = lexer.tokenize(include_comments=True)
            p1_duration = (time.perf_counter() - p1_start) * 1000

            lexer_rec["output"] = {
                "tokens": [t.to_dict() for t in tokens],
                "total_tokens": len(tokens),
                "summary": lexer.get_summary(),
                "duration_ms": round(p1_duration, 2),
            }

            lexer_errors = [d for d in self.diagnostics.errors() if d.phase == DiagnosticPhase.LEXER]
            if lexer_errors:
                lexer_rec["status"] = "error"
                # If lexer encountered critical illegal characters, abort downstream
                for p in phases[1:]:
                    p["status"] = "skipped"
                return self._build_result(False, phases, start_time)

            lexer_rec["status"] = "success"

            # -------------------------------------------------------------
            # PHASE 2: SYNTAX ANALYSIS
            # -------------------------------------------------------------
            parser_rec = get_phase_record("parser")
            p2_start = time.perf_counter()
            # Feed token stream excluding comments to parser
            non_comment_tokens = [t for t in tokens if t.category != "Comment"]
            parser = Parser(non_comment_tokens, self.diagnostics)
            ast = parser.parse()
            p2_duration = (time.perf_counter() - p2_start) * 1000

            parser_rec["output"] = {
                "ast": ast.to_dict() if ast else None,
                "duration_ms": round(p2_duration, 2),
            }

            parser_errors = [d for d in self.diagnostics.errors() if d.phase == DiagnosticPhase.PARSER]
            if parser_errors:
                parser_rec["status"] = "error"
                for p in phases[2:]:
                    p["status"] = "skipped"
                return self._build_result(False, phases, start_time)

            parser_rec["status"] = "success"

            # -------------------------------------------------------------
            # PHASE 3: SEMANTIC ANALYSIS
            # -------------------------------------------------------------
            semantic_rec = get_phase_record("semantic")
            p3_start = time.perf_counter()
            semantic = SemanticAnalyzer(ast, self.diagnostics)
            symbol_table = semantic.analyze()
            p3_duration = (time.perf_counter() - p3_start) * 1000

            semantic_rec["output"] = {
                "symbol_table": symbol_table.to_list(),
                "total_symbols": symbol_table.count(),
                "checklist": semantic.get_checklist_dict(),
                "duration_ms": round(p3_duration, 2),
            }

            semantic_errors = [d for d in self.diagnostics.errors() if d.phase == DiagnosticPhase.SEMANTIC]
            if semantic_errors:
                semantic_rec["status"] = "error"
                for p in phases[3:]:
                    p["status"] = "skipped"
                return self._build_result(False, phases, start_time)

            semantic_rec["status"] = "success"

            # -------------------------------------------------------------
            # PHASE 4: INTERMEDIATE REPRESENTATION GENERATION
            # -------------------------------------------------------------
            ir_rec = get_phase_record("ir")
            p4_start = time.perf_counter()
            ir_gen = IRGenerator(ast)
            ir_instructions = ir_gen.generate()
            p4_duration = (time.perf_counter() - p4_start) * 1000

            ir_rec["output"] = {
                "instructions": [inst.to_dict() for inst in ir_instructions],
                "readable_ir": "\n".join(inst.to_readable() for inst in ir_instructions),
                "count": len(ir_instructions),
                "duration_ms": round(p4_duration, 2),
            }
            ir_rec["status"] = "success"

            # -------------------------------------------------------------
            # PHASE 5: CODE OPTIMIZATION
            # -------------------------------------------------------------
            opt_rec = get_phase_record("optimizer")
            p5_start = time.perf_counter()
            optimizer = IROptimizer(ir_instructions)
            optimized_ir, transformations, opt_metrics = optimizer.optimize()
            p5_duration = (time.perf_counter() - p5_start) * 1000

            opt_rec["output"] = {
                "original_ir": [inst.to_dict() for inst in ir_instructions],
                "optimized_ir": [inst.to_dict() for inst in optimized_ir],
                "readable_original": "\n".join(inst.to_readable() for inst in ir_instructions),
                "readable_optimized": "\n".join(inst.to_readable() for inst in optimized_ir),
                "transformations": [t.to_dict() for t in transformations],
                "passes_summary": optimizer.passes_summary,
                "metrics": opt_metrics,
                "duration_ms": round(p5_duration, 2),
            }
            opt_rec["status"] = "success"

            # -------------------------------------------------------------
            # PHASE 6: TARGET CODE GENERATION
            # -------------------------------------------------------------
            codegen_rec = get_phase_record("codegen")
            p6_start = time.perf_counter()
            codegen = CodeGenerator(optimized_ir)
            target_instructions = codegen.generate()
            assembly_text = codegen.to_assembly_text()
            p6_duration = (time.perf_counter() - p6_start) * 1000

            codegen_rec["output"] = {
                "instructions": [ti.to_dict() for ti in target_instructions],
                "assembly_text": assembly_text,
                "total_instructions": len(target_instructions),
                "total_cycle_cost": sum(ti.cycle_cost for ti in target_instructions),
                "duration_ms": round(p6_duration, 2),
            }
            codegen_rec["status"] = "success"

            return self._build_result(True, phases, start_time)

        except Exception as ex:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SYSTEM,
                message=f"Internal compiler failure: {str(ex)}",
                line=1,
                column=1,
                code="ERR_INTERNAL_COMPILER",
            )
            # Mark any remaining pending phases as error/skipped
            for p in phases:
                if p["status"] == "pending":
                    p["status"] = "error"
                    break
            for p in phases:
                if p["status"] == "pending":
                    p["status"] = "skipped"

            return self._build_result(False, phases, start_time)

    def _build_result(self, success: bool, phases: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
        """Construct the final structured JSON response payload."""
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        errors = self.diagnostics.errors()
        warnings = self.diagnostics.warnings()

        return {
            "success": success and len(errors) == 0,
            "compilation_time_ms": total_time_ms,
            "phases": phases,
            "diagnostics": self.diagnostics.to_list(),
            "summary": {
                "success": success and len(errors) == 0,
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "phases_succeeded": sum(1 for p in phases if p["status"] == "success"),
                "phases_failed": sum(1 for p in phases if p["status"] == "error"),
                "phases_skipped": sum(1 for p in phases if p["status"] == "skipped"),
            },
        }
