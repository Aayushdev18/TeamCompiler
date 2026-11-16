"""Phase 5: Intermediate Code Optimization.

Implements multi-pass semantic-preserving transformations:
1. Canonical Measurement & Time Unit Normalization
2. Adjacent Compatible Instruction Merging (Peephole Optimization)
3. Redundant / Dead Instruction Elimination
Provides transparent before-and-after tracking with mathematical justifications.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy
from .ir import IRInstruction
from .language_spec import (
    VOLUME_TO_ML,
    MASS_TO_GRAM,
    TIME_TO_SECONDS,
    get_ingredient_spec,
)


@dataclass
class OptimizationTransformation:
    """Detailed log record of an applied optimization transformation."""
    pass_name: str
    rule_name: str
    original_instructions: List[str]
    transformed_instructions: List[str]
    reason: str
    safety_justification: str
    lines: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass_name": self.pass_name,
            "rule_name": self.rule_name,
            "original_instructions": self.original_instructions,
            "transformed_instructions": self.transformed_instructions,
            "reason": self.reason,
            "safety_justification": self.safety_justification,
            "lines": self.lines,
        }


class IROptimizer:
    """Multi-pass optimizer operating on 3AC intermediate code."""

    def __init__(self, ir_instructions: List[IRInstruction]) -> None:
        self.original_ir: List[IRInstruction] = deepcopy(ir_instructions)
        self.current_ir: List[IRInstruction] = deepcopy(ir_instructions)
        self.transformations: List[OptimizationTransformation] = []
        self.passes_summary: List[Dict[str, Any]] = []

    def optimize(self) -> Tuple[List[IRInstruction], List[OptimizationTransformation], Dict[str, Any]]:
        """Run all optimization passes sequentially."""
        # Pass 1: Unit Normalization
        p1_before = len(self.current_ir)
        self._pass_unit_normalization()
        p1_after = len(self.current_ir)
        self.passes_summary.append({
            "pass_id": "P1_UNIT_NORMALIZATION",
            "name": "Measurement & Temporal Normalization",
            "description": "Converts disparate volume, mass, and duration units to standardized base units (ML, GRAM, SECONDS).",
            "instructions_before": p1_before,
            "instructions_after": p1_after,
        })

        # Pass 2: Adjacent Compatible Instruction Merging (Peephole)
        p2_before = len(self.current_ir)
        self._pass_adjacent_merging()
        p2_after = len(self.current_ir)
        self.passes_summary.append({
            "pass_id": "P2_ADJACENT_MERGING",
            "name": "Peephole Adjacent Instruction Merging",
            "description": "Combines consecutive unseparated additions of identical ingredients and contiguous timed actions.",
            "instructions_before": p2_before,
            "instructions_after": p2_after,
        })

        # Pass 3: Dead / Zero-Action Elimination
        p3_before = len(self.current_ir)
        self._pass_dead_code_elimination()
        p3_after = len(self.current_ir)
        self.passes_summary.append({
            "pass_id": "P3_DEAD_CODE",
            "name": "Redundant Instruction Elimination",
            "description": "Prunes zero-quantity dispensations and null-duration actions that produce no culinary effect.",
            "instructions_before": p3_before,
            "instructions_after": p3_after,
        })

        # Renumber remaining instructions cleanly
        for idx, inst in enumerate(self.current_ir, start=1):
            inst.id = idx
            inst.result = f"t{idx}"

        count_before = len(self.original_ir)
        count_after = len(self.current_ir)
        reduction_pct = round(((count_before - count_after) / count_before) * 100, 1) if count_before > 0 else 0.0

        metrics = {
            "count_before": count_before,
            "count_after": count_after,
            "difference": count_before - count_after,
            "reduction_percentage": reduction_pct,
            "total_transformations": len(self.transformations),
        }

        return self.current_ir, self.transformations, metrics

    def _pass_unit_normalization(self) -> None:
        """Pass 1: Normalize units to canonical base units (ML, GRAM, SECONDS)."""
        for inst in self.current_ir:
            # 1. Normalize ingredient additions (DISPENSE)
            if inst.op == "DISPENSE":
                ing = inst.arg1
                qty = inst.arg2
                unit = inst.arg3

                if unit in VOLUME_TO_ML and unit != "ML":
                    factor = VOLUME_TO_ML[unit]
                    new_qty = round(qty * factor, 2)
                    orig_repr = inst.to_readable()
                    inst.arg2 = new_qty
                    inst.arg3 = "ML"
                    inst.comment = f"Normalized from {qty} {unit} (1 {unit} = {factor} ML)"
                    self.transformations.append(OptimizationTransformation(
                        pass_name="Measurement Normalization",
                        rule_name="RULE_NORMALIZE_VOLUME",
                        original_instructions=[orig_repr],
                        transformed_instructions=[inst.to_readable()],
                        reason=f"Standardize {unit} to canonical liquid volume base unit (ML).",
                        safety_justification=f"Mathematically equivalent volume: {qty} {unit} = {new_qty} ML.",
                        lines=[inst.line],
                    ))
                elif unit in MASS_TO_GRAM and unit != "GRAM":
                    factor = MASS_TO_GRAM[unit]
                    new_qty = round(qty * factor, 2)
                    orig_repr = inst.to_readable()
                    inst.arg2 = new_qty
                    inst.arg3 = "GRAM"
                    inst.comment = f"Normalized from {qty} {unit} (1 {unit} = {factor} GRAM)"
                    self.transformations.append(OptimizationTransformation(
                        pass_name="Measurement Normalization",
                        rule_name="RULE_NORMALIZE_MASS",
                        original_instructions=[orig_repr],
                        transformed_instructions=[inst.to_readable()],
                        reason=f"Standardize {unit} to canonical mass base unit (GRAM).",
                        safety_justification=f"Mathematically equivalent mass: {qty} {unit} = {new_qty} GRAM.",
                        lines=[inst.line],
                    ))

            # 2. Normalize timed cooking operations (COOK)
            elif inst.op == "COOK":
                op_name = inst.arg1
                dur = inst.arg2
                time_unit = inst.arg3

                if time_unit in TIME_TO_SECONDS and time_unit != "SECONDS":
                    factor = TIME_TO_SECONDS[time_unit]
                    new_dur = round(dur * factor, 2)
                    orig_repr = inst.to_readable()
                    inst.arg2 = new_dur
                    inst.arg3 = "SECONDS"
                    inst.comment = f"Normalized from {dur} {time_unit} (1 {time_unit} = {factor} SECONDS)"
                    self.transformations.append(OptimizationTransformation(
                        pass_name="Measurement Normalization",
                        rule_name="RULE_NORMALIZE_TIME",
                        original_instructions=[orig_repr],
                        transformed_instructions=[inst.to_readable()],
                        reason=f"Standardize {time_unit} to canonical temporal base unit (SECONDS).",
                        safety_justification=f"Mathematically identical duration: {dur} {time_unit} = {new_dur} SECONDS.",
                        lines=[inst.line],
                    ))

    def _pass_adjacent_merging(self) -> None:
        """Pass 2: Merge adjacent compatible dispensations or identical operations."""
        merged: List[IRInstruction] = []
        i = 0
        n = len(self.current_ir)

        while i < n:
            curr = self.current_ir[i]

            # Case A: Check consecutive DISPENSE of identical ingredient with identical unit
            if curr.op == "DISPENSE" and i + 1 < n:
                nxt = self.current_ir[i + 1]
                if nxt.op == "DISPENSE" and nxt.arg1 == curr.arg1 and nxt.arg3 == curr.arg3:
                    # Safe to merge!
                    combined_qty = round(curr.arg2 + nxt.arg2, 2)
                    orig_reprs = [curr.to_readable(), nxt.to_readable()]

                    # Create combined instruction
                    merged_inst = deepcopy(curr)
                    merged_inst.arg2 = combined_qty
                    merged_inst.comment = f"Merged {curr.arg2} + {nxt.arg2} {curr.arg3} of {curr.arg1}"
                    merged.append(merged_inst)

                    self.transformations.append(OptimizationTransformation(
                        pass_name="Adjacent Instruction Merging",
                        rule_name="RULE_MERGE_ADJACENT_DISPENSE",
                        original_instructions=orig_reprs,
                        transformed_instructions=[merged_inst.to_readable()],
                        reason=f"Consecutive additions of identical ingredient '{curr.arg1}' without intervening actions.",
                        safety_justification=(
                            f"Because no intermediate mixing or cooking occurs between lines {curr.line} and {nxt.line}, "
                            f"dispensing {combined_qty} {curr.arg3} in one batch yields the exact same vessel state."
                        ),
                        lines=[curr.line, nxt.line],
                    ))
                    i += 2
                    continue

            # Case B: Check consecutive COOK of identical operation with identical time unit
            if curr.op == "COOK" and i + 1 < n:
                nxt = self.current_ir[i + 1]
                if nxt.op == "COOK" and nxt.arg1 == curr.arg1 and nxt.arg3 == curr.arg3:
                    combined_dur = round(curr.arg2 + nxt.arg2, 2)
                    orig_reprs = [curr.to_readable(), nxt.to_readable()]

                    merged_inst = deepcopy(curr)
                    merged_inst.arg2 = combined_dur
                    merged_inst.comment = f"Combined consecutive {curr.arg1} operations: {curr.arg2}s + {nxt.arg2}s"
                    merged.append(merged_inst)

                    self.transformations.append(OptimizationTransformation(
                        pass_name="Adjacent Instruction Merging",
                        rule_name="RULE_MERGE_ADJACENT_COOK",
                        original_instructions=orig_reprs,
                        transformed_instructions=[merged_inst.to_readable()],
                        reason=f"Consecutive identical operation '{curr.arg1}' without intervening state change.",
                        safety_justification=(
                            f"Running {curr.arg1} continuously for {combined_dur} {curr.arg3} achieves the exact same culinary "
                            f"result without machine cycle restart."
                        ),
                        lines=[curr.line, nxt.line],
                    ))
                    i += 2
                    continue

            merged.append(curr)
            i += 1

        self.current_ir = merged

    def _pass_dead_code_elimination(self) -> None:
        """Pass 3: Prune 0-quantity additions and 0-duration actions."""
        alive: List[IRInstruction] = []

        for inst in self.current_ir:
            if inst.op == "DISPENSE" and inst.arg2 == 0:
                self.transformations.append(OptimizationTransformation(
                    pass_name="Dead Code Elimination",
                    rule_name="RULE_PRUNE_ZERO_QUANTITY",
                    original_instructions=[inst.to_readable()],
                    transformed_instructions=[],
                    reason="Dispense instruction with zero quantity adds no substance to the dish.",
                    safety_justification="Adding zero grams or milliliters produces zero physical change to the vessel.",
                    lines=[inst.line],
                ))
                continue
            if inst.op == "COOK" and inst.arg2 == 0:
                self.transformations.append(OptimizationTransformation(
                    pass_name="Dead Code Elimination",
                    rule_name="RULE_PRUNE_ZERO_DURATION",
                    original_instructions=[inst.to_readable()],
                    transformed_instructions=[],
                    reason=f"Operation {inst.arg1} with zero duration performs no physical processing.",
                    safety_justification="Executing zero seconds of mixing or cooking consumes no thermal/mechanical energy.",
                    lines=[inst.line],
                ))
                continue

            alive.append(inst)

        self.current_ir = alive
