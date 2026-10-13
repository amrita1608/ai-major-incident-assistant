"""Tests for knowledge-base article retrieval."""

from incident_analyzer.kb_retriever import retrieve_knowledge_articles
from models.incident import Incident


def make_incident(
    summary: str = "Database connection pool exhausted",
) -> Incident:
    """Create a sample incident."""
    return Incident(
        incident_id="INC-KB-001",
        summary=summary,
        impact="Some application requests are failing",
        affected_service="Checkout API",
        environment="test",
        alerts=[],
        log_snippets=[],
    )


def test_retriever_finds_relevant_database_article():
    """A database connection incident should find the matching article."""
    results = retrieve_knowledge_articles(make_incident())

    article_ids = [article.article_id for article in results]
    article_titles = [article.title for article in results]

    assert len(results) > 0
    assert "KB-DB-001" in article_ids or any(
        "database" in title.lower()
        or "connection" in title.lower()
        for title in article_titles
    )


def test_retriever_returns_knowledge_article_objects():
    """Retrieved results should have the expected article fields."""
    results = retrieve_knowledge_articles(make_incident())

    if results:
        article = results[0]

        assert article.article_id
        assert article.title
        assert article.content
        assert article.source


def test_retriever_respects_top_k():
    """The number of results should not exceed top_k."""
    results = retrieve_knowledge_articles(
        make_incident(),
        top_k=1,
    )

    assert len(results) <= 1


def test_retriever_handles_unrelated_incident():
    """An unrelated incident should not match a database article."""
    incident = make_incident(
        summary="A garden sprinkler has stopped working"
    )

    results = retrieve_knowledge_articles(incident)

    unrelated_database_articles = [
        article
        for article in results
        if "database" in article.title.lower()
        or "connection" in article.title.lower()
    ]

    assert unrelated_database_articles == []