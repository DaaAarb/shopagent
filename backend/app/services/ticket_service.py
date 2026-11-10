from collections.abc import Sequence

from sqlmodel import Session, col, select

from app.models import Ticket
from app.services.exceptions import InvalidInput
from app.services.order_service import OrderService


class TicketService:
    """Escalado a humano: el agente abre un ticket cuando no puede resolver algo."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.orders = OrderService(session)

    def open_ticket(
        self,
        user_id: int,
        subject: str,
        description: str,
        order_id: int | None = None,
    ) -> Ticket:
        subject, description = subject.strip(), description.strip()
        if not subject or not description:
            raise InvalidInput("El asunto y la descripción no pueden estar vacíos.")

        if order_id is not None:
            # Reutiliza la comprobación de propiedad: no se puede abrir un
            # ticket sobre el pedido de otra persona (ni saber si existe).
            self.orders.get_order(user_id, order_id)

        ticket = Ticket(
            user_id=user_id, order_id=order_id, subject=subject, description=description
        )
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def list_tickets(self, user_id: int) -> Sequence[Ticket]:
        statement = (
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(col(Ticket.created_at).desc(), col(Ticket.id).desc())
        )
        return self.session.exec(statement).all()
