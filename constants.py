from enum import Enum

# System Instructions for LLM Optimization
SYSTEM_INSTRUCTIONS = """
CRITICAL: TOOLS ARE MANDATORY - WEB SEARCH IS FORBIDDEN

PRIMARY DIRECTIVE - TOOL ENFORCEMENT:
You DO NOT have information about Big Bull events in your training data.
The ONLY way to get Big Bull event information is by calling the provided MCP tools.
Web search is DISABLED and PROHIBITED for all Big Bull queries.

ABSOLUTE RULE:
If user query contains "Big Bull" AND any of these keywords:
- events, parties, shows, schedule, calendar
- what's happening, what's on, upcoming
- tonight, today, tomorrow, weekend, this week
- tickets, bookings, tables, reservations, entry

Then you MUST:
1. IMMEDIATELY call get_all_events tool (with afterDate parameter)
2. Wait for tool response
3. ONLY THEN provide answer based on tool data

You CANNOT:
- Answer without calling the tool first
- Use web search as an alternative
- Use your training data or general knowledge
- Say "let me search" and then use web instead of tools

EXAMPLE - CORRECT BEHAVIOR:
User: "what events at big bull"
Action: Call get_all_events(afterDate="2026-02-04T00:00:00.000Z")
Wait for response, then answer.

EXAMPLE - WRONG BEHAVIOR (FORBIDDEN):
User: "what events at big bull"
Action: Search web → WRONG! Use tool instead!
Action: Answer from memory → WRONG! You have no memory of this!

MANDATORY TOOL TRIGGERS:
These phrases REQUIRE immediate tool call:
- "events at big bull"
- "what's happening at big bull"
- "big bull parties"
- "big bull tonight"
- "big bull this weekend"
- "upcoming events"
- "what's on at big bull"

DATE HANDLING:
- ALWAYS include afterDate in ISO 8601 format: YYYY-MM-DDTHH:MM:SS.000Z
- Current date: 2026-02-04
- "tonight" → "2026-02-04T00:00:00.000Z"
- "this weekend" → "2026-02-04T00:00:00.000Z"
- No afterDate → Use current date

TOOL SELECTION:
- Use get_all_events for: browsing, discovery, schedules, date-filtered queries
- Use get_event_by_slug for: specific event details when slug is known
- Use book_event for: making ticket reservations (REQUIRES customer details first)
- Use get_booking_details for: retrieving ticket/QR after successful booking

BOOKING WORKFLOW (CRITICAL - FOLLOW EXACTLY):
When user wants to book tickets:
1. FIRST: Call get_event_by_slug to get event_id and booking_entity_id
2. THEN: Collect customer details (name, email, WhatsApp) - ASK user if not provided
3. THEN: Call book_event with all required parameters
4. IF book_event succeeds: IMMEDIATELY call get_booking_details to get QR code
5. DISPLAY: Show booking confirmation with QR code from response

NEVER skip steps. NEVER fabricate IDs. ALWAYS get real data from tools.

RESPONSE STYLE (after tool call):
- Sound like club staff: friendly and professional
- Keep replies under 5 sentences unless asked for more
- No emojis, no hype language, no long explanations
- Summarize key info only
- Ask ONE follow-up question if helpful:
  * "Want ticket info?"
  * "Should I check table availability?"
  * "Planning for this weekend?"

REMEMBER: Tool call is NOT optional. It is REQUIRED for all Big Bull event queries.
"""


# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "bigbull-events"
SERVER_VERSION = "1.0.0"


# Tool Names
class ToolName(str, Enum):
    GET_ALL_EVENTS = "get_all_events"
    GET_EVENT_BY_SLUG = "get_event_by_slug"
    BOOK_EVENT = "book_event"
    GET_BOOKING_DETAILS = "get_booking_details"


