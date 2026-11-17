import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import require_roles
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.schemas.user import UserRegister, UserResponse, UserLogin, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter()


# REGISTER API
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        organization = Organization(
            name=f"{user_data.full_name}'s Organization",
            slug=f"org-{uuid.uuid4().hex[:12]}"
        )

        db.add(organization)
        db.flush()

        hashed_password = hash_password(user_data.password)

        new_user = User(
            organization_id=organization.id,
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse(
            id=str(new_user.id),
            full_name=new_user.full_name,
            email=new_user.email,
            role=new_user.role,
            is_active=new_user.is_active
        )

    except Exception:
        db.rollback()
        raise


# LOGIN API
@router.post("/login", response_model=Token)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.get("/admin-only")
def admin_dashboard(
    current_user: User = Depends(require_roles("admin"))
):
    return {
        "message": "Welcome to the Admin Dashboard",
        "user": current_user.full_name,
        "role": current_user.role
    }

