"""Cookbook DSL Symbol Table Implementation.

Manages program symbols (dishes, ingredients, operational timers) with rich metadata,
including cumulative quantities, units, categories, and source coordinates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SymbolRecord:
    """Represents a symbol table entry in the Cookbook DSL."""
    identifier: str
    category: str        # 'Dish', 'Ingredient', 'Cooking Operation', 'Preparation'
    data_type: str       # 'Liquid', 'Dry Solid', 'Produce', 'Dairy', 'Egg', 'Spice', 'DishType', 'Timer'
    unit: str            # 'CUP', 'GRAM', 'ML', 'PIECE', 'MINUTES', etc.
    total_quantity: float
    occurrences: int = 1
    first_line: int = 1
    first_column: int = 1
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to a dictionary for frontend UI display."""
        return {
            "identifier": self.identifier,
            "category": self.category,
            "data_type": self.data_type,
            "unit": self.unit,
            "total_quantity": round(self.total_quantity, 2),
            "occurrences": self.occurrences,
            "source_location": f"Line {self.first_line}, Col {self.first_column}",
            "notes": self.notes,
        }


class SymbolTable:
    """Symbol Table scoped to the compiled culinary recipe program."""

    def __init__(self) -> None:
        self.entries: Dict[str, SymbolRecord] = {}

    def insert_dish(self, dish_name: str, line: int, column: int, description: str = "") -> SymbolRecord:
        """Register the recipe dish identifier."""
        record = SymbolRecord(
            identifier=dish_name.upper(),
            category="Dish",
            data_type="DishType",
            unit="N/A",
            total_quantity=1.0,
            occurrences=1,
            first_line=line,
            first_column=column,
            notes=f"Target recipe goal: {description or dish_name}",
        )
        self.entries[dish_name.upper()] = record
        return record

    def insert_or_accumulate_ingredient(
        self,
        name: str,
        quantity: float,
        unit: str,
        category_type: str,
        line: int,
        column: int,
    ) -> SymbolRecord:
        """Register an ingredient or accumulate quantity if already present with compatible unit."""
        key = name.upper()
        if key in self.entries:
            record = self.entries[key]
            record.occurrences += 1
            record.total_quantity += quantity
            record.notes = f"Dispensed across {record.occurrences} steps."
            return record

        record = SymbolRecord(
            identifier=key,
            category="Ingredient",
            data_type=category_type,
            unit=unit.upper(),
            total_quantity=quantity,
            occurrences=1,
            first_line=line,
            first_column=column,
            notes=f"Added {quantity} {unit}",
        )
        self.entries[key] = record
        return record

    def insert_operation(
        self,
        op_name: str,
        duration: float,
        time_unit: str,
        line: int,
        column: int,
    ) -> SymbolRecord:
        """Register an operational timer execution step."""
        key = f"OP_{op_name.upper()}_{line}"
        record = SymbolRecord(
            identifier=op_name.upper(),
            category="Cooking Operation",
            data_type="Timer",
            unit=time_unit.upper(),
            total_quantity=duration,
            occurrences=1,
            first_line=line,
            first_column=column,
            notes=f"Timed procedure: {duration} {time_unit}",
        )
        self.entries[key] = record
        return record

    def lookup(self, identifier: str) -> Optional[SymbolRecord]:
        """Lookup a symbol by identifier."""
        return self.entries.get(identifier.upper())

    def get_all_ingredients(self) -> List[SymbolRecord]:
        """Return all ingredient records."""
        return [r for r in self.entries.values() if r.category == "Ingredient"]

    def to_list(self) -> List[Dict[str, Any]]:
        """Return all symbol entries as sorted list of dictionaries."""
        return [r.to_dict() for r in self.entries.values()]

    def count(self) -> int:
        """Return count of registered symbols."""
        return len(self.entries)
