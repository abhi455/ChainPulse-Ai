from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.data_connection import DataConnection
from backend.database.repositories.base import BaseRepository


class DataConnectionRepository(
    BaseRepository[DataConnection]
):

    def __init__(self, session: Session):
        super().__init__(
            session,
            DataConnection,
        )

    def get_by_organization(
        self,
        organization_id: str,
    ) -> list[DataConnection]:

        return list(
            self.session.scalars(
                select(DataConnection)
                .where(
                    DataConnection.organization_id
                    == organization_id
                )
                .order_by(
                    DataConnection.created_at.desc()
                )
            ).all()
        )

    def get_for_organization(
        self,
        organization_id: str,
        connection_id: str,
    ) -> DataConnection | None:

        return self.session.scalar(
            select(DataConnection).where(
                DataConnection.id == connection_id,
                DataConnection.organization_id
                == organization_id,
            )
        )
