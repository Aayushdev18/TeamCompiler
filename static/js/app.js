/**
 * Digital Cookbook — Frontend Application Controller
 * Handles UI interactions, API communications, tab navigation, and phase data binding.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const editor = document.getElementById("code-editor");
    const lineNumbers = document.getElementById("line-numbers");
    const compileBtn = document.getElementById("compile-btn");
    const resetBtn = document.getElementById("reset-btn");
    const clearBtn = document.getElementById("clear-btn");
    const copySourceBtn = document.getElementById("copy-source-btn");
    const exampleSelect = document.getElementById("example-select");
    const globalStatus = document.getElementById("global-status");
    const statusText = document.getElementById("status-text");
    const compileMetrics = document.getElementById("compile-metrics");
    const metricTime = document.getElementById("metric-time");
    const themeBtn = document.getElementById("theme-btn");
    const themeIcon = document.getElementById("theme-icon");
    const docsBtn = document.getElementById("docs-btn");
    const docsModal = document.getElementById("docs-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");

    // Phase Tab Buttons & Panes
    const phaseTabs = document.querySelectorAll(".phase-tab");
    const phasePanes = document.querySelectorAll(".phase-pane");

    // Phase 1 Elements
    const tokensTable = document.getElementById("tokens-table").querySelector("tbody");
    const tokenFilter = document.getElementById("token-filter");
    const tokenSearch = document.getElementById("token-search");
    const tokenCountPill = document.getElementById("token-count-pill");

    // Phase 2 Elements
    const astTreeCanvas = document.getElementById("ast-tree-view");
    const astJsonCanvas = document.getElementById("ast-json-view");
    const astJsonCode = document.getElementById("ast-json-code");
    const astTreeViewBtn = document.getElementById("ast-tree-view-btn");
    const astJsonViewBtn = document.getElementById("ast-json-view-btn");
    const expandAllAstBtn = document.getElementById("expand-all-ast-btn");
    const collapseAllAstBtn = document.getElementById("collapse-all-ast-btn");

    // Phase 3 Elements
    const symbolsTable = document.getElementById("symbols-table").querySelector("tbody");
    const symbolCountPill = document.getElementById("symbol-count-pill");
    const checklistContainer = document.getElementById("checklist-container");

    // Phase 4 Elements
    const irListing = document.getElementById("ir-listing");
    const copyIrBtn = document.getElementById("copy-ir-btn");

    // Phase 5 Elements
    const optBeforeNum = document.getElementById("opt-before-num");
    const optAfterNum = document.getElementById("opt-after-num");
    const optReductionPct = document.getElementById("opt-reduction-pct");
    const irOriginalDiff = document.getElementById("ir-original-diff");
    const irOptimizedDiff = document.getElementById("ir-optimized-diff");
    const transformationsList = document.getElementById("transformations-list");

    // Phase 6 Elements
    const vkmAssemblyCode = document.getElementById("vkm-assembly-code");
    const vkmCyclePill = document.getElementById("vkm-cycle-pill");
    const copyVkmBtn = document.getElementById("copy-vkm-btn");

    // Diagnostics Elements
    const diagCount = document.getElementById("diag-count");
    const diagContent = document.getElementById("diag-content");

    // State
    let currentTokens = [];
    let astVisualizerInstance = new ASTVisualizer(astTreeCanvas);
    let lastCompilationResult = null;
    let builtInExamples = [];

    // -------------------------------------------------------------------------
    // 1. Line Numbers & Editor Synchronization
    // -------------------------------------------------------------------------
    function updateLineNumbers() {
        const lines = editor.value.split("\n");
        lineNumbers.textContent = Array.from({ length: lines.length }, (_, i) => i + 1).join("\n");
    }

    editor.addEventListener("input", updateLineNumbers);
    editor.addEventListener("scroll", () => {
        lineNumbers.scrollTop = editor.scrollTop;
    });

    // Keyboard Shortcut: Ctrl/Cmd + Enter to Compile
    editor.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            runCompilation();
        }
        // Handle Tab key for indentation
        if (e.key === "Tab") {
            e.preventDefault();
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            editor.value = editor.value.substring(0, start) + "    " + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + 4;
            updateLineNumbers();
        }
    });

    // -------------------------------------------------------------------------
    // 2. Tab Navigation
    // -------------------------------------------------------------------------
    phaseTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetPhase = tab.getAttribute("data-phase");
            phaseTabs.forEach(t => t.classList.remove("active"));
            phasePanes.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            const targetPane = document.getElementById(`pane-${targetPhase}`);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    // -------------------------------------------------------------------------
    // 3. Examples Loading
    // -------------------------------------------------------------------------
    async function loadExamplesCatalog() {
        try {
            const res = await fetch("/api/examples");
            const data = await res.json();
            if (data.success && data.examples) {
                builtInExamples = data.examples;
                exampleSelect.innerHTML = '<option value="" disabled selected>Select an Example Recipe...</option>';

                const validGroup = document.createElement("optgroup");
                validGroup.label = "Valid Cookbook DSL Recipes";

                const invalidGroup = document.createElement("optgroup");
                invalidGroup.label = "Error Diagnostics & Edge Cases";

                builtInExamples.forEach(ex => {
                    const opt = document.createElement("option");
                    opt.value = ex.id;
                    opt.textContent = `${ex.is_valid ? "✓" : "✗"} ${ex.title}`;
                    if (ex.is_valid) {
                        validGroup.appendChild(opt);
                    } else {
                        invalidGroup.appendChild(opt);
                    }
                });

                exampleSelect.appendChild(validGroup);
                exampleSelect.appendChild(invalidGroup);

                // Load default example (01_pancake.cook)
                const defaultEx = builtInExamples.find(e => e.id.includes("01_pancake"));
                if (defaultEx) {
                    editor.value = defaultEx.code;
                    updateLineNumbers();
                    runCompilation();
                }
            }
        } catch (err) {
            console.error("Failed to load examples catalog:", err);
        }
    }

    exampleSelect.addEventListener("change", () => {
        const selectedId = exampleSelect.value;
        const ex = builtInExamples.find(e => e.id === selectedId);
        if (ex) {
            editor.value = ex.code;
            updateLineNumbers();
            runCompilation();
        }
    });

    // -------------------------------------------------------------------------
    // 4. Compilation Pipeline Execution
    // -------------------------------------------------------------------------
    async function runCompilation() {
        const sourceCode = editor.value;

        // UI state update
        globalStatus.className = "status-indicator ready";
        statusText.textContent = "Compiling...";
        compileBtn.disabled = true;

        try {
            const res = await fetch("/api/compile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source: sourceCode }),
            });

            const result = await res.json();
            lastCompilationResult = result;
            renderCompilationResults(result);

        } catch (err) {
            console.error("Compilation request error:", err);
            statusText.textContent = "Network / Internal Error";
            globalStatus.className = "status-indicator error";
        } finally {
            compileBtn.disabled = false;
        }
    }

    compileBtn.addEventListener("click", runCompilation);

    // -------------------------------------------------------------------------
    // 5. Render Compilation Results Across All 6 Phases
    // -------------------------------------------------------------------------
    function renderCompilationResults(result) {
        // Global status & timing
        if (result.success) {
            globalStatus.className = "status-indicator success";
            statusText.textContent = "Compilation Successful";
        } else {
            globalStatus.className = "status-indicator error";
            statusText.textContent = "Compilation Failed";
        }

        compileMetrics.style.display = "inline-flex";
        metricTime.textContent = `${result.compilation_time_ms} ms`;

        // Update Phase Badges
        result.phases.forEach(p => {
            const badge = document.getElementById(`badge-${p.id}`);
            if (badge) {
                badge.className = `phase-badge badge-${p.status}`;
                badge.textContent = p.status;
            }
        });

        // Diagnostics
        renderDiagnostics(result.diagnostics, result.summary);

        // Bind Phase 1: Lexer
        const lexerPhase = result.phases.find(p => p.id === "lexer");
        if (lexerPhase && lexerPhase.output && lexerPhase.output.tokens) {
            currentTokens = lexerPhase.output.tokens;
            renderTokensTable(currentTokens);
        }

        // Bind Phase 2: Parser & AST
        const parserPhase = result.phases.find(p => p.id === "parser");
        if (parserPhase && parserPhase.output && parserPhase.output.ast) {
            astVisualizerInstance.render(parserPhase.output.ast);
            astJsonCode.textContent = JSON.stringify(parserPhase.output.ast, null, 2);
        } else {
            astTreeCanvas.innerHTML = '<div class="empty-state">Parser did not construct AST due to earlier phase errors.</div>';
            astJsonCode.textContent = "// No AST available";
        }

        // Bind Phase 3: Semantic & Symbol Table
        const semanticPhase = result.phases.find(p => p.id === "semantic");
        if (semanticPhase && semanticPhase.output) {
            renderSymbolTable(semanticPhase.output.symbol_table || []);
            renderChecklist(semanticPhase.output.checklist || []);
        }

        // Bind Phase 4: Intermediate Representation (IR)
        const irPhase = result.phases.find(p => p.id === "ir");
        if (irPhase && irPhase.output && irPhase.output.instructions) {
            renderIRListing(irPhase.output.instructions);
        } else {
            irListing.innerHTML = '<div class="empty-state">IR generation skipped.</div>';
        }

        // Bind Phase 5: Optimization
        const optPhase = result.phases.find(p => p.id === "optimizer");
        if (optPhase && optPhase.output && optPhase.output.metrics) {
            renderOptimization(optPhase.output);
        } else {
            irOriginalDiff.innerHTML = '<div class="empty-state">Optimization skipped.</div>';
            irOptimizedDiff.innerHTML = '<div class="empty-state">Optimization skipped.</div>';
            transformationsList.innerHTML = '<div class="empty-state">No optimization transformations.</div>';
            optBeforeNum.textContent = "0";
            optAfterNum.textContent = "0";
            optReductionPct.textContent = "0%";
        }

        // Bind Phase 6: Target Code Generation
        const codegenPhase = result.phases.find(p => p.id === "codegen");
        if (codegenPhase && codegenPhase.output && codegenPhase.output.assembly_text) {
            vkmAssemblyCode.textContent = codegenPhase.output.assembly_text;
            vkmCyclePill.textContent = `Total Cycles: ${codegenPhase.output.total_cycle_cost || 0}`;
        } else {
            vkmAssemblyCode.textContent = "; Target Code Generation skipped due to upstream errors.";
            vkmCyclePill.textContent = "Total Cycles: 0";
        }

        // Automatically switch to the failed tab if compilation failed
        if (!result.success) {
            const failedPhase = result.phases.find(p => p.status === "error");
            if (failedPhase) {
                const targetTab = document.querySelector(`.phase-tab[data-phase="${failedPhase.id}"]`);
                if (targetTab) targetTab.click();
            }
        }
    }

    // -------------------------------------------------------------------------
    // Diagnostics Renderer
    // -------------------------------------------------------------------------
    function renderDiagnostics(diagnostics, summary) {
        if (!diagnostics || diagnostics.length === 0) {
            diagCount.textContent = "0 issues";
            diagContent.innerHTML = '<div class="empty-diag" style="color: var(--accent-primary);">✓ All compiler checks passed without diagnostics.</div>';
            return;
        }

        diagCount.textContent = `${summary.total_errors} errors, ${summary.total_warnings} warnings`;
        diagContent.innerHTML = "";

        diagnostics.forEach(diag => {
            const item = document.createElement("div");
            item.className = "diag-item";

            const badge = document.createElement("span");
            badge.className = `diag-badge ${diag.severity}`;
            badge.textContent = `${diag.phase}: ${diag.severity}`;

            const loc = document.createElement("span");
            loc.className = "diag-loc";
            loc.textContent = `Line ${diag.line}, Col ${diag.column}`;

            const body = document.createElement("div");
            body.className = "diag-msg";
            body.innerHTML = `<div>${escapeHtml(diag.message)}</div>`;

            if (diag.suggestion) {
                const sugg = document.createElement("div");
                sugg.className = "diag-suggestion";
                sugg.textContent = `💡 Suggestion: ${diag.suggestion}`;
                body.appendChild(sugg);
            }

            item.appendChild(badge);
            item.appendChild(loc);
            item.appendChild(body);
            diagContent.appendChild(item);
        });
    }

    // -------------------------------------------------------------------------
    // Phase 1: Tokens Table
    // -------------------------------------------------------------------------
    function renderTokensTable(tokens) {
        tokensTable.innerHTML = "";
        const filterVal = tokenFilter.value;
        const query = tokenSearch.value.trim().toLowerCase();

        const filtered = tokens.filter(t => {
            if (filterVal !== "ALL" && t.category !== filterVal) return false;
            if (query && !t.lexeme.toLowerCase().includes(query) && !t.type.toLowerCase().includes(query)) return false;
            return true;
        });

        tokenCountPill.textContent = `Tokens: ${filtered.length} / ${tokens.length}`;

        if (filtered.length === 0) {
            tokensTable.innerHTML = '<tr><td colspan="6" class="table-empty">No tokens match current filter.</td></tr>';
            return;
        }

        filtered.forEach((tok, idx) => {
            const tr = document.createElement("tr");
            const catClass = tok.category.replace(/\s+/g, "-");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td><strong>${escapeHtml(tok.lexeme)}</strong></td>
                <td><code>${tok.type}</code></td>
                <td><span class="token-badge ${catClass}">${tok.category}</span></td>
                <td>${tok.line}</td>
                <td>${tok.column}</td>
            `;
            tokensTable.appendChild(tr);
        });
    }

    tokenFilter.addEventListener("change", () => renderTokensTable(currentTokens));
    tokenSearch.addEventListener("input", () => renderTokensTable(currentTokens));

    // -------------------------------------------------------------------------
    // Phase 2: AST Controls
    // -------------------------------------------------------------------------
    astTreeViewBtn.addEventListener("click", () => {
        astTreeViewBtn.classList.add("active");
        astJsonViewBtn.classList.remove("active");
        astTreeCanvas.style.display = "block";
        astJsonCanvas.style.display = "none";
    });

    astJsonViewBtn.addEventListener("click", () => {
        astJsonViewBtn.classList.add("active");
        astTreeViewBtn.classList.remove("active");
        astTreeCanvas.style.display = "none";
        astJsonCanvas.style.display = "block";
    });

    expandAllAstBtn.addEventListener("click", () => astVisualizerInstance.expandAll());
    collapseAllAstBtn.addEventListener("click", () => astVisualizerInstance.collapseAll());

    // -------------------------------------------------------------------------
    // Phase 3: Symbol Table & Checklist
    // -------------------------------------------------------------------------
    function renderSymbolTable(symbols) {
        symbolsTable.innerHTML = "";
        symbolCountPill.textContent = `Symbols: ${symbols.length}`;

        if (symbols.length === 0) {
            symbolsTable.innerHTML = '<tr><td colspan="7" class="table-empty">No symbols registered.</td></tr>';
            return;
        }

        symbols.forEach(sym => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${sym.identifier}</strong></td>
                <td>${sym.category}</td>
                <td><code>${sym.data_type}</code></td>
                <td>${sym.unit}</td>
                <td>${sym.total_quantity}</td>
                <td>${sym.occurrences}</td>
                <td>${sym.source_location}</td>
            `;
            symbolsTable.appendChild(tr);
        });
    }

    function renderChecklist(checklist) {
        checklistContainer.innerHTML = "";
        if (checklist.length === 0) {
            checklistContainer.innerHTML = '<div class="empty-state">No semantic rules evaluated.</div>';
            return;
        }

        checklist.forEach(item => {
            const card = document.createElement("div");
            card.className = "checklist-item";

            const statusIcon = document.createElement("span");
            statusIcon.className = `chk-status ${item.status}`;
            statusIcon.textContent = item.status === "passed" ? "✓" : (item.status === "failed" ? "✗" : "⚠");

            const desc = document.createElement("div");
            desc.className = "chk-desc";
            desc.textContent = item.description;

            const msg = document.createElement("div");
            msg.className = "chk-msg";
            msg.textContent = item.message;

            card.appendChild(statusIcon);
            card.appendChild(desc);
            if (item.message) card.appendChild(msg);
            checklistContainer.appendChild(card);
        });
    }

    // -------------------------------------------------------------------------
    // Phase 4: Intermediate Representation (IR)
    // -------------------------------------------------------------------------
    function renderIRListing(instructions) {
        irListing.innerHTML = "";
        instructions.forEach(inst => {
            const lineDiv = document.createElement("div");
            lineDiv.className = "ir-line";
            lineDiv.innerHTML = `
                <span class="ir-id">${inst.id}:</span>
                <span class="ir-code">${escapeHtml(inst.readable)}</span>
                <span class="ir-comment">; [Line ${inst.line}] ${escapeHtml(inst.comment)}</span>
            `;
            irListing.appendChild(lineDiv);
        });
    }

    copyIrBtn.addEventListener("click", () => {
        if (lastCompilationResult && lastCompilationResult.phases) {
            const irPhase = lastCompilationResult.phases.find(p => p.id === "ir");
            if (irPhase && irPhase.output && irPhase.output.readable_ir) {
                navigator.clipboard.writeText(irPhase.output.readable_ir);
                copyIrBtn.textContent = "✓ Copied!";
                setTimeout(() => copyIrBtn.textContent = "📋 Copy IR", 2000);
            }
        }
    });

    // -------------------------------------------------------------------------
    // Phase 5: Optimization Diff & Transformations
    // -------------------------------------------------------------------------
    function renderOptimization(optData) {
        optBeforeNum.textContent = optData.metrics.count_before;
        optAfterNum.textContent = optData.metrics.count_after;
        optReductionPct.textContent = `${optData.metrics.reduction_percentage}%`;

        // Diff views
        irOriginalDiff.innerHTML = `<pre>${escapeHtml(optData.readable_original)}</pre>`;
        irOptimizedDiff.innerHTML = `<pre>${escapeHtml(optData.readable_optimized)}</pre>`;

        // Transformations
        transformationsList.innerHTML = "";
        if (!optData.transformations || optData.transformations.length === 0) {
            transformationsList.innerHTML = '<div class="empty-state">No instructions required optimization. Source is already in canonical form.</div>';
            return;
        }

        optData.transformations.forEach(t => {
            const card = document.createElement("div");
            card.className = "trans-card";

            let diffHtml = "";
            t.original_instructions.forEach(orig => {
                diffHtml += `<div class="trans-diff-del">- ${escapeHtml(orig)}</div>`;
            });
            t.transformed_instructions.forEach(trans => {
                diffHtml += `<div class="trans-diff-add">+ ${escapeHtml(trans)}</div>`;
            });

            card.innerHTML = `
                <div class="trans-header">
                    <span>${escapeHtml(t.pass_name)}</span>
                    <span class="trans-rule">${escapeHtml(t.rule_name)}</span>
                </div>
                <div class="trans-diff">${diffHtml}</div>
                <div class="trans-reason"><strong>Reason:</strong> ${escapeHtml(t.reason)}</div>
                <div class="trans-safety"><strong>Safety Justification:</strong> ${escapeHtml(t.safety_justification)}</div>
            `;
            transformationsList.appendChild(card);
        });
    }

    // -------------------------------------------------------------------------
    // Phase 6: Target Code Copy
    // -------------------------------------------------------------------------
    copyVkmBtn.addEventListener("click", () => {
        if (lastCompilationResult && lastCompilationResult.phases) {
            const cgPhase = lastCompilationResult.phases.find(p => p.id === "codegen");
            if (cgPhase && cgPhase.output && cgPhase.output.assembly_text) {
                navigator.clipboard.writeText(cgPhase.output.assembly_text);
                copyVkmBtn.textContent = "✓ Copied!";
                setTimeout(() => copyVkmBtn.textContent = "📋 Copy Assembly", 2000);
            }
        }
    });

    // -------------------------------------------------------------------------
    // Helper Buttons (Reset, Clear, Copy Source)
    // -------------------------------------------------------------------------
    resetBtn.addEventListener("click", () => {
        const defaultEx = builtInExamples.find(e => e.id.includes("01_pancake"));
        if (defaultEx) {
            editor.value = defaultEx.code;
            updateLineNumbers();
            runCompilation();
        }
    });

    clearBtn.addEventListener("click", () => {
        editor.value = "";
        updateLineNumbers();
        runCompilation();
    });

    copySourceBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(editor.value);
        copySourceBtn.textContent = "✓ Copied!";
        setTimeout(() => copySourceBtn.textContent = "📋 Copy", 2000);
    });

    // -------------------------------------------------------------------------
    // Theme Toggle & Docs Modal
    // -------------------------------------------------------------------------
    themeBtn.addEventListener("click", () => {
        const html = document.documentElement;
        const currentTheme = html.getAttribute("data-theme") || "dark";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", newTheme);
        themeIcon.textContent = newTheme === "dark" ? "🌙" : "☀️";
        localStorage.setItem("digital_cookbook_theme", newTheme);
    });

    // Restore saved theme
    const savedTheme = localStorage.getItem("digital_cookbook_theme");
    if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
        themeIcon.textContent = savedTheme === "dark" ? "🌙" : "☀️";
    }

    docsBtn.addEventListener("click", () => {
        docsModal.style.display = "flex";
    });

    modalCloseBtn.addEventListener("click", () => {
        docsModal.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === docsModal) docsModal.style.display = "none";
    });

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initialize
    loadExamplesCatalog();
});
