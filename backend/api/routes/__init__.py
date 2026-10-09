from backend.api.routes.ai import router as ai_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.bullwhip import router as bullwhip_router
from backend.api.routes.decisions import router as decisions_router
from backend.api.routes.demand import router as demand_router
from backend.api.routes.forecasting import router as forecasting_router
from backend.api.routes.inventory import router as inventory_router
from backend.api.routes.intelligence import router as intelligence_router
from backend.api.routes.organizations import router as organizations_router
from backend.api.routes.products import router as products_router
from backend.api.routes.simulations import router as simulations_router
from backend.api.routes.suppliers import router as suppliers_router

__all__ = [
    "ai_router",
    "auth_router",
    "bullwhip_router",
    "decisions_router",
    "demand_router",
    "forecasting_router",
    "inventory_router",
    "intelligence_router",
    "organizations_router",
    "products_router",
    "simulations_router",
    "suppliers_router",
]
