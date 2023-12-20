from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from src.database.db import SessionLocal
from src.database.models import User
from src.repository import contacts
from src.schemas import ContactResponse, ContactUpdate, ContactSchema
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=['contacts'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactSchema, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    new_contact = contacts.create_contact(db, contact.model_dump(), current_user.id)
    if new_contact is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return new_contact


@router.get("/", response_model=list[ContactResponse])
def get_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    db_contacts = contacts.get_contacts(db, current_user.id, skip, limit)
    return db_contacts


@router.get("/search")
def search_contacts(first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None,
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_contact = contacts.search_contacts(db, current_user.id, first_name, last_name, email)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return db_contact


@router.get("/birthdays")
def upcoming_birthdays(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return contacts.get_upcoming_birthdays(db, current_user.id)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_contact = contacts.get_contact(db, current_user.id, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, updated_contact: ContactUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_contact = contacts.update_contact(db, current_user.id, contact_id,
                                         updated_contact.model_dump(exclude_unset=True))
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return db_contact


@router.delete("/{contact_id}", response_model=ContactResponse)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_contact = contacts.delete_contact(db, current_user.id, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return db_contact
