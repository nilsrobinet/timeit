"""Config handler."""

import tomllib
from typing import Any


# TODO: add config validation
class ConfigHandler:
    """Handles config. loads and provides access."""

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config: dict[str, Any] | None = None

    def get_daily_target(self) -> str:
        """Get daily target as string.
        :returns: work target as string H:MM:SS
        """
        h, m = map(int, self._loaded_config().get("work", {}).get("target"))
        target = f"{h:02d}:{m:02d}:00"
        return target

    def get_persistence(self) -> str:
        """Get persistence type.
        :returns: persistence type as string
        """
        return self._loaded_config().get("data", {}).get("persistence")

    def get_timekeeping_path(self) -> str:
        """Get timekeeping path.
        :returns: path as string
        """
        return self._loaded_config().get("data", {}).get("timekeeping_path")

    def load(self) -> None:
        """Load config."""
        with open(self.config_path, "rb") as f:
            self.config = tomllib.load(f)

    def get_config(self) -> dict[str, Any]:
        """Get full config.
        :returns: full config
        """
        return self._loaded_config()

    def _loaded_config(self) -> dict[str, Any]:
        if self.config is None:
            raise RuntimeError("Configuration has not been loaded.")
        return self.config
