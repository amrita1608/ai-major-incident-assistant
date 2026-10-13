"""Command-line entry point for the incident analyzer."""

import argparse
import sys
from pathlib import Path

from incident_analyzer.analysis_engine import analyze_incident
from incident_analyzer.email_drafter import draft_stakeholder_email
from incident_analyzer.incident_loader import load_incident


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Load an incident, analyze it, and optionally save outputs."""
    parser = argparse.ArgumentParser(
        description="Analyze a major incident using knowledge-base articles."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample_incident.json",
        help="Path to the incident JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save the analysis JSON.",
    )
    parser.add_argument(
        "--email-output",
        type=Path,
        help="Optional path to save a stakeholder email draft.",
    )
    args = parser.parse_args()

    input_path = (
        args.input
        if args.input.is_absolute()
        else Path.cwd() / args.input
    )

    try:
        incident = load_incident(input_path)
        analysis = analyze_incident(incident)

        result = analysis.model_dump_json(indent=2)

        if args.output:
            output_path = (
                args.output
                if args.output.is_absolute()
                else Path.cwd() / args.output
            )
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            output_path.write_text(
                result + "\n",
                encoding="utf-8",
            )
            print(f"Analysis saved to: {output_path}")
        elif not args.email_output:
            print(result)

        if args.email_output:
            email_output_path = (
                args.email_output
                if args.email_output.is_absolute()
                else Path.cwd() / args.email_output
            )
            email_output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            email_draft = draft_stakeholder_email(
                incident,
                analysis,
            )
            email_output_path.write_text(
                email_draft,
                encoding="utf-8",
            )
            print(f"Stakeholder email draft saved to: {email_output_path}")

        return 0

    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"File operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())