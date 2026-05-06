from ..domain.entity import Message
from ..infrastructure.repository import ChatRepository

class GetPendingMessages:
    def __init__(self, repository: ChatRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: str) -> list[Message]:
        return await self._repository.get_pending_messages(user_id)
