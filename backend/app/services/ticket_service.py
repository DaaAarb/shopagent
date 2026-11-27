from app.dtos import TicketRead
from app.models import Ticket
from app.repositories import UnitOfWork
from app.services.exceptions import InvalidInput
from app.services.order_service import OrderService


class TicketService:
    """Escalado a humano: el agente abre un ticket cuando no puede resolver algo."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.orders = OrderService(uow)

    def open_ticket(
        self,
        user_id: int,
        subject: str,
        description: str,
        order_id: int | None = None,
    ) -> TicketRead:
        subject, description = subject.strip(), description.strip()
        if not subject or not description:
            raise InvalidInput("El asunto y la descripción no pueden estar vacíos.")

        if order_id is not None:
            # Comprueba la propiedad del pedido (404 si es ajeno).
            self.orders.get_order(user_id, order_id)

        with self.uow:
            ticket = self.uow.tickets.add(
                Ticket(
                    user_id=user_id,
                    order_id=order_id,
                    subject=subject,
                    description=description,
                )
            )
            self.uow.commit()
            return TicketRead.model_validate(ticket)

    def list_tickets(self, user_id: int) -> list[TicketRead]:
        return [TicketRead.model_validate(t) for t in self.uow.tickets.list_for_user(user_id)]
