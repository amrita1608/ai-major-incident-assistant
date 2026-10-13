
"""Load and validate incident input from JSON files."""

import json
from pathlib import Path

from pydantic import ValidationError

from models.incident import Incident


def load_incident(file_path: str | Path) -> Incident:
    """
    Load incident data from a JSON file and validate it.

    Args:
        file_path: Path to the incident JSON file.

    Returns:
        A validated Incident model instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON is invalid or the data fails validation.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Incident file not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            incident_data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in incident file {path}: {exc}"
        ) from exc

    if not isinstance(incident_data, dict):
        raise ValueError(
            "Incident JSON must contain a single JSON object."
        )

    try:
        return Incident.model_validate(incident_data)
    except ValidationError as exc:
        raise ValueError(
            f"Incident validation failed for {path}:\n{exc}"
        ) from exc
