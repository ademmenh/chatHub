import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from src.shared.infrastructure.metadata import metadata
from src.users.infrastructure.schema import users_table  # Ensure tables are registered
from src.app import create_app
from src.config.infrastructure.adapter import ConfigAdapter

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_waslini"

class TestConfig(ConfigAdapter):
    @property
    def async_database_url(self) -> str:
        return TEST_DATABASE_URL

    @property
    def env(self) -> str:
        return "test"

test_config = TestConfig()

test_engine = create_async_engine(test_config.async_database_url)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    yield

    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_engine():
    yield test_engine


@pytest_asyncio.fixture
async def client():
    app = create_app(config=test_config, show_docs=False)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
