"""Cookbook DSL Token Definitions and Data Structures.

Defines the complete lexical vocabulary, token types, categories, and representations
for the Digital Cookbook Compiler.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class TokenType(Enum):
    """Enumeration of all token kinds in Cookbook DSL."""
    # Program Keywords
    RECIPE = auto()
    ADD = auto()
    MIX = auto()
    BOIL = auto()
    BAKE = auto()
    FRY = auto()
    SIMMER = auto()
    CHILL = auto()
    WHISK = auto()
    CHOP = auto()
    REST = auto()
    SERVE = auto()

    # Measurement Units
    UNIT_CUP = auto()
    UNIT_TBSP = auto()
    UNIT_TSP = auto()
    UNIT_GRAM = auto()
    UNIT_KG = auto()
    UNIT_ML = auto()
    UNIT_LITER = auto()
    UNIT_PIECE = auto()
    UNIT_PINCH = auto()

    # Time Units
    TIME_SECONDS = auto()
    TIME_MINUTES = auto()
    TIME_HOURS = auto()

    # Literals & Identifiers
    INTEGER_CONST = auto()
    FLOAT_CONST = auto()
    IDENTIFIER = auto()

    # Punctuators & Delimiters
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # Metadata & End of File
    COMMENT = auto()
    EOF = auto()
    UNKNOWN = auto()


# Map keyword strings to their TokenType
KEYWORDS: Dict[str, TokenType] = {
    "RECIPE": TokenType.RECIPE,
    "ADD": TokenType.ADD,
    "MIX": TokenType.MIX,
    "BOIL": TokenType.BOIL,
    "BAKE": TokenType.BAKE,
    "FRY": TokenType.FRY,
    "SIMMER": TokenType.SIMMER,
    "CHILL": TokenType.CHILL,
    "WHISK": TokenType.WHISK,
    "CHOP": TokenType.CHOP,
    "REST": TokenType.REST,
    "SERVE": TokenType.SERVE,
}

# Measurement unit keywords
MEASUREMENT_UNITS: Dict[str, TokenType] = {
    "CUP": TokenType.UNIT_CUP,
    "CUPS": TokenType.UNIT_CUP,
    "TBSP": TokenType.UNIT_TBSP,
    "TABLESPOON": TokenType.UNIT_TBSP,
    "TABLESPOONS": TokenType.UNIT_TBSP,
    "TSP": TokenType.UNIT_TSP,
    "TEASPOON": TokenType.UNIT_TSP,
    "TEASPOONS": TokenType.UNIT_TSP,
    "GRAM": TokenType.UNIT_GRAM,
    "GRAMS": TokenType.UNIT_GRAM,
    "G": TokenType.UNIT_GRAM,
    "KG": TokenType.UNIT_KG,
    "KILOGRAM": TokenType.UNIT_KG,
    "ML": TokenType.UNIT_ML,
    "MILLILITER": TokenType.UNIT_ML,
    "LITER": TokenType.UNIT_LITER,
    "LITERS": TokenType.UNIT_LITER,
    "L": TokenType.UNIT_LITER,
    "PIECE": TokenType.UNIT_PIECE,
    "PIECES": TokenType.UNIT_PIECE,
    "PINCH": TokenType.UNIT_PINCH,
    "PINCHES": TokenType.UNIT_PINCH,
}

# Time unit keywords
TIME_UNITS: Dict[str, TokenType] = {
    "SECONDS": TokenType.TIME_SECONDS,
    "SECOND": TokenType.TIME_SECONDS,
    "SEC": TokenType.TIME_SECONDS,
    "MINUTES": TokenType.TIME_MINUTES,
    "MINUTE": TokenType.TIME_MINUTES,
    "MIN": TokenType.TIME_MINUTES,
    "HOURS": TokenType.TIME_HOURS,
    "HOUR": TokenType.TIME_HOURS,
    "HR": TokenType.TIME_HOURS,
}


@dataclass
class Token:
    """Represents a lexical token generated during Phase 1 (Scanning)."""
    type: TokenType
    lexeme: str
    value: Any
    line: int
    column: int
    category: str = "Unknown"

    def __post_init__(self) -> None:
        if self.category == "Unknown":
            self.category = self._classify_category()

    def _classify_category(self) -> str:
        """Categorize token for frontend presentation and compiler inspection."""
        name = self.type.name
        if name in KEYWORDS:
            return "Keyword"
        if name.startswith("UNIT_"):
            return "Measurement Unit"
        if name.startswith("TIME_"):
            return "Time Unit"
        if "CONST" in name:
            return "Numeric Constant"
        if name == "IDENTIFIER":
            return "Identifier"
        if name in {"LPAREN", "RPAREN", "COMMA", "SEMICOLON"}:
            return "Delimiter"
        if name == "COMMENT":
            return "Comment"
        if name == "EOF":
            return "End of File"
        return "Special"

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to JSON-friendly representation for the UI."""
        return {
            "type": self.type.name,
            "lexeme": self.lexeme,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "category": self.category,
        }

    def __repr__(self) -> str:
        return f"Token({self.type.name}, lexeme='{self.lexeme}', line={self.line}, col={self.column})"
