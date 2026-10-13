
"""Retrieve and rank knowledge-base articles for an incident."""

import re
from pathlib import Path

from models.analysis import KnowledgeArticle
from models.incident import Incident


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = PROJECT_ROOT / "knowledge_base"


def _tokenize(text: str) -> set[str]:
    """Convert text into normalized keyword tokens."""
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1
    }


def load_knowledge_articles(
    directory: str | Path = KB_DIR,
) -> list[KnowledgeArticle]:
    """
    Load Markdown knowledge articles from a directory.

    Each Markdown file becomes an article. The filename is its article ID,
    the first Markdown heading is its title, and the full text is its content.
    """
    kb_path = Path(directory)

    if not kb_path.is_dir():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {kb_path}"
        )

    articles: list[KnowledgeArticle] = []

    for file_path in sorted(kb_path.rglob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        heading = re.search(r"(?m)^#\s+(.+?)\s*$", content)
        title = heading.group(1).strip() if heading else file_path.stem

        articles.append(
            KnowledgeArticle(
                article_id=file_path.stem,
                title=title,
                content=content,
                source=str(file_path.relative_to(kb_path)),
            )
        )

    return articles


def _incident_text(incident: Incident) -> str:
    """Combine searchable text from an incident and its evidence."""
    parts = [incident.summary]

    if incident.impact:
        parts.append(incident.impact)

    if incident.affected_service:
        parts.append(incident.affected_service)

    if incident.environment:
        parts.append(incident.environment)

    for alert in incident.alerts:
        parts.extend([alert.name, alert.severity])

        if alert.description:
            parts.append(alert.description)

        if alert.status:
            parts.append(alert.status)

    for snippet in incident.log_snippets:
        parts.extend([snippet.source, snippet.message])

    return " ".join(parts)


def retrieve_knowledge_articles(
    incident: Incident,
    articles: list[KnowledgeArticle] | None = None,
    top_k: int = 5,
) -> list[KnowledgeArticle]:
    """
    Return the most relevant knowledge articles for an incident.

    Articles are ranked by keyword overlap. This is a baseline retrieval
    method, not semantic search or proof of a root cause.
    """
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    candidates = (
        load_knowledge_articles()
        if articles is None
        else articles
    )

    incident_tokens = _tokenize(_incident_text(incident))

    if not incident_tokens:
        return []

    scored_articles: list[tuple[int, str, KnowledgeArticle]] = []

    for article in candidates:
        searchable_text = " ".join(
            [
                article.title,
                article.content,
                " ".join(article.symptoms),
            ]
        )
        article_tokens = _tokenize(searchable_text)
        score = len(incident_tokens & article_tokens)

        if score > 0:
            scored_articles.append(
                (score, article.article_id, article)
            )

    scored_articles.sort(key=lambda item: (-item[0], item[1]))

    return [
        article
        for _, _, article in scored_articles[:top_k]
    ]
