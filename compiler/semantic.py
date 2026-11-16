"""Phase 3: Semantic Analysis and Contextual Validation.

Enforces culinary domain semantics, ingredient-dish compatibility, unit constraints,
execution order dependencies, operational duration limits, and populates the Symbol Table.
"""

from typing import List, Dict, Set, Optional, Any
from .ast_nodes import ProgramNode, RecipeDeclNode, AddNode, TimedOpNode, ChopNode, ServeNode
from .symbol_table import SymbolTable, SymbolRecord
from .diagnostics import DiagnosticBag, DiagnosticPhase
from .language_spec import (
    DISHES,
    INGREDIENTS,
    OPERATION_TIME_LIMITS,
    get_dish_spec,
    get_ingredient_spec,
    TIME_TO_SECONDS,
    VOLUME_TO_ML,
    MASS_TO_GRAM,
)


class SemanticCheckItem:
    """Represents an individual semantic rule evaluation item for the checklist."""
    def __init__(self, rule_id: str, description: str, status: str = "pending", message: str = ""):
        self.rule_id = rule_id
        self.description = description
        self.status = status  # 'passed', 'failed', 'warning', 'skipped'
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "status": self.status,
            "message": self.message,
        }


class SemanticAnalyzer:
    """Performs comprehensive semantic validation on the Cookbook DSL Abstract Syntax Tree."""

    def __init__(self, ast: ProgramNode, diagnostics: Optional[DiagnosticBag] = None) -> None:
        self.ast: ProgramNode = ast
        self.diagnostics: DiagnosticBag = diagnostics if diagnostics is not None else DiagnosticBag()
        self.symbol_table: SymbolTable = SymbolTable()
        self.checklist: List[SemanticCheckItem] = []

        # Tracking state
        self.dish_name: Optional[str] = None
        self.ingredients_added: Set[str] = set()
        self.operations_performed: Set[str] = set()
        self.has_mixed: bool = False
        self.has_heated: bool = False

    def _add_check(self, rule_id: str, desc: str, passed: bool, msg: str = "", is_warning: bool = False) -> None:
        """Record validation outcome in the semantic checklist."""
        if passed:
            status = "passed"
        else:
            status = "warning" if is_warning else "failed"
        self.checklist.append(SemanticCheckItem(rule_id, desc, status, msg))

    def analyze(self) -> SymbolTable:
        """Run all semantic analysis phases and return the populated Symbol Table."""
        # 1. Recipe Declaration Validation
        self._validate_recipe_decl()

        # If recipe declaration failed completely, skip dish-dependent checks safely
        dish_spec = get_dish_spec(self.dish_name) if self.dish_name else None

        # 2. Sequential Statement Semantic Checks
        added_count = 0
        for idx, stmt in enumerate(self.ast.statements):
            if isinstance(stmt, AddNode):
                self._validate_add(stmt, dish_spec)
                added_count += 1
            elif isinstance(stmt, TimedOpNode):
                self._validate_timed_op(stmt, dish_spec, added_count)
            elif isinstance(stmt, ChopNode):
                self._validate_chop(stmt, dish_spec)

        # 3. Whole-Recipe Aggregate Checks
        self._validate_recipe_requirements(dish_spec)

        # 4. Final Serve Validation
        self._validate_serve(dish_spec, added_count)

        return self.symbol_table

    def _validate_recipe_decl(self) -> None:
        """Validate recipe header and recognized dish."""
        if self.ast.recipe_decl is None:
            self._add_check("RULE_DISH_DECL", "Recipe header declares target dish", False, "Missing recipe header.")
            return

        dish = self.ast.recipe_decl.dish_name.upper()
        self.dish_name = dish
        dish_spec = get_dish_spec(dish)

        if dish_spec is not None:
            self.symbol_table.insert_dish(dish, self.ast.recipe_decl.line, self.ast.recipe_decl.column, dish_spec.description)
            self._add_check("RULE_DISH_DECL", f"Valid dish declaration: {dish_spec.display_name}", True, f"Recognized dish '{dish}'.")
        else:
            self.diagnostics.add_warning(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Custom or unregistered dish name '{dish}'. Using permissive culinary validation.",
                line=self.ast.recipe_decl.line,
                column=self.ast.recipe_decl.column,
                code="WARN_CUSTOM_DISH",
                suggestion="Standard supported dishes: PANCAKE, SPONGE_CAKE, PASTA, HERBAL_TEA, FRENCH_OMELETTE, FRESH_SALAD.",
            )
            self.symbol_table.insert_dish(dish, self.ast.recipe_decl.line, self.ast.recipe_decl.column, "Custom recipe")
            self._add_check("RULE_DISH_DECL", f"Custom dish declaration '{dish}'", True, "Permissive custom dish mode enabled.", is_warning=True)

    def _validate_add(self, node: AddNode, dish_spec: Optional[Any]) -> None:
        """Validate ADD(quantity, unit, ingredient);"""
        ing_name = node.ingredient.upper()
        unit_name = node.unit.upper()
        qty = node.quantity

        # Rule A: Positive quantity
        if qty <= 0:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Ingredient quantity for '{ing_name}' must be strictly positive (> 0), received {qty}.",
                line=node.line,
                column=node.column,
                code="ERR_NON_POSITIVE_QTY",
                related_identifier=ing_name,
                suggestion="Specify a quantity greater than zero.",
            )
            self._add_check(f"RULE_QTY_POS_{ing_name}_{node.line}", f"Positive quantity for {ing_name}", False, f"Quantity {qty} <= 0.")
        else:
            self._add_check(f"RULE_QTY_POS_{ing_name}_{node.line}", f"Positive quantity for {ing_name}", True)

        # Rule B: Known ingredient lookup
        ing_spec = get_ingredient_spec(ing_name)
        if ing_spec is None:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Unrecognized ingredient '{ing_name}' in recipe.",
                line=node.line,
                column=node.column,
                code="ERR_UNKNOWN_INGREDIENT",
                related_identifier=ing_name,
                suggestion="Check spelling or use recognized ingredients (e.g. FLOUR, MILK, EGG, SUGAR, SALT, WATER, BUTTER).",
            )
            self._add_check(f"RULE_ING_KNOWN_{ing_name}_{node.line}", f"Known ingredient '{ing_name}'", False, "Unrecognized ingredient.")
            return
        else:
            self._add_check(f"RULE_ING_KNOWN_{ing_name}_{node.line}", f"Recognized ingredient '{ing_name}' ({ing_spec.category})", True)

        # Rule C: Ingredient-dish compatibility
        if dish_spec is not None:
            allowed_for_dish = dish_spec.required_ingredients | dish_spec.optional_ingredients
            if ing_name not in allowed_for_dish:
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Ingredient '{ing_name}' is not compatible with dish '{dish_spec.name}'.",
                    line=node.line,
                    column=node.column,
                    code="ERR_INCOMPATIBLE_INGREDIENT",
                    related_identifier=ing_name,
                    suggestion=f"Allowed ingredients for {dish_spec.name}: {', '.join(sorted(allowed_for_dish))}",
                )
                self._add_check(f"RULE_COMPAT_{ing_name}_{node.line}", f"Compatibility of {ing_name} with {dish_spec.name}", False, "Incompatible ingredient.")
            else:
                self._add_check(f"RULE_COMPAT_{ing_name}_{node.line}", f"Compatibility of {ing_name} with {dish_spec.name}", True)

        # Rule D: Measurement unit compatibility
        if unit_name not in ing_spec.allowed_units:
            allowed_units_str = ", ".join(sorted(ing_spec.allowed_units))
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Invalid measurement unit '{unit_name}' for ingredient '{ing_name}'. Allowed units: {allowed_units_str}.",
                line=node.line,
                column=node.column,
                code="ERR_INCOMPATIBLE_UNIT",
                related_identifier=ing_name,
                suggestion=f"Change unit to one of: {allowed_units_str}",
            )
            self._add_check(f"RULE_UNIT_{ing_name}_{node.line}", f"Unit '{unit_name}' valid for {ing_name}", False, f"Expected one of: {allowed_units_str}")
        else:
            self._add_check(f"RULE_UNIT_{ing_name}_{node.line}", f"Unit '{unit_name}' valid for {ing_name}", True)

        # Rule E: Maximum reasonable quantity
        # Approximate quantity check
        if unit_name in VOLUME_TO_ML and qty * VOLUME_TO_ML[unit_name] > ing_spec.max_reasonable_quantity:
            self.diagnostics.add_warning(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Unusually large volume ({qty} {unit_name}) for '{ing_name}'. Exceeds standard home cooking threshold.",
                line=node.line,
                column=node.column,
                code="WARN_EXCESSIVE_QUANTITY",
                related_identifier=ing_name,
            )
        elif unit_name in MASS_TO_GRAM and qty * MASS_TO_GRAM[unit_name] > ing_spec.max_reasonable_quantity:
            self.diagnostics.add_warning(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Unusually large mass ({qty} {unit_name}) for '{ing_name}'. Exceeds standard home cooking threshold.",
                line=node.line,
                column=node.column,
                code="WARN_EXCESSIVE_QUANTITY",
                related_identifier=ing_name,
            )
        elif unit_name == "PIECE" and qty > ing_spec.max_reasonable_quantity:
            self.diagnostics.add_warning(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Unusually high piece count ({qty}) for '{ing_name}'.",
                line=node.line,
                column=node.column,
                code="WARN_EXCESSIVE_QUANTITY",
                related_identifier=ing_name,
            )

        # Register in symbol table
        self.symbol_table.insert_or_accumulate_ingredient(
            name=ing_name,
            quantity=qty,
            unit=unit_name,
            category_type=ing_spec.category.replace("_", " ").title(),
            line=node.line,
            column=node.column,
        )
        self.ingredients_added.add(ing_name)

    def _validate_timed_op(self, node: TimedOpNode, dish_spec: Optional[Any], ingredients_count: int) -> None:
        """Validate timed cooking operations (MIX, BOIL, BAKE, FRY, etc.)."""
        op = node.operation.upper()
        dur = node.duration
        time_unit = node.time_unit.upper()

        # Rule A: Cannot cook or mix an empty vessel!
        if ingredients_count == 0:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Cannot execute '{op}' operation before adding any ingredients. The cooking vessel is empty.",
                line=node.line,
                column=node.column,
                code="ERR_EMPTY_VESSEL_OPERATION",
                suggestion="Add ingredients using ADD(...) before mixing or cooking.",
            )
            self._add_check(f"RULE_EMPTY_VESSEL_{node.line}", f"Ingredients present before {op}", False, "Vessel is empty.")
        else:
            self._add_check(f"RULE_EMPTY_VESSEL_{node.line}", f"Ingredients present before {op}", True)

        # Rule B: Positive duration
        if dur <= 0:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Duration for '{op}' must be strictly positive, received {dur}.",
                line=node.line,
                column=node.column,
                code="ERR_NON_POSITIVE_DURATION",
                suggestion="Specify duration > 0.",
            )
            self._add_check(f"RULE_DUR_POS_{op}_{node.line}", f"Positive duration for {op}", False, f"Duration {dur} <= 0.")
        else:
            self._add_check(f"RULE_DUR_POS_{op}_{node.line}", f"Positive duration for {op}", True)

        # Rule C: Operation allowed for dish
        if dish_spec is not None:
            if op in dish_spec.forbidden_operations:
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Operation '{op}' is forbidden for dish '{dish_spec.name}'.",
                    line=node.line,
                    column=node.column,
                    code="ERR_FORBIDDEN_OPERATION",
                    suggestion=f"Permitted operations for {dish_spec.name}: {', '.join(sorted(dish_spec.allowed_operations))}",
                )
                self._add_check(f"RULE_OP_ALLOWED_{op}_{node.line}", f"Operation {op} permitted for {dish_spec.name}", False, "Forbidden operation.")
            elif op not in dish_spec.allowed_operations:
                self.diagnostics.add_warning(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Unusual operation '{op}' for dish '{dish_spec.name}'.",
                    line=node.line,
                    column=node.column,
                    code="WARN_UNUSUAL_OPERATION",
                )
                self._add_check(f"RULE_OP_ALLOWED_{op}_{node.line}", f"Operation {op} standard for {dish_spec.name}", True, is_warning=True)
            else:
                self._add_check(f"RULE_OP_ALLOWED_{op}_{node.line}", f"Operation {op} permitted for {dish_spec.name}", True)

        # Rule D: Operational time boundaries
        duration_sec = dur * TIME_TO_SECONDS.get(time_unit, 1.0)
        if op in OPERATION_TIME_LIMITS:
            min_sec, max_sec = OPERATION_TIME_LIMITS[op]
            if duration_sec < min_sec:
                self.diagnostics.add_warning(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Duration ({dur} {time_unit}) is unusually short for {op} (minimum recommended {min_sec}s).",
                    line=node.line,
                    column=node.column,
                    code="WARN_DURATION_TOO_SHORT",
                )
            elif duration_sec > max_sec:
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Excessive duration ({dur} {time_unit} = {duration_sec}s) for {op}. Exceeds maximum safety limit of {max_sec}s.",
                    line=node.line,
                    column=node.column,
                    code="ERR_EXCESSIVE_DURATION",
                    suggestion=f"Reduce {op} duration below {max_sec / 60:.0f} minutes.",
                )
                self._add_check(f"RULE_TIME_BOUND_{op}_{node.line}", f"Duration bounds for {op}", False, "Exceeds safety limit.")
            else:
                self._add_check(f"RULE_TIME_BOUND_{op}_{node.line}", f"Duration bounds for {op}", True)

        # Track operations
        self.operations_performed.add(op)
        if op in {"MIX", "WHISK"}:
            self.has_mixed = True
        if op in {"BOIL", "SIMMER", "BAKE", "FRY"}:
            self.has_heated = True

        self.symbol_table.insert_operation(op, dur, time_unit, node.line, node.column)

    def _validate_chop(self, node: ChopNode, dish_spec: Optional[Any]) -> None:
        """Validate CHOP(ingredient);"""
        ing = node.ingredient.upper()
        ing_spec = get_ingredient_spec(ing)

        if ing_spec is None:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Cannot chop unrecognized ingredient '{ing}'.",
                line=node.line,
                column=node.column,
                code="ERR_UNKNOWN_INGREDIENT",
            )
            self._add_check(f"RULE_CHOP_{ing}_{node.line}", f"Chop valid ingredient {ing}", False)
        elif ing_spec.category not in {"produce", "meat", "dairy"}:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Cannot chop liquid or powder ingredient '{ing}' ({ing_spec.category}).",
                line=node.line,
                column=node.column,
                code="ERR_INVALID_CHOP_TARGET",
                suggestion="CHOP is reserved for solid produce, vegetables, meats, or solid cheeses.",
            )
            self._add_check(f"RULE_CHOP_{ing}_{node.line}", f"Chop valid ingredient {ing}", False, f"Ingredient category '{ing_spec.category}' cannot be chopped.")
        else:
            self._add_check(f"RULE_CHOP_{ing}_{node.line}", f"Chop valid ingredient {ing}", True)

    def _validate_recipe_requirements(self, dish_spec: Optional[Any]) -> None:
        """Validate recipe-level required ingredients and minimal complexity."""
        if dish_spec is None:
            return

        # Check required ingredients
        missing_reqs = dish_spec.required_ingredients - self.ingredients_added
        if missing_reqs:
            missing_str = ", ".join(sorted(missing_reqs))
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Missing essential ingredients for '{dish_spec.name}': {missing_str}.",
                line=self.ast.line,
                column=self.ast.column,
                code="ERR_MISSING_REQUIRED_INGREDIENTS",
                suggestion=f"Add missing required ingredients: {missing_str}",
            )
            self._add_check("RULE_REQUIRED_INGREDIENTS", f"All required ingredients present for {dish_spec.name}", False, f"Missing: {missing_str}")
        else:
            self._add_check("RULE_REQUIRED_INGREDIENTS", f"All required ingredients present for {dish_spec.name}", True, "All mandatory ingredients included.")

        # Check minimum ingredient count
        if len(self.ingredients_added) < dish_spec.min_ingredients:
            self.diagnostics.add_warning(
                phase=DiagnosticPhase.SEMANTIC,
                message=f"Recipe '{dish_spec.name}' has only {len(self.ingredients_added)} ingredients; typical recipe requires at least {dish_spec.min_ingredients}.",
                line=self.ast.line,
                column=self.ast.column,
                code="WARN_INSUFFICIENT_INGREDIENTS",
            )

    def _validate_serve(self, dish_spec: Optional[Any], added_count: int) -> None:
        """Validate SERVE statement readiness."""
        if self.ast.serve_stmt is None:
            self._add_check("RULE_FINAL_SERVE", "Recipe finishes with SERVE", False, "Missing terminating SERVE statement.")
            return

        # Check if ingredients were added
        if added_count == 0:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.SEMANTIC,
                message="Cannot serve an empty recipe without ingredients.",
                line=self.ast.serve_stmt.line,
                column=self.ast.serve_stmt.column,
                code="ERR_SERVE_EMPTY",
            )
            self._add_check("RULE_FINAL_SERVE", "Recipe serves prepared dish", False, "No ingredients were prepared.")
            return

        # Baked goods or cooked dishes must undergo cooking before serving
        if dish_spec is not None and dish_spec.name in {"PANCAKE", "SPONGE_CAKE", "CAKE", "PASTA", "HERBAL_TEA", "FRENCH_OMELETTE"}:
            if not self.has_heated:
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.SEMANTIC,
                    message=f"Dish '{dish_spec.name}' cannot be served raw. A thermal cooking step (e.g. BAKE, BOIL, FRY) is required.",
                    line=self.ast.serve_stmt.line,
                    column=self.ast.serve_stmt.column,
                    code="ERR_SERVE_RAW_DISH",
                    suggestion="Add a cooking operation before SERVE (e.g. BAKE, FRY, or BOIL).",
                )
                self._add_check("RULE_THERMAL_PREP", f"Thermal preparation for {dish_spec.name}", False, "Dish cannot be served raw.")
            else:
                self._add_check("RULE_THERMAL_PREP", f"Thermal preparation for {dish_spec.name}", True)

        self._add_check("RULE_FINAL_SERVE", "Recipe finishes with valid SERVE statement", True)

    def get_checklist_dict(self) -> List[Dict[str, Any]]:
        """Return semantic checklist as list of dicts."""
        return [item.to_dict() for item in self.checklist]
