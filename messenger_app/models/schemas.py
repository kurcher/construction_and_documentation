from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from storage.database import MessageStatus

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, example="Alice")

class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    type: str = Field(default="direct", example="direct")

class ConversationResponse(BaseModel):
    id: int
    type: str

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    text: str = Field(..., min_length=1, example="Hello, World!")

class MessageStatusUpdate(BaseModel):
    status: MessageStatus

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    text: str
    status: MessageStatus
    created_at: datetime

    class Config:
        from_attributes = True