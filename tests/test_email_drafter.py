"""Tests for stakeholder email draft generation."""

from incident_analyzer.analysis_engine import analyze_incident
from incident_analyzer.email_drafter import draft_stakeholder_email
from incident_analyzer.incident_loader import load_incident


def test_email_draft_contains_incident_details():
    """The email should identify the incident and its reported impact."""
    incident = load_incident("data/sample_incident.json")
    analysis = analyze_incident(incident)

    email = draft_stakeholder_email(incident, analysis)

    assert f"Subject: [{incident.severity}] [Major Incident] {incident.incident_id}" in email
    assert incident.summary in email
    assert "Investigation status:" in email
    assert "Next steps:" in email
    assert "14:30 IST" in email


def test_email_draft_includes_analysis_findings():
    """Root-cause hypotheses and articles should appear when available."""
    incident = load_incident("data/sample_incident.json")
    analysis = analyze_incident(incident)

    email = draft_stakeholder_email(incident, analysis)

    for cause in analysis.probable_root_causes:
        assert cause.description in email

    for article in analysis.relevant_articles:
        assert article.title in email


def test_email_draft_preserves_workaround_approval():
    """Workaround approval requirements should be communicated."""
    incident = load_incident("data/sample_incident.json")
    analysis = analyze_incident(incident)

    email = draft_stakeholder_email(incident, analysis)

    for workaround in analysis.proposed_workarounds:
        if workaround.requires_approval:
            assert "Approval required before execution." in email
        for step in workaround.steps:
            assert step in email


def test_email_draft_does_not_send_email():
    """The function should return draft text rather than send a message."""
    incident = load_incident("data/sample_incident.json")
    analysis = analyze_incident(incident)

    email = draft_stakeholder_email(incident, analysis)

    assert isinstance(email, str)
    assert email.endswith("\n")
    assert "Draft for review:" in email

def test_email_draft_includes_custom_incident_metadata():
    """Custom severity, owner, and update time should appear in the draft."""
    incident = load_incident("data/sample_incident.json")
    incident.severity = "SEV-1"
    incident.incident_owner = "Major Incident Team"
    incident.next_update_time = "14:30 IST"

    analysis = analyze_incident(incident)
    email = draft_stakeholder_email(incident, analysis)

    assert "Subject: [SEV-1] [Major Incident]" in email
    assert "Severity: SEV-1" in email
    assert "Incident owner: Major Incident Team" in email
    assert "We will provide the next update at 14:30 IST." in email
    assert "Regards,\nMajor Incident Team" in email


def test_email_draft_uses_defaults_when_metadata_is_missing():
    """Missing optional metadata should retain safe fallback text."""
    incident = load_incident("data/sample_incident.json")
    incident.severity = None
    incident.incident_owner = None
    incident.next_update_time = None

    analysis = analyze_incident(incident)
    email = draft_stakeholder_email(incident, analysis)

    assert "Subject: [Major Incident]" in email
    assert "[insert next update time]" in email
    assert "[Incident Manager / Response Team]" in email