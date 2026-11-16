# Digital Cookbook Compiler — Comprehensive Viva Preparation Guide

This technical guide prepares students and evaluators for the viva voce and technical defense of the **Digital Cookbook Compiler**.

---

## Part A: Compiler Design Fundamentals

### 1. What is a Compiler?
A compiler is a language translator that accepts a program written in a high-level source language and translates it into an equivalent program in a lower-level target language (such as machine code, bytecode, or assembly) while preserving operational semantics.

### 2. How does a Compiler differ from an Interpreter?
- **Compiler**: Translates the entire source program ahead of time, performs deep multi-pass optimizations across the whole Abstract Syntax Tree, and emits standalone target code for execution.
- **Interpreter**: Reads, parses, and immediately executes instructions line-by-line or statement-by-statement at runtime without generating persistent target code.
- **Digital Cookbook**: Functions as a **true multi-phase compiler**. It parses source code, validates semantics across the whole recipe, constructs Three-Address Code (3AC) intermediate representation, applies optimization passes, and emits Virtual Kitchen Machine (VKM) bytecode.

### 3. What are the Six Classic Compiler Phases?
1. **Lexical Analysis (Scanner)**: Converts character stream into a token stream.
2. **Syntax Analysis (Parser)**: Validates grammatical structure and builds an Abstract Syntax Tree (AST).
3. **Semantic Analysis**: Checks context-sensitive domain rules, types, bounds, and builds the Symbol Table.
4. **Intermediate Representation (IR) Generation**: Translates AST into linear, machine-independent three-address code.
5. **Code Optimization**: Improves intermediate code efficiency (reducing cycles, normalizing units, pruning redundancy) while preserving program semantics.
6. **Target Code Generation**: Translates optimized IR into target virtual machine assembly instructions.

### 4. What is the difference between Compiler Frontend and Backend?
- **Frontend (Phases 1–3)**: Language-dependent. Understands the source grammar, tokens, keywords, and culinary domain logic.
- **Intermediate Representation (Phase 4)**: The decouple bridge. Separates source language syntax from hardware execution.
- **Backend (Phases 5–6)**: Target-dependent. Optimizes machine operations and emits specific Virtual Kitchen Machine (VKM) bytecode.

---

## Part B: Digital Cookbook Implementation Architecture

### 1. Request-to-Compilation Workflow
1. User enters Cookbook DSL source in the web IDE and clicks **Compile** (`POST /api/compile`).
2. `CompilationPipeline` instantiates `Lexer` -> scans characters, tracks exact lines/columns, returns token list.
3. `Parser` consumes non-comment tokens, applies recursive-descent rules, returns `ProgramNode` AST.
4. `SemanticAnalyzer` walks AST, checks ingredient compatibility against `DISHES` dictionary, checks valid units, populates `SymbolTable`.
5. `IRGenerator` translates AST into linear `IRInstruction` (3-Address Code) sequence.
6. `IROptimizer` runs 3 transformation passes: unit normalization, adjacent instruction merging, dead-code removal.
7. `CodeGenerator` emits Virtual Kitchen Machine assembly code with hardware parameters and cycle costs.
8. Pipeline packs outputs into a JSON payload; frontend dynamically renders tables, AST tree, checklist, IR diffs, and assembly listings.

### 2. Key Source Code Files to Study
- `compiler/lexer.py`: Character lookahead (`_peek`, `_advance`), whitespace/comment handling, coordinate tracking.
- `compiler/parser.py`: Recursive descent logic (`_parse_add`, `_parse_timed_op`), synchronization error recovery (`_synchronize`).
- `compiler/semantic.py`: Domain rule enforcement, ingredient compatibility, positive quantity checks, checklist builder.
- `compiler/optimizer.py`: Peephole optimization, adjacent batch merging, unit conversion factors.
- `compiler/codegen.py`: VKM instruction mapping and cycle estimation.

---

## Part C: Complete Recipe Walkthrough Across All Six Phases

