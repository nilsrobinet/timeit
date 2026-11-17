import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_config_handler():
    from ConfigHandler import ConfigHandler
    config_path = os.path.join(os.path.dirname(__file__), 'test_config.toml')
    handler = ConfigHandler(config_path)
    handler.load()
    assert handler.get_daily_target() is not None
    assert handler.get_persistence() is not None
    assert handler.get_timekeeping_path() is not None
    assert handler.get_attendance_path() is not None
    assert handler.get_daily_target() == [1,2]
    assert handler.get_persistence() == "json"
    assert handler.get_timekeeping_path() == "data.json"
    assert handler.get_attendance_path() == "attendance.json"