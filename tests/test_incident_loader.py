"""Tests for loading incident data from JSON files."""

import json

import pytest

from incident_analyzer.incident_loader import load_incident


def test_load_incident_from_valid_json(tmp_path):
    """A valid incident JSON file should load successfully."""
    incident_data = {
        "incident_id": "INC-TEST-002",
        "summary": "Payment API is returning database connection errors",
        "impact": "Some payment requests are failing",
        "affected_service": "Payment API",
        "environment": "test",
        "alerts": [],
        "log_snippets": [],
    }

    incident_file = tmp_path / "incident.json"
    incident_file.write_text(
        json.dumps(incident_data),
        encoding="utf-8",
    )

    incident = load_incident(incident_file)

    assert incident.incident_id == "INC-TEST-002"
    assert incident.summary == (
        "Payment API is returning database connection errors"
    )
    assert incident.affected_service == "Payment API"
    assert incident.alerts == []
    assert incident.log_snippets == []


def test_load_incident_rejects_invalid_json(tmp_path):
    """Malformed JSON should raise a decoding error."""
    incident_file = tmp_path / "invalid.json"
    incident_file.write_text(
        '{"incident_id": "INC-TEST-003",',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_incident(incident_file)


def test_load_incident_rejects_missing_required_fields(tmp_path):
    """Missing required fields should fail validation."""
    incident_data = {
        "incident_id": "INC-TEST-004",
    }

    incident_file = tmp_path / "incomplete.json"
    incident_file.write_text(
        json.dumps(incident_data),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Incident validation failed"):
        load_incident(incident_file)


def test_load_incident_rejects_missing_file(tmp_path):
    """A nonexistent file should raise FileNotFoundError."""
    incident_file = tmp_path / "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        load_incident(incident_file)