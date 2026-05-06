from dataclasses import dataclass, field
import uuid
from datetime import datetime
import json

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    content: str = ""
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OutboxEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    topic: str = ""
    payload: str = ""
    processed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create_for_message(cls, message: Message) -> "OutboxEvent":
        payload = {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "status": message.status,
            "created_at": message.created_at.isoformat()
        }
        return cls(
            aggregate_id=message.id,
            topic="chat.message.created",
            payload=json.dumps(payload)
        )
