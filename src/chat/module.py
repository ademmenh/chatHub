import logging
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine
from .application.send_message import SendMessage
from .application.get_pending_messages import GetPendingMessages
from .infrastructure.repository import ChatRepository
from .infrastructure.rabbitmq_adapter import RabbitMQAdapter
from .infrastructure.outbox_processor import OutboxProcessor
from .presentation.controller import ChatController
from src.config.domain.interface import IConfig


class ChatModule:
    def __init__(self, engine: AsyncEngine, config: IConfig, logger: logging.Logger) -> None:
        self.router = APIRouter(prefix="/chat", tags=["chat"])

        # ── infrastructure ────────────────────────────────────────────────────
        repository = ChatRepository(engine)
        rabbitmq_url = (
            f"amqp://{config.rabbitmq_user}:{config.rabbitmq_password}"
            f"@rabbitmq:5672/"
        )
        self.broker = RabbitMQAdapter(rabbitmq_url, logger)
        self.outbox_processor = OutboxProcessor(engine, self.broker, logger, config)

        # ── use-cases ─────────────────────────────────────────────────────────
        send_message = SendMessage(repository)
        get_pending_messages = GetPendingMessages(repository)

        # ── presentation ──────────────────────────────────────────────────────
        self.controller = ChatController(
            self.router,
            send_message=send_message,
            get_pending_messages=get_pending_messages,
        )

    async def start(self) -> None:
        """Connect to the broker and start the outbox processor."""
        await self.broker.connect()
        await self.outbox_processor.start()

    async def stop(self) -> None:
        """Stop the outbox processor and disconnect from the broker."""
        await self.outbox_processor.stop()
        await self.broker.disconnect()
