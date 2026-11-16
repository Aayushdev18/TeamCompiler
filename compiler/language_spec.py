"""Language Specification and Central Culinary Domain Knowledge Base.

Defines the centralized vocabulary, ingredient rules, unit compatibility constraints,
operational boundaries, and dish specifications for Cookbook DSL.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any


@dataclass
class DishSpec:
    """Domain specification for a supported culinary recipe."""
    name: str
    display_name: str
    description: str
    required_ingredients: Set[str]
    optional_ingredients: Set[str]
    allowed_operations: Set[str]
    forbidden_operations: Set[str]
    min_ingredients: int = 2


@dataclass
class IngredientSpec:
    """Domain specification for an ingredient."""
    name: str
    category: str  # 'liquid', 'dry_solid', 'produce', 'dairy', 'egg', 'spice'
    allowed_units: Set[str]
    base_unit: str  # 'ML', 'GRAM', 'PIECE', 'PINCH'
    density_g_per_ml: Optional[float] = None  # for volumetric-to-mass approximation
    max_reasonable_quantity: float = 5000.0  # in base units


# Standard unit normalization factors to base units (ML for volume, GRAM for mass, SECONDS for time)
VOLUME_TO_ML: Dict[str, float] = {
    "ML": 1.0,
    "MILLILITER": 1.0,
    "LITER": 1000.0,
    "LITERS": 1000.0,
    "L": 1000.0,
    "CUP": 240.0,
    "CUPS": 240.0,
    "TBSP": 15.0,
    "TABLESPOON": 15.0,
    "TABLESPOONS": 15.0,
    "TSP": 5.0,
    "TEASPOON": 5.0,
    "TEASPOONS": 5.0,
}

MASS_TO_GRAM: Dict[str, float] = {
    "GRAM": 1.0,
    "GRAMS": 1.0,
    "G": 1.0,
    "KG": 1000.0,
    "KILOGRAM": 1000.0,
    "PINCH": 0.5,
    "PINCHES": 0.5,
}

TIME_TO_SECONDS: Dict[str, float] = {
    "SECONDS": 1.0,
    "SECOND": 1.0,
    "SEC": 1.0,
    "MINUTES": 60.0,
    "MINUTE": 60.0,
    "MIN": 60.0,
    "HOURS": 3600.0,
    "HOUR": 3600.0,
    "HR": 3600.0,
}

# Supported Ingredients Knowledge Base
INGREDIENTS: Dict[str, IngredientSpec] = {
    # Liquids
    "WATER": IngredientSpec("WATER", "liquid", {"ML", "LITER", "CUP", "TBSP", "TSP"}, "ML", 1.0, 10000.0),
    "MILK": IngredientSpec("MILK", "liquid", {"ML", "LITER", "CUP", "TBSP", "TSP"}, "ML", 1.03, 5000.0),
    "OIL": IngredientSpec("OIL", "liquid", {"ML", "CUP", "TBSP", "TSP"}, "ML", 0.92, 1000.0),
    "OLIVE_OIL": IngredientSpec("OLIVE_OIL", "liquid", {"ML", "CUP", "TBSP", "TSP"}, "ML", 0.92, 1000.0),
    "SYRUP": IngredientSpec("SYRUP", "liquid", {"ML", "CUP", "TBSP", "TSP"}, "ML", 1.33, 1000.0),
    "HONEY": IngredientSpec("HONEY", "liquid", {"ML", "CUP", "TBSP", "TSP", "GRAM"}, "ML", 1.42, 1000.0),
    "LEMON_JUICE": IngredientSpec("LEMON_JUICE", "liquid", {"ML", "TBSP", "TSP"}, "ML", 1.0, 500.0),

    # Dry Goods / Powders
    "FLOUR": IngredientSpec("FLOUR", "dry_solid", {"GRAM", "KG", "CUP", "TBSP"}, "GRAM", None, 5000.0),
    "SUGAR": IngredientSpec("SUGAR", "dry_solid", {"GRAM", "KG", "CUP", "TBSP", "TSP"}, "GRAM", None, 3000.0),
    "SALT": IngredientSpec("SALT", "spice", {"GRAM", "TSP", "PINCH", "TBSP"}, "GRAM", None, 200.0),
    "BAKING_POWDER": IngredientSpec("BAKING_POWDER", "dry_solid", {"GRAM", "TSP", "TBSP"}, "GRAM", None, 100.0),
    "COCOA": IngredientSpec("COCOA", "dry_solid", {"GRAM", "CUP", "TBSP", "TSP"}, "GRAM", None, 500.0),
    "PEPPER": IngredientSpec("PEPPER", "spice", {"GRAM", "TSP", "PINCH"}, "GRAM", None, 50.0),
    "CARDAMOM": IngredientSpec("CARDAMOM", "spice", {"PIECE", "PINCH", "GRAM", "TSP"}, "PIECE", None, 50.0),
    "TEA_LEAVES": IngredientSpec("TEA_LEAVES", "dry_solid", {"GRAM", "TSP", "TBSP"}, "GRAM", None, 200.0),
    "COFFEE": IngredientSpec("COFFEE", "dry_solid", {"GRAM", "TSP", "TBSP"}, "GRAM", None, 200.0),
    "PASTA": IngredientSpec("PASTA", "dry_solid", {"GRAM", "KG", "CUP"}, "GRAM", None, 2000.0),

    # Dairy & Eggs
    "EGG": IngredientSpec("EGG", "egg", {"PIECE"}, "PIECE", None, 50.0),
    "BUTTER": IngredientSpec("BUTTER", "dairy", {"GRAM", "TBSP", "CUP"}, "GRAM", None, 1000.0),
    "CHEESE": IngredientSpec("CHEESE", "dairy", {"GRAM", "CUP", "TBSP"}, "GRAM", None, 1000.0),
    "CREAM": IngredientSpec("CREAM", "dairy", {"ML", "CUP", "TBSP"}, "ML", 1.0, 1000.0),

    # Produce & Aromatics
    "ONION": IngredientSpec("ONION", "produce", {"PIECE", "GRAM", "CUP"}, "PIECE", None, 20.0),
    "TOMATO": IngredientSpec("TOMATO", "produce", {"PIECE", "GRAM", "CUP"}, "PIECE", None, 20.0),
    "GARLIC": IngredientSpec("GARLIC", "produce", {"PIECE", "PINCH", "GRAM"}, "PIECE", None, 20.0),
    "GINGER": IngredientSpec("GINGER", "produce", {"GRAM", "TSP", "PIECE"}, "GRAM", None, 200.0),
    "MUSHROOM": IngredientSpec("MUSHROOM", "produce", {"GRAM", "PIECE", "CUP"}, "GRAM", None, 1000.0),
    "LETTUCE": IngredientSpec("LETTUCE", "produce", {"GRAM", "CUP", "PIECE"}, "GRAM", None, 1000.0),
    "CUCUMBER": IngredientSpec("CUCUMBER", "produce", {"PIECE", "GRAM", "CUP"}, "PIECE", None, 10.0),
    "BACON": IngredientSpec("BACON", "meat", {"GRAM", "PIECE"}, "GRAM", None, 1000.0),
    "VANILLA": IngredientSpec("VANILLA", "liquid", {"TSP", "TBSP", "ML"}, "ML", 1.0, 50.0),
}


# Supported Dishes Knowledge Base
DISHES: Dict[str, DishSpec] = {
    "PANCAKE": DishSpec(
        name="PANCAKE",
        display_name="Golden Fluffy Pancake",
        description="Classic breakfast pancake prepared on a griddle.",
        required_ingredients={"FLOUR", "MILK", "EGG"},
        optional_ingredients={"SUGAR", "BUTTER", "BAKING_POWDER", "SALT", "SYRUP", "VANILLA", "OIL"},
        allowed_operations={"ADD", "MIX", "WHISK", "FRY", "REST", "SERVE"},
        forbidden_operations={"BOIL", "BAKE", "CHILL", "CHOP"},
        min_ingredients=3,
    ),
    "SPONGE_CAKE": DishSpec(
        name="SPONGE_CAKE",
        display_name="Classic Vanilla Sponge Cake",
        description="Airy baked sponge cake served warm or iced.",
        required_ingredients={"FLOUR", "SUGAR", "EGG", "BUTTER"},
        optional_ingredients={"BAKING_POWDER", "MILK", "VANILLA", "COCOA", "SALT"},
        allowed_operations={"ADD", "MIX", "WHISK", "BAKE", "REST", "CHILL", "SERVE"},
        forbidden_operations={"BOIL", "FRY", "CHOP"},
        min_ingredients=4,
    ),
    "CAKE": DishSpec(
        name="CAKE",
        display_name="Standard Baked Cake",
        description="General oven-baked confectionery cake.",
        required_ingredients={"FLOUR", "SUGAR", "EGG"},
        optional_ingredients={"BUTTER", "BAKING_POWDER", "MILK", "VANILLA", "COCOA", "SALT", "OIL"},
        allowed_operations={"ADD", "MIX", "WHISK", "BAKE", "REST", "CHILL", "SERVE"},
        forbidden_operations={"BOIL", "FRY", "CHOP"},
        min_ingredients=3,
    ),
    "PASTA": DishSpec(
        name="PASTA",
        display_name="Italian Pasta Carbonara",
        description="Boiled pasta tossed with cheese, eggs, and seasonings.",
        required_ingredients={"PASTA", "WATER", "SALT"},
        optional_ingredients={"CHEESE", "EGG", "BACON", "PEPPER", "GARLIC", "OIL", "BUTTER"},
        allowed_operations={"ADD", "BOIL", "SIMMER", "FRY", "MIX", "CHOP", "SERVE"},
        forbidden_operations={"BAKE", "CHILL", "WHISK"},
        min_ingredients=3,
    ),
    "HERBAL_TEA": DishSpec(
        name="HERBAL_TEA",
        display_name="Aromatic Herbal Tea",
        description="Steeped botanical tea beverage infused with herbs and spices.",
        required_ingredients={"WATER", "TEA_LEAVES"},
        optional_ingredients={"SUGAR", "MILK", "HONEY", "GINGER", "CARDAMOM", "LEMON_JUICE"},
        allowed_operations={"ADD", "BOIL", "SIMMER", "REST", "SERVE"},
        forbidden_operations={"BAKE", "FRY", "CHOP", "WHISK", "CHILL"},
        min_ingredients=2,
    ),
    "TEA": DishSpec(
        name="TEA",
        display_name="Classic Spiced Tea",
        description="Standard brewed tea beverage with optional condiments.",
        required_ingredients={"WATER", "TEA_LEAVES"},
        optional_ingredients={"SUGAR", "MILK", "HONEY", "GINGER", "CARDAMOM", "LEMON_JUICE"},
        allowed_operations={"ADD", "BOIL", "SIMMER", "REST", "SERVE"},
        forbidden_operations={"BAKE", "FRY", "CHOP", "WHISK", "CHILL"},
        min_ingredients=2,
    ),
    "FRENCH_OMELETTE": DishSpec(
        name="FRENCH_OMELETTE",
        display_name="Soft French Omelette",
        description="Delicately folded egg omelette cooked over gentle butter heat.",
        required_ingredients={"EGG", "BUTTER", "SALT"},
        optional_ingredients={"CHEESE", "MILK", "PEPPER", "ONION", "MUSHROOM", "OIL"},
        allowed_operations={"ADD", "WHISK", "CHOP", "FRY", "SERVE"},
        forbidden_operations={"BOIL", "BAKE", "SIMMER", "CHILL"},
        min_ingredients=3,
    ),
    "FRESH_SALAD": DishSpec(
        name="FRESH_SALAD",
        display_name="Crisp Garden Salad",
        description="Freshly tossed raw vegetable salad with vinaigrette dressing.",
        required_ingredients={"LETTUCE", "TOMATO", "OIL"},
        optional_ingredients={"CUCUMBER", "ONION", "SALT", "PEPPER", "CHEESE", "LEMON_JUICE"},
        allowed_operations={"ADD", "CHOP", "MIX", "CHILL", "REST", "SERVE"},
        forbidden_operations={"BOIL", "BAKE", "FRY", "SIMMER", "WHISK"},
        min_ingredients=3,
    ),
}


# Operational limits (in seconds)
OPERATION_TIME_LIMITS: Dict[str, Tuple[float, float]] = {
    "MIX": (1.0, 3600.0),       # 1 sec to 60 mins
    "WHISK": (1.0, 1800.0),     # 1 sec to 30 mins
    "BOIL": (10.0, 7200.0),     # 10 sec to 2 hours
    "SIMMER": (30.0, 14400.0),  # 30 sec to 4 hours
    "BAKE": (60.0, 18000.0),    # 1 min to 5 hours
    "FRY": (10.0, 3600.0),      # 10 sec to 1 hour
    "CHILL": (60.0, 86400.0),   # 1 min to 24 hours
    "REST": (10.0, 7200.0),     # 10 sec to 2 hours
}


# Virtual Kitchen Machine (VKM) hardware operational mappings
VKM_HARDWARE_MAPPING: Dict[str, Dict[str, Any]] = {
    "MIX": {"command": "STIR", "param1_name": "rpm", "param1_val": 120},
    "WHISK": {"command": "STIR", "param1_name": "rpm", "param1_val": 350},
    "BOIL": {"command": "HEAT_BOIL", "param1_name": "temp_c", "param1_val": 100},
    "SIMMER": {"command": "HEAT_SIMMER", "param1_name": "temp_c", "param1_val": 85},
    "BAKE": {"command": "HEAT_BAKE", "param1_name": "temp_c", "param1_val": 180},
    "FRY": {"command": "HEAT_FRY", "param1_name": "temp_c", "param1_val": 160},
    "CHILL": {"command": "COOL_CHILL", "param1_name": "temp_c", "param1_val": 4},
    "REST": {"command": "STATION_REST", "param1_name": "temp_c", "param1_val": 22},
    "CHOP": {"command": "CHOP_BLADE", "param1_name": "speed", "param1_val": "MED"},
}


def get_dish_spec(dish_name: str) -> Optional[DishSpec]:
    """Retrieve dish specification by name (case-insensitive)."""
    return DISHES.get(dish_name.upper())


def get_ingredient_spec(ingredient_name: str) -> Optional[IngredientSpec]:
    """Retrieve ingredient specification by name (case-insensitive)."""
    return INGREDIENTS.get(ingredient_name.upper())


def normalize_unit_name(unit_str: str) -> str:
    """Normalize unit string alias to standard unit token name."""
    u = unit_str.upper()
    if u in {"CUP", "CUPS"}:
        return "CUP"
    if u in {"TBSP", "TABLESPOON", "TABLESPOONS"}:
        return "TBSP"
    if u in {"TSP", "TEASPOON", "TEASPOONS"}:
        return "TSP"
    if u in {"GRAM", "GRAMS", "G"}:
        return "GRAM"
    if u in {"KG", "KILOGRAM"}:
        return "KG"
    if u in {"ML", "MILLILITER"}:
        return "ML"
    if u in {"LITER", "LITERS", "L"}:
        return "LITER"
    if u in {"PIECE", "PIECES"}:
        return "PIECE"
    if u in {"PINCH", "PINCHES"}:
        return "PINCH"
    return u


def normalize_time_unit_name(time_unit_str: str) -> str:
    """Normalize time unit string alias to standard time unit name."""
    t = time_unit_str.upper()
    if t in {"SECONDS", "SECOND", "SEC"}:
        return "SECONDS"
    if t in {"MINUTES", "MINUTE", "MIN"}:
        return "MINUTES"
    if t in {"HOURS", "HOUR", "HR"}:
        return "HOURS"
    return t
