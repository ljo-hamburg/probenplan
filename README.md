# Probenplan

![Docker Image](https://github.com/ljo-hamburg/probenplan/actions/workflows/build.yml/badge.svg)
![MIT License](https://img.shields.io/github/license/ljo-hamburg/probenplan)

This is the Probenplan app of the LJO Hamburg.

## Quick Start

The quickest way to get up and running is by using the docker container:

```shell
docker run -p 8080:8080 -e PROBENPLAN_CALENDAR="https://..." ghcr.io/ljo-hamburg/probenplan
```

The following environment variables are supported:

| Environment Variable  | Required | Description                                                  |
| --------------------- | -------- | ------------------------------------------------------------ |
| `PROBENPLAN_CALENDAR` | yes      | This variable sets the source of the calendar data. The probenplan will query this calendar for events to be displayed. |
| `CACHE_TTL`           | no       | The number of seconds the calendar data is cached for. Default is 3600. |
| `LOCALE`              | no       | The display locale/language. Default is `de-de`.             |
| `HEADING_PATTERN`     | no       | A regular expression that identifies events that are interpreted as headings. See below for details. Default: `^--(?P<value>.+)--$` |
| `HIGHLIGHT_…`         | no       | See below.                                                   |

### Headings

Some events get treated in a special way by the calendar. These are called _heading events_. They are identified by a regular expression `HEADING_PATTERN` that is matched with the title of an event. If the title of an event matches this expression, the event will be treated as a heading and will be excluded from the regular event list.

The pattern may include a named capture group `value`. If an event’s title matches the expression the value of this capture group is used as the heading value. If no such capture group exists the full match is used as the heading.

The regular expression may match only part of an event’s title. Use `^` and `$` to match the full title. The match is case insensitive.

### Highlights

You can specify multiple highlights. A highlight consists of a pattern, a color and a name. You specify these via the environment: `HIGHLIGHT_PATTERN_1`, `HIGHLIGHT_COLOR_1`, `HIGHLIGHT_NAME_1`, … You can specify multiple highlights by incrementing the trailing number.

Highlight patterns are matched against the title of events. If an event’s title matches a given pattern, the respective color is shown next to it. The highlight name is displayed as a legend to help users interpret highlight colors.

Regular expressions may match only part of an event’s title. Use `^` and `$` to match the full title. The match is case insensitive.

Colors have to be valid CSS color specifications.

## Building the application

In order to run the probenplan, two things need to happen first:

- The CSS bundle needs to be built
- The required fonts need to be downloaded

Both of these things can be done through `npm run`. This required Node.js.

First install the required dependencies by running `npm install`. Then create the static files by running `npm run build`.

That’s it. You can now run the flask dev server or use a production server to run the app.
