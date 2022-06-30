"""
This module provides an interface to inject configuration via the environment.
"""

__all__ = ["Config"]

import os
import re
from functools import lru_cache


class Config:
    """
    The `Config` class provides a singleton `instance()` that loads configuration
    values from the environment.

    You usually should only use the singleton `instance()`.
    """

    @classmethod
    @lru_cache
    def instance(cls):
        """Returns the singleton `Config` instance."""
        return cls()

    def __init__(self):
        """Initializes the `Config` object with values from the environment."""

        self.url = os.getenv("PROBENPLAN_CALENDAR")
        self.cache_ttl = int(os.getenv("CACHE_TTL", 60 * 60))
        self.locale = os.getenv("LOCALE", "de-de")

        heading_regex = os.getenv("HEADING_PATTERN", "^--(?P<value>.+)--$")
        self.heading_pattern = re.compile(
            heading_regex, re.IGNORECASE
        ) if heading_regex else None

        self.highlights = []
        index = 1
        try:
            while True:
                regex = os.environ[f"HIGHLIGHT_PATTERN_{index}"]
                self.highlights.append({
                    "pattern": re.compile(regex, re.IGNORECASE),
                    "name": os.getenv(f"HIGHLIGHT_NAME_{index}", ""),
                    "color": os.environ[f"HIGHLIGHT_COLOR_{index}"],
                })
                index += 1
        except KeyError:
            pass

    def validate(self):
        """
        Validates the current configuration raising errors if a misconfiguration
        is detected.
        """

        if not self.url:
            raise KeyError("PROBENPLAN_CALENDAR is required.")
