from sqlalchemy.orm import Session

from backend.database.models import Organization
from backend.database.repositories import OrganizationRepository


class OrganizationService:
    def __init__(self, session: Session):
        self.repository = OrganizationRepository(session)

    def create(self, name: str) -> Organization:
        name = name.strip()

        if not name:
            raise ValueError("Organization name cannot be empty")

        existing = self.repository.get_by_name(name)

        if existing:
            raise ValueError("Organization already exists")

        organization = Organization(name=name)

        return self.repository.add(organization)

    def get(self, organization_id: str) -> Organization | None:
        return self.repository.get_by_id(organization_id)

    def list(self) -> list[Organization]:
        return self.repository.get_all()
