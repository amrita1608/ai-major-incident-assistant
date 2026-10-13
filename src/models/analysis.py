
"""Data models for incident analysis and knowledge-base results."""

from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgeArticle(BaseModel):
    """Represents a knowledge-base article."""

    article_id: str = Field(
        ...,
        description="Unique knowledge article identifier",
    )
    title: str = Field(
        ...,
        description="Knowledge article title",
    )
    content: str = Field(
        ...,
        description="Full article content",
    )
    symptoms: List[str] = Field(
        default_factory=list,
        description="Symptoms addressed by the article",
    )
    root_cause: Optional[str] = Field(
        default=None,
        description="Documented root cause",
    )
    workaround: Optional[str] = Field(
        default=None,
        description="Documented workaround",
    )
    source: Optional[str] = Field(
        default=None,
        description="Source or path of the article",
    )


class RootCause(BaseModel):
    """Represents a probable cause of an incident."""

    description: str = Field(
        ...,
        description="Description of the probable root cause",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1",
    )
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence supporting the probable cause",
    )
    related_articles: List[str] = Field(
        default_factory=list,
        description="IDs of related knowledge-base articles",
    )


class Workaround(BaseModel):
    """Represents a proposed incident workaround."""

    description: str = Field(
        ...,
        description="Description of the workaround",
    )
    steps: List[str] = Field(
        default_factory=list,
        description="Ordered steps to apply the workaround",
    )
    source_article_ids: List[str] = Field(
        default_factory=list,
        description="Knowledge article IDs supporting the workaround",
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether approval is required before execution",
    )


class IncidentAnalysis(BaseModel):
    """Represents the analysis results for a major incident."""

    incident_id: str = Field(
        ...,
        description="ID of the analyzed incident",
    )
    summary: str = Field(
        ...,
        description="Summary of the analysis",
    )
    probable_root_causes: List[RootCause] = Field(
        default_factory=list,
        description="Ranked probable root causes",
    )
    relevant_articles: List[KnowledgeArticle] = Field(
        default_factory=list,
        description="Relevant knowledge-base articles",
    )
    proposed_workarounds: List[Workaround] = Field(
        default_factory=list,
        description="Proposed workarounds for review",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Gaps in evidence or analysis limitations",
    )
