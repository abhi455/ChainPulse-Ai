from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.scenario import Scenario
from backend.database.repositories.base import BaseRepository


class ScenarioRepository(BaseRepository[Scenario]):
    def __init__(self, session: Session):
        super().__init__(session, Scenario)

    def get_by_organization(self, organization_id: str) -> list[Scenario]:
        return list(
            self.session.scalars(
                select(Scenario).where(
                    Scenario.organization_id == organization_id
                )
            ).all()
        )
