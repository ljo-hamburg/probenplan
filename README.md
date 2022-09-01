# Probenplan

![Docker Image](https://github.com/ljo-hamburg/probenplan/actions/workflows/build.yml/badge.svg)
![MIT License](https://img.shields.io/github/license/ljo-hamburg/probenplan)

This is the Probenplan app of the LJO Hamburg.

## Quick Start

The quickest way to get up and running is by using the docker container:

```shell
docker run -p 8080:8080 -e AZURE_TENANT="..." -e ... ghcr.io/ljo-hamburg/probenplan
```

The following environment variables are supported:

| Environment Variable  | Required | Description                                                  |
| --------------------- | -------- | ------------------------------------------------------------ |
| `AZURE_TENANT`        | yes      | The ID of the Azure Tenant from which data will be fetched.  |
| `AZURE_CLINET_ID`     | yes      | The client ID for the application. Needs read permissions for the selected calendar. |
| `AZURE_CLIENT_SECRET` | yes      | The client secret for the application.                       |
| `CALENDAR_USER`       | yes      | The ID or UPN of the user whose primary calendar will be used as data source. |
| `HIGHLIGHT_…`         | no       | See below.                                                   |

### Headings

Some events get treated in a special way by the calendar. These are called _heading events_. They are identified by a leading double dash `--` in the subject of an event. Such events will be treated as headings and are otherwise excluded from the event list.

Headings may be found outside of the queried date range (specified via GET paramters `from` and `to`) to be able to display a heading above the first event.

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
