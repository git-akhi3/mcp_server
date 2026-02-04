from app.services.event_api import EventAPIService
import json


async def tool_get_all_events(input_data):
    try:
        data = await EventAPIService.get_all_events(**input_data)

        return {
            "success": True,
            "events": data["content"],
            "page": data["pageNo"],
            "total": data["totalElements"],
        }

    except Exception as e:
        print(f"[ERROR] get_all_events failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }


async def tool_get_event_by_slug(input_data):
    try:
        data = await EventAPIService.get_event_by_slug(
            input_data["event_slug"]
        )

        return {
            "success": True,
            "event": data["event"],
            "bookingTypes": data.get("bookingTypes"),
            "tables": data.get("eventTables"),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
