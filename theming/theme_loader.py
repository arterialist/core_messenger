import re
from pathlib import Path

from models.logging import Logger
from models.theming import Theme
from tools import uri2path


class ThemeLoader:
    loaded_theme = Theme({})

    @staticmethod
    def load_from_file(path):
        path = uri2path(path)
        if not Path(path).is_file():
            Logger.get_channel("ThemeEngine", True).log(
                f"Failed to load theme file at path {path}, falling back to default.")
            path = "./themes/default.ctheme"

        with open(Path(path).absolute()) as theme_file:
            lines = theme_file.readlines()
            theme_entry_regexp = re.compile("([a-z]+[a-zA-Z]*)\s?=\s?(#([a-fA-F0-9]{2})?([a-fA-F0-9]{6}))")

            theme_entries = {}

            for line in lines:
                if theme_entry_regexp.match(line):
                    parts = line.strip("\n").split("=")
                    parts = [part.strip(" ") for part in parts]

                    theme_entries[parts[0]] = parts[1]

            theme = Theme(theme_entries)
            ThemeLoader.loaded_theme = theme
            return theme
