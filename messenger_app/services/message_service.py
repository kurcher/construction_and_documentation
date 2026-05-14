from sqlalchemy.orm import Session
from fastapi import HTTPException
from storage.database import UserDB, ConversationDB, MessageDB, MessageStatus
from models.schemas import UserCreate, ConversationCreate, MessageCreate, MessageStatusUpdate


def create_user(db: Session, user: UserCreate):
    db_user = UserDB(name=user.name.strip())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_conversation(db: Session, conv: ConversationCreate):
    db_conv = ConversationDB(type=conv.type)
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv


def send_message(db: Session, msg: MessageCreate):
    if not msg.text or not msg.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    sender = db.query(UserDB).filter(UserDB.id == msg.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender user does not exist")

    conv = db.query(ConversationDB).filter(ConversationDB.id == msg.conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation does not exist")

    db_msg = MessageDB(
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        text=msg.text.strip(),
        status=MessageStatus.SENT  # Початковий статус завжди Sent
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


def get_conversation_messages(db: Session, conversation_id: int):
    conv = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation does not exist")

    return db.query(MessageDB).filter(MessageDB.conversation_id == conversation_id).order_by(
        MessageDB.created_at.asc()).all()


def update_message_status(db: Session, message_id: int, update_data: MessageStatusUpdate):
    db_msg = db.query(MessageDB).filter(MessageDB.id == message_id).first()
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")

    # Оновлюємо статус на основі підтверджень клієнта (ACKs)
    db_msg.status = update_data.status
    db.commit()
    db.refresh(db_msg)
    return db_msg