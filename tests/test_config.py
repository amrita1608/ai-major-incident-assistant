
from pathlib import Path

import pytest

from incident_analyzer import config


def test_load_yaml_file_returns_dictionary(tmp_path):
    """Valid YAML should load into a dictionary."""
    file_path = tmp_path / "settings.yaml"
    file_path.write_text(
        "app_name: incident-analyzer\nmax_results: 5\n",
        encoding="utf-8",
    )

    result = config.load_yaml_file(file_path)

    assert result == {
        "app_name": "incident-analyzer",
        "max_results": 5,
    }


def test_load_yaml_file_returns_empty_dictionary_for_empty_file(tmp_path):
    """An empty YAML file should return an empty dictionary."""
    file_path = tmp_path / "empty.yaml"
    file_path.write_text("", encoding="utf-8")

    assert config.load_yaml_file(file_path) == {}


def test_load_yaml_file_raises_for_missing_file(tmp_path):
    """A missing configuration file should raise FileNotFoundError."""
    file_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        config.load_yaml_file(file_path)


def test_load_yaml_file_raises_for_invalid_yaml(tmp_path):
    """Malformed YAML should raise ValueError."""
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text("setting: [unclosed", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML"):
        config.load_yaml_file(file_path)


@pytest.mark.parametrize(
    "yaml_content",
    [
        "- item1\n- item2\n",
        "just a string\n",
        "42\n",
    ],
)
def test_load_yaml_file_rejects_non_dictionary_content(tmp_path, yaml_content):
    """Valid YAML that isn't a dictionary should raise ValueError."""
    file_path = tmp_path / "not_a_dictionary.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a YAML dictionary"):
        config.load_yaml_file(file_path)


def test_load_config_uses_config_yaml(monkeypatch):
    """The application config loader should use config/config.yaml."""
    expected_path = config.CONFIG_DIR / "config.yaml"
    expected_data = {"environment": "test"}
    requested_paths = []

    def fake_load_yaml_file(path):
        requested_paths.append(path)
        return expected_data

    monkeypatch.setattr(config, "load_yaml_file", fake_load_yaml_file)

    result = config.load_config()

    assert result == expected_data
    assert requested_paths == [expected_path]


def test_load_kb_sources_uses_kb_sources_yaml(monkeypatch):
    """The KB loader should use config/kb_sources.yaml."""
    expected_path = config.CONFIG_DIR / "kb_sources.yaml"
    expected_data = {"sources": []}
    requested_paths = []

    def fake_load_yaml_file(path):
        requested_paths.append(path)
        return expected_data

    monkeypatch.setattr(config, "load_yaml_file", fake_load_yaml_file)

    result = config.load_kb_sources()

    assert result == expected_data
    assert requested_paths == [expected_path]
