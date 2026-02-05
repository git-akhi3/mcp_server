from typing import Dict, Any, List
from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
    tool_book_event,
    tool_get_booking_details,
)
from app.mcp.schemas import (
    GET_ALL_EVENTS_SCHEMA,
    GET_EVENT_BY_SLUG_SCHEMA,
    BOOK_EVENT_SCHEMA,
    GET_BOOKING_DETAILS_SCHEMA,
)
from constants import ToolName, TOOL_DESCRIPTIONS


# Tools Registry 
TOOLS: Dict[str, Dict[str, Any]] = {
    ToolName.GET_ALL_EVENTS: {
        "description": TOOL_DESCRIPTIONS[ToolName.GET_ALL_EVENTS],
        "inputSchema": GET_ALL_EVENTS_SCHEMA,
        "handler": tool_get_all_events,
    },
    ToolName.GET_EVENT_BY_SLUG: {
        "description": TOOL_DESCRIPTIONS[ToolName.GET_EVENT_BY_SLUG],
        "inputSchema": GET_EVENT_BY_SLUG_SCHEMA,
        "handler": tool_get_event_by_slug,
    },
    ToolName.BOOK_EVENT: {
        "description": TOOL_DESCRIPTIONS[ToolName.BOOK_EVENT],
        "inputSchema": BOOK_EVENT_SCHEMA,
        "handler": tool_book_event,
    },
    ToolName.GET_BOOKING_DETAILS: {
        "description": TOOL_DESCRIPTIONS[ToolName.GET_BOOKING_DETAILS],
        "inputSchema": GET_BOOKING_DETAILS_SCHEMA,
        "handler": tool_get_booking_details,
    },
}


def get_tools_list() -> List[Dict[str, Any]]:
    return [
        {
            "name": name,
            "description": tool["description"],
            "inputSchema": tool["inputSchema"]
        }
        for name, tool in TOOLS.items()
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name not in TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {name}"
        }
    
    tool = TOOLS[name]
    
    try:
        if name == ToolName.GET_ALL_EVENTS:
            processed_args = {
                "page": arguments.get("page", 0),
                "size": arguments.get("size", 4),
                "sortBy": arguments.get("sortBy", "eventDateTime"),
                "sortDir": arguments.get("sortDir", "asc"),
                "afterDate": arguments.get("afterDate")
            }
            
            if not processed_args["afterDate"]:
                return {
                    "success": False,
                    "error": "afterDate is required. Please provide a date in ISO 8601 format (e.g., 2026-02-04T00:00:00.000Z)"
                }
            
            return await tool["handler"](processed_args)
        
        elif name == ToolName.GET_EVENT_BY_SLUG:
            if not arguments.get("event_slug"):
                return {
                    "success": False,
                    "error": "event_slug is required"
                }
            
            return await tool["handler"](arguments)
        
        elif name == ToolName.BOOK_EVENT:
            # Validate all required fields for booking
            required_fields = [
                "event_id", "booking_entity_type", "booking_entity_id",
                "quantity", "customer_name", "customer_email", "customer_whatsapp"
            ]
            
            missing_fields = [field for field in required_fields if not arguments.get(field)]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}. Please collect all customer details (name, email, WhatsApp number) before booking."
                }
            
            # Validate booking_entity_type
            if arguments.get("booking_entity_type") not in ["TICKET_TYPE", "TABLE"]:
                return {
                    "success": False,
                    "error": "booking_entity_type must be either 'TICKET_TYPE' or 'TABLE'"
                }
            
            # Validate quantity
            quantity = arguments.get("quantity", 1)
            if not isinstance(quantity, int) or quantity < 1:
                return {
                    "success": False,
                    "error": "quantity must be a positive integer (minimum 1)"
                }
            
            processed_args = {
                "event_id": arguments["event_id"],
                "booking_entity_type": arguments["booking_entity_type"],
                "booking_entity_id": arguments["booking_entity_id"],
                "quantity": quantity,
                "customer_name": arguments["customer_name"],
                "customer_email": arguments["customer_email"],
                "customer_whatsapp": arguments["customer_whatsapp"],
            }
            
            return await tool["handler"](processed_args)
        
        elif name == ToolName.GET_BOOKING_DETAILS:
            if not arguments.get("booking_id"):
                return {
                    "success": False,
                    "error": "booking_id is required. This should be the UUID returned from a successful book_event call."
                }
            
            if not arguments.get("customer_id"):
                return {
                    "success": False,
                    "error": "customer_id is required. This should be the numeric ID returned from a successful book_event call."
                }
            
            processed_args = {
                "booking_id": arguments["booking_id"],
                "customer_id": arguments["customer_id"],
            }
            
            return await tool["handler"](processed_args)
        
        return await tool["handler"](arguments)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": name
        }
