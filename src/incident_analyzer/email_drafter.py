"""Generate a stakeholder email draft from incident analysis results."""

from models.analysis import IncidentAnalysis
from models.incident import Incident


def draft_stakeholder_email(
    incident: Incident,
    analysis: IncidentAnalysis,
) -> str:
    """Create a stakeholder email draft for review."""

    severity_label = (
        f"[{incident.severity.strip()}] "
        if incident.severity and incident.severity.strip()
        else ""
    )

    subject = (
        f"{severity_label}[Major Incident] {incident.incident_id} - "
        f"{incident.summary.strip()}"
    )

    next_update_time = (
        incident.next_update_time.strip()
        if incident.next_update_time
        and incident.next_update_time.strip()
        else "[insert next update time]"
    )

    incident_owner = (
        incident.incident_owner.strip()
        if incident.incident_owner
        and incident.incident_owner.strip()
        else "[Incident Manager / Response Team]"
    )

    lines = [
        f"Subject: {subject}",
        "",
        "Hello Stakeholders,",
        "",
        f"We are investigating incident {incident.incident_id}.",
        "",
        "Incident details reported:",
        incident.summary.strip(),
    ]

    if incident.severity and incident.severity.strip():
        lines.append(f"Severity: {incident.severity.strip()}")

    if incident.impact:
        lines.extend(
            [
                "",
                "Reported customer or business impact:",
                incident.impact.strip(),
            ]
        )

    if incident.affected_service:
        lines.append(
            f"Affected service: {incident.affected_service.strip()}"
        )

    if incident.environment:
        lines.append(
            f"Environment: {incident.environment.strip()}"
        )

    if incident_owner != "[Incident Manager / Response Team]":
        lines.append(f"Incident owner: {incident_owner}")

    lines.extend(
        [
            "",
            "Investigation status:",
            analysis.summary.strip(),
            "",
            "The following root causes are preliminary hypotheses, "
            "not confirmed diagnoses. They require validation against "
            "incident evidence, logs, metrics, and operational checks.",
        ]
    )

    if analysis.probable_root_causes:
        lines.extend(
            [
                "",
                "Possible causes under investigation:",
            ]
        )

        for index, cause in enumerate(
            analysis.probable_root_causes,
            start=1,
        ):
            lines.append(f"{index}. {cause.description}")

            if cause.supporting_evidence:
                lines.append("   Current supporting information:")
                for evidence in cause.supporting_evidence:
                    lines.append(f"   - {evidence}")

            if cause.related_articles:
                lines.append(
                    "   Related knowledge article IDs: "
                    + ", ".join(cause.related_articles)
                )
    else:
        lines.extend(
            [
                "",
                "Possible causes under investigation:",
                "No probable root causes have been identified from "
                "the currently retrieved knowledge-base information.",
            ]
        )

    if analysis.relevant_articles:
        lines.extend(
            [
                "",
                "Knowledge-base articles reviewed:",
            ]
        )

        for article in analysis.relevant_articles:
            lines.append(
                f"- {article.title} (ID: {article.article_id})"
            )

    if analysis.proposed_workarounds:
        lines.extend(
            [
                "",
                "Proposed workaround options — review before execution:",
            ]
        )

        for index, workaround in enumerate(
            analysis.proposed_workarounds,
            start=1,
        ):
            lines.append(f"{index}. {workaround.description}")

            for step_number, step in enumerate(
                workaround.steps,
                start=1,
            ):
                lines.append(f"   {step_number}. {step}")

            if workaround.source_article_ids:
                lines.append(
                    "   Source article IDs: "
                    + ", ".join(workaround.source_article_ids)
                )

            if workaround.requires_approval:
                lines.append(
                    "   Approval required before execution."
                )
            else:
                lines.append(
                    "   Validate applicability, safety, and operational "
                    "impact before execution."
                )

    if analysis.limitations:
        lines.extend(
            [
                "",
                "Analysis limitations:",
            ]
        )

        for limitation in analysis.limitations:
            lines.append(f"- {limitation}")

    lines.extend(
        [
            "",
            "Next steps:",
            "- Validate the reported symptoms using logs, metrics, "
            "and relevant operational checks.",
            "- Confirm or rule out the proposed root-cause hypotheses.",
            "- Review proposed workaround options and obtain required "
            "approvals before taking action.",
            "- Monitor service health and confirm recovery before "
            "declaring the incident resolved.",
            "",
            f"We will provide the next update at {next_update_time}.",
            "",
            "Regards,",
            incident_owner,
            "",
            "Draft for review: validate the incident details, findings, "
            "and proposed actions before sending.",
        ]
    )

    return "\n".join(lines) + "\n"