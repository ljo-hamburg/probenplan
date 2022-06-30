"""
This module contains the routes of the Probenplan app.
"""

from arrow import Arrow
from flask import redirect, render_template, request, Response, url_for

from .app import app
from .config import Config
from .util import custom_color_css, event_timeline

config = Config.instance()


@app.route("/")
def probenplan():
    """
    This is the main endpoint of the app. This will render and return the plan.
    """
    now = Arrow.now()
    all_events = request.args.get("all", False)
    events = []
    headings = []
    for event in event_timeline():
        if getattr(event, "probenplan").get("heading", False):
            if events or not headings:
                headings.append(event)
            else:
                headings[0] = event
        elif all_events or event.end > now:
            events.append(event)

    return render_template(
        "probenplan.html.j2",
        events=events,
        headings=headings,
        now=Arrow.now(),
        highlights=config.highlights,
        all_events=all_events
    )


@app.route("/reload")
def reload():
    """
    This endpoint is very similar to the main endpoint. However, this method will
    clear the internal cache first, thereby making sure that we will receive up-to-date
    data.
    """
    event_timeline.cache.clear()
    return redirect(url_for("probenplan"))


@app.route("/colors.css")
def dynamic_css():
    """
    This endpoint returns a CSS document that sets CSS variables according to the
    configured highlighters.
    """
    return Response(custom_color_css(), mimetype="text/css")
