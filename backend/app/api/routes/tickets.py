from fastapi import APIRouter, status

from app.api.deps import CurrentUserId, TicketServiceDep
from app.api.schemas import TicketCreate, TicketRead

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketRead])
def list_tickets(user_id: CurrentUserId, tickets: TicketServiceDep):
    return [
        TicketRead.model_validate(t, from_attributes=True)
        for t in tickets.list_tickets(user_id)
    ]


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def open_ticket(body: TicketCreate, user_id: CurrentUserId, tickets: TicketServiceDep):
    ticket = tickets.open_ticket(user_id, body.subject, body.description, body.order_id)
    return TicketRead.model_validate(ticket, from_attributes=True)
