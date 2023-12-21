from sqlalchemy.orm import Session
from src.database.models import User
from src.services.auth import get_password_hash

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def register_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


