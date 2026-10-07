from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def create(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)

    return db.scalars(statement).first()


def get_all(db: Session) -> list[User]:
    statement = select(User)
    result = db.scalars(statement)

    return list(result)


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()