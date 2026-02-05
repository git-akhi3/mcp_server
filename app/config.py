from pydantic import BaseModel


class Settings(BaseModel):
    EVENT_BASE_URL: str = "https://api.nyteflow.brynklabs.in/api/customer"
    TICKET_BASE_URL: str = "https://api.nyteflow.brynklabs.in/api/ticket"
    TICKET_WEB_BASE_URL: str = "https://api.nyteflow.brynklabs.in/api/ticket/web"
    TENANT_ID: str = "bigbull-tenant-123"
    TENANT_SECRET: str = "bigbull-tenant-secret-123"


settings = Settings()
