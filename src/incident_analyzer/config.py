
"""Load application and knowledge-base configuration."""

from pathlib import Path
from typing import Any

import yaml


# Project root: ai-major-incident-assistant/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = PROJECT_ROOT / "config"


def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Invalid YAML in {file_path}: {exc}"
        ) from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a YAML dictionary in {file_path}"
        )

    return data


def load_config() -> dict[str, Any]:
    """Load the main application configuration."""
    return load_yaml_file(CONFIG_DIR / "config.yaml")


def load_kb_sources() -> dict[str, Any]:
    """Load knowledge-base source definitions."""
    return load_yaml_file(CONFIG_DIR / "kb_sources.yaml")
