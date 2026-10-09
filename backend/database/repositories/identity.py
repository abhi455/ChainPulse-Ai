from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.identity import UserIdentity
from backend.database.repositories.base import BaseRepository


class UserIdentityRepository(BaseRepository[UserIdentity]):

    def __init__(self, session: Session):
        super().__init__(session, UserIdentity)

    def get_by_provider_subject(
        self,
        provider: str,
        provider_subject: str,
    ) -> UserIdentity | None:

        return self.session.scalar(
            select(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_subject == provider_subject,
            )
        )

    def get_by_user_and_provider(
        self,
        user_id: str,
        provider: str,
    ) -> UserIdentity | None:

        return self.session.scalar(
            select(UserIdentity).where(
                UserIdentity.user_id == user_id,
                UserIdentity.provider == provider,
            )
        )
