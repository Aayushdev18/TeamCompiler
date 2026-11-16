"""Cookbook DSL Abstract Syntax Tree (AST) Node Hierarchy.

Defines the structured, strongly-typed AST nodes representing valid grammatical
constructs in the Cookbook DSL.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ASTNode(ABC):
    """Abstract base class for all Abstract Syntax Tree nodes."""
    line: int
    column: int
    node_type: str = field(init=False)

    def __post_init__(self) -> None:
        self.node_type = self.__class__.__name__

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert AST node to a JSON-serializable dictionary for interactive tree inspection."""
        pass


@dataclass
class RecipeDeclNode(ASTNode):
    """AST node representing the recipe header: RECIPE <dish_name>;"""
    dish_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "RecipeDeclNode",
            "title": f"RECIPE {self.dish_name}",
            "dish_name": self.dish_name,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": f"Declared Target Dish: {self.dish_name}",
        }


@dataclass
class StatementNode(ASTNode):
    """Base class for recipe statements."""
    pass


@dataclass
class AddNode(StatementNode):
    """AST node representing: ADD(quantity, unit, ingredient);"""
    quantity: float
    unit: str
    ingredient: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "AddNode",
            "title": f"ADD({self.quantity}, {self.unit}, {self.ingredient})",
            "quantity": self.quantity,
            "unit": self.unit,
            "ingredient": self.ingredient,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": f"Dispense {self.quantity} {self.unit} of {self.ingredient}",
        }


@dataclass
class TimedOpNode(StatementNode):
    """AST node representing: OPERATION(duration, time_unit); e.g. MIX(3, MINUTES);"""
    operation: str
    duration: float
    time_unit: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "TimedOpNode",
            "title": f"{self.operation}({self.duration}, {self.time_unit})",
            "operation": self.operation,
            "duration": self.duration,
            "time_unit": self.time_unit,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": f"Execute {self.operation} for {self.duration} {self.time_unit}",
        }


@dataclass
class ChopNode(StatementNode):
    """AST node representing: CHOP(ingredient);"""
    ingredient: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "ChopNode",
            "title": f"CHOP({self.ingredient})",
            "ingredient": self.ingredient,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": f"Cut and prepare produce item: {self.ingredient}",
        }


@dataclass
class ServeNode(StatementNode):
    """AST node representing the terminating statement: SERVE;"""
    style: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "ServeNode",
            "title": "SERVE" if not self.style else f"SERVE({self.style})",
            "style": self.style,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": "Terminate recipe execution and present finished dish",
        }


@dataclass
class ErrorNode(StatementNode):
    """AST node representing a recovered syntax error statement."""
    error_message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "ErrorNode",
            "title": f"SYNTAX_ERROR: {self.error_message}",
            "error_message": self.error_message,
            "line": self.line,
            "column": self.column,
            "children": [],
            "details": f"Unparsed invalid syntax at line {self.line}",
        }


@dataclass
class ProgramNode(ASTNode):
    """Root AST node containing the complete parsed recipe program."""
    recipe_decl: Optional[RecipeDeclNode]
    statements: List[StatementNode] = field(default_factory=list)
    serve_stmt: Optional[ServeNode] = None

    def to_dict(self) -> Dict[str, Any]:
        children = []
        if self.recipe_decl is not None:
            children.append(self.recipe_decl.to_dict())
        for stmt in self.statements:
            children.append(stmt.to_dict())
        if self.serve_stmt is not None:
            children.append(self.serve_stmt.to_dict())

        dish = self.recipe_decl.dish_name if self.recipe_decl else "UNDEFINED"
        return {
            "node_type": "ProgramNode",
            "title": f"Cookbook Program: {dish}",
            "dish": dish,
            "line": self.line,
            "column": self.column,
            "total_statements": len(self.statements) + (1 if self.recipe_decl else 0) + (1 if self.serve_stmt else 0),
            "children": children,
            "details": f"Complete recipe AST with {len(self.statements)} inner statements",
        }
