"""End-to-end tests for the incident analysis workflow."""

import json
from pathlib import Path

from incident_analyzer.analysis_engine import analyze_incident
from incident_analyzer.incident_loader import load_incident
from models.analysis import IncidentAnalysis


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_INCIDENT = PROJECT_ROOT / "data" / "sample_incident.json"


def test_sample_incident_loads_and_produces_analysis():
    """The sample incident should produce a valid structured analysis."""
    incident = load_incident(SAMPLE_INCIDENT)

    analysis = analyze_incident(incident)

    assert isinstance(analysis, IncidentAnalysis)
    assert analysis.incident_id == incident.incident_id
    assert analysis.summary
    assert isinstance(analysis.probable_root_causes, list)
    assert isinstance(analysis.relevant_articles, list)
    assert isinstance(analysis.proposed_workarounds, list)
    assert isinstance(analysis.limitations, list)


def test_analysis_can_be_serialized_to_json():
    """The analysis result should serialize into valid JSON."""
    incident = load_incident(SAMPLE_INCIDENT)

    analysis = analyze_incident(incident)

    serialized = analysis.model_dump_json(indent=2)
    result = json.loads(serialized)

    assert result["incident_id"] == incident.incident_id
    assert isinstance(result["probable_root_causes"], list)
    assert isinstance(result["relevant_articles"], list)
    assert isinstance(result["proposed_workarounds"], list)
    assert isinstance(result["limitations"], list)


def test_analysis_preserves_incident_evidence():
    """Retrieved findings should reference articles and evidence."""
    incident = load_incident(SAMPLE_INCIDENT)

    analysis = analyze_incident(incident)

    for cause in analysis.probable_root_causes:
        assert cause.description
        assert isinstance(cause.supporting_evidence, list)
        assert isinstance(cause.related_articles, list)

    for article in analysis.relevant_articles:
        assert article.article_id
        assert article.title
        assert article.content
        assert article.source

    for workaround in analysis.proposed_workarounds:
        assert workaround.description
        assert workaround.steps
        assert workaround.source_article_ids
        assert workaround.requires_approval is True
