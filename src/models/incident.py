from typing import List, Optional
from pydantic import BaseModel, Field


class Alert(BaseModel):
    """
    Represents an alert associated with a major incident.
    """

    alert_id: str = Field(..., description="Unique alert identifier")
    name: str = Field(..., description="Alert name")
    severity: str = Field(..., description="Alert severity")
    status: Optional[str] = Field(
        default=None,
        description="Current alert status"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Alert timestamp"
    )
    description: Optional[str] = Field(
        default=None,
        description="Alert description"
    )


class LogSnippet(BaseModel):
    """
    Represents a relevant log snippet associated with an incident.
    """

    source: str = Field(..., description="Source of the log")
    timestamp: Optional[str] = Field(
        default=None,
        description="Log timestamp"
    )
    message: str = Field(..., description="Log message")


class Incident(BaseModel):
    """
    Represents the complete input for a major incident analysis.
    """

    incident_id: str = Field(
        ...,
        description="Unique incident identifier"
    )

    summary: str = Field(
        ...,
        description="Short description of the incident"
    )

    impact: Optional[str] = Field(
        default=None,
        description="Business or technical impact"
    )

    alerts: List[Alert] = Field(
        default_factory=list,
        description="Alerts associated with the incident"
    )

    log_snippets: List[LogSnippet] = Field(
        default_factory=list,
        description="Relevant log snippets"
    )

    affected_service: Optional[str] = Field(
        default=None,
        description="Service affected by the incident"
    )

    environment: Optional[str] = Field(
        default=None,
        description="Environment where the incident occurred"
    )
