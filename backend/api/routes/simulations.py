from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas.simulations import SimulationRequest
from backend.auth.dependencies import get_current_user
from backend.database.database import get_db
from backend.database.models import User, Scenario as DBScenario, SimulationRun
from backend.database.repositories import ScenarioRepository, SimulationRepository
from backend.simulation import Scenario, SimulationService


router = APIRouter(
    prefix="/simulations",
    tags=["Simulations"],
)


@router.post("/run")
def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        calculation_scenario = Scenario(
            name=request.scenario.name,
            demand_change_pct=request.scenario.demand_change_pct,
            lead_time_change_pct=request.scenario.lead_time_change_pct,
            inventory_change_pct=request.scenario.inventory_change_pct,
        )

        result = SimulationService.run(
            scenario=calculation_scenario,
            average_daily_demand=request.average_daily_demand,
            demand_std=request.demand_std,
            lead_time_days=request.lead_time_days,
            current_inventory=request.current_inventory,
            annual_demand=request.annual_demand,
            ordering_cost=request.ordering_cost,
            holding_cost=request.holding_cost,
            service_level_z=request.service_level_z,
        )

        db_scenario = DBScenario(
            organization_id=user.organization_id,
            name=request.scenario.name,
            scenario_type="inventory_simulation",
            description="Inventory simulation scenario",
            parameters={
                "demand_change_pct": request.scenario.demand_change_pct,
                "lead_time_change_pct": request.scenario.lead_time_change_pct,
                "inventory_change_pct": request.scenario.inventory_change_pct,
                "average_daily_demand": request.average_daily_demand,
                "demand_std": request.demand_std,
                "lead_time_days": request.lead_time_days,
                "current_inventory": request.current_inventory,
                "annual_demand": request.annual_demand,
                "ordering_cost": request.ordering_cost,
                "holding_cost": request.holding_cost,
                "service_level_z": request.service_level_z,
            },
        )

        scenario_repo = ScenarioRepository(db)
        simulation_repo = SimulationRepository(db)

        scenario_record = scenario_repo.add(db_scenario)

        simulation_record = SimulationRun(
            scenario_id=scenario_record.id,
            status="completed",
            bullwhip_index=None,
            service_level=None,
            inventory_impact=None,
            results=result,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        simulation_repo.add(simulation_record)

        db.commit()

        return result

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise
