"""Phase 6: Target Code Generation.

Translates optimized intermediate representation instructions into deterministic
Virtual Kitchen Machine (VKM) bytecode assembly instructions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .ir import IRInstruction
from .language_spec import VKM_HARDWARE_MAPPING, TIME_TO_SECONDS


@dataclass
class TargetInstruction:
    """Represents an assembly instruction for the Virtual Kitchen Machine (VKM)."""
    address: str
    mnemonic: str
    operands: List[str]
    source_line: int
    raw_assembly: str
    cycle_cost: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "mnemonic": self.mnemonic,
            "operands": self.operands,
            "source_line": self.source_line,
            "assembly": self.raw_assembly,
            "cycle_cost": self.cycle_cost,
            "description": self.description,
        }


class CodeGenerator:
    """Generates Virtual Kitchen Machine (VKM) assembly code from optimized IR."""

    def __init__(self, optimized_ir: List[IRInstruction]) -> None:
        self.ir_instructions: List[IRInstruction] = optimized_ir
        self.target_instructions: List[TargetInstruction] = []

    def generate(self) -> List[TargetInstruction]:
        """Translate IR instructions to VKM assembly instructions."""
        self.target_instructions = []
        pc = 0  # Program Counter

        for inst in self.ir_instructions:
            addr_str = f"0x{pc:04X}"

            if inst.op == "DECLARE_RECIPE":
                dish = str(inst.arg1).upper()
                asm = f"LOAD_VESSEL {dish}"
                self.target_instructions.append(TargetInstruction(
                    address=addr_str,
                    mnemonic="LOAD_VESSEL",
                    operands=[dish],
                    source_line=inst.line,
                    raw_assembly=asm,
                    cycle_cost=10,
                    description=f"Mount and sanitize automated preparation vessel for {dish}.",
                ))
                pc += 1

            elif inst.op == "DISPENSE":
                ing = str(inst.arg1).upper()
                qty = inst.arg2
                unit = str(inst.arg3).upper()
                asm = f"DISPENSE {ing}, {qty}, {unit}"
                self.target_instructions.append(TargetInstruction(
                    address=addr_str,
                    mnemonic="DISPENSE",
                    operands=[ing, str(qty), unit],
                    source_line=inst.line,
                    raw_assembly=asm,
                    cycle_cost=5,
                    description=f"Engage feeder #{ing} to dispense {qty} {unit} into active vessel.",
                ))
                pc += 1

            elif inst.op == "COOK":
                op_name = str(inst.arg1).upper()
                dur = float(inst.arg2)
                time_unit = str(inst.arg3).upper()
                # Ensure duration in seconds
                dur_sec = dur * TIME_TO_SECONDS.get(time_unit, 1.0)

                mapping = VKM_HARDWARE_MAPPING.get(op_name, {"command": "EXEC_ACTION", "param1_name": "val", "param1_val": 0})
                vkm_cmd = mapping["command"]
                param_val = mapping["param1_val"]

                asm = f"{vkm_cmd} {param_val}, {dur_sec:.0f}s"
                self.target_instructions.append(TargetInstruction(
                    address=addr_str,
                    mnemonic=vkm_cmd,
                    operands=[str(param_val), f"{dur_sec:.0f}s"],
                    source_line=inst.line,
                    raw_assembly=asm,
                    cycle_cost=int(dur_sec),
                    description=f"Activate {vkm_cmd} actuator ({mapping['param1_name']}={param_val}) for {dur_sec:.0f} seconds.",
                ))
                pc += 1

            elif inst.op == "CHOP":
                ing = str(inst.arg1).upper()
                asm = f"CHOP_BLADE {ing}, MED_SPEED"
                self.target_instructions.append(TargetInstruction(
                    address=addr_str,
                    mnemonic="CHOP_BLADE",
                    operands=[ing, "MED_SPEED"],
                    source_line=inst.line,
                    raw_assembly=asm,
                    cycle_cost=15,
                    description=f"Engage rotary blade cutting station for produce item {ing}.",
                ))
                pc += 1

            elif inst.op == "SERVE":
                style = str(inst.arg1).upper() if inst.arg1 else "DEFAULT"
                asm = f"PLATING_SERVE {style}"
                self.target_instructions.append(TargetInstruction(
                    address=addr_str,
                    mnemonic="PLATING_SERVE",
                    operands=[style],
                    source_line=inst.line,
                    raw_assembly=asm,
                    cycle_cost=8,
                    description=f"Discharge finished culinary dish onto serving plate (style={style}).",
                ))
                pc += 1

        # Final Halt instruction to stop virtual machine processing
        halt_addr = f"0x{pc:04X}"
        self.target_instructions.append(TargetInstruction(
            address=halt_addr,
            mnemonic="HALT",
            operands=[],
            source_line=self.target_instructions[-1].source_line if self.target_instructions else 1,
            raw_assembly="HALT",
            cycle_cost=1,
            description="Power down all cooking heaters, stirrers, and dispensers. Program execution terminated.",
        ))

        return self.target_instructions

    def to_assembly_text(self) -> str:
        """Render complete formatted VKM assembly code listing."""
        lines = [
            "; ==========================================================================",
            "; DIGITAL COOKBOOK VIRTUAL MACHINE (VKM) TARGET ASSEMBLY",
            "; Architecture: 64-bit Automated Culinary Processor",
            "; ==========================================================================",
            "",
            ".text",
            ".global _start",
            "",
            "_start:",
        ]

        for inst in self.target_instructions:
            lines.append(f"    {inst.address}    {inst.raw_assembly:<32} ; [Line {inst.source_line}] {inst.description}")

        lines.append("")
        lines.append("; End of VKM Assembly Program")
        return "\n".join(lines)
