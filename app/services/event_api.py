from app.utils.http import get_json
from app.config import settings


class EventAPIService:

    @staticmethod
    def _get_headers():
        """Get the required tenant headers for all API calls"""
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
