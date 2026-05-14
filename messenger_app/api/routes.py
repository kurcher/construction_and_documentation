from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from storage.database import get_db
from models.schemas import (
    UserCreate, UserResponse,
    ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse, MessageStatusUpdate
)
from services import message_service

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=201)
def api_create_user(user: UserCreate, db: Session = Depends(get_db)):
    return message_service.create_user(db, user)

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
def api_create_conversation(conv: ConversationCreate, db: Session = Depends(get_db)):
    return message_service.create_conversation(db, conv)

@router.post("/messages", response_model=MessageResponse, status_code=201)
def api_send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    return message_service.send_message(db, msg)

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def api_get_messages(conversation_id: int, db: Session = Depends(get_db)):
    return message_service.get_conversation_messages(db, conversation_id)

# Окремий ендпоінт для Варіанту 2: Message Status Tracking
@router.patch("/messages/{message_id}/status", response_model=MessageResponse)
def api_update_status(message_id: int, status_update: MessageStatusUpdate, db: Session = Depends(get_db)):
    return message_service.update_message_status(db, message_id, status_update)