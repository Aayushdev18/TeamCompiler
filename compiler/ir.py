"""Phase 4: Intermediate Representation (IR) Generation.

Constructs structured three-address code (3AC) instructions from the validated Abstract Syntax Tree,
maintaining operational metadata and source line coordinates.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from .ast_nodes import ProgramNode, RecipeDeclNode, AddNode, TimedOpNode, ChopNode, ServeNode


@dataclass
class IRInstruction:
    """Represents a single Three-Address Code (3AC) Intermediate Representation instruction."""
    id: int
    op: str
    arg1: Any
    arg2: Any = None
    arg3: Any = None
    result: Optional[str] = None
    line: int = 1
    comment: str = ""

    def to_readable(self) -> str:
        """Format instruction into human-readable 3AC syntax."""
        res_prefix = f"{self.result} = " if self.result else ""

        def fmt_val(v: Any) -> str:
            if isinstance(v, float) and v.is_integer():
                return str(int(v))
            return str(v)

        if self.op == "DECLARE_RECIPE":
            return f"{res_prefix}RECIPE {self.arg1}"
        if self.op == "DISPENSE":
            return f"{res_prefix}ADD {self.arg1}, {fmt_val(self.arg2)} {self.arg3}"
        if self.op == "COOK":
            return f"{res_prefix}{self.arg1} {fmt_val(self.arg2)} {self.arg3}"
        if self.op == "CHOP":
            return f"{res_prefix}CHOP {self.arg1}"
        if self.op == "SERVE":
            opt = f" ({self.arg1})" if self.arg1 else ""
            return f"{res_prefix}SERVE{opt}"
        if self.op == "HALT":
            return f"{res_prefix}HALT"

        # General fallback
        args_str = ", ".join(fmt_val(a) for a in [self.arg1, self.arg2, self.arg3] if a is not None)
        return f"{res_prefix}{self.op} {args_str}".strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction to dictionary for API and UI serialization."""
        return {
            "id": self.id,
            "result": self.result,
            "op": self.op,
            "arg1": self.arg1,
            "arg2": self.arg2,
            "arg3": self.arg3,
            "line": self.line,
            "comment": self.comment,
            "readable": self.to_readable(),
        }


class IRGenerator:
    """Generates Three-Address Code IR from a validated AST."""

    def __init__(self, ast: ProgramNode) -> None:
        self.ast: ProgramNode = ast
        self.instructions: List[IRInstruction] = []
        self.temp_counter: int = 1
        self.inst_counter: int = 1

    def _next_temp(self) -> str:
        t = f"t{self.temp_counter}"
        self.temp_counter += 1
        return t

    def _emit(self, op: str, arg1: Any, arg2: Any = None, arg3: Any = None, line: int = 1, comment: str = "") -> IRInstruction:
        res = self._next_temp()
        inst = IRInstruction(
            id=self.inst_counter,
            op=op,
            arg1=arg1,
            arg2=arg2,
            arg3=arg3,
            result=res,
            line=line,
            comment=comment,
        )
        self.inst_counter += 1
        self.instructions.append(inst)
        return inst

    def generate(self) -> List[IRInstruction]:
        """Execute IR generation walk on the AST."""
        self.instructions = []
        self.temp_counter = 1
        self.inst_counter = 1

        # 1. Recipe Header
        if self.ast.recipe_decl is not None:
            self._emit(
                op="DECLARE_RECIPE",
                arg1=self.ast.recipe_decl.dish_name.upper(),
                line=self.ast.recipe_decl.line,
                comment=f"Initialize recipe vessel for {self.ast.recipe_decl.dish_name}",
            )

        # 2. Sequential statements
        for stmt in self.ast.statements:
            if isinstance(stmt, AddNode):
                self._emit(
                    op="DISPENSE",
                    arg1=stmt.ingredient.upper(),
                    arg2=stmt.quantity,
                    arg3=stmt.unit.upper(),
                    line=stmt.line,
                    comment=f"Measure and dispense {stmt.quantity} {stmt.unit} of {stmt.ingredient}",
                )
            elif isinstance(stmt, TimedOpNode):
                self._emit(
                    op="COOK",
                    arg1=stmt.operation.upper(),
                    arg2=stmt.duration,
                    arg3=stmt.time_unit.upper(),
                    line=stmt.line,
                    comment=f"Execute {stmt.operation} for {stmt.duration} {stmt.time_unit}",
                )
            elif isinstance(stmt, ChopNode):
                self._emit(
                    op="CHOP",
                    arg1=stmt.ingredient.upper(),
                    line=stmt.line,
                    comment=f"Cut produce item {stmt.ingredient}",
                )

        # 3. Terminating Serve statement
        if self.ast.serve_stmt is not None:
            self._emit(
                op="SERVE",
                arg1=self.ast.serve_stmt.style,
                line=self.ast.serve_stmt.line,
                comment="Plating and presentation of final dish",
            )

        return self.instructions
