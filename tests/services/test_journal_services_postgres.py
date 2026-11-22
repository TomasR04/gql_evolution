"""Služby časopisů nad PostgreSQL, vždy v samostatném testovacím schématu."""

import json
import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema

from src.DBDefinitions import BaseDBModel, ComposeConnectionString
from src.Dataloaders import LoaderMap
from src.ServiceDefinitions.ServiceContext import ServiceContext
from src.ServiceDefinitions import main as service_cli


@pytest_asyncio.fixture
async def service_sessions():
    schema = "test_services_" + uuid.uuid4().hex
    engine = create_async_engine(
        ComposeConnectionString(),
        execution_options={"schema_translate_map": {None: schema}},
    )
    created = False
    try:
        async with engine.begin() as connection:
            await connection.execute(CreateSchema(schema))
            await connection.run_sync(BaseDBModel.metadata.create_all)
        created = True
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        if created:
            async with engine.begin() as connection:
                await connection.execute(DropSchema(schema, cascade=True))
        await engine.dispose()


def context(session):
    return ServiceContext(loaders=LoaderMap(session), session=session)


async def create(ctx, entity_name, **values):
    service = service_cli.resolve_service(entity_name)
    entity = await service.Model(ctx, **values)
    return await service.Create(ctx, entity)


@pytest.mark.parametrize("entity_name", ["Journal", "JournalType"])
async def test_crud_persists_between_sessions(service_sessions, entity_name):
    service = service_cli.resolve_service(entity_name)
    async with service_sessions.begin() as session:
        row = await create(context(session), entity_name, name="Původní název")
        record_id = row.id

    # Nové spojení ověří skutečně uložená data, ne jen obsah paměti loaderu.
    async with service_sessions.begin() as session:
        ctx = context(session)
        row = await service.ReadById(ctx, record_id)
        assert row.name == "Původní název"
        await service.Update(ctx, SimpleNamespace(
            id=record_id, lastchange=row.lastchange, name="Nový název",
        ))

    async with service_sessions.begin() as session:
        ctx = context(session)
        rows = await service.ReadPage(ctx, where={"id": {"_eq": record_id}})
        assert len(rows) == 1
        assert rows[0].name == "Nový název"
        await service.Delete(ctx, rows[0])

    async with service_sessions() as session:
        assert await service.ReadById(context(session), record_id) is None


@pytest.mark.parametrize("entity_name, field", [
    ("Journal", "journal_type_id"), ("JournalType", "parent_id"),
])
@pytest.mark.parametrize("operation", ["create", "update"])
async def test_invalid_reference_rolls_back(service_sessions, entity_name, field, operation):
    service = service_cli.resolve_service(entity_name)
    async with service_sessions.begin() as session:
        ctx = context(session)
        parent = await create(ctx, "JournalType", name="Nadřazený typ")
        parent_id = parent.id
        row = await create(ctx, entity_name, name="Původní název", **{field: parent_id})
        record_id = row.id

    with pytest.raises(IntegrityError):
        async with service_sessions.begin() as session:
            ctx = context(session)
            if operation == "create":
                await create(ctx, entity_name, name="Neplatný odkaz", **{field: uuid.uuid4()})
            else:
                row = await service.ReadById(ctx, record_id)
                await service.Update(ctx, SimpleNamespace(
                    id=record_id, lastchange=row.lastchange,
                    name="Neuložená změna", **{field: uuid.uuid4()},
                ))

    async with service_sessions() as session:
        ctx = context(session)
        row = await service.ReadById(ctx, record_id)
        assert row.name == "Původní název"
        assert getattr(row, field) == parent_id
        assert await service.ReadPage(ctx, where={"name": {"_eq": "Neplatný odkaz"}}) == []


@pytest.mark.parametrize("parent_name, child_name, field", [
    ("JournalType", "JournalType", "parent_id"),
    ("JournalType", "Journal", "journal_type_id"),
    ("Journal", "Publication", "journal_id"),
])
async def test_used_record_cannot_be_deleted(service_sessions, parent_name, child_name, field):
    parent_service = service_cli.resolve_service(parent_name)
    child_service = service_cli.resolve_service(child_name)
    async with service_sessions.begin() as session:
        ctx = context(session)
        parent = await create(ctx, parent_name, name="Používaný záznam")
        parent_id = parent.id
        values = {"title": "Článek"} if child_name == "Publication" else {"name": "Podřízený záznam"}
        child = await create(ctx, child_name, **values, **{field: parent_id})
        child_id = child.id

    with pytest.raises(IntegrityError):
        async with service_sessions.begin() as session:
            ctx = context(session)
            parent = await parent_service.ReadById(ctx, parent_id)
            await parent_service.Delete(ctx, parent)

    async with service_sessions.begin() as session:
        ctx = context(session)
        parent = await parent_service.ReadById(ctx, parent_id)
        child = await child_service.ReadById(ctx, child_id)
        assert getattr(child, field) == parent_id
        await child_service.Delete(ctx, child)
        await parent_service.Delete(ctx, parent)

    async with service_sessions() as session:
        ctx = context(session)
        assert await parent_service.ReadById(ctx, parent_id) is None
        assert await child_service.ReadById(ctx, child_id) is None


