from fastapi import APIRouter, status

from app.api.deps import CurrentUserId, TicketServiceDep
from app.dtos import TicketCreate, TicketRead

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketRead])
def list_tickets(user_id: CurrentUserId, tickets: TicketServiceDep):
    return tickets.list_tickets(user_id)


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def open_ticket(body: TicketCreate, user_id: CurrentUserId, tickets: TicketServiceDep):
    return tickets.open_ticket(user_id, body.subject, body.description, body.order_id)
