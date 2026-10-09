from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.simulation import SimulationRun
from backend.database.repositories.base import BaseRepository


class SimulationRepository(BaseRepository[SimulationRun]):
    def __init__(self, session: Session):
        super().__init__(session, SimulationRun)

    def get_by_scenario(self, scenario_id: str) -> list[SimulationRun]:
        return list(
            self.session.scalars(
                select(SimulationRun).where(
                    SimulationRun.scenario_id == scenario_id
                )
            ).all()
        )
