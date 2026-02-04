from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

TOOLS = {
    "get_all_events": {
        "description": "Fetch list of upcoming events with pagination and filtering. IMPORTANT: afterDate must be in ISO 8601 format with timezone (example: 2026-02-04T18:30:00.000Z)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (0-indexed)",
                    "default": 0
                },
                "size": {
                    "type": "integer",
                    "description": "Number of events per page",
                    "default": 4
                },
                "sortBy": {
                    "type": "string",
                    "description": "Field to sort by",
                    "default": "eventDateTime"
                },
                "sortDir": {
                    "type": "string",
                    "description": "Sort direction (asc or desc)",
                    "enum": ["asc", "desc"],
                    "default": "asc"
                },
                "afterDate": {
                    "type": "string",
                    "description": "ISO 8601 datetime with timezone. Example: 2026-02-04T18:30:00.000Z (MUST include time and .000Z suffix)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$"
                }
            },
            "required": ["page", "size", "sortBy", "sortDir", "afterDate"]
        },
        "handler": tool_get_all_events,
    },
    "get_event_by_slug": {
        "description": "Fetch full event details using event slug",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_slug": {
                    "type": "string",
                    "description": "Unique slug identifier for the event"
                }
            },
            "required": ["event_slug"]
        },
        "handler": tool_get_event_by_slug,
    },
}