Consider the canonical recipe:
```text
RECIPE PANCAKE;
ADD(150, GRAM, FLOUR);
ADD(150, GRAM, FLOUR);
ADD(1, CUP, MILK);
MIX(2, MINUTES);
FRY(4, MINUTES);
SERVE;
```

### Phase 1: Lexical Output (Tokens)
- `Token(RECIPE, 'RECIPE', line 1, col 1)`
- `Token(IDENTIFIER, 'PANCAKE', line 1, col 8)`
- `Token(SEMICOLON, ';', line 1, col 15)`
- `Token(ADD, 'ADD', line 2, col 1)`
- `Token(LPAREN, '(', line 2, col 4)`
- `Token(INTEGER_CONST, 150, line 2, col 5)`
- `Token(COMMA, ',', line 2, col 8)`
- `Token(UNIT_GRAM, 'GRAM', line 2, col 10)`
- ... up to `Token(EOF, '', line 8, col 1)`

### Phase 2: Syntax Output (AST)
```text
ProgramNode(dish="PANCAKE")
 ├── RecipeDeclNode(dish_name="PANCAKE")
 ├── AddNode(quantity=150, unit="GRAM", ingredient="FLOUR")
 ├── AddNode(quantity=150, unit="GRAM", ingredient="FLOUR")
 ├── AddNode(quantity=1, unit="CUP", ingredient="MILK")
 ├── TimedOpNode(operation="MIX", duration=2, time_unit="MINUTES")
 ├── TimedOpNode(operation="FRY", duration=4, time_unit="MINUTES")
 └── ServeNode()
```

### Phase 3: Semantic Output (Symbol Table & Checklist)
- **Symbol Table**:
  - `PANCAKE` | Dish | DishType | Qty: 1 | Line 1
  - `FLOUR` | Ingredient | Dry Solid | Unit: GRAM | Qty: 300.0 | Occurrences: 2
  - `MILK` | Ingredient | Liquid | Unit: CUP | Qty: 1.0 | Occurrences: 1
  - `MIX` | Cooking Operation | Timer | Unit: MINUTES | Qty: 2.0
  - `FRY` | Cooking Operation | Timer | Unit: MINUTES | Qty: 4.0
- **Validation**: All checks pass (`FLOUR` and `MILK` compatible with `PANCAKE`; thermal cooking step present).

### Phase 4: Intermediate Representation (Initial 3AC)
```text
t1 = RECIPE PANCAKE
t2 = ADD FLOUR, 150 GRAM
t3 = ADD FLOUR, 150 GRAM
t4 = ADD MILK, 1 CUP
t5 = MIX 2 MINUTES
t6 = FRY 4 MINUTES
t7 = SERVE
```

### Phase 5: Code Optimization (Optimized 3AC)
1. *Pass 1 (Unit Normalization)*:
   - `t4 = ADD MILK, 1 CUP` converted to `t4 = ADD MILK, 240 ML`
   - `t5 = MIX 2 MINUTES` converted to `t5 = MIX 120 SECONDS`
   - `t6 = FRY 4 MINUTES` converted to `t6 = FRY 240 SECONDS`
2. *Pass 2 (Adjacent Merging)*:
   - `t2 = ADD FLOUR, 150 GRAM` and `t3 = ADD FLOUR, 150 GRAM` merged into `t2 = ADD FLOUR, 300 GRAM`!
3. **Instruction Count**: Reduced from 7 instructions down to 6 instructions (14.3% reduction)!

### Phase 6: Target Code Generation (VKM Assembly)
```text
    0x0000    LOAD_VESSEL PANCAKE              ; [Line 1] Mount vessel for PANCAKE
    0x0001    DISPENSE FLOUR, 300.0, GRAM       ; [Line 2] Dispense 300g flour
    0x0002    DISPENSE MILK, 240.0, ML          ; [Line 4] Dispense 240ml milk
    0x0003    STIR 120, 120s                    ; [Line 5] Stir at 120 RPM for 120s
    0x0004    HEAT_FRY 160, 240s                ; [Line 6] Heat griddle to 160C for 240s
    0x0005    PLATING_SERVE DEFAULT             ; [Line 7] Present dish on serving plate
    0x0006    HALT                              ; [Line 7] Power down actuators
```

