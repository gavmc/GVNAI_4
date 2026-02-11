from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Signup ──────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    """Creates a new organization + the first user (owner)."""
    email: EmailStr
    password: str
    full_name: str
    organization_name: str
    industry: Optional[str] = None


class SignupResponse(BaseModel):
    user_id: str
    organization_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


# ── Login ───────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    organization_id: str


# ── Invite (owner adds a team member) ──────────────────────────

class InviteUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str  # In production, send an invite email instead


class InviteUserResponse(BaseModel):
    user_id: str
    email: str


# ── User info ──────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_owner: bool
    organization_id: str
    organization_name: str

    class Config:
        from_attributes = True
