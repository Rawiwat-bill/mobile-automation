import yaml
from pathlib import Path


class ConfigLoader:

    @staticmethod
    def load_yaml_file(file_path):
        """
        Load YAML file and return dictionary
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"YAML file not found: {file_path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    @staticmethod
    def get_value(file_path, key):
        """
        Get top-level key from yaml
        """

        data = ConfigLoader.load_yaml_file(file_path)

        return data.get(key)

    @staticmethod
    def get_nested_value(file_path, *keys):
        """
        Get nested value from yaml
        Example:
        get_nested_value(
            'configs/env/dev.yaml',
            'app',
            'package'
        )
        """

        data = ConfigLoader.load_yaml_file(file_path)

        current = data

        for key in keys:
            current = current[key]

        return current