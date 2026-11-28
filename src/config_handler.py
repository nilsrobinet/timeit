"""Config handler."""

import os
import re
import datetime
from typing import Any, Callable

import yaml


# TODO: add config validation
class ConfigHandler:
    """Handles config. loads and provides access."""

    def __init__(self, config_path: str, config_update_callbacks: list[Callable]) -> None:
        self.config_path = config_path
        self.config: dict[str, Any] | None = None
        self.config_update_callbacks = config_update_callbacks

    def get_daily_target(self) -> str:
        """Get daily target as string.
        :returns: work target as string H:MM:SS
        """
        h, m = map(int, self._loaded_config().get("work", {}).get("target").split(":"))
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
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        print(f"Loaded {self.config}")

    def get_config(self) -> dict[str, Any]:
        """Get full config.
        :returns: full config
        """
        return self._loaded_config()

    def get_attendance_target(self) -> float:
        """Get attendance target as float.
        :returns: target as float
        """
        return self._loaded_config().get("attendance", {}).get("target")

    def get_number_of_workdays(self) -> int:
        """Get number of workdays.
        :returns: number of workdays
        """
        return len(self._loaded_config().get("attendance", {}).get("workdays", []))

    def get_workdays(self) -> list:
        """Get workdays as list of strings."""
        return self._loaded_config().get("attendance", {}).get("workdays", [])

    def get_server_port(self) -> int:
        """Get server port."""
        return self._loaded_config().get("server", {}).get("port")

    def set_config(self, new_config: dict) -> ValueError | None:
        """Set values from new config. Returns ValueError if invalid."""
        if self.config is None:
            raise RuntimeError("Config not loaded.")
        for k, v in new_config.items():
            print(f"Updating {k} with {v}")
            if k not in self.config:
                return ValueError(f"Invalid key: {k}")
            self.config[k] = v
        self._persist()
        for cb in self.config_update_callbacks:
            cb(updated_keys=list(new_config.keys()))
        return None

    def _loaded_config(self) -> dict[str, Any]:
        if self.config is None:
            raise RuntimeError("Configuration has not been loaded.")
        return self.config

    def _persist(self):
        if self._loaded_config().get("userwritable") is False:
            raise RuntimeError("Config is not user writable.")
        today = datetime.date.today().strftime("%Y-%m-%d")
        # backup old config
        old = self.config_path.replace(".yaml", f".{today}.yaml")
        os.rename(self.config_path, old)
        # write new config
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f)
        # cleanup old backups if needed
        backups = sorted([f for f in os.listdir(os.path.dirname(self.config_path)) if re.match(r".*\.\d{4}-\d{2}-\d{2}\.yaml", f)])[:-5]
        for bs in backups:
            os.remove(os.path.join(os.path.dirname(self.config_path), bs))
