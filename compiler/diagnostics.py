"""Compiler Diagnostic Reporting System.

Provides structured, line-precise diagnostic messages (errors, warnings, informational notes)
across all phases of the Digital Cookbook Compiler.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class DiagnosticSeverity(str, Enum):
    """Severity levels for compiler messages."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DiagnosticPhase(str, Enum):
    """Compiler phase where the diagnostic originated."""
    LEXER = "lexer"
    PARSER = "parser"
    SEMANTIC = "semantic"
    IR = "ir"
    OPTIMIZER = "optimizer"
    CODEGEN = "codegen"
    SYSTEM = "system"


@dataclass
class CompilerDiagnostic:
    """Represents a single diagnostic message with source code coordinate mapping."""
    phase: DiagnosticPhase
    severity: DiagnosticSeverity
    message: str
    line: int
    column: int
    code: str
    related_identifier: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic to JSON-serializable dictionary."""
        return {
            "phase": self.phase.value if isinstance(self.phase, Enum) else str(self.phase),
            "severity": self.severity.value if isinstance(self.severity, Enum) else str(self.severity),
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "related_identifier": self.related_identifier,
            "suggestion": self.suggestion,
        }


class DiagnosticBag:
    """Manages an aggregated collection of diagnostics during compilation."""

    def __init__(self) -> None:
        self.diagnostics: List[CompilerDiagnostic] = []

    def add(
        self,
        phase: DiagnosticPhase,
        severity: DiagnosticSeverity,
        message: str,
        line: int = 1,
        column: int = 1,
        code: str = "ERR_GENERIC",
        related_identifier: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> CompilerDiagnostic:
        """Add a new diagnostic record."""
        diag = CompilerDiagnostic(
            phase=phase,
            severity=severity,
            message=message,
            line=line,
            column=column,
            code=code,
            related_identifier=related_identifier,
            suggestion=suggestion,
        )
        self.diagnostics.append(diag)
        return diag

    def add_error(
        self,
        phase: DiagnosticPhase,
        message: str,
        line: int = 1,
        column: int = 1,
        code: str = "ERR_COMPILER",
        related_identifier: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> CompilerDiagnostic:
        """Helper to add an error diagnostic."""
        return self.add(
            phase=phase,
            severity=DiagnosticSeverity.ERROR,
            message=message,
            line=line,
            column=column,
            code=code,
            related_identifier=related_identifier,
            suggestion=suggestion,
        )

    def add_warning(
        self,
        phase: DiagnosticPhase,
        message: str,
        line: int = 1,
        column: int = 1,
        code: str = "WARN_COMPILER",
        related_identifier: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> CompilerDiagnostic:
        """Helper to add a warning diagnostic."""
        return self.add(
            phase=phase,
            severity=DiagnosticSeverity.WARNING,
            message=message,
            line=line,
            column=column,
            code=code,
            related_identifier=related_identifier,
            suggestion=suggestion,
        )

    def has_errors(self) -> bool:
        """Return True if any error diagnostic has been recorded."""
        return any(d.severity == DiagnosticSeverity.ERROR for d in self.diagnostics)

    def errors(self) -> List[CompilerDiagnostic]:
        """Return all error diagnostics."""
        return [d for d in self.diagnostics if d.severity == DiagnosticSeverity.ERROR]

    def warnings(self) -> List[CompilerDiagnostic]:
        """Return all warning diagnostics."""
        return [d for d in self.diagnostics if d.severity == DiagnosticSeverity.WARNING]

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize all diagnostics to list of dictionaries."""
        return [d.to_dict() for d in self.diagnostics]

    def clear(self) -> None:
        """Clear all stored diagnostics."""
        self.diagnostics.clear()