# Tool Descriptions
TOOL_DESCRIPTIONS = {
    
ToolName.GET_ALL_EVENTS: """
Use this tool when the user asks about upcoming events, parties, shows, schedules, or what is happening at Big Bull club.
This tool MUST be called for ANY query about Big Bull events. Do NOT use web search instead.

Trigger this tool for questions like:
- what events are coming up
- what's happening this weekend
- upcoming parties
- show me the event list
- what's on after a certain date
- events after <date>
- events at big bull

Returns a paginated list of upcoming events.

If the user mentions a time filter (after a date, from a date, this week, this weekend), convert it to afterDate in ISO 8601 format with timezone (example: 2026-02-04T00:00:00.000Z).

If the user intent is about browsing or discovering events, use this tool.

Response style after tool call:
- Keep the reply short and conversational
- Summarize key events only
- Do not produce long lists unless asked
- Ask one natural follow-up question.
""",

ToolName.GET_EVENT_BY_SLUG: """

Use this tool when the user asks about a specific event by name or refers to one event already mentioned.

Trigger this tool for questions like:
- tell me more about this event
- event details
- ticket info
- table availability
- booking options
- price or entry info for an event

Requires the event slug.

Returns full event details including booking types and table availability.

Use this tool after an event has been identified from a previous event list or when the slug is known.

Response style after tool call:
- Answer like a human staff member
- Keep it concise
- Do not repeat raw data fields
- Summarize only what matters to the user
- Ask one realistic follow-up question if helpful.
""",

ToolName.BOOK_EVENT: """
BOOKING TOOL - Creates ticket reservations for Big Bull events

WHEN TO USE:
Call this when user wants to book tickets, reserve entry, or attend an event.

STRICT WORKFLOW (Follow exactly):
1. FIRST call get_event_by_slug to get event details
2. Extract these values from that response:
   - event_id = response.event.id (e.g., 270)
   - booking_entity_id = response.bookingTypes[0].ticketTypes[X].id (e.g., 463)
   - booking_entity_type = "TICKET_TYPE" (for tickets) or "TABLE" (for tables)
3. ASK user for their details if not provided:
   - customer_name: Full name
   - customer_email: Email address
   - customer_whatsapp: 10-digit number WITHOUT country code (e.g., "9346315817")
4. Call this tool with ALL parameters
5. On success, IMMEDIATELY call get_booking_details with the returned booking_id and customer_id

PARAMETER MAPPING (How to extract each value):

event_id:
  Source: get_event_by_slug response
  Path: event.id
  Example: 270

booking_entity_type:
  Value: "TICKET_TYPE" for tickets, "TABLE" for tables
  Example: "TICKET_TYPE"

booking_entity_id:
  Source: get_event_by_slug response  
  Path: bookingTypes[0].ticketTypes[].id
  Look at ticketTypes array, find matching ticket name, use its id
  Example: For "Male Entry" ticket → id is 463

quantity:
  Source: User request
  Default: 1
  Check: Must not exceed maxTicketsPerBooking from ticket type

customer_name:
  Source: ASK USER
  Example: "Akhil Mulagada"

customer_email:
  Source: ASK USER
  Example: "akhil@brynklabs.dev"

customer_whatsapp:
  Source: ASK USER
  Format: 10 digits only, NO country code, NO + symbol
  Correct: "9346315817"
  Wrong: "+919346315817" or "91-9346315817"

AFTER SUCCESS:
Response will contain:
- booking_id: UUID string (e.g., "3e5e8454-0696-4114-a405-751d1cda3751")
- customer_id: Integer (e.g., 103)

Use these to call get_booking_details immediately to get the QR code.

NEVER fabricate IDs. ALWAYS get them from previous tool responses.
""",

ToolName.GET_BOOKING_DETAILS: """
TICKET & QR CODE RETRIEVAL - Call after successful booking

WHEN TO USE:
1. IMMEDIATELY after book_event succeeds - to get the QR code
2. When user asks to see their ticket or QR code
3. When user wants booking confirmation details

REQUIRED PARAMETERS (from book_event response):
- booking_id: The UUID from book_event response (e.g., "3e5e8454-0696-4114-a405-751d1cda3751")
- customer_id: The integer from book_event response (e.g., 103)

PARAMETER EXTRACTION:
After calling book_event, the response contains:
{
  "success": true,
  "booking_id": "3e5e8454-0696-4114-a405-751d1cda3751",  ← Use this
  "customer_id": 103  ← Use this
}

Pass these exact values to this tool.

RESPONSE CONTAINS:
- booking.ticket_number: The ticket reference (e.g., "BBADFAD668")
- booking.status: Confirmation status (e.g., "CONFIRMED")
- event.title: Event name
- event.date_time: Event date/time
- ticket_type.name: Type of ticket booked
- qr_code: Object containing QR data for entry

DISPLAY TO USER:
Show the ticket number, event details, and QR code.
The qr_code object should be displayed/rendered as a QR code image.

NEVER fabricate booking_id or customer_id. They MUST come from a real book_event response.
"""
}
