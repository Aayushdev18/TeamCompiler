# Digital Cookbook — Interactive Compiler Design Project

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0+](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/pytest-42%20passed-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/pipeline-6%20phases-purple.svg)](compiler/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive, web-based compiler for **Cookbook DSL**, a domain-specific programming language designed for culinary procedure modeling, static semantic verification, intermediate code optimization, and automated Virtual Kitchen Machine (VKM) bytecode generation.

Built on classic compiler engineering principles, this project demonstrates a complete, deterministic, decoupled six-phase compilation pipeline from lexical scanning to target code generation with an interactive developer IDE.

---

## Table of Contents
1. [Abstract](#abstract)
2. [Problem Statement](#problem-statement)
3. [Project Objectives](#project-objectives)
4. [Cookbook DSL Overview](#cookbook-dsl-overview)
5. [Key Features](#key-features)
6. [Technology Stack](#technology-stack)
7. [System Architecture](#system-architecture)
8. [The Six Compiler Phases](#the-six-compiler-phases)
   - [Phase 1: Lexical Analysis](#phase-1-lexical-analysis)
   - [Phase 2: Syntax Analysis & AST](#phase-2-syntax-analysis--ast)
   - [Phase 3: Semantic Analysis & Symbol Table](#phase-3-semantic-analysis--symbol-table)
   - [Phase 4: Intermediate Code Generation (IR)](#phase-4-intermediate-code-generation-ir)
   - [Phase 5: Code Optimization](#phase-5-code-optimization)
   - [Phase 6: Target Code Generation (VKM)](#phase-6-target-code-generation-vkm)
9. [Formal Grammar (EBNF)](#formal-grammar-ebnf)
10. [REST API Documentation](#rest-api-documentation)
11. [Built-in Example Recipes](#built-in-example-recipes)
12. [Project Structure](#project-structure)
13. [Installation & Setup](#installation--setup)
14. [Running the Application](#running-the-application)
15. [Running Automated Tests](#running-automated-tests)
16. [Academic Deliverables](#academic-deliverables)
17. [Limitations & Future Scope](#limitations--future-scope)
18. [References & Acknowledgements](#references--acknowledgements)

---

## Abstract
Traditional natural-language recipes are ambiguous, unstandardized, and error-prone when translated into automated culinary execution systems. The **Digital Cookbook** compiler provides a formal domain-specific language and execution pipeline that statically verifies recipe validity, enforces domain-specific culinary constraints, generates linear Three-Address Code (3AC), performs multi-pass peephole and normalization optimizations, and synthesizes Virtual Kitchen Machine assembly code. Designed as a comprehensive academic compiler project, it features an interactive dual-pane IDE visualizing real data produced at every stage of compilation.

---

## Problem Statement
Robotic culinary systems and smart kitchen appliances require deterministic, verifiable execution sequences. Natural-language recipes introduce significant failure modes:
1. **Ambiguous units and quantities**: Using inconsistent units without standard base-unit conversions.
2. **Missing static verification**: Physical mistakes (such as baking raw dough without mixing, adding incompatible ingredients, or running empty vessels) are caught only during physical execution.
3. **Inefficient machine actuation**: Fragmented, un-optimized instructions trigger redundant mechanical dispenser cycles unless optimized through compiler passes.

---

## Project Objectives
- Implement a genuine, hand-written character-level lexical analyzer with exact line and column tracking.
- Construct a recursive-descent syntax parser producing a strongly-typed Abstract Syntax Tree with panic-mode error recovery.
- Develop a context-sensitive semantic analyzer and comprehensive symbol table enforcing culinary rules.
- Linearize the AST into a machine-independent Three-Address Code (3AC) intermediate representation.
- Implement multi-pass optimizations: unit canonicalization, adjacent instruction merging, and dead-code elimination.
- Generate deterministic target assembly code for a Virtual Kitchen Machine (VKM) architecture.
- Build an interactive, dark-first developer IDE displaying actual compilation results across all six phases.

---

## Cookbook DSL Overview
A Cookbook DSL program declares a target dish, followed by sequential ingredient additions, mechanical preparation, and thermal cooking operations, terminated by a mandatory serving instruction:

```text
RECIPE PANCAKE;

# Add dry base ingredients
ADD(2, CUP, FLOUR);
ADD(2, TBSP, SUGAR);
ADD(1, PINCH, SALT);

# Add liquid bindings
ADD(1, PIECE, EGG);
ADD(1, CUP, MILK);

# Mechanical preparation & thermal cooking
WHISK(2, MINUTES);
FRY(4, MINUTES);

# Plating and final presentation
SERVE;
```

---

## Key Features
- **100% Deterministic & Hand-Written**: No generative AI mocks or static hardcoded outputs. Every phase operates dynamically on parsed data structures.
- **Panic-Mode Error Recovery**: Parser synchronizes to statement boundaries upon syntax errors, enabling discovery of multiple errors in one pass.
- **Rich Interactive Visualizations**:
  - Filterable and searchable lexical token stream table.
  - Interactive hierarchical AST tree visualizer with node collapse/expand controls.
  - Multi-attribute symbol table tracking cumulative quantities and occurrences.
  - Semantic domain rules validation checklist with pass/fail/warning indicators.
  - Side-by-side Intermediate Representation diff view with instruction reduction metrics.
  - Virtual Kitchen Machine assembly code listing with instruction cycle costs.
- **18 Built-in Examples**: Covering 6 diverse valid culinary recipes, multi-pass optimization showcases, and all categories of lexical, syntax, and semantic errors.
- **Comprehensive Quality Assurance**: 42 automated `pytest` test cases verifying 100% pass rate.

---

## Technology Stack
- **Backend**: Python 3.11+, Flask 3.0+, Dataclasses, Pytest.
- **Frontend**: Vanilla JavaScript (ES6+), Modern Semantic HTML5, CSS3 with Custom Properties (Dark-first IDE theme).
- **Visualization**: Custom SVG & DOM hierarchical AST tree visualizer.
- **Architecture**: Modular compiler pipeline decoupled from the web framework.

---

## System Architecture

```text
+-------------------------------------------------------------------------+
|                        DIGITAL COOKBOOK COMPILER                        |
+-------------------------------------------------------------------------+
                                     |
                                     v
[Phase 1: Lexer] ------------> Tokens Stream + (Line, Col) Coordinates
                                     |
                                     v
[Phase 2: Parser] -----------> Strongly-Typed Abstract Syntax Tree (AST)
                                     |
                                     v
[Phase 3: Semantic] ---------> Validated AST + Scoped Symbol Table
                                     |
                                     v
[Phase 4: IR Generator] -----> Three-Address Code (3AC) Linear Instructions
                                     |
                                     v
[Phase 5: Optimizer] --------> Multi-Pass Optimized 3AC (Peephole & Canonical)
                                     |
                                     v
[Phase 6: Code Generator] ---> Virtual Kitchen Machine (VKM) Target Assembly
                                     |
                                     v
[Flask REST API & Web IDE] --> JSON Payloads & Interactive Phase Dashboards
```

---

## The Six Compiler Phases

### Phase 1: Lexical Analysis
- Hand-written scanner reading character-by-character (`compiler/lexer.py`).
- Identifies keywords, measurement units, time units, numeric literals (integers, floats), identifiers, comments, and delimiters.
- Tracks 1-indexed line and column numbers.
- Emits structured `Token` objects and detects unexpected characters (`@`, `$`) without crashing.

### Phase 2: Syntax Analysis & AST
- Recursive-descent parser (`compiler/parser.py`) implementing the documented EBNF grammar.
- Constructs a strongly-typed AST (`compiler/ast_nodes.py`).
- Detects missing recipe headers, missing semicolons, missing or extra arguments, unclosed parentheses, and statements after `SERVE`.
- Implements statement boundary synchronization for error recovery.

### Phase 3: Semantic Analysis & Symbol Table
- Contextual analyzer (`compiler/semantic.py`) operating on the AST.
- Validates dish declarations against known recipes (`PANCAKE`, `SPONGE_CAKE`, `PASTA`, `HERBAL_TEA`, `FRENCH_OMELETTE`, `FRESH_SALAD`).
- Enforces ingredient compatibility (e.g. rejecting bacon in tea or salt in cake).
- Enforces physical unit restrictions (e.g. rejecting eggs measured in milliliters).
- Rejects non-positive quantities ($q \le 0$) and empty vessel operations.
- Populates the `SymbolTable` tracking cumulative quantities, occurrences, and source locations.

### Phase 4: Intermediate Code Generation (IR)
- Translates AST into Three-Address Code (`compiler/ir.py`).
- Each instruction is an `IRInstruction` dataclass with an opcode, up to three arguments, a temporary result variable (`t1`, `t2`, etc.), line mapping, and descriptive comments.

### Phase 5: Code Optimization
- Multi-pass semantic-preserving transformations (`compiler/optimizer.py`):
  1. **Unit Normalization Pass**: Standardizes volumes to milliliters (`ML`), mass to grams (`GRAM`), and durations to seconds (`SECONDS`).
  2. **Adjacent Instruction Merging (Peephole Pass)**: Combines contiguous additions of identical ingredients (e.g. `150g FLOUR` + `150g FLOUR` $\to$ `300g FLOUR`), saving machine dispensing cycles.
  3. **Dead Code Elimination Pass**: Prunes zero-quantity and zero-duration operations.
- Outputs side-by-side diffs and calculates reduction percentage.

### Phase 6: Target Code Generation (VKM)
- Translates optimized IR into assembly instructions for the Virtual Kitchen Machine (`compiler/codegen.py`).
- Emits instruction addresses (`0x0000`, `0x0001`), mnemonics (`LOAD_VESSEL`, `DISPENSE`, `STIR`, `HEAT_BOIL`, `HEAT_BAKE`, `HEAT_FRY`, `PLATING_SERVE`, `HALT`), cycle costs, and descriptions.

---

## Formal Grammar (EBNF)

```ebnf
program         ::= recipe_decl statement_list serve_stmt EOF ;
recipe_decl     ::= "RECIPE" identifier ";" ;
statement_list  ::= { statement } ;
statement       ::= add_stmt | timed_stmt | chop_stmt ;
add_stmt        ::= "ADD" "(" number "," unit "," identifier ")" ";" ;
timed_stmt      ::= timed_op "(" number "," time_unit ")" ";" ;
chop_stmt       ::= "CHOP" "(" identifier ")" ";" ;
serve_stmt      ::= "SERVE" [ "(" identifier ")" ] ";" ;
timed_op        ::= "MIX" | "BOIL" | "BAKE" | "FRY" | "SIMMER" | "CHILL" | "WHISK" | "REST" ;
unit            ::= "CUP" | "TBSP" | "TSP" | "GRAM" | "KG" | "ML" | "LITER" | "PIECE" | "PINCH" ;
time_unit       ::= "SECONDS" | "MINUTES" | "HOURS" ;
number          ::= integer | float ;
integer         ::= [0-9]+ ;
float           ::= [0-9]+ "." [0-9]+ ;
identifier      ::= [A-Za-z_][A-Za-z0-9_]* ;
```

---

## REST API Documentation

### `POST /api/compile`
Executes the full six-phase compilation pipeline.
- **Request Body**: `{"source": "RECIPE PANCAKE; ADD(2, CUP, FLOUR); SERVE;"}`
- **Response**:
```json
{
  "success": true,
  "compilation_time_ms": 1.45,
  "phases": [
    {"id": "lexer", "phase_number": 1, "status": "success", "output": {...}},
    {"id": "parser", "phase_number": 2, "status": "success", "output": {...}},
    {"id": "semantic", "phase_number": 3, "status": "success", "output": {...}},
    {"id": "ir", "phase_number": 4, "status": "success", "output": {...}},
    {"id": "optimizer", "phase_number": 5, "status": "success", "output": {...}},
    {"id": "codegen", "phase_number": 6, "status": "success", "output": {...}}
  ],
  "diagnostics": [],
  "summary": {
    "success": true,
    "total_errors": 0,
    "total_warnings": 0,
    "phases_succeeded": 6
  }
}
```

### `GET /api/examples`
Retrieves all 18 built-in recipes with source code and categorization.

### `GET /api/vocabulary`
Returns the complete vocabulary knowledge base (dishes, ingredients, units, limits).

### `GET /api/health`
Monitors API health and returns service status.

---

## Built-in Example Recipes
Located in `examples/`:
- **Valid Recipes**:
  - `01_pancake.cook`: Classic breakfast pancake.
  - `02_sponge_cake.cook`: Vanilla baked confectionery.
  - `03_pasta_carbonara.cook`: Boiled pasta with savory emulsion.
  - `04_herbal_tea.cook`: Steeping botanical infusion.
  - `05_french_omelette.cook`: Delicate pan-fried egg dish.
  - `06_fresh_salad.cook`: Crisp raw produce with vinaigrette.
  - `07_optimization_demo.cook`: Showcases unit canonicalization, adjacent flour batch merging, and consecutive mixing aggregation.
  - `08_no_optimization.cook`: Demonstrates pipeline behavior when source is already in canonical base form.
- **Error Diagnostics & Edge Cases**:
  - `09_lexical_error.cook`: Illegal symbols (`@`, `$`) and malformed float (`2.`).
  - `10_syntax_error.cook`: Missing semicolons and unclosed parentheses.
  - `11_semantic_unknown_ingredient.cook`: Unrecognized ingredient `DRAGON_SCALE`.
  - `12_semantic_incompatible_unit.cook`: Measuring eggs in milliliters.
  - `13_missing_serve.cook`: Missing mandatory terminating `SERVE;`.
  - `14_statement_after_serve.cook`: Illegal instructions placed after `SERVE;`.
  - `15_invalid_instruction_order.cook`: Mixing and frying an empty vessel.
  - `16_multiple_semantic_errors.cook`: Multiple independent errors reported simultaneously.
  - `17_empty_input.cook`: Completely empty file handling.
  - `18_comments_only.cook`: Comments-only program handling.

---

## Project Structure
```text
Teamcompiler/
│
├── app.py                      # Flask Application & REST API
├── requirements.txt            # Python Dependencies (Flask, Pytest)
├── pytest.ini                  # Pytest Configuration
├── README.md                   # Comprehensive Documentation
├── .gitignore                  # Git Ignore Rules
│
├── compiler/                   # Core Compiler Package
│   ├── __init__.py             # Package Exports
│   ├── tokens.py               # Token Definitions & Categories
│   ├── diagnostics.py          # Structured Diagnostic Reporting System
│   ├── language_spec.py        # Central Culinary Domain Knowledge Base
│   ├── lexer.py                # Phase 1: Lexical Scanner
│   ├── ast_nodes.py            # Phase 2: Strongly-Typed AST Nodes
│   ├── parser.py               # Phase 2: Recursive-Descent Parser
│   ├── symbol_table.py         # Phase 3: Scoped Symbol Table
│   ├── semantic.py             # Phase 3: Semantic Domain Validator
│   ├── ir.py                   # Phase 4: Three-Address Code IR Generator
│   ├── optimizer.py            # Phase 5: Multi-Pass Code Optimizer
│   ├── codegen.py              # Phase 6: VKM Bytecode Assembly Generator
│   └── pipeline.py             # Central Pipeline Coordinator
│
├── examples/                   # Built-in DSL Example Programs
│   ├── valid/                  # 8 Valid Recipe Programs
│   └── invalid/                # 10 Error & Edge Case Programs
│
├── tests/                      # 42 Comprehensive Unit & Integration Tests
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_symbol_table.py
│   ├── test_ir.py
│   ├── test_optimizer.py
│   ├── test_codegen.py
│   ├── test_pipeline.py
│   └── test_api.py
│
├── templates/
│   └── index.html              # Modern Developer IDE Interface
│
├── static/
│   ├── css/
│   │   └── style.css           # Dark-first Developer IDE Theme
│   └── js/
│       ├── app.js              # Application Controller & Data Binding
│       └── ast_visualizer.js   # Hierarchical Tree Visualizer
│
└── docs/                       # Academic Deliverables
    ├── architecture.md         # Compiler Architecture Specifications
    ├── grammar.md              # Formal EBNF Grammar & Lexical Rules
    ├── viva_preparation.md     # Viva Voce Defense Guide & Q&A
    ├── contribution_matrix.md  # Team Contribution & Ownership Matrix
    └── IEEE_Project_Report.tex # IEEE Conference Format Academic Paper
```

---

## Installation & Setup

### Prerequisites
- Python 3.11 or newer
- Git

### Installation Steps

#### macOS / Linux
```bash
# Clone the repository
git clone https://github.com/Aayushdev18/TeamCompiler.git
cd TeamCompiler

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/Aayushdev18/TeamCompiler.git
cd TeamCompiler

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Application
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the Flask compiler server
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## Running Automated Tests
Run the complete automated test suite using `pytest`:
```bash
# Run all 42 tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific phase test group
pytest tests/test_lexer.py
pytest tests/test_parser.py
pytest tests/test_semantic.py
pytest tests/test_optimizer.py
pytest tests/test_codegen.py
pytest tests/test_pipeline.py
pytest tests/test_api.py
```

---

## Academic Deliverables
- **IEEE Format Academic Paper**: `docs/IEEE_Project_Report.tex` (Full conference-ready paper with architecture diagrams, grammar tables, and experimental results).
- **Viva Voce Preparation Guide**: `docs/viva_preparation.md` (Detailed answers to fundamental compiler design questions, pipeline walkthroughs, and error demonstrations).
- **Team Contribution Matrix**: `docs/contribution_matrix.md` (Role division, module assignments, and viva defense areas).
- **Formal Grammar Documentation**: `docs/grammar.md`.
- **System Architecture**: `docs/architecture.md`.

---

## Limitations & Future Scope
- **Current Limitations**: Sequential single-vessel preparation model; thermodynamic temperature gradient simulation is approximated.
- **Future Scope**:
  - Concurrent multi-vessel preparation and synchronization barriers.
  - Physical hardware actuator integration via serial / GPIO interfaces.
  - Thermodynamic heat-transfer modeling for real-time oven temperature curves.

---

## References & Acknowledgements
- A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed. Addison-Wesley, 2006.
- K. D. Cooper and L. Torczon, *Engineering a Compiler*, 2nd ed. Morgan Kaufmann, 2011.
- **Architectural Inspiration**: This project was inspired by the open-source Cookbook Compiler project by Kartik Yadav ([github.com/antedotee/cookbook-compiler](https://github.com/antedotee/cookbook-compiler)). The Digital Cookbook Compiler was independently engineered with an original Abstract Syntax Tree node hierarchy, multi-pass optimization engine, Virtual Kitchen Machine assembly generator, interactive IDE, and test suite.

---

**Developed for the Compiler Design Laboratory Evaluation.**
