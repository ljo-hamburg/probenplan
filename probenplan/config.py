"""
This module provides an interface to inject configuration via the environment.
"""

import os
import re

tenant = os.getenv("AZURE_TENANT")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
calendar_user = os.getenv("CALENDAR_USER")
locale = os.getenv("LOCALE", "de-de")

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

if not tenant:
    raise KeyError("AZURE_TENANT is required.")
if not client_id:
    raise KeyError("AZURE_CLIENT_ID is required.")
if not client_secret:
    raise KeyError("AZURE_CLIENT_SECRET is required.")
