from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User, Organization
from app.schemas.auth import (
    SignupRequest, SignupResponse,
    LoginRequest, LoginResponse,
    InviteUserRequest, InviteUserResponse,
    UserResponse,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.api.deps import get_current_active_user, get_current_owner

router = APIRouter()


@router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new organization and the first user (owner).

    This is the entry point for new businesses. It:
    1. Checks the email isn't already taken
    2. Creates the Organization
    3. Creates the User as owner
    4. Returns a JWT so they're immediately logged in
    """

    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    org = Organization(
        name=request.organization_name,
        industry=request.industry,
    )
    db.add(org)
    db.flush()

    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        is_owner=True,
        organization_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(org)

    token = create_access_token(subject=str(user.id))

    return SignupResponse(
        user_id=str(user.id),
        organization_id=str(org.id),
        email=user.email,
        access_token=token,
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password, get a JWT back.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(subject=str(user.id))

    return LoginResponse(
        access_token=token,
        user_id=str(user.id),
        organization_id=str(user.organization_id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the current authenticated user's info.
    Useful for the frontend to know who's logged in and what org they belong to.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_owner=current_user.is_owner,
        organization_id=str(current_user.organization_id),
        organization_name=current_user.organization.name,
    )


@router.post("/invite", response_model=InviteUserResponse)
async def invite_user(
    request: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner),
):
    """
    Owner invites a new team member to their organization.

    In production you'd send an invite email with a setup link
    instead of accepting a password directly here.
    """
  
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        is_owner=False,
        organization_id=current_user.organization_id, 
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return InviteUserResponse(
        user_id=str(user.id),
        email=user.email,
    )
