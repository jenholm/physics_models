"""Configuration loading and validation for ISR."""

import yaml
from pathlib import Path
from typing import Any
import collections.abc


class ISRConfig(collections.abc.Mapping):
    """Dict-like container for ISR configuration loaded from YAML."""

    def __init__(self, raw: dict):
        self._raw = dict(raw)

    def __getitem__(self, key: str):
        return self._raw[key]

    def __iter__(self):
        return iter(self._raw)

    def __len__(self) -> int:
        return len(self._raw)

    def __getattr__(self, item: str):
        try:
            return self._raw[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __repr__(self) -> str:
        return f"ISRConfig({self._raw})"


def load_config(path: str | Path) -> ISRConfig:
    path = Path(path)
    with path.open("r") as f:
        raw = yaml.safe_load(f) or {}
    return ISRConfig(raw)


def load_all_configs(config_dir: str | Path = "configs") -> dict[str, ISRConfig]:
    config_dir = Path(config_dir)
    configs = {}
    for fname in ["base.yaml", "landscapes.yaml", "kernels.yaml"]:
        key = fname.replace(".yaml", "")
        configs[key] = load_config(config_dir / fname)
    return configs
