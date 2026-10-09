from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.auth.dependencies import get_current_user
from backend.auth.schemas import (
    LoginRequest,
    OnboardRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from backend.database.models import Organization, User
from backend.services import OrganizationService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


@router.post(
    "/onboard",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def onboard(
    request: OnboardRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Create a new ChainPulse organization and its
    first administrator in one database transaction.
    """

    organization_name = request.organization_name.strip()
    name = request.name.strip()
    email = str(request.email).strip().lower()

    if not organization_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name cannot be empty.",
        )

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty.",
        )

    existing_user = _get_user_by_email(
        db,
        email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    existing_organization = (
        db.query(Organization)
        .filter(
            Organization.name == organization_name
        )
        .first()
    )

    if existing_organization is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this name already exists.",
        )

    try:
        organization = OrganizationService(db).create(
            organization_name
        )

        user = User(
            organization_id=organization.id,
            name=name,
            email=email,
            password_hash=hash_password(
                request.password
            ),
            role="admin",
            is_active=True,
        )

        db.add(user)

        db.commit()
        db.refresh(user)

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The account could not be created because "
                "the email or organization already exists."
            ),
        ) from exc

    except Exception:
        db.rollback()
        raise

    token = create_access_token(
        subject=user.id,
        organization_id=user.organization_id,
    )

    return TokenResponse(
        access_token=token,
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = _get_user_by_email(
        db,
        request.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        organization_id=request.organization_id,
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create the user.",
        ) from exc

    except Exception:
        db.rollback()
        raise

    token = create_access_token(
        subject=user.id,
        organization_id=user.organization_id,
    )

    return TokenResponse(
        access_token=token,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    email = str(request.email).strip().lower()

    user = _get_user_by_email(
        db,
        email,
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(
            request.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token = create_access_token(
        subject=user.id,
        organization_id=user.organization_id,
    )

    return TokenResponse(
        access_token=token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )
