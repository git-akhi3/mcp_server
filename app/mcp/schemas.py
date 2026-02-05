from typing import Dict, Any

# Schema Definitions
GET_ALL_EVENTS_SCHEMA = {
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
}

GET_EVENT_BY_SLUG_SCHEMA = {
    "type": "object",
    "properties": {
        "event_slug": {
            "type": "string",
            "description": "The unique slug identifier for the event (e.g., 'new-year-party-2026')"
        }
    },
    "required": ["event_slug"],
    "additionalProperties": False
}

BOOK_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "event_id": {
            "type": "integer",
            "description": "The event's numeric ID. Get this from get_event_by_slug response: event.id (e.g., 270). This becomes 'eventId' in the API request. NEVER guess - always fetch from get_event_by_slug first."
        },
        "booking_entity_type": {
            "type": "string",
            "description": "Type of booking. Use exactly 'TICKET_TYPE' for ticket bookings or 'TABLE' for table reservations. This becomes 'bookingEntityType' in the API request.",
            "enum": ["TICKET_TYPE", "TABLE"]
        },
        "booking_entity_id": {
            "type": "integer",
            "description": "The ticket type ID or table ID to book. Get this from get_event_by_slug response: bookingTypes[].ticketTypes[].id (e.g., 463 for 'Male Entry'). This becomes 'bookingEntityId' in the API request. NEVER guess - always fetch from get_event_by_slug first."
        },
        "quantity": {
            "type": "integer",
            "description": "Number of tickets to book. Minimum 1. Check maxTicketsPerBooking from ticket type to ensure you don't exceed the limit. Default to 1 if user doesn't specify.",
            "minimum": 1,
            "default": 1
        },
        "customer_name": {
            "type": "string",
            "description": "Customer's full name for the booking (e.g., 'Akhil Mulagada'). This goes into customerDetails.name in the API. ASK the user if not provided."
        },
        "customer_email": {
            "type": "string",
            "description": "Customer's email address for booking confirmation (e.g., 'akhil@example.com'). This goes into customerDetails.email in the API. ASK the user if not provided.",
            "format": "email"
        },
        "customer_whatsapp": {
            "type": "string",
            "description": "Customer's WhatsApp number - 10 digits only, NO country code (e.g., '9346315817' not '+919346315817'). This goes into customerDetails.whatsappNo in the API. ASK the user if not provided.",
            "pattern": "^[0-9]{10,15}$"
        }
    },
    "required": ["event_id", "booking_entity_type", "booking_entity_id", "quantity", "customer_name", "customer_email", "customer_whatsapp"],
    "additionalProperties": False
}

GET_BOOKING_DETAILS_SCHEMA = {
    "type": "object",
    "properties": {
        "booking_id": {
            "type": "string",
            "description": "The UUID booking ID from successful book_event response (e.g., '3e5e8454-0696-4114-a405-751d1cda3751'). This becomes 'bookingId' query parameter. Get this from book_event response's booking_id field. NEVER fabricate.",
            "format": "uuid"
        },
        "customer_id": {
            "type": "integer",
            "description": "The numeric customer ID from successful book_event response (e.g., 103). This becomes 'customerId' query parameter. Get this from book_event response's customer_id field. NEVER fabricate."
        }
    },
    "required": ["booking_id", "customer_id"],
    "additionalProperties": False
}


def get_all_schemas() -> Dict[str, Dict[str, Any]]:
    return {
        "get_all_events": GET_ALL_EVENTS_SCHEMA,
        "get_event_by_slug": GET_EVENT_BY_SLUG_SCHEMA,
        "book_event": BOOK_EVENT_SCHEMA,
        "get_booking_details": GET_BOOKING_DETAILS_SCHEMA,
    }