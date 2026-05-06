from pydantic import BaseModel
from datetime import datetime

class SendMessageRequest(BaseModel):
    receiver_id: str
    content: str

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    content: str
    status: str
    created_at: datetime
