"""Tests for the incident analyzer command-line interface."""

import json

from incident_analyzer import main as main_module


def test_main_prints_analysis_json(monkeypatch, capsys):
    """The CLI should print valid JSON when no output file is specified."""
    monkeypatch.setattr(
        "sys.argv",
        ["incident-analyzer", "--input", "data/sample_incident.json"],
    )

    exit_code = main_module.main()

    captured = capsys.readouterr()

    assert exit_code == 0

    result = json.loads(captured.out)
    assert result["incident_id"]
    assert "probable_root_causes" in result
    assert "relevant_articles" in result
    assert "proposed_workarounds" in result
    assert "limitations" in result


def test_main_saves_analysis_to_output_file(
    monkeypatch, capsys, tmp_path
):
    """The CLI should save valid JSON when --output is specified."""
    output_file = tmp_path / "reports" / "incident_analysis.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "incident-analyzer",
            "--input",
            "data/sample_incident.json",
            "--output",
            str(output_file),
        ],
    )

    exit_code = main_module.main()

    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_file.exists()
    assert "Analysis saved to:" in captured.out

    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert result["incident_id"]
    assert "probable_root_causes" in result


def test_main_returns_error_for_missing_input(
    monkeypatch, capsys, tmp_path
):
    """The CLI should return an error for a missing input file."""
    missing_file = tmp_path / "does_not_exist.json"

    monkeypatch.setattr(
        "sys.argv",
        ["incident-analyzer", "--input", str(missing_file)],
    )

    exit_code = main_module.main()

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error:" in captured.err

def test_main_saves_stakeholder_email(
    monkeypatch, capsys, tmp_path
):
    """The CLI should save the stakeholder email when requested."""
    email_file = tmp_path / "reports" / "stakeholder_email.txt"

    monkeypatch.setattr(
        "sys.argv",
        [
            "incident-analyzer",
            "--input",
            "data/sample_incident.json",
            "--email-output",
            str(email_file),
        ],
    )

    exit_code = main_module.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert email_file.exists()
    assert "Stakeholder email draft saved to:" in captured.out

    email = email_file.read_text(encoding="utf-8")
    assert "Subject:" in email
    assert "INC-2026-1042" in email


def test_main_returns_error_for_invalid_input_json(
    monkeypatch, capsys, tmp_path
):
    """The CLI should report an error when the input JSON is invalid."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["incident-analyzer", "--input", str(invalid_file)],
    )

    exit_code = main_module.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error:" in captured.err


def test_main_returns_error_when_output_cannot_be_written(
    monkeypatch, capsys, tmp_path
):
    """The CLI should report an error if the output path is a directory."""
    output_dir = tmp_path / "output.json"
    output_dir.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        [
            "incident-analyzer",
            "--input",
            "data/sample_incident.json",
            "--output",
            str(output_dir),
        ],
    )

    exit_code = main_module.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "File operation failed:" in captured.err
