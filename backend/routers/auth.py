from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import create_access_token, get_password_hash, verify_password
from database import get_db
from models import User
from schemas import TokenOut, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenOut:
    existing_user = await db.scalar(select(User).where(User.email == user_data.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        notification_email=str(user_data.notification_email) if user_data.notification_email else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenOut(access_token=create_access_token(user.id), token_type="bearer")


@router.post("/login", response_model=TokenOut)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await db.scalar(select(User).where(User.email == credentials.email))
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenOut(access_token=create_access_token(user.id), token_type="bearer")
