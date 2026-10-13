"""Tests for the incident analysis engine."""

from incident_analyzer import analysis_engine
from models.analysis import KnowledgeArticle
from models.incident import Incident


def make_incident() -> Incident:
    """Create a sample incident for testing."""
    return Incident(
        incident_id="INC-TEST-001",
        summary="Checkout API database connection pool exhausted",
        impact="Some checkout requests are failing",
        affected_service="Checkout API",
        environment="test",
        alerts=[],
        log_snippets=[],
    )


def make_article() -> KnowledgeArticle:
    """Create a sample knowledge-base article."""
    content = """# Database Connection Troubleshooting

## Possible Root Causes
- The application connection pool has reached its maximum size.
- Database CPU utilization is unusually high.

## Suggested Workaround
1. Check active database connections.
2. Review application logs.
3. Follow the approved incident runbook.
"""

    return KnowledgeArticle(
        article_id="KB-TEST-001",
        title="Database Connection Troubleshooting",
        content=content,
        symptoms=["connection pool exhausted"],
        source="test_article.md",
    )


def test_extract_section_supports_numbered_steps():
    """Verify that numbered Markdown steps are extracted."""
    content = """## Suggested Workaround
1. Check the connection pool.
2. Review application logs.

## Safety Notes
- Follow the approved runbook.
"""

    result = analysis_engine._extract_section(
        content,
        "Suggested Workaround",
    )

    assert result == [
        "Check the connection pool.",
        "Review application logs.",
    ]


def test_analysis_includes_causes_and_workarounds(monkeypatch):
    """Verify that analysis includes findings from retrieved articles."""
    article = make_article()

    monkeypatch.setattr(
        analysis_engine,
        "retrieve_knowledge_articles",
        lambda incident, top_k=5: [article],
    )

    result = analysis_engine.analyze_incident(make_incident())

    assert result.incident_id == "INC-TEST-001"
    assert len(result.relevant_articles) == 1
    assert len(result.probable_root_causes) == 2
    assert len(result.proposed_workarounds) == 1

    cause = result.probable_root_causes[0]
    assert cause.related_articles == ["KB-TEST-001"]
    assert 0.0 <= cause.confidence <= 1.0

    workaround = result.proposed_workarounds[0]
    assert len(workaround.steps) == 3
    assert workaround.requires_approval is True


def test_analysis_handles_no_matching_articles(monkeypatch):
    """Verify that missing knowledge articles are reported."""
    monkeypatch.setattr(
        analysis_engine,
        "retrieve_knowledge_articles",
        lambda incident, top_k=5: [],
    )

    result = analysis_engine.analyze_incident(make_incident())

    assert result.incident_id == "INC-TEST-001"
    assert result.relevant_articles == []
    assert result.probable_root_causes == []
    assert result.proposed_workarounds == []

    assert any(
        "No relevant knowledge-base articles" in limitation
        for limitation in result.limitations
    )