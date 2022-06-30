"""
This module contains the main Flask app. This module mainly exists in order to
avoid cyclic imports.
"""

from flask import Flask

app = Flask(__name__)
