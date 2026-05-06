from fastapi import APIRouter
from .dto import SendMessageRequest, MessageResponse
from ..application.send_message import SendMessage, SendMessageInput
from ..application.get_pending_messages import GetPendingMessages
from src.shared.presentation.responses import Response

class ChatController:
    def __init__(
        self,
        router: APIRouter,
        send_message: SendMessage,
        get_pending_messages: GetPendingMessages
    ) -> None:
        self.router = router
        self._send_message = send_message
        self._get_pending_messages = get_pending_messages
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.post("/messages", response_model=Response[MessageResponse])(self.send_message)
        self.router.get("/messages/pending/{user_id}", response_model=Response[list[MessageResponse]])(self.get_pending_messages)

    async def send_message(self, request: SendMessageRequest, sender_id: str = "current_user_id") -> Response[MessageResponse]:
        input = SendMessageInput(
            sender_id=sender_id,
            receiver_id=request.receiver_id,
            content=request.content
        )
        message = await self._send_message.execute(input)
        return Response(
            message="Message created successfully",
            status_code=201,
            data=MessageResponse(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                status=message.status,
                created_at=message.created_at
            )
        )

    async def get_pending_messages(self, user_id: str) -> Response[list[MessageResponse]]:
        messages = await self._get_pending_messages.execute(user_id)
        data = [
            MessageResponse(
                id=m.id,
                sender_id=m.sender_id,
                receiver_id=m.receiver_id,
                content=m.content,
                status=m.status,
                created_at=m.created_at,
            ) for m in messages
        ]
        
        return Response(
            message="Pending messages retrieved successfully",
            status_code=200,
            data=data
        )
