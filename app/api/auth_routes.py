from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependecies.auth import get_current_user
from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
    )

from app.services.auth_service import register_user, forgot_password

from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.services.auth_service import login_user, logout_user, logout_all_devices
from app.schemas.auth_schema import RefreshRequest, RefreshResponse
from app.services.auth_service import refresh_access_token


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=RegisterResponse)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:

        user = register_user(
            db=db,
            email=data.email,
            username=data.username,
            password=data.password
        )

        return user

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        tokens = login_user(
            db=db,
            email=data.email,
            password=data.password
        )

        return tokens

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    try:

        result = refresh_access_token(
            db=db,
            refresh_token=data.refresh_token
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):

    logout_user(db, data.refresh_token)

    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    logout_all_devices(db, current_user.id)

    return {"message": "Logged out from all devices"}


@router.post("/forgot-password")
def forgot_password_route(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    token = forgot_password(db, data.email)

    return {"message": "Reset link sent"}


@router.post("/reset-password")
def reset_password_route(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    reset_password(
        db,
        data.token,
        data.new_password
    )

    return {"message": "Password reset successful"}