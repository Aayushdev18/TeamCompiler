"""Phase 1: Lexical Analysis (Hand-written Scanner).

Reads source code character-by-character, maintains exact line and column coordinates,
and produces a stream of strongly-typed lexical tokens while capturing diagnostics.
"""

from typing import List, Optional, Tuple, Dict, Any
from .tokens import (
    Token,
    TokenType,
    KEYWORDS,
    MEASUREMENT_UNITS,
    TIME_UNITS,
)
from .diagnostics import DiagnosticBag, DiagnosticPhase


class Lexer:
    """Hand-written lexical analyzer for Cookbook DSL."""

    def __init__(self, source_code: str, diagnostics: Optional[DiagnosticBag] = None) -> None:
        self.source: str = source_code
        self.length: int = len(source_code)
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.diagnostics: DiagnosticBag = diagnostics if diagnostics is not None else DiagnosticBag()
        self.tokens: List[Token] = []

    def _peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead without consuming characters."""
        target = self.pos + offset
        if target >= self.length:
            return None
        return self.source[target]

    def _advance(self) -> Optional[str]:
        """Consume and return the current character, updating line and column."""
        if self.pos >= self.length:
            return None
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _skip_whitespace(self) -> None:
        """Skip whitespace characters (spaces, tabs, carriage returns, newlines)."""
        while self.pos < self.length:
            char = self.source[self.pos]
            if char in {" ", "\t", "\r", "\n"}:
                self._advance()
            else:
                break

    def _skip_comment(self) -> Optional[Token]:
        """Skip single-line comments prefixed with '#' or '//'."""
        start_line = self.line
        start_col = self.column

        # Check for # or //
        char = self._peek()
        if char == "#":
            self._advance()
        elif char == "/" and self._peek(1) == "/":
            self._advance()
            self._advance()
        else:
            return None

        comment_chars = []
        while self.pos < self.length and self._peek() != "\n":
            comment_chars.append(self._advance())

        lexeme = "".join(comment_chars).strip()
        return Token(
            type=TokenType.COMMENT,
            lexeme=lexeme,
            value=lexeme,
            line=start_line,
            column=start_col,
            category="Comment",
        )

    def _scan_number(self) -> Token:
        """Scan integer or floating-point literal with decimal validation."""
        start_line = self.line
        start_col = self.column
        chars = []
        has_dot = False

        while self.pos < self.length:
            char = self._peek()
            if char is not None and char.isdigit():
                chars.append(self._advance())
            elif char == "." and not has_dot:
                # Check whether next char is digit (float format like 1.5)
                next_char = self._peek(1)
                if next_char is not None and next_char.isdigit():
                    has_dot = True
                    chars.append(self._advance())  # consume '.'
                else:
                    # Dot without trailing digits (e.g. "12.")
                    self.diagnostics.add_error(
                        phase=DiagnosticPhase.LEXER,
                        message=f"Malformed floating-point literal: decimal point must be followed by digits.",
                        line=start_line,
                        column=start_col,
                        code="ERR_MALFORMED_NUMBER",
                        suggestion="Ensure decimals have digits on both sides, e.g. 1.0",
                    )
                    break
            elif char == "." and has_dot:
                # Multiple decimal points e.g. "1.2.3"
                self.diagnostics.add_error(
                    phase=DiagnosticPhase.LEXER,
                    message="Malformed number with multiple decimal points.",
                    line=start_line,
                    column=start_col,
                    code="ERR_MULTIPLE_DECIMALS",
                )
                chars.append(self._advance())
            else:
                break

        lexeme = "".join(chars)
        if has_dot:
            try:
                val = float(lexeme)
                token_type = TokenType.FLOAT_CONST
            except ValueError:
                val = 0.0
                token_type = TokenType.FLOAT_CONST
        else:
            try:
                val = int(lexeme)
                token_type = TokenType.INTEGER_CONST
            except ValueError:
                val = 0
                token_type = TokenType.INTEGER_CONST

        return Token(
            type=token_type,
            lexeme=lexeme,
            value=val,
            line=start_line,
            column=start_col,
            category="Numeric Constant",
        )

    def _scan_identifier_or_keyword(self) -> Token:
        """Scan word token and distinguish Keywords, Measurement Units, Time Units, and Identifiers."""
        start_line = self.line
        start_col = self.column
        chars = []

        while self.pos < self.length:
            char = self._peek()
            if char is not None and (char.isalnum() or char == "_"):
                chars.append(self._advance())
            else:
                break

        raw_lexeme = "".join(chars)
        upper_lexeme = raw_lexeme.upper()

        # 1. Check primary keywords
        if upper_lexeme in KEYWORDS:
            return Token(
                type=KEYWORDS[upper_lexeme],
                lexeme=raw_lexeme,
                value=upper_lexeme,
                line=start_line,
                column=start_col,
                category="Keyword",
            )

        # 2. Check measurement units
        if upper_lexeme in MEASUREMENT_UNITS:
            return Token(
                type=MEASUREMENT_UNITS[upper_lexeme],
                lexeme=raw_lexeme,
                value=upper_lexeme,
                line=start_line,
                column=start_col,
                category="Measurement Unit",
            )

        # 3. Check time units
        if upper_lexeme in TIME_UNITS:
            return Token(
                type=TIME_UNITS[upper_lexeme],
                lexeme=raw_lexeme,
                value=upper_lexeme,
                line=start_line,
                column=start_col,
                category="Time Unit",
            )

        # 4. Standard identifier (dish name, ingredient name)
        return Token(
            type=TokenType.IDENTIFIER,
            lexeme=raw_lexeme,
            value=upper_lexeme,
            line=start_line,
            column=start_col,
            category="Identifier",
        )

    def tokenize(self, include_comments: bool = False) -> List[Token]:
        """Perform full lexical scanning and return token sequence."""
        self.tokens = []

        # Empty input check
        if not self.source or self.source.strip() == "":
            eof_token = Token(
                type=TokenType.EOF,
                lexeme="",
                value=None,
                line=1,
                column=1,
                category="End of File",
            )
            self.tokens.append(eof_token)
            return self.tokens

        while self.pos < self.length:
            self._skip_whitespace()
            if self.pos >= self.length:
                break

            current_char = self._peek()
            current_line = self.line
            current_col = self.column

            # Comments
            if current_char == "#" or (current_char == "/" and self._peek(1) == "/"):
                comment_token = self._skip_comment()
                if include_comments and comment_token is not None:
                    self.tokens.append(comment_token)
                continue

            # Delimiters and punctuators
            if current_char == "(":
                self._advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", "(", current_line, current_col, "Delimiter"))
                continue
            if current_char == ")":
                self._advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", ")", current_line, current_col, "Delimiter"))
                continue
            if current_char == ",":
                self._advance()
                self.tokens.append(Token(TokenType.COMMA, ",", ",", current_line, current_col, "Delimiter"))
                continue
            if current_char == ";":
                self._advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", ";", current_line, current_col, "Delimiter"))
                continue

            # Numeric literals (starting with digit)
            if current_char.isdigit():
                self.tokens.append(self._scan_number())
                continue

            # Identifiers and keywords (starting with letter or underscore)
            if current_char.isalpha() or current_char == "_":
                self.tokens.append(self._scan_identifier_or_keyword())
                continue

            # Unexpected / illegal character
            illegal_char = self._advance()
            self.diagnostics.add_error(
                phase=DiagnosticPhase.LEXER,
                message=f"Unexpected illegal character '{illegal_char}' encountered.",
                line=current_line,
                column=current_col,
                code="ERR_ILLEGAL_CHARACTER",
                suggestion=f"Remove or replace character '{illegal_char}'.",
            )
            self.tokens.append(Token(
                type=TokenType.UNKNOWN,
                lexeme=illegal_char or "",
                value=illegal_char,
                line=current_line,
                column=current_col,
                category="Special",
            ))

        # Always terminate with EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            lexeme="",
            value=None,
            line=self.line,
            column=self.column,
            category="End of File",
        ))

        return self.tokens

    def get_summary(self) -> Dict[str, Any]:
        """Return diagnostic metrics and summary of lexical scanning."""
        counts: Dict[str, int] = {}
        for tok in self.tokens:
            counts[tok.category] = counts.get(tok.category, 0) + 1

        return {
            "total_tokens": len(self.tokens),
            "category_counts": counts,
            "has_errors": self.diagnostics.has_errors(),
            "error_count": len(self.diagnostics.errors()),
        }
