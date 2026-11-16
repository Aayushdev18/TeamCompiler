"""Digital Cookbook Compiler Package.

An Interactive Domain-Specific Language (DSL) Compiler for Culinary Procedures.
Provides a complete 6-phase compiler pipeline:
1. Lexical Analysis (Scanner)
2. Syntax Analysis (Recursive-Descent Parser & AST)
3. Semantic Analysis & Symbol Table Generation
4. Intermediate Representation (Three-Address Code IR)
5. Optimization Passes (Unit Normalization, Instruction Merging, Dead Code Elimination)
6. Target Code Generation (Virtual Kitchen Machine Bytecode)
"""

from .pipeline import CompilationPipeline

__version__ = "1.0.0"
__all__ = ["CompilationPipeline"]
