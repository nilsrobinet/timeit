import tomllib
import json

class ConfigHandler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def get_daily_target(self):
        return self.config.get('work', {}).get('target')

    def get_persistence(self):
        return self.config.get('data', {}).get('persistence')

    def get_timekeeping_path(self):
        return self.config.get('data', {}).get('timekeeping_path')

    def get_attendance_path(self):
        return self.config.get('data', {}).get('attendance_path')

    def load(self):
        with open(self.config_path, 'rb') as f:
            self.config = tomllib.load(f)

    def get_config(self):
        return self.config