---

## Part D: Error Detection Demonstrations

| Error Category | Example Code | Compiler Phase | Diagnostic Code | Behavior |
|---|---|---|---|---|
| **Lexical Error** | `RECIPE @PANCAKE$;` | Phase 1 (Lexer) | `ERR_ILLEGAL_CHARACTER` | Scans illegal char `@`, creates `UNKNOWN` token, records coordinate `Line 1: Col 8`. |
| **Syntax Error** | `ADD 2, CUP, FLOUR;` | Phase 2 (Parser) | `ERR_MISSING_LPAREN` | Detects missing `(`, synchronizes to statement end, skips downstream. |
| **Semantic Error** | `ADD(500, ML, EGG);` | Phase 3 (Semantic) | `ERR_INCOMPATIBLE_UNIT` | Egg cannot be dispensed in milliliters (only `PIECE`). Emits error with allowed units. |
| **Domain Constraint**| `BAKE(20, MIN);` in Salad | Phase 3 (Semantic) | `ERR_FORBIDDEN_OPERATION` | Salad is a raw cold dish; oven baking is forbidden by domain rules. |
| **Execution Order**| `MIX(5, MIN);` at line 2 | Phase 3 (Semantic) | `ERR_EMPTY_VESSEL_OPERATION` | Cannot mix before adding ingredients. |
| **Post-Termination**| `ADD(...)` after `SERVE;` | Phase 2 (Parser) | `ERR_STATEMENT_AFTER_SERVE` | Rejects instructions placed after dish completion. |

---

## Part E: Common Viva Voce Questions & Answers

### Q1: Why did you build a Domain-Specific Language (DSL) instead of using a general-purpose language like Python or C?
**Answer**: A domain-specific language provides specialized syntactic primitives tailored to a specific problem space (culinary automation). By embedding domain semantics (e.g. ingredient compatibilities, physical unit transformations, and preparation sequences) into the grammar and semantic analyzer, we can verify recipe correctness at compile-time rather than encountering physical cooking failures at runtime.

### Q2: How does your recursive-descent parser recover from syntax errors?
**Answer**: Our parser implements synchronization-based panic-mode recovery. When an invalid token is encountered inside a statement, an error diagnostic with line and column numbers is appended to the diagnostic bag. The parser then advances through the token stream until it reaches a synchronizing token—specifically a semicolon (`;`) or a statement-starting keyword (`RECIPE`, `ADD`, `MIX`, `BOIL`, `SERVE`). This allows the parser to discover subsequent syntax errors in the program without crashing or halting at the first defect.

### Q3: Why is Three-Address Code (3AC) used as the Intermediate Representation?
**Answer**: Three-Address Code linearizes complex hierarchical AST constructs into elementary instructions with at most three addresses (two operands and one result). This representation is machine-independent, making it simple to implement compiler optimization algorithms (such as constant folding, unit canonicalization, and peephole merging) without being tied to specific target machine registers or hardware configurations.

### Q4: Why is your adjacent instruction merging optimization safe?
**Answer**: In cooking semantics, adding 150 grams of flour followed immediately by another 150 grams of flour without an intervening operational boundary (such as mixing, whisking, or thermal cooking) results in the exact same physical state in the cooking vessel. Therefore, combining them into a single 300-gram dispensation preserves identical operational semantics while saving a machine feeder actuation cycle.

### Q5: How do you prevent downstream phases from crashing when a syntax error occurs?
**Answer**: The central `CompilationPipeline` orchestrates the phase lifecycle using a strict status model (`success`, `error`, `skipped`). If an upstream phase (such as the lexer or parser) reports fatal errors, downstream phases (semantic analysis, IR generation, optimizer, and codegen) are safely marked as `skipped` and bypassed, ensuring that the application never encounters an unhandled exception or dumps an uncontrolled traceback to the user.
