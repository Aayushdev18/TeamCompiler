# Cookbook DSL — Formal Language Specification & Grammar

## 1. Overview
**Cookbook DSL** is a domain-specific programming language designed for formal modeling, verification, and automated compilation of culinary recipes. It enforces strict structural and semantic rules governing ingredient declarations, physical measurement units, time bounds, and preparation steps.

---

## 2. Lexical Grammar

### 2.1 Character Set
Source files are encoded in standard UTF-8 text. Keywords and identifiers are case-insensitive and canonicalized to uppercase.

### 2.2 Whitespace and Comments
- **Whitespace**: Space (`0x20`), Tab (`0x09`), Carriage Return (`0x0D`), Newline (`0x0A`) separate tokens and are otherwise discarded outside lexemes.
- **Single-Line Comments**:
  - Hash syntax: `# comment text until end of line`
  - C-style syntax: `// comment text until end of line`

### 2.3 Reserved Keywords
```text
RECIPE      ADD         MIX         BOIL        BAKE
FRY         SIMMER      CHILL       WHISK       CHOP
REST        SERVE
```

### 2.4 Measurement Unit Tokens
```text
CUP         CUPS        TBSP        TABLESPOON  TABLESPOONS
TSP         TEASPOON    TEASPOONS   GRAM        GRAMS
G           KG          KILOGRAM    ML          MILLILITER
LITER       LITERS      L           PIECE       PIECES
PINCH       PINCHES
```

### 2.5 Time Unit Tokens
```text
SECONDS     SECOND      SEC
MINUTES     MINUTE      MIN
HOURS       HOUR        HR
```

### 2.6 Numeric Literals
- **Integer Constants**: Sequence of one or more decimal digits:
  $$\text{INTEGER} = [0-9]+$$
- **Floating-Point Constants**: Decimal digits with a required decimal point and trailing digits:
  $$\text{FLOAT} = [0-9]+\;.\;[0-9]+$$
- *Malformed Numbers*: A period without trailing digits (`12.`) or multiple periods (`1.2.3`) is flagged as a lexical error (`ERR_MALFORMED_NUMBER`).

### 2.7 Identifiers
Identifiers represent dish names and culinary ingredient names:
$$\text{IDENTIFIER} = [A-Za-z\_][A-Za-z0-9\_]*$$

### 2.8 Punctuators and Delimiters
```text
(   LPAREN
)   RPAREN
,   COMMA
;   SEMICOLON
```

---

## 3. Formal EBNF Syntax Grammar

```ebnf
(* Root program rule *)
program             ::= recipe_decl statement_list serve_stmt EOF ;

(* Recipe declaration header *)
recipe_decl         ::= "RECIPE" identifier ";" ;

(* Sequence of zero or more culinary statements *)
statement_list      ::= { statement } ;

(* Statement production *)
statement           ::= add_statement
                      | timed_statement
                      | chop_statement ;

(* Ingredient addition statement *)
add_statement       ::= "ADD" "(" quantity "," measurement_unit "," identifier ")" ";" ;

(* Timed cooking / mechanical preparation statement *)
timed_statement     ::= timed_operator "(" duration "," time_unit ")" ";" ;

(* Produce cut / prep statement *)
chop_statement      ::= "CHOP" "(" identifier ")" ";" ;

(* Mandatory terminating plating statement *)
serve_stmt          ::= "SERVE" [ "(" identifier ")" ] ";" ;

(* Timed operator set *)
timed_operator      ::= "MIX"
                      | "BOIL"
                      | "BAKE"
                      | "FRY"
                      | "SIMMER"
                      | "CHILL"
                      | "WHISK"
                      | "REST" ;

(* Measurement units *)
measurement_unit    ::= "CUP" | "CUPS"
                      | "TBSP" | "TABLESPOON" | "TABLESPOONS"
                      | "TSP" | "TEASPOON" | "TEASPOONS"
                      | "GRAM" | "GRAMS" | "G"
                      | "KG" | "KILOGRAM"
                      | "ML" | "MILLILITER"
                      | "LITER" | "LITERS" | "L"
                      | "PIECE" | "PIECES"
                      | "PINCH" | "PINCHES" ;

(* Time units *)
time_unit           ::= "SECONDS" | "SECOND" | "SEC"
                      | "MINUTES" | "MINUTE" | "MIN"
                      | "HOURS" | "HOUR" | "HR" ;

(* Quantity and duration expressions *)
quantity            ::= number ;
duration            ::= number ;
number              ::= integer | float ;
integer             ::= digit { digit } ;
float               ::= digit { digit } "." digit { digit } ;
digit               ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
identifier          ::= letter { letter | digit | "_" } ;
letter              ::= "A" .. "Z" | "a" .. "z" ;
```

---

## 4. Syntax Constraints & Operator Precedence
1. **Mandatory Header**: Every recipe file must open with `RECIPE <dish>;`. Missing headers raise `ERR_MISSING_RECIPE_HEADER`.
2. **Terminal Semicolons**: Every statement must conclude with `;`. Missing semicolons trigger parser synchronization (`ERR_MISSING_SEMICOLON`).
3. **Parentheses Matching**: Parameterized statements (`ADD`, `MIX`, `CHOP`, etc.) require balanced `(` and `)`.
4. **Mandatory Finalizer**: The program must conclude with `SERVE;`. Any instruction placed after `SERVE;` is illegal and rejected with `ERR_STATEMENT_AFTER_SERVE`.
