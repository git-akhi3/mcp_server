from app.utils.http import get_json, post_json
from app.config import settings


class EventAPIService:

    @staticmethod
    def _get_headers():
        return {
            "Content-Type": "application/json",
            "X-Tenant-Id": settings.TENANT_ID,
            "X-Tenant-Secret": settings.TENANT_SECRET,
        }

    @staticmethod
    async def get_all_events(
        page: int,
        size: int,
        sortBy: str,
        sortDir: str,
        afterDate: str,
    ):
        url = f"{settings.EVENT_BASE_URL}/events"

        params = {
            "page": page,
            "size": size,
            "sortBy": sortBy,
            "sortDir": sortDir,
            "afterDate": afterDate,
        }

        data = await get_json(url, params=params, headers=EventAPIService._get_headers())

        if not data.get("success"):
            raise ValueError("Upstream API returned success=false")

        return data["data"]

    @staticmethod
    async def get_event_by_slug(slug: str):
        url = f"{settings.EVENT_BASE_URL}/events/{slug}"

        data = await get_json(url, headers=EventAPIService._get_headers())

        if not data.get("success"):
            raise ValueError("Event not found")

        return data["data"]

    @staticmethod
    async def book_event(
        event_id: int,
        booking_entity_type: str,
        booking_entity_id: int,
        quantity: int,
        customer_name: str,
        customer_email: str,
        customer_whatsapp: str,
    ):
        url = f"{settings.TICKET_WEB_BASE_URL}/book"

        payload = {
            "eventId": event_id,
            "bookingEntityType": booking_entity_type,
            "bookingEntityId": booking_entity_id,
            "quantity": quantity,
            "customerDetails": {
                "name": customer_name,
                "email": customer_email,
                "whatsappNo": customer_whatsapp,
            }
        }

        print(f"[DEBUG] book_event URL: {url}")
        print(f"[DEBUG] book_event payload: {payload}")
        print(f"[DEBUG] book_event headers: {EventAPIService._get_headers()}")

        data = await post_json(url, json_data=payload, headers=EventAPIService._get_headers())

        print(f"[DEBUG] book_event response: {data}")

        if not data.get("success"):
            raise ValueError(data.get("message", "Booking failed"))

        return data["data"]

    @staticmethod
    async def get_booking_details(booking_id: str, customer_id: int):
        url = f"{settings.TICKET_BASE_URL}/booking-details"

        params = {
            "bookingId": booking_id,
            "customerId": customer_id,
        }

        data = await get_json(url, params=params, headers=EventAPIService._get_headers())

        if not data.get("success"):
            raise ValueError(data.get("message", "Failed to fetch booking details"))

        return data["data"]
