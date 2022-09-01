"""
This module provides an interface to inject configuration via the environment.
"""

import os
import re


def read_env(key, default=None, required=True):
    if key in os.environ:
        return os.getenv(key)
    elif f"{key}_FILE" in os.environ:
        with open(os.environ[key + "_FILE"], "r") as f:
            return f.read().strip()
    elif required and default is None:
        raise KeyError(f"{key} or {key}_FILE is required in the environment.")
    else:
        return default


tenant = read_env("AZURE_TENANT")
client_id = read_env("AZURE_CLIENT_ID")
client_secret = read_env("AZURE_CLIENT_SECRET")
calendar_user = read_env("CALENDAR_USER")
locale = read_env("LOCALE", "de-de")

highlights = []
__index = 1
try:
    while True:
        regex = os.environ[f"HIGHLIGHT_PATTERN_{__index}"]
        highlights.append(
            {
                "pattern": re.compile(regex, re.IGNORECASE),
                "name": os.getenv(f"HIGHLIGHT_NAME_{__index}", ""),
                "color": os.environ[f"HIGHLIGHT_COLOR_{__index}"],
            }
        )
        __index += 1
except KeyError:
    pass
