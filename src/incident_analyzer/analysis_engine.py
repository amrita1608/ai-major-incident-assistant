
"""Build an evidence-linked preliminary incident analysis."""

import re

from models.analysis import (
    IncidentAnalysis,
    RootCause,
    Workaround,
)
from models.incident import Incident

from incident_analyzer.kb_retriever import (
    retrieve_knowledge_articles,
)


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are",
    "was", "were", "be", "been", "being", "to", "of",
    "in", "on", "for", "from", "by", "with", "as", "at",
    "it", "its", "this", "that", "their", "has", "have",
    "had", "not", "can", "could", "may", "might", "into",
    "after", "before", "within", "under", "between",
}


def _tokens(text: str) -> set[str]:
    """Extract normalized, meaningful words."""
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 1 and word not in STOP_WORDS
    }


def _extract_section(content: str, heading: str) -> list[str]:
    """Extract bullet points or numbered steps from a Markdown section."""
    pattern = (
        rf"(?ims)^##\s+{re.escape(heading)}\s*$"
        rf"(.*?)(?=^##\s+|\Z)"
    )
    match = re.search(pattern, content)

    if not match:
        return []

    items = re.findall(
        r"(?m)^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$",
        match.group(1),
    )
    return [item.strip() for item in items if item.strip()]


def _incident_evidence(incident: Incident) -> list[str]:
    """Collect observable incident evidence without inventing facts."""
    evidence = [f"Incident summary: {incident.summary}"]

    if incident.impact:
        evidence.append(f"Reported impact: {incident.impact}")

    if incident.affected_service:
        evidence.append(f"Affected service: {incident.affected_service}")

    if incident.environment:
        evidence.append(f"Environment: {incident.environment}")

    for alert in incident.alerts:
        evidence.append(
            f"Alert {alert.alert_id}: {alert.name}; "
            f"severity={alert.severity}"
        )
        if alert.description:
            evidence.append(f"Alert details: {alert.description}")

    for snippet in incident.log_snippets:
        evidence.append(
            f"Log from {snippet.source}: {snippet.message}"
        )

    return evidence


def _score_cause(
    cause: str,
    incident_text: str,
) -> tuple[float, list[str]]:
    """
    Estimate textual support for a cause.

    This is a simple keyword heuristic, not a calibrated probability.
    """
    cause_tokens = _tokens(cause)
    incident_tokens = _tokens(incident_text)

    if not cause_tokens:
        return 0.0, []

    matched = cause_tokens & incident_tokens
    coverage = len(matched) / len(cause_tokens)

    # Keep scores conservative: keyword overlap cannot confirm a cause.
    score = min(0.85, round(coverage * 0.7, 2))

    return score, sorted(matched)


def analyze_incident(
    incident: Incident,
    top_k: int = 5,
) -> IncidentAnalysis:
    """Analyze an incident using retrieved knowledge-base articles."""
    articles = retrieve_knowledge_articles(
        incident=incident,
        top_k=top_k,
    )

    evidence = _incident_evidence(incident)
    incident_text = " ".join(evidence)

    # Aggregate duplicate hypotheses across articles.
    cause_results: dict[str, dict] = {}
    workarounds: list[Workaround] = []
    limitations: list[str] = []

    if not articles:
        limitations.append(
            "No relevant knowledge-base articles were found. "
            "Investigate using approved runbooks and incident evidence."
        )

    for article in articles:
        documented_causes = (
            _extract_section(article.content, "Possible Root Causes")
            or _extract_section(article.content, "Root Causes")
        )

        for cause in documented_causes:
            score, matched_terms = _score_cause(
                cause,
                incident_text,
            )
            key = cause.casefold()

            supporting_evidence = [
                f"Documented in KB article: {article.title}"
            ]

            if matched_terms:
                supporting_evidence.append(
                    "Incident text shares these keywords with the "
                    f"hypothesis: {', '.join(matched_terms)}"
                )

            if key not in cause_results:
                cause_results[key] = {
                    "description": cause,
                    "confidence": score,
                    "supporting_evidence": supporting_evidence,
                    "related_articles": [article.article_id],
                }
            else:
                existing = cause_results[key]
                existing["confidence"] = max(
                    existing["confidence"], score
                )
                if article.article_id not in existing["related_articles"]:
                    existing["related_articles"].append(
                        article.article_id
                    )
                for item in supporting_evidence:
                    if item not in existing["supporting_evidence"]:
                        existing["supporting_evidence"].append(item)

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

    ranked_causes = sorted(
        cause_results.values(),
        key=lambda item: (
            -item["confidence"],
            item["description"].casefold(),
        ),
    )

    probable_root_causes = [
        RootCause(**item) for item in ranked_causes
    ]

    if articles and not probable_root_causes:
        limitations.append(
            "Retrieved articles contained no recognized root-cause section."
        )

    if articles and not workarounds:
        limitations.append(
            "No recognized workaround section was found in the "
            "retrieved articles."
        )

    if probable_root_causes:
        limitations.append(
            "Root-cause scores are heuristic keyword-overlap estimates, "
            "not calibrated probabilities or confirmed diagnoses."
        )

    return IncidentAnalysis(
        incident_id=incident.incident_id,
        summary=(
            f"Preliminary analysis of incident {incident.incident_id}: "
            f"{len(articles)} relevant KB article(s) retrieved."
        ),
        probable_root_causes=probable_root_causes,
        relevant_articles=articles,
        proposed_workarounds=workarounds,
        limitations=limitations,
    )
