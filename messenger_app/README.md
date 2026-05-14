# Messenger System Prototype (Lab 2)

Цей проект є реалізацією прототипу месенджера з підтримкою відстеження статусу повідомлень (**Variant 2: Message Status Tracking**) на базі архітектури, розробленої в Лабораторній роботі 1.

## Стек технологій
* **Мова:** Python 3.10+
* **Фреймворк:** FastAPI
* **ORM та БД:** SQLAlchemy + SQLite
* **Валідація:** Pydantic v2
* **Тестування:** PyTest + HTTP TestClient

## Запуск проекту

1. Встановіть залежності:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic pytest