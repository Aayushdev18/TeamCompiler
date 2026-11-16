"""Phase 2: Syntax Analysis (Recursive-Descent Parser).

Consumes token stream, enforces EBNF grammar production rules, performs error recovery
via synchronization tokens, and constructs a strongly-typed Abstract Syntax Tree (AST).
"""

from typing import List, Optional, Set
from .tokens import Token, TokenType, KEYWORDS, MEASUREMENT_UNITS, TIME_UNITS
from .ast_nodes import (
    ProgramNode,
    RecipeDeclNode,
    StatementNode,
    AddNode,
    TimedOpNode,
    ChopNode,
    ServeNode,
    ErrorNode,
)
from .diagnostics import DiagnosticBag, DiagnosticPhase
from .language_spec import normalize_unit_name, normalize_time_unit_name


# Timed operation tokens
TIMED_OP_TOKENS: Set[TokenType] = {
    TokenType.MIX,
    TokenType.BOIL,
    TokenType.BAKE,
    TokenType.FRY,
    TokenType.SIMMER,
    TokenType.CHILL,
    TokenType.WHISK,
    TokenType.REST,
}

# Statement synchronization keywords
STATEMENT_START_TOKENS: Set[TokenType] = {
    TokenType.RECIPE,
    TokenType.ADD,
    TokenType.CHOP,
    TokenType.SERVE,
} | TIMED_OP_TOKENS


