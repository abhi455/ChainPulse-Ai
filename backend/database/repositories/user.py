from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.user import User
from backend.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.email == email)
        )

    def get_by_organization(self, organization_id: str) -> list[User]:
        return list(
            self.session.scalars(
                select(User).where(User.organization_id == organization_id)
            ).all()
        )
