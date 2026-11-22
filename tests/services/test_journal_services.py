"""Ověření služeb časopisů přes skutečné loadery a dočasnou databázi."""

import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.DBDefinitions import BaseDBModel
from src.Dataloaders import LoaderMap
from src.ServiceDefinitions.ServiceContext import ServiceContext
from src.ServiceDefinitions.main import resolve_service


@pytest_asyncio.fixture
async def journal_service_ctx():
    # Databáze existuje jen v paměti; naše data v PostgreSQL se nemění.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(BaseDBModel.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            yield ServiceContext(loaders=LoaderMap(session), session=session)
    finally:
        await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("entity_name", ["Journal", "JournalType"])
async def test_service_crud(journal_service_ctx, entity_name):
    ctx = journal_service_ctx
    service = getattr(ctx.Services, entity_name + "Service")
    assert resolve_service(entity_name) is service

    record_id = uuid.uuid4()
    entity = await service.Model(ctx, id=record_id, name="Původní název")
    created = await service.Create(ctx, entity)
    assert created.id == record_id

    loaded = await service.ReadById(ctx, record_id)
    assert loaded.name == "Původní název"
    rows = await service.ReadPage(ctx, where={"id": {"_eq": record_id}})
    assert [row.id for row in rows] == [record_id]

    # Posíláme pouze změněné pole a aktuální lastchange.
    updated = await service.Update(ctx, SimpleNamespace(
        id=record_id, lastchange=loaded.lastchange, name="Nový název",
    ))
    assert updated.name == "Nový název"
    assert (await service.ReadById(ctx, record_id)).name == "Nový název"

    await service.Delete(ctx, SimpleNamespace(
        id=record_id, lastchange=updated.lastchange,
    ))
    assert await service.ReadById(ctx, record_id) is None
