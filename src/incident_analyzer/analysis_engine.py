
"""Build a structured, evidence-linked incident analysis."""

import re

from models.analysis import (
    IncidentAnalysis,
    KnowledgeArticle,
    RootCause,
    Workaround,
)
from models.incident import Incident

from incident_analyzer.kb_retriever import (
    retrieve_knowledge_articles,
)


def _extract_section(content: str, heading: str) -> list[str]:
    """Extract bullet points from a Markdown section."""
    pattern = (
        rf"(?ims)^##\s+{re.escape(heading)}\s*$"
        rf"(.*?)(?=^##\s+|\Z)"
    )
    match = re.search(pattern, content)

    if not match:
        return []

    return [
        item.strip()
        for item in re.findall(
            r"(?m)^\s*[-*]\s+(.+?)\s*$",
            match.group(1),
        )
        if item.strip()
    ]


def analyze_incident(
    incident: Incident,
    top_k: int = 5,
) -> IncidentAnalysis:
    """
    Produce a preliminary analysis using keyword-matched KB articles.

    Root causes are presented as hypotheses, not confirmed diagnoses.
    """
    articles = retrieve_knowledge_articles(
        incident=incident,
        top_k=top_k,
    )

    root_causes: list[RootCause] = []
    workarounds: list[Workaround] = []
    limitations: list[str] = []

    if not articles:
        limitations.append(
            "No relevant knowledge-base articles were found. "
            "Add verified articles or investigate manually."
        )

    for article in articles:
        documented_causes = (
            _extract_section(article.content, "Possible Root Causes")
            or _extract_section(article.content, "Root Causes")
        )

        for cause in documented_causes:
            root_causes.append(
                RootCause(
                    description=cause,
                    confidence=0.3,
                    supporting_evidence=[
                        f"Incident matched KB article: {article.title}"
                    ],
                    related_articles=[article.article_id],
                )
            )

        steps = (
            _extract_section(article.content, "Suggested Workaround")
            or _extract_section(article.content, "Workaround")
        )

        if steps:
            workarounds.append(
                Workaround(
                    description=(
                        f"Suggested actions from {article.title}; "
                        "verify applicability before execution."
                    ),
                    steps=steps,
                    source_article_ids=[article.article_id],
                    requires_approval=True,
                )
            )

    if articles and not root_causes:
        limitations.append(
            "Relevant articles were found, but no recognized root-cause "
            "section was available in their Markdown content."
        )

    if articles and not workarounds:
        limitations.append(
            "No recognized workaround section was found in the "
            "retrieved articles."
        )

    return IncidentAnalysis(
        incident_id=incident.incident_id,
        summary=(
            f"Preliminary analysis of incident {incident.incident_id}: "
            f"{len(articles)} relevant KB article(s) retrieved."
        ),
        probable_root_causes=root_causes,
        relevant_articles=articles,
        proposed_workarounds=workarounds,
        limitations=limitations,
    )
