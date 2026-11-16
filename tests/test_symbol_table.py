"""Unit Tests for Symbol Table Data Structure."""

import pytest
from compiler.symbol_table import SymbolTable


def test_symbol_table_insert_and_lookup():
    sym = SymbolTable()
    sym.insert_dish("PANCAKE", 1, 1, "Classic pancake recipe")
    record = sym.lookup("PANCAKE")
    assert record is not None
    assert record.identifier == "PANCAKE"
    assert record.category == "Dish"
    assert record.data_type == "DishType"


def test_symbol_table_ingredient_accumulation():
    sym = SymbolTable()
    sym.insert_or_accumulate_ingredient("FLOUR", 2.0, "CUP", "Dry Solid", 2, 1)
    sym.insert_or_accumulate_ingredient("FLOUR", 1.5, "CUP", "Dry Solid", 4, 1)

    record = sym.lookup("FLOUR")
    assert record is not None
    assert record.occurrences == 2
    assert record.total_quantity == 3.5
    assert record.unit == "CUP"


def test_symbol_table_serialization():
    sym = SymbolTable()
    sym.insert_dish("CAKE", 1, 1)
    sym.insert_or_accumulate_ingredient("SUGAR", 100.0, "GRAM", "Dry Solid", 2, 1)
    sym.insert_operation("BAKE", 20.0, "MINUTES", 5, 1)

    entries = sym.to_list()
    assert len(entries) == 3
    ident_set = {e["identifier"] for e in entries}
    assert "CAKE" in ident_set
    assert "SUGAR" in ident_set
    assert "BAKE" in ident_set
