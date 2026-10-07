from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import user as repository
from app.schemas.user import UserCreate


def create(
    db: Session,
    user_data: UserCreate,
) -> User:
    existing = repository.get_by_email(
        db,
        user_data.email,
    )

    if existing:
        raise ValueError("User with this email already exists")

    return repository.create(db, user_data)