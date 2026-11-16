# Digital Cookbook Compiler — Team Contribution Matrix

This document provides a structured framework detailing the division of responsibilities, module ownership, implementation deliverables, and viva defense areas for academic evaluation.

---

## 1. Team Contribution Overview

| Team Member | Roll / Registration No. | Assigned Compiler Modules | Key Contributions | Viva Defense Focus |
|---|---|---|---|---|
| **[Student 1 Name - Team Lead]** | `[Roll Number 1]` | Project Architecture, Central Pipeline, Lexer & Tokenizer | Designed system architecture, character scanner, lexical token definitions, coordinate tracking, and pipeline coordination. | Lexical analysis, scanner design, token classification, regular expressions, and pipeline orchestration. |
| **[Student 2 Name]** | `[Roll Number 2]` | Grammar Specification, Recursive-Descent Parser & AST | Defined formal EBNF grammar, implemented recursive-descent parsing routines, statement synchronization, and AST data hierarchy. | Context-free grammars, EBNF production rules, recursive-descent parsing, AST nodes, and syntax error recovery. |
| **[Student 3 Name]** | `[Roll Number 3]` | Semantic Analyzer & Symbol Table | Implemented culinary domain rules, ingredient-dish validation, unit constraints, execution order dependencies, and symbol table manager. | Semantic analysis, symbol table attributes, type checking, context-sensitive validation, and multi-error reporting. |
| **[Student 4 Name]** | `[Roll Number 4]` | IR Generation, Optimizer Passes, Target Code Generator | Implemented Three-Address Code (3AC) generation, multi-pass optimization (unit canonicalization, peephole merging), and VKM bytecode generator. | Intermediate representations (3AC), optimization passes, peephole algorithms, safety proofs, and target virtual machine ISA. |

---

## 2. Module Ownership & Source File Mapping

### Module A: Frontend (Lexer & Parser)
- **Primary Owner**: `[Student 1 Name]` & `[Student 2 Name]`
- **Source Files**:
  - `compiler/tokens.py`
  - `compiler/lexer.py`
  - `compiler/ast_nodes.py`
  - `compiler/parser.py`
  - `docs/grammar.md`
- **Key Responsibilities**:
  - Scanning character-by-character without regex shortcuts.
  - Tracking exact line and column coordinates for every token.
  - Recursive-descent grammar implementation covering `RECIPE`, `ADD`, `MIX`, `BOIL`, `BAKE`, `FRY`, `CHOP`, `SERVE`.
  - Panic-mode parser synchronization on semicolons and statement start tokens.

### Module B: Contextual Verification (Semantic Analysis & Symbol Table)
- **Primary Owner**: `[Student 3 Name]`
- **Source Files**:
  - `compiler/language_spec.py`
  - `compiler/symbol_table.py`
  - `compiler/semantic.py`
  - `compiler/diagnostics.py`
- **Key Responsibilities**:
  - Constructing the culinary domain knowledge base (dishes, ingredients, units, operational limits).
  - Checking ingredient compatibility with declared dishes.
  - Symbol table design tracking quantities, units, categories, and source coordinates.
  - Sequential validation (preventing empty vessel mixing, requiring thermal steps before serving).

### Module C: Synthesis (IR, Optimization & Target Machine)
- **Primary Owner**: `[Student 4 Name]`
- **Source Files**:
  - `compiler/ir.py`
  - `compiler/optimizer.py`
  - `compiler/codegen.py`
  - `compiler/pipeline.py`
- **Key Responsibilities**:
  - Designing structured Three-Address Code (3AC) instruction dataclasses.
  - Implementing multi-pass optimizations:
    1. Canonical unit normalization (converting to `ML`, `GRAM`, `SECONDS`).
    2. Adjacent instruction merging (combining consecutive dispensations and contiguous mixing cycles).
    3. Dead code elimination.
  - Designing Virtual Kitchen Machine (VKM) bytecode assembly instruction set architecture.
  - Calculating execution cycle costs.

### Module D: Web Interface & Integration Testing
- **Shared Responsibility**: All Team Members
- **Source Files**:
  - `app.py`
  - `templates/index.html`
  - `static/css/style.css`
  - `static/js/app.js`
  - `static/js/ast_visualizer.js`
  - `tests/`
- **Key Responsibilities**:
  - Developing interactive developer IDE interface.
  - Tree visualizer for Abstract Syntax Tree inspection.
  - Unit and integration testing with 100% pass rate across 42 test cases.

---

## 3. Academic Integrity & Acknowledgements
This project is an independent implementation developed for the Compiler Design course curriculum. The team acknowledges the open-source repository `https://github.com/antedotee/cookbook-compiler` by Kartik Yadav as conceptual and architectural inspiration for a culinary domain-specific language. All data structures, recursive-descent routines, AST nodes, symbol tables, intermediate representations, optimization algorithms, target assembly instruction sets, web interfaces, and documentation were designed and implemented independently.
