from sqlalchemy import Column, DateTime, String, Table, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from src.shared.infrastructure.metadata import metadata

messages_table = Table(
    "messages",
    metadata,
    Column("id", UUID(as_uuid=False), primary_key=True),
    Column("sender_id", UUID(as_uuid=False), nullable=False),
    Column("receiver_id", UUID(as_uuid=False), nullable=False),
    Column("content", Text, nullable=False),
    Column("status", String, nullable=False, default="pending"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

outbox_events_table = Table(
    "outbox_events",
    metadata,
    Column("id", UUID(as_uuid=False), primary_key=True),
    Column("aggregate_id", String, nullable=False),
    Column("topic", String, nullable=False),
    Column("payload", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("processed", Boolean, nullable=False, default=False),
)
