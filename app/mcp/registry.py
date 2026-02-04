from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

TOOLS = {
    "get_all_events": {
        "description": "Retrieve a paginated list of upcoming events at Big Bull club. Use afterDate parameter to filter events occurring after a specific date. The afterDate MUST be in ISO 8601 format with timezone (e.g., 2026-02-04T00:00:00.000Z).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number for pagination (0-indexed). Default is 0.",
                    "default": 0
                },
                "size": {
                    "type": "integer",
                    "description": "Number of events per page. Default is 4.",
                    "default": 4
                },
                "sortBy": {
                    "type": "string",
                    "description": "Field to sort by. Default is 'eventDateTime'.",
                    "default": "eventDateTime"
                },
                "sortDir": {
                    "type": "string",
                    "description": "Sort direction: 'asc' for ascending, 'desc' for descending. Default is 'asc'.",
                    "enum": ["asc", "desc"],
                    "default": "asc"
                },
                "afterDate": {
                    "type": "string",
                    "description": "ISO 8601 datetime string with timezone. MUST be in format: YYYY-MM-DDTHH:MM:SS.000Z (e.g., 2026-02-04T00:00:00.000Z). This filters events occurring after this date."
                }
            },
            "required": ["afterDate"],
            "additionalProperties": False
        },
        "handler": tool_get_all_events,
    },
    "get_event_by_slug": {
        "description": "Retrieve complete details of a specific event using its unique slug identifier. Returns event information including booking types and table availability.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_slug": {
                    "type": "string",
                    "description": "The unique slug identifier for the event (e.g., 'new-year-party-2026')"
                }
            },
            "required": ["event_slug"],
            "additionalProperties": False
        },
        "handler": tool_get_event_by_slug,
    },
}
