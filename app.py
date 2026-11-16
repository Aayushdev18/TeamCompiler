"""Digital Cookbook — Flask Web Application and REST API.

Provides backend API endpoints for compilation, example catalog retrieval,
domain vocabulary introspection, and health monitoring.
"""

import os
import glob
from typing import Dict, Any, List
from flask import Flask, request, jsonify, render_template

from compiler.pipeline import CompilationPipeline
from compiler.language_spec import (
    DISHES,
    INGREDIENTS,
    VOLUME_TO_ML,
    MASS_TO_GRAM,
    TIME_TO_SECONDS,
    OPERATION_TIME_LIMITS,
)

app = Flask(__name__, static_folder="static", template_folder="templates")
MAX_SOURCE_LENGTH = 500_000  # 500 KB maximum source size


def load_example_files() -> List[Dict[str, Any]]:
    """Scan and load all built-in valid and invalid example recipes."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    examples_dir = os.path.join(base_dir, "examples")
    result: List[Dict[str, Any]] = []

    # Valid examples
    for path in sorted(glob.glob(os.path.join(examples_dir, "valid", "*.cook"))):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        name = filename.replace(".cook", "").replace("_", " ").title()
        result.append({
            "id": filename,
            "filename": filename,
            "title": name,
            "category": "Valid Recipes",
            "is_valid": True,
            "code": content,
        })

    # Invalid examples
    for path in sorted(glob.glob(os.path.join(examples_dir, "invalid", "*.cook"))):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        name = filename.replace(".cook", "").replace("_", " ").title()
        result.append({
            "id": filename,
            "filename": filename,
            "title": name,
            "category": "Error Diagnostics",
            "is_valid": False,
            "code": content,
        })

    return result


@app.route("/", methods=["GET"])
def index():
    """Serve the single-page compiler web interface."""
    return render_template("index.html")


@app.route("/api/compile", methods=["POST"])
def compile_code():
    """POST /api/compile: Run full 6-phase compiler pipeline on source program."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be valid application/json with a 'source' string field.",
        }), 400

    data = request.get_json()
    source = data.get("source", "")

    if not isinstance(source, str):
        return jsonify({
            "success": False,
            "error": "'source' field must be a string.",
        }), 400

    if len(source) > MAX_SOURCE_LENGTH:
        return jsonify({
            "success": False,
            "error": f"Source code length exceeds limit of {MAX_SOURCE_LENGTH} characters.",
        }), 413

    # Run genuine compiler pipeline
    pipeline = CompilationPipeline(source)
    compilation_result = pipeline.compile()

    return jsonify(compilation_result), 200


@app.route("/api/examples", methods=["GET"])
def get_examples():
    """GET /api/examples: Retrieve all built-in culinary DSL examples."""
    examples = load_example_files()
    return jsonify({
        "success": True,
        "count": len(examples),
        "examples": examples,
    }), 200


@app.route("/api/vocabulary", methods=["GET"])
def get_vocabulary():
    """GET /api/vocabulary: Inspect language specifications, dishes, units, and grammar."""
    dishes_data = {
        k: {
            "name": v.name,
            "display_name": v.display_name,
            "description": v.description,
            "required_ingredients": sorted(list(v.required_ingredients)),
            "optional_ingredients": sorted(list(v.optional_ingredients)),
            "allowed_operations": sorted(list(v.allowed_operations)),
            "forbidden_operations": sorted(list(v.forbidden_operations)),
        }
        for k, v in DISHES.items()
    }

    ingredients_data = {
        k: {
            "name": v.name,
            "category": v.category,
            "allowed_units": sorted(list(v.allowed_units)),
            "base_unit": v.base_unit,
        }
        for k, v in INGREDIENTS.items()
    }

    return jsonify({
        "success": True,
        "dishes": dishes_data,
        "ingredients": ingredients_data,
        "units": {
            "volume_ml": VOLUME_TO_ML,
            "mass_gram": MASS_TO_GRAM,
            "time_seconds": TIME_TO_SECONDS,
        },
        "operations": list(OPERATION_TIME_LIMITS.keys()),
    }), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    """GET /api/health: Operational health monitor."""
    return jsonify({
        "status": "healthy",
        "service": "Digital Cookbook Compiler",
        "version": "1.0.0",
        "engine": "Python Recursive-Descent Architecture",
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
