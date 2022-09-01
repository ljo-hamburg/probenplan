"""
This module contains the routes of the Probenplan app.
"""

import arrow
from arrow import Arrow
from flask import Response, redirect, render_template, request, url_for

from . import config
from .app import app
from .events import get_events


@app.route("/")
def probenplan2():
    begin = arrow.get(request.args.get("from", arrow.utcnow()))
    end = arrow.get(request.args["to"]) if "to" in request.args else None
    # return [event.location for event in get_events(begin, end)]
    return render_template(
        "probenplan.html.j2",
        events=get_events(begin, end),
        now=Arrow.now(),
        highlights=config.highlights,
    )


@app.route("/colors.css")
def dynamic_css():
    """
    This endpoint returns a CSS document that sets CSS variables according to the
    configured highlighters.
    """
    css = "\n".join(
        f".custom-color-{index} {{--color: {highlight['color']}}}"
        for (index, highlight) in enumerate(config.highlights)
    )
    return Response(css, mimetype="text/css")
