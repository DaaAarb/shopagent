from sqlmodel import col

from app.models import Ticket
from app.repositories.base import Repository


class TicketRepository(Repository[Ticket]):
    model = Ticket

    def list_for_user(self, user_id: int) -> list[Ticket]:
        """Tickets de un usuario, del más reciente al más antiguo."""
        return self.find(
            Ticket.user_id == user_id,
            order_by=(col(Ticket.created_at).desc(), col(Ticket.id).desc()),
        )