class Parser:
    """Recursive-Descent Parser for Cookbook DSL."""

    def __init__(self, tokens: List[Token], diagnostics: Optional[DiagnosticBag] = None) -> None:
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.diagnostics: DiagnosticBag = diagnostics if diagnostics is not None else DiagnosticBag()

    def _peek(self, offset: int = 0) -> Token:
        """Peek at current or lookahead token."""
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[idx]

    def _current(self) -> Token:
        return self._peek(0)

    def _is_at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        """Advance position and return the consumed token."""
        tok = self._current()
        if not self._is_at_end():
            self.pos += 1
        return tok

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._current().type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        """Check and consume if current token matches any expected type."""
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, error_message: str, code: str = "ERR_SYNTAX", suggestion: Optional[str] = None) -> Optional[Token]:
        """Consume expected token or record a syntax diagnostic."""
        if self._check(token_type):
            return self._advance()

        current_tok = self._current()
        self.diagnostics.add_error(
            phase=DiagnosticPhase.PARSER,
            message=f"{error_message} Found '{current_tok.lexeme}' ({current_tok.type.name}).",
            line=current_tok.line,
            column=current_tok.column,
            code=code,
            suggestion=suggestion,
        )
        return None

    def _synchronize(self) -> None:
        """Recover from a syntax error by advancing to the next statement boundary."""
        self._advance()
        while not self._is_at_end():
            if self.tokens[self.pos - 1].type == TokenType.SEMICOLON:
                return
            if self._current().type in STATEMENT_START_TOKENS:
                return
            self._advance()

    def parse(self) -> ProgramNode:
        """Entry point: parses a full Cookbook DSL program into an AST."""
        start_tok = self._current()
        program = ProgramNode(
            line=start_tok.line,
            column=start_tok.column,
            recipe_decl=None,
            statements=[],
            serve_stmt=None,
        )

        # Handle empty token stream (only EOF)
        if self._is_at_end():
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message="Source program is empty. A valid recipe must begin with 'RECIPE <DISH_NAME>;'.",
                line=1,
                column=1,
                code="ERR_EMPTY_PROGRAM",
                suggestion="Add 'RECIPE PANCAKE;' at the top of your program.",
            )
            return program

        # 1. Parse mandatory recipe header: RECIPE <DISH_NAME>;
        if self._check(TokenType.RECIPE):
            program.recipe_decl = self._parse_recipe_decl()
        else:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Missing recipe declaration header. Program must begin with 'RECIPE <dish>;', found '{self._current().lexeme}'.",
                line=self._current().line,
                column=self._current().column,
                code="ERR_MISSING_RECIPE_HEADER",
                suggestion="Add 'RECIPE <dish_name>;' at line 1.",
            )
            # Try to recover if an identifier is at line 1
            if self._current().type == TokenType.IDENTIFIER and self._peek(1).type == TokenType.SEMICOLON:
                dish_tok = self._advance()
                self._advance()  # consume semicolon
                program.recipe_decl = RecipeDeclNode(line=dish_tok.line, column=dish_tok.column, dish_name=dish_tok.value)

        # 2. Parse body statements until SERVE or EOF
        found_serve = False
        while not self._is_at_end():
            current_tok = self._current()

            # Check if this is the terminating SERVE statement
            if current_tok.type == TokenType.SERVE:
                serve_node = self._parse_serve()
                if not found_serve:
                    program.serve_stmt = serve_node
                    found_serve = True
                else:
                    self.diagnostics.add_warning(
                        phase=DiagnosticPhase.PARSER,
                        message="Duplicate 'SERVE;' statement encountered.",
                        line=current_tok.line,
                        column=current_tok.column,
                        code="WARN_DUPLICATE_SERVE",
                    )
                continue

            # If we already encountered SERVE, any subsequent statement is illegal
            if found_serve:
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.PARSER,
                    message=f"Illegal statement '{current_tok.lexeme}' after final 'SERVE;' instruction.",
                    line=current_tok.line,
                    column=current_tok.column,
                    code="ERR_STATEMENT_AFTER_SERVE",
                    suggestion="Move or remove statements appearing after SERVE.",
                )
                self._synchronize()
                continue

            # Parse standard statement
            stmt = self._parse_statement()
            if stmt is not None:
                program.statements.append(stmt)

        # 3. Check if mandatory SERVE statement was present
        if program.serve_stmt is None and not self.diagnostics.has_errors():
            last_line = self.tokens[-1].line if self.tokens else 1
            last_col = self.tokens[-1].column if self.tokens else 1
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message="Missing mandatory terminating 'SERVE;' statement.",
                line=last_line,
                column=last_col,
                code="ERR_MISSING_SERVE",
                suggestion="Add 'SERVE;' at the end of the recipe.",
            )

        return program

    def _parse_recipe_decl(self) -> Optional[RecipeDeclNode]:
        """Parse: RECIPE <dish_name>;"""
        recipe_tok = self._advance()  # consume RECIPE

        # Expect dish identifier
        dish_tok = self._current()
        if dish_tok.type not in {TokenType.IDENTIFIER, TokenType.RECIPE}:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Expected recipe dish name identifier after 'RECIPE', found '{dish_tok.lexeme}'.",
                line=dish_tok.line,
                column=dish_tok.column,
                code="ERR_EXPECTED_DISH_NAME",
                suggestion="Specify a valid dish name e.g. 'RECIPE PANCAKE;'",
            )
            self._synchronize()
            return None

        self._advance()
        dish_name = dish_tok.value

        # Expect semicolon
        if not self._consume(TokenType.SEMICOLON, "Expected ';' after recipe declaration.", "ERR_MISSING_SEMICOLON", "Add ';' after the recipe name."):
            self._synchronize()

        return RecipeDeclNode(line=recipe_tok.line, column=recipe_tok.column, dish_name=dish_name)

    def _parse_statement(self) -> Optional[StatementNode]:
        """Parse one recipe statement."""
        tok = self._current()

        try:
            if tok.type == TokenType.ADD:
                return self._parse_add()
            if tok.type in TIMED_OP_TOKENS:
                return self._parse_timed_op()
            if tok.type == TokenType.CHOP:
                return self._parse_chop()

            # Unexpected token at statement position
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Unexpected statement token '{tok.lexeme}'. Expected ADD, MIX, BOIL, BAKE, FRY, CHOP, etc.",
                line=tok.line,
                column=tok.column,
                code="ERR_UNEXPECTED_STATEMENT",
                suggestion="Ensure statements follow the syntax: ADD(qty, unit, ingredient); or OPERATION(time, unit);",
            )
            self._synchronize()
            return None

        except Exception as e:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Syntax parsing exception near '{tok.lexeme}': {str(e)}",
                line=tok.line,
                column=tok.column,
                code="ERR_PARSER_EXCEPTION",
            )
            self._synchronize()
            return ErrorNode(line=tok.line, column=tok.column, error_message=str(e))

    def _parse_add(self) -> Optional[AddNode]:
        """Parse: ADD(quantity, unit, ingredient);"""
        add_tok = self._advance()  # consume ADD

        if not self._consume(TokenType.LPAREN, "Expected '(' after 'ADD'.", "ERR_MISSING_LPAREN"):
            self._synchronize()
            return None

        # 1. Quantity (Number)
        qty_tok = self._current()
        if qty_tok.type not in {TokenType.INTEGER_CONST, TokenType.FLOAT_CONST}:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"First argument to ADD must be a numeric quantity, found '{qty_tok.lexeme}'.",
                line=qty_tok.line,
                column=qty_tok.column,
                code="ERR_INVALID_QUANTITY",
                suggestion="Provide an integer or float, e.g. ADD(2, CUP, FLOUR);",
            )
            self._synchronize()
            return None
        self._advance()
        quantity = float(qty_tok.value)

        # Expect comma
        if not self._consume(TokenType.COMMA, "Expected ',' after quantity in ADD statement.", "ERR_MISSING_COMMA"):
            self._synchronize()
            return None

        # 2. Unit
        unit_tok = self._current()
        if not (unit_tok.type.name.startswith("UNIT_") or unit_tok.type == TokenType.IDENTIFIER):
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Second argument to ADD must be a measurement unit (e.g. CUP, GRAM, ML, PIECE), found '{unit_tok.lexeme}'.",
                line=unit_tok.line,
                column=unit_tok.column,
                code="ERR_INVALID_UNIT",
                suggestion="Use a recognized unit such as CUP, TBSP, TSP, GRAM, ML, PIECE.",
            )
            self._synchronize()
            return None
        self._advance()
        unit_str = normalize_unit_name(unit_tok.lexeme)

        # Expect comma
        if not self._consume(TokenType.COMMA, "Expected ',' after measurement unit in ADD statement.", "ERR_MISSING_COMMA"):
            self._synchronize()
            return None

        # 3. Ingredient (Identifier)
        ing_tok = self._current()
        if ing_tok.type != TokenType.IDENTIFIER:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Third argument to ADD must be an ingredient identifier (e.g. FLOUR, MILK), found '{ing_tok.lexeme}'.",
                line=ing_tok.line,
                column=ing_tok.column,
                code="ERR_INVALID_INGREDIENT_ARG",
                suggestion="Specify the ingredient name as an identifier, e.g. FLOUR, SUGAR, EGG.",
            )
            self._synchronize()
            return None
        self._advance()
        ingredient_str = ing_tok.value

        # Check for extra arguments before RPAREN
        if self._check(TokenType.COMMA):
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message="Too many arguments provided to ADD statement (expected 3: quantity, unit, ingredient).",
                line=self._current().line,
                column=self._current().column,
                code="ERR_EXTRA_ARGUMENTS",
                suggestion="ADD takes exactly three arguments: ADD(quantity, unit, ingredient);",
            )
            self._synchronize()
            return None

        # Expect RPAREN
        if not self._consume(TokenType.RPAREN, "Expected ')' closing ADD statement.", "ERR_MISSING_RPAREN"):
            self._synchronize()
            return None

        # Expect SEMICOLON
        if not self._consume(TokenType.SEMICOLON, "Expected ';' terminating ADD statement.", "ERR_MISSING_SEMICOLON"):
            self._synchronize()
            return None

        return AddNode(
            line=add_tok.line,
            column=add_tok.column,
            quantity=quantity,
            unit=unit_str,
            ingredient=ingredient_str,
        )

    def _parse_timed_op(self) -> Optional[TimedOpNode]:
        """Parse: OPERATION(duration, time_unit); e.g. MIX(3, MINUTES);"""
        op_tok = self._advance()
        operation_name = op_tok.value

        if not self._consume(TokenType.LPAREN, f"Expected '(' after '{operation_name}'.", "ERR_MISSING_LPAREN"):
            self._synchronize()
            return None

        # 1. Duration (Number)
        dur_tok = self._current()
        if dur_tok.type not in {TokenType.INTEGER_CONST, TokenType.FLOAT_CONST}:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"First argument to {operation_name} must be a numeric duration, found '{dur_tok.lexeme}'.",
                line=dur_tok.line,
                column=dur_tok.column,
                code="ERR_INVALID_DURATION",
                suggestion=f"Provide numeric duration, e.g. {operation_name}(5, MINUTES);",
            )
            self._synchronize()
            return None
        self._advance()
        duration = float(dur_tok.value)

        # Expect comma
        if not self._consume(TokenType.COMMA, f"Expected ',' after duration in {operation_name} statement.", "ERR_MISSING_COMMA"):
            self._synchronize()
            return None

        # 2. Time Unit
        time_tok = self._current()
        if not (time_tok.type.name.startswith("TIME_") or time_tok.type == TokenType.IDENTIFIER):
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Second argument to {operation_name} must be a time unit (SECONDS, MINUTES, HOURS), found '{time_tok.lexeme}'.",
                line=time_tok.line,
                column=time_tok.column,
                code="ERR_INVALID_TIME_UNIT",
                suggestion="Use SECONDS, MINUTES, or HOURS.",
            )
            self._synchronize()
            return None
        self._advance()
        time_unit = normalize_time_unit_name(time_tok.lexeme)

        # Check for extra arguments
        if self._check(TokenType.COMMA):
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Too many arguments provided to {operation_name} statement (expected 2: duration, time_unit).",
                line=self._current().line,
                column=self._current().column,
                code="ERR_EXTRA_ARGUMENTS",
            )
            self._synchronize()
            return None

        # Expect RPAREN
        if not self._consume(TokenType.RPAREN, f"Expected ')' closing {operation_name} statement.", "ERR_MISSING_RPAREN"):
            self._synchronize()
            return None

        # Expect SEMICOLON
        if not self._consume(TokenType.SEMICOLON, f"Expected ';' terminating {operation_name} statement.", "ERR_MISSING_SEMICOLON"):
            self._synchronize()
            return None

        return TimedOpNode(
            line=op_tok.line,
            column=op_tok.column,
            operation=operation_name,
            duration=duration,
            time_unit=time_unit,
        )

    def _parse_chop(self) -> Optional[ChopNode]:
        """Parse: CHOP(ingredient);"""
        chop_tok = self._advance()

        if not self._consume(TokenType.LPAREN, "Expected '(' after 'CHOP'.", "ERR_MISSING_LPAREN"):
            self._synchronize()
            return None

        ing_tok = self._current()
        if ing_tok.type != TokenType.IDENTIFIER:
            self.diagnostics.add_error(
                phase=DiagnosticPhase.PARSER,
                message=f"Expected ingredient identifier inside CHOP(...), found '{ing_tok.lexeme}'.",
                line=ing_tok.line,
                column=ing_tok.column,
                code="ERR_INVALID_CHOP_TARGET",
            )
            self._synchronize()
            return None
        self._advance()
        target_ing = ing_tok.value

        if not self._consume(TokenType.RPAREN, "Expected ')' closing CHOP statement.", "ERR_MISSING_RPAREN"):
            self._synchronize()
            return None

        if not self._consume(TokenType.SEMICOLON, "Expected ';' terminating CHOP statement.", "ERR_MISSING_SEMICOLON"):
            self._synchronize()
            return None

        return ChopNode(line=chop_tok.line, column=chop_tok.column, ingredient=target_ing)

    def _parse_serve(self) -> Optional[ServeNode]:
        """Parse: SERVE; or SERVE(style);"""
        serve_tok = self._advance()
        style: Optional[str] = None

        if self._check(TokenType.LPAREN):
            self._advance()
            if self._check(TokenType.IDENTIFIER):
                style_tok = self._advance()
                style = style_tok.value
            self._consume(TokenType.RPAREN, "Expected ')' after SERVE style option.", "ERR_MISSING_RPAREN")

        self._consume(TokenType.SEMICOLON, "Expected ';' terminating SERVE statement.", "ERR_MISSING_SEMICOLON", "Add ';' after SERVE.")
        return ServeNode(line=serve_tok.line, column=serve_tok.column, style=style)
