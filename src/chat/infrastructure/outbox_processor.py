import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..domain.ports import IMessageBroker
from .schema import outbox_events_table
from src.config.domain.interface import IConfig

class OutboxProcessor:
    """Infrastructure worker that polls the outbox table and publishes events."""

    def __init__(self, engine: AsyncEngine, broker: IMessageBroker, logger: logging.Logger, config: IConfig) -> None:
        self._engine = engine
        self._broker = broker
        self._logger = logger
        self._config = config
        self._running = False

    async def start(self) -> None:
        self._running = True
        asyncio.create_task(self._run_loop())
        self._logger.info("OutboxProcessor started")

    async def stop(self) -> None:
        self._running = False
        self._logger.info("OutboxProcessor stopped")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self._process_batch()
                self._logger.info("Processing outbox")
            except Exception as e:
                self._logger.error("Error processing outbox: %s", e)
            await asyncio.sleep(self._config.worker_interval)

    async def _process_batch(self) -> None:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(outbox_events_table)
                    .where(outbox_events_table.c.processed == False)  # noqa: E712
                    .limit(50)
                )
                events = result.fetchall()

                for event in events:
                    await self._broker.publish(event.topic, event.payload)

                    await session.execute(
                        outbox_events_table.update()
                        .where(outbox_events_table.c.id == event.id)
                        .values(processed=True)
                    )
