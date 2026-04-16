# 🧪 Laboratory Work 1: Designing a Messaging System

**Variant 2:** Message Status Tracking
**Author:** [Твоє Прізвище та Ім'я]

## 🎯 Goal
Learn how to design software systems before coding; reason about architecture and responsibilities; use Component, Sequence, and State diagrams; document decisions using RFC and ADR.

## 🧠 Context
This document outlines the architecture for a minimal messenger system with a specific focus on **message status tracking (sent, delivered, read)** and handling client acknowledgements.

---

## 🧱 Part 1 — Component Diagram

**Focus:** The system separates message processing from status tracking. The `Status Tracking Service` is introduced to handle the high volume of delivery and read acknowledgements without overloading the main `Message Service`.

```mermaid
graph TD
    Client_A[Client A - Sender] <-->|WebSocket / REST| API[API Gateway]
    Client_B[Client B - Receiver] <-->|WebSocket / REST| API
    
    API --> Auth[Auth Service]
    API --> MS[Message Service]
    API --> STS[Status Tracking Service]
    
    MS -->|Save Message| DB[(Database)]
    MS -->|Publish Deliver Event| MQ[Message Broker]
    
    MQ -->|Push/WS to Client| Delivery[Delivery Service]
    Delivery --> Client_B
    
    Client_B -.->|1. Send Delivery Ack| API
    Client_B -.->|2. Send Read Ack| API
    
    STS -->|Update Status| DB
    STS -->|Notify Sender| MQ
    
    MQ -->|Push/WS to Sender| Delivery
    Delivery --> Client_A


Key Responsibilities:
Status Tracking Service: Exclusively handles Delivery and Read acks from clients, updates the database, and triggers events to notify the sender.

Message Broker (e.g., RabbitMQ/Kafka): Ensures reliable, asynchronous delivery of messages and status updates to the Delivery Service.

Delivery Service (WebSocket / Push): Manages real-time connections with online clients and delegates to APNs/FCM for offline clients.

🔁 Part 2 — Sequence Diagram
Scenario: A complete message lifecycle. User A sends a message to User B. The diagram shows how the system updates statuses at each stage: Sent -> Delivered -> Read.

Фрагмент коду
sequenceDiagram
    actor A as Client A (Sender)
    participant API as API Gateway
    participant DB as Database
    participant MQ as Message Queue
    actor B as Client B (Receiver)

    Note over A, API: 1. Status: SENT (1 Tick)
    A->>API: POST /messages {text: "Hello!", msgId: "uuid-1"}
    API->>DB: Save {msgId: "uuid-1", status: "Sent"}
    API-->>A: 200 OK (Ack: Sent)
    API->>MQ: Enqueue: Deliver msgId "uuid-1" to B

    Note over MQ, B: 2. Status: DELIVERED (2 Grey Ticks)
    MQ->>B: Push/WS Message {msgId: "uuid-1"}
    B->>API: POST /acks {msgId: "uuid-1", type: "Delivered"}
    API->>DB: Update {msgId: "uuid-1", status: "Delivered"}
    API->>MQ: Enqueue: Notify A -> msgId "uuid-1" Delivered
    MQ->>A: Push/WS Event: Status Update (Delivered)

    Note over B, API: 3. Status: READ (2 Blue Ticks)
    B->>B: User opens chat
    B->>API: POST /acks {msgId: "uuid-1", type: "Read"}
    API->>DB: Update {msgId: "uuid-1", status: "Read"}
    API->>MQ: Enqueue: Notify A -> msgId "uuid-1" Read
    MQ->>A: Push/WS Event: Status Update (Read)
🔄 Part 3 — State Diagram
Object: Message Lifecycle.
This state machine includes error handling for network issues between the client and the server.

Фрагмент коду
stateDiagram-v2
    [*] --> Draft: User starts typing
    Draft --> Sending: User clicks "Send"
    
    Sending --> Failed: Network Error / Timeout
    Failed --> Sending: User clicks "Retry"
    
    Sending --> Sent: Received & Saved by Server
    
    Sent --> Delivered: Delivery Ack Received from Receiver
    
    Delivered --> Read: Read Ack Received from Receiver
    
    Read --> [*]
📚 Part 4 — ADR (Architecture Decision Record)
# ADR-001: Implementing "At-Least-Once" Delivery with Idempotency for Acknowledgements
Status
Accepted

Context
In mobile networks, connections drop frequently. If the server delivers a message to Client B, but Client B loses connection before sending a Delivery Ack, the sender will incorrectly see the status as merely Sent. Furthermore, if the server retries sending the message, Client B might receive duplicates.

Decision
We will use an At-Least-Once delivery guarantee combined with Client-Side Idempotency:

Server Retries: If the Status Tracking Service does not receive a Delivery Ack within a specified timeout (e.g., 60 seconds for active WebSocket connections), the message broker will re-queue the message for delivery.

Idempotency Keys: Every message is generated with a unique UUID by the sender. If the receiver gets a message with an already processed UUID, it silently ignores the payload but resends the Delivery Ack.

Offline Sync: Upon reconnecting, clients pull a list of missed messages and push an array (batch) of pending Acks that failed to send while offline.

Alternatives
Fire-and-Forget (Rejected): The server assumes the message is delivered the moment it is pushed to the WebSocket. This leads to inaccurate statuses if the connection drops mid-flight.

Exactly-Once Delivery (Rejected): Too complex and computationally expensive to implement reliably in a distributed mobile system.

Consequences
Positive: High reliability in status tracking. Messages are never "stuck" in the Sent state if they were actually delivered. No duplicated messages shown to the user.

Negative: Increased complexity on the client side (needs local database to store processed UUIDs and queues for unsent Acks). Slight increase in network payload due to retry mechanisms.
