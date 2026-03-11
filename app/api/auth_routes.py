from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependecies.auth import get_current_user
from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse
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
    response: Response,
    db: Session = Depends(get_db)
):

    try:

        tokens = login_user(
            db=db,
            email=data.email,
            password=data.password
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            samesite="lax",
            secure=False, # Use True in production with https
            max_age=7 * 24 * 60 * 60
        )

        return {"access_token": tokens["access_token"], "refresh_token": "Cookie", "token_type": "bearer"}

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    refresh_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:

        result = refresh_access_token(
            db=db,
            refresh_token=refresh_token
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):

    if refresh_token:
        logout_user(db, refresh_token)
        response.delete_cookie("refresh_token")

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


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user=Depends(get_current_user)
):
    """
    Returns the currently authenticated user details.
    """
    return current_user