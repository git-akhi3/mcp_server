from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

TOOLS = {
    "get_all_events": {
        "description": "Fetch list of upcoming events",
        "handler": tool_get_all_events,
    },
    "get_event_by_slug": {
        "description": "Fetch full event details using event slug",
        "handler": tool_get_event_by_slug,
    },
}
