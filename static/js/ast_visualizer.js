/**
 * Digital Cookbook — Abstract Syntax Tree (AST) Interactive Visualizer
 * Renders nested collapsible tree nodes with typed chips and details inspection.
 */

class ASTVisualizer {
    constructor(containerElement) {
        this.container = containerElement;
    }

    render(astData) {
        if (!astData) {
            this.container.innerHTML = '<div class="empty-state">No Abstract Syntax Tree available.</div>';
            return;
        }

        this.container.innerHTML = "";
        const rootElement = this.createNodeElement(astData, true);
        this.container.appendChild(rootElement);
    }

    createNodeElement(node, isRoot = false) {
        const nodeWrapper = document.createElement("div");
        nodeWrapper.className = "tree-node";

        const content = document.createElement("div");
        content.className = "tree-node-content";

        const hasChildren = node.children && node.children.length > 0;

        // Expander arrow (+/-)
        const expander = document.createElement("span");
        expander.className = "node-expander";
        expander.textContent = hasChildren ? "▼" : "•";
        content.appendChild(expander);

        // Type badge chip
        const typeChip = document.createElement("span");
        typeChip.className = `node-type-chip ${node.node_type || 'Generic'}`;
        typeChip.textContent = node.node_type || "Node";
        content.appendChild(typeChip);

        // Title / description
        const titleSpan = document.createElement("span");
        titleSpan.className = "node-title";
        titleSpan.textContent = node.title || node.node_type || "";
        content.appendChild(titleSpan);

        // Coordinates
        if (node.line) {
            const locSpan = document.createElement("span");
            locSpan.className = "node-loc";
            locSpan.textContent = `[L${node.line}:C${node.column}]`;
            content.appendChild(locSpan);
        }

        nodeWrapper.appendChild(content);

        // Render children
        if (hasChildren) {
            const childrenWrapper = document.createElement("div");
            childrenWrapper.className = "tree-children";

            node.children.forEach(child => {
                childrenWrapper.appendChild(this.createNodeElement(child));
            });

            nodeWrapper.appendChild(childrenWrapper);

            // Toggle collapse/expand on click
            content.addEventListener("click", () => {
                const isCollapsed = childrenWrapper.classList.toggle("collapsed");
                expander.textContent = isCollapsed ? "▶" : "▼";
            });
        }

        return nodeWrapper;
    }

    expandAll() {
        const childrenDivs = this.container.querySelectorAll(".tree-children");
        childrenDivs.forEach(div => div.classList.remove("collapsed"));
        const expanders = this.container.querySelectorAll(".node-expander");
        expanders.forEach(exp => {
            if (exp.textContent === "▶") exp.textContent = "▼";
        });
    }

    collapseAll() {
        const childrenDivs = this.container.querySelectorAll(".tree-children");
        childrenDivs.forEach(div => div.classList.add("collapsed"));
        const expanders = this.container.querySelectorAll(".node-expander");
        expanders.forEach(exp => {
            if (exp.textContent === "▼") exp.textContent = "▶";
        });
    }
}

window.ASTVisualizer = ASTVisualizer;
