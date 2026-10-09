from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.organization import Organization
from backend.database.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: Session):
        super().__init__(session, Organization)

    def get_by_name(self, name: str) -> Organization | None:
        return self.session.scalar(
            select(Organization).where(Organization.name == name)
        )
