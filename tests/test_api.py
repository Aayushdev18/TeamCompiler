"""Integration Tests for Flask Web API."""

import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "Digital Cookbook" in data["service"]


def test_examples_endpoint(client):
    res = client.get("/api/examples")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] >= 16
    example_names = [e["filename"] for e in data["examples"]]
    assert "01_pancake.cook" in example_names
    assert "07_optimization_demo.cook" in example_names


def test_vocabulary_endpoint(client):
    res = client.get("/api/vocabulary")
    assert res.status_code == 200
    data = res.get_json()
    assert "PANCAKE" in data["dishes"]
    assert "FLOUR" in data["ingredients"]


def test_compile_endpoint_valid_code(client):
    payload = {
        "source": """
        RECIPE PANCAKE;
        ADD(2, CUP, FLOUR);
        ADD(1, PIECE, EGG);
        ADD(1, CUP, MILK);
        MIX(3, MINUTES);
        FRY(5, MINUTES);
        SERVE;
        """
    }
    res = client.post("/api/compile", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["phases"]) == 6
    assert data["phases"][0]["status"] == "success"
    assert data["phases"][5]["status"] == "success"


def test_compile_endpoint_invalid_code(client):
    payload = {
        "source": "RECIPE PANCAKE; ADD(2, CUP, FLOUR) SERVE;"
    }
    res = client.post("/api/compile", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is False
    assert data["phases"][1]["status"] == "error"
    assert data["phases"][2]["status"] == "skipped"


def test_compile_endpoint_bad_requests(client):
    # Non-JSON
    res = client.post("/api/compile", data="raw string")
    assert res.status_code == 400

    # Non-string source
    res = client.post("/api/compile", json={"source": 12345})
    assert res.status_code == 400
