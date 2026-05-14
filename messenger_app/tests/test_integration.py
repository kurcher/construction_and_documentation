import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from storage.database import Base, get_db

# Використовуємо in-memory БД для чистоти тестів
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_full_messaging_flow_with_status_tracking():
    # 1. Створення користувачів
    resp_u1 = client.post("/users", json={"name": "User A"})
    assert resp_u1.status_code == 201
    user_a_id = resp_u1.json()["id"]

    resp_u2 = client.post("/users", json={"name": "User B"})
    assert resp_u2.status_code == 201

    # 2. Створення розмови
    resp_conv = client.post("/conversations", json={"type": "direct"})
    assert resp_conv.status_code == 201
    conv_id = resp_conv.json()["id"]

    # 3. Відправка повідомлення (Перевірка статусу за замовчуванням: sent)
    msg_payload = {
        "conversation_id": conv_id,
        "sender_id": user_a_id,
        "text": "Hello API Integration Test!"
    }
    resp_msg = client.post("/messages", json=msg_payload)
    assert resp_msg.status_code == 201
    msg_data = resp_msg.json()
    assert msg_data["text"] == "Hello API Integration Test!"
    assert msg_data["status"] == "sent"
    message_id = msg_data["id"]

    # 4. Симуляція отримання пакету пристроєм (ACK -> Delivered)
    resp_ack = client.patch(f"/messages/{message_id}/status", json={"status": "delivered"})
    assert resp_ack.status_code == 200
    assert resp_ack.json()["status"] == "delivered"

    # 5. Симуляція відкриття чату користувачем (Read)
    resp_read = client.patch(f"/messages/{message_id}/status", json={"status": "read"})
    assert resp_read.status_code == 200
    assert resp_read.json()["status"] == "read"

    # 6. Перевірка історії повідомлень
    resp_history = client.get(f"/conversations/{conv_id}/messages")
    assert resp_history.status_code == 200
    history = resp_history.json()
    assert len(history) == 1
    assert history[0]["status"] == "read"

def test_error_handling():
    # Відправка порожнього повідомлення
    resp = client.post("/messages", json={"conversation_id": 1, "sender_id": 1, "text": ""})
    assert resp.status_code == 400

    # Неіснуючий відправник
    resp = client.post("/messages", json={"conversation_id": 1, "sender_id": 999, "text": "Test"})
    assert resp.status_code == 404