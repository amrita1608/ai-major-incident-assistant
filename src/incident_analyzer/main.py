
"""Command-line entry point for the incident analyzer."""

import argparse
import json
import sys
from pathlib import Path

from incident_analyzer.analysis_engine import analyze_incident
from incident_analyzer.incident_loader import load_incident


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Load an incident, analyze it, and print JSON results."""
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
        else:
            print(result)

        return 0

    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"File operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