@pytest.mark.parametrize("entity_name", ["Journal", "JournalType"])
async def test_stale_update_does_not_overwrite_data(service_sessions, entity_name):
    service = service_cli.resolve_service(entity_name)
    async with service_sessions.begin() as session:
        row = await create(context(session), entity_name, name="Původní název")
        record_id, old_lastchange = row.id, row.lastchange

    async with service_sessions.begin() as session:
        await service.Update(context(session), SimpleNamespace(
            id=record_id, lastchange=old_lastchange, name="Aktuální název",
        ))

    async with service_sessions.begin() as session:
        result = await service.Update(context(session), SimpleNamespace(
            id=record_id, lastchange=old_lastchange, name="Zastaralá změna",
        ))
        assert result is None

    async with service_sessions() as session:
        assert (await service.ReadById(context(session), record_id)).name == "Aktuální název"


async def test_failed_transaction_saves_nothing(service_sessions):
    with pytest.raises(IntegrityError):
        async with service_sessions.begin() as session:
            ctx = context(session)
            await create(ctx, "JournalType", name="Neuložený typ")
            await create(ctx, "Journal", name="Neplatný časopis", journal_type_id=uuid.uuid4())
    async with service_sessions() as session:
        ctx = context(session)
        assert await ctx.Services.JournalTypeService.ReadPage(ctx) == []
        assert await ctx.Services.JournalService.ReadPage(ctx) == []


@pytest.fixture
def run_cli(service_sessions, monkeypatch):
    async def test_engine(*args, **kwargs):
        return service_sessions

    # Stejná příkazová aplikace, pouze s oddělenou testovací databází.
    monkeypatch.setattr(service_cli, "startEngine", test_engine)

    async def run(entity_name, operation, payload):
        args = service_cli.create_arg_parser().parse_args([
            entity_name, operation, json.dumps(payload, default=service_cli.json_default),
        ])
        return await service_cli.run_async(args)
    return run


@pytest.mark.parametrize("entity_name, preserved_field", [
    ("Journal", "short_name"), ("JournalType", "label"),
])
async def test_cli_crud_persists_and_preserves_other_fields(run_cli, entity_name, preserved_field):
    async def run(operation, payload):
        return await run_cli(entity_name, operation, payload)

    created = await run("create", {"name": "Původní název", preserved_field: "Zachovat"})
    loaded = await run("get", {"id": created["id"]})
    assert loaded.get("name") == "Původní název"
    updated = await run("update", {
        "id": loaded["id"], "lastchange": loaded["lastchange"], "name": "Nový název",
    })
    assert updated["name"] == "Nový název"
    loaded = await run("get", {"id": created["id"]})
    assert loaded[preserved_field] == "Zachovat"
    assert loaded["created"] == created["created"]
    assert len(await run("list", {})) == 1
    await run("delete", {"id": loaded["id"], "lastchange": loaded["lastchange"]})
    assert (await run("get", {"id": loaded["id"]}))["error"] == "not_found"


@pytest.mark.parametrize("entity_name, field", [
    ("Journal", "journal_type_id"), ("JournalType", "parent_id"),
])
async def test_cli_failed_update_preserves_record(run_cli, entity_name, field):
    created = await run_cli(entity_name, "create", {"name": "Původní název"})
    with pytest.raises(IntegrityError):
        await run_cli(entity_name, "update", {
            "id": created["id"], "lastchange": created["lastchange"],
            "name": "Neuložená změna", field: str(uuid.uuid4()),
        })
    loaded = await run_cli(entity_name, "get", {"id": created["id"]})
    assert loaded["name"] == "Původní název"
    assert loaded[field] is None


@pytest.mark.parametrize("entity_name", ["Journal", "JournalType"])
async def test_cli_rejects_missing_or_stale_lastchange(run_cli, entity_name):
    created = await run_cli(entity_name, "create", {"name": "Původní název"})
    with pytest.raises(service_cli.CliError, match="requires"):
        await run_cli(entity_name, "update", {"id": created["id"], "name": "Chybí čas"})
    await run_cli(entity_name, "update", {
        "id": created["id"], "lastchange": created["lastchange"], "name": "Aktuální název",
    })
    with pytest.raises(service_cli.CliError, match="outdated"):
        await run_cli(entity_name, "update", {
            "id": created["id"], "lastchange": created["lastchange"], "name": "Zastaralá změna",
        })
    loaded = await run_cli(entity_name, "get", {"id": created["id"]})
    assert loaded["name"] == "Aktuální název"


async def test_services_filter_journals_by_type_and_page(service_sessions):
    async with service_sessions.begin() as session:
        ctx = context(session)
        root = await create(ctx, "JournalType", name="scientific")
        child = await create(ctx, "JournalType", name="technical", parent_id=root.id)
        child_id, root_id = child.id, root.id
        await create(ctx, "Journal", name="A", journal_type_id=child_id)
        await create(ctx, "Journal", name="B", journal_type_id=child_id)
        await create(ctx, "Journal", name="C", journal_type_id=root_id)
    async with service_sessions() as session:
        ctx = context(session)
        children = await ctx.Services.JournalTypeService.ReadPage(
            ctx, where={"parent_id": {"_eq": root_id}},
        )
        assert [row.id for row in children] == [child_id]
        rows = await ctx.Services.JournalService.ReadPage(
            ctx, where={"journal_type_id": {"_eq": child_id}},
            orderby="name", skip=1, limit=1,
        )
        assert [row.name for row in rows] == ["B"]
