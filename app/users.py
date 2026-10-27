import uuid
import logging
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db

import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("sharethat.users")

SECRET = os.getenv("JWT_SECRET", "sharethat-insecure-dev-jwt-secret-key-change-in-prod")
JWT_LIFETIME_SECONDS = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User registered successfully: {user.id} ({user.email})")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(f"Password reset requested for user {user.id}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(f"Verification requested for user {user.id}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy():
    return JWTStrategy(secret=SECRET, lifetime_seconds=JWT_LIFETIME_SECONDS)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)