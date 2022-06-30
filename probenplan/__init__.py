"""
This module initializes the application.
"""

from probenplan.app import app
from probenplan.config import Config
import probenplan.filters
import probenplan.routes

Config.instance().validate()
