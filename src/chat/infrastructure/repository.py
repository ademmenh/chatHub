import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select
from .schema import messages_table, outbox_events_table
from ..domain.entity import Message, OutboxEvent

class ChatRepository:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def save_message_and_event(self, message: Message, event: OutboxEvent) -> None:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                # Save message
                await session.execute(
                    messages_table.insert().values(
                        id=message.id,
                        sender_id=message.sender_id,
                        receiver_id=message.receiver_id,
                        content=message.content,
                        status=message.status,
                        created_at=message.created_at
                    )
                )
                # Save outbox event
                await session.execute(
                    outbox_events_table.insert().values(
                        id=event.id,
                        aggregate_id=event.aggregate_id,
                        topic=event.topic,
                        payload=event.payload,
                        processed=event.processed,
                        created_at=event.created_at
                    )
                )

    async def get_pending_messages(self, receiver_id: str) -> list[Message]:
        async with AsyncSession(self._engine) as session:
            result = await session.execute(
                select(messages_table).where(
                    messages_table.c.receiver_id == receiver_id,
                    messages_table.c.status == "pending"
                )
            )
            rows = result.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    id=str(row.id),
                    sender_id=str(row.sender_id),
                    receiver_id=str(row.receiver_id),
                    content=row.content,
                    status=row.status,
                    created_at=row.created_at
                ))
            return messages
