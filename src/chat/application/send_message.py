from dataclasses import dataclass
from ..domain.entity import Message, OutboxEvent
from ..infrastructure.repository import ChatRepository

@dataclass
class SendMessageInput:
    sender_id: str
    receiver_id: str
    content: str

class SendMessage:
    def __init__(self, repository: ChatRepository) -> None:
        self._repository = repository

    async def execute(self, input: SendMessageInput) -> Message:
        message = Message(
            sender_id=input.sender_id,
            receiver_id=input.receiver_id,
            content=input.content,
        )
        event = OutboxEvent.create_for_message(message)
        await self._repository.save_message_and_event(message, event)
        return message
