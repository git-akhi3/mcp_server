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


async def tool_book_event(input_data):
    try:
        data = await EventAPIService.book_event(
            event_id=input_data["event_id"],
            booking_entity_type=input_data["booking_entity_type"],
            booking_entity_id=input_data["booking_entity_id"],
            quantity=input_data["quantity"],
            customer_name=input_data["customer_name"],
            customer_email=input_data["customer_email"],
            customer_whatsapp=input_data["customer_whatsapp"],
        )

        return {
            "success": True,
            "message": "Booking created successfully",
            "booking_id": data.get("bookingId"),
            "customer_id": data.get("customerId"),
            "razorpay_order_id": data.get("razorPayOrderId"),
        }

    except Exception as e:
        print(f"[ERROR] book_event failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }


async def tool_get_booking_details(input_data):
    try:
        data = await EventAPIService.get_booking_details(
            booking_id=input_data["booking_id"],
            customer_id=input_data["customer_id"],
        )

        # Extract key booking information
        confirmed_booking = data.get("confirmedBooking", {})
        event = data.get("event", {})
        ticket_type = data.get("ticketType", {})
        customer = data.get("customer", {})

        return {
            "success": True,
            "booking": {
                "id": data.get("id"),
                "status": data.get("status"),
                "ticket_number": confirmed_booking.get("ticketNumber"),
                "quantity": data.get("quantity"),
                "booking_price": data.get("bookingPrice"),
                "paid_amount": data.get("paidAmount"),
                "max_pax": confirmed_booking.get("maxPax"),
                "checked_in_count": confirmed_booking.get("checkedInCount"),
            },
            "event": {
                "id": event.get("id"),
                "title": event.get("title"),
                "date_time": event.get("eventDateTime"),
                "genre": event.get("genre"),
                "slug": event.get("slug"),
            },
            "ticket_type": {
                "id": ticket_type.get("id"),
                "name": ticket_type.get("name"),
                "description": ticket_type.get("description"),
                "price": ticket_type.get("currentPrice"),
            },
            "customer": {
                "id": customer.get("id"),
                "name": customer.get("firstName"),
                "email": customer.get("email"),
                "phone": customer.get("phoneNumber"),
            },
            "qr_code": confirmed_booking.get("qrCode"),
        }

    except Exception as e:
        print(f"[ERROR] get_booking_details failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }
