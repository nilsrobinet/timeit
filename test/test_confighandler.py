"""Test config handler"""

import os

from src.config_handler import ConfigHandler


def test_config_handler():
    """Test config handler"""

    config_path = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    handler = ConfigHandler(config_path)
    handler.load()
    assert handler.get_daily_target() is not None
    assert handler.get_persistence() is not None
    assert handler.get_timekeeping_path() is not None
    assert handler.get_daily_target() == "01:02:00"
    assert handler.get_persistence() == "json"
    assert handler.get_timekeeping_path() == "data.json"
    assert handler.get_number_of_workdays() == 5
