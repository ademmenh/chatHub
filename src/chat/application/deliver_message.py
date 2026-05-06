import logging
from ..domain.ports import IMessageBroker, ISocketGateway

class DeliverMessage:
    """Application use-case: consume broker events and deliver via the socket gateway."""

    def __init__(self, broker: IMessageBroker, gateway: ISocketGateway, logger: logging.Logger) -> None:
        self._broker = broker
        self._gateway = gateway
        self._logger = logger

    async def execute(self) -> None:
        """Start consuming `chat.message.created` events and push to the gateway."""
        await self._broker.consume(
            queue_name="ws_chat_queue",
            routing_key="chat.message.created",
            callback=self._on_message,
        )

    async def _on_message(self, payload: dict) -> None:
        receiver_id = payload.get("receiver_id")
        if receiver_id:
            self._logger.info("Delivering message to user %s", receiver_id)
            await self._gateway.send_to_user(receiver_id, "new_message", payload)
