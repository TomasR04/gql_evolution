"""Databázové testy časopisů přes učitelovy CRUD funkce."""

import json
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema

from src.DBDefinitions import (
    BaseDBModel, ComposeConnectionString, JournalModel, JournalTypeModel,
    PublicationModel, PublicationTypeModel, AuthorModel, AuthorshipModel,
)
from src.DBDefinitions.main import (
    op_create, op_get, op_list, op_update, op_delete,
)
from src.DBDefinitions.seed import init_database_data


ROOT = Path(__file__).resolve().parents[2]


@pytest_asyncio.fixture
async def publication_sessions():
    # Každý test má vlastní schéma. Tabulek v public se nedotýkáme.
    schema = "test_publications_" + uuid.uuid4().hex
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


@pytest.mark.parametrize("model", [JournalTypeModel, JournalModel])
async def test_create_read_update_delete(publication_sessions, model):
    async with publication_sessions() as session:
        created = await op_create(session, model, {"name": "Původní název"})
        record_id = created["id"]
        assert isinstance(record_id, uuid.UUID)
        assert created["created"] is not None

    # Nové spojení ověřuje, že se záznam opravdu uložil.
    async with publication_sessions() as session:
        loaded = await op_get(session, model, {"id": record_id})
        assert loaded["name"] == "Původní název"
        await op_update(session, model, {"id": record_id, "name": "Nový název"})

    async with publication_sessions() as session:
        rows = await op_list(session, model, {"where": {"id": {"_eq": record_id}}})
        assert len(rows) == 1
        assert rows[0]["name"] == "Nový název"
        assert (await op_delete(session, model, {"id": record_id}))["ok"] is True

    async with publication_sessions() as session:
        assert (await op_get(session, model, {"id": record_id}))["error"] == "not_found"


@pytest.mark.parametrize("model", [JournalTypeModel, JournalModel])
@pytest.mark.parametrize("operation", [op_get, op_update, op_delete])
async def test_missing_record(publication_sessions, model, operation):
    async with publication_sessions() as session:
        result = await operation(session, model, {"id": uuid.uuid4()})
        assert result["ok"] is False
        assert result["error"] == "not_found"


async def test_journal_type_relationship(publication_sessions):
    async with publication_sessions() as session:
        first = await op_create(session, JournalTypeModel, {"name": "scientific"})
        second = await op_create(session, JournalTypeModel, {"name": "professional"})
        journal = await op_create(session, JournalModel, {
            "name": "Zkušební časopis", "journal_type_id": first["id"],
            "short_name": "ZČ", "issn": "1234-5679", "eissn": None,
            "publisher": "Zkušební vydavatel", "website": "https://example.org",
        })

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"], "include": ["type"]})
        assert loaded["type"]["name"] == "scientific"
        assert loaded["issn"] == "1234-5679"
        assert loaded["eissn"] is None
        await op_update(session, JournalModel, {"id": journal["id"], "journal_type_id": second["id"]})

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"], "include": ["type"]})
        assert loaded["type"]["name"] == "professional"


async def test_type_tree(publication_sessions):
    async with publication_sessions() as session:
        root = await op_create(session, JournalTypeModel, {
            "name": "scientific", "children": [{"name": "technical"}],
        })

    async with publication_sessions() as session:
        root = await op_get(session, JournalTypeModel, {"id": root["id"], "include": ["children"]})
        assert root["parent_id"] is None
        assert len(root["children"]) == 1

        child = root["children"][0]
        assert child["parent_id"] == root["id"]
        loaded = await op_get(session, JournalTypeModel, {"id": child["id"], "include": ["parent"]})
        assert loaded["parent"]["id"] == root["id"]


@pytest.mark.parametrize("model, field", [
    (JournalModel, "journal_type_id"), (JournalTypeModel, "parent_id"),
])
async def test_unknown_foreign_key(publication_sessions, model, field):
    async with publication_sessions() as session:
        with pytest.raises(IntegrityError):
            await op_create(session, model, {"name": "Neplatný odkaz", field: uuid.uuid4()})
        await session.rollback()
        assert await op_list(session, model, {}) == []


@pytest.mark.parametrize("dependent_model, field", [
    (JournalModel, "journal_type_id"), (JournalTypeModel, "parent_id"),
])
@pytest.mark.parametrize("load_children", [False, True])
async def test_used_type_cannot_be_deleted(publication_sessions, dependent_model, field, load_children):
    async with publication_sessions() as session:
        parent = await op_create(session, JournalTypeModel, {"name": "Používaný typ"})
        dependent = await op_create(session, dependent_model, {"name": "Navázaný záznam", field: parent["id"]})

    async with publication_sessions() as session:
        if load_children:
            loaded_parent = await session.get(JournalTypeModel, parent["id"])
            await op_get(session, JournalTypeModel, {"id": parent["id"], "include": ["children"]})
            assert len(loaded_parent.children) == (1 if dependent_model is JournalTypeModel else 0)
        with pytest.raises(IntegrityError):
            await op_delete(session, JournalTypeModel, {"id": parent["id"]})
        await session.rollback()

    async with publication_sessions() as session:
        loaded = await op_get(session, dependent_model, {"id": dependent["id"]})
        assert loaded[field] == parent["id"]
        await op_delete(session, dependent_model, {"id": dependent["id"]})
        assert (await op_delete(session, JournalTypeModel, {"id": parent["id"]}))["ok"] is True


async def test_failed_update_keeps_original_data(publication_sessions):
    async with publication_sessions() as session:
        journal_type = await op_create(session, JournalTypeModel, {"name": "scientific"})
        journal = await op_create(session, JournalModel, {
            "name": "Původní název", "journal_type_id": journal_type["id"],
        })
        with pytest.raises(IntegrityError):
            await op_update(session, JournalModel, {
                "id": journal["id"], "name": "Neuložená změna", "journal_type_id": uuid.uuid4(),
            })
        await session.rollback()

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"]})
        assert loaded["name"] == "Původní název"
        assert loaded["journal_type_id"] == journal_type["id"]


async def test_demo_import_is_repeatable(publication_sessions, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("DEMODATA", "True")
    data = json.loads((ROOT / "systemdata.json").read_text(encoding="utf-8"))
    for _ in range(2):
        async with publication_sessions() as session:
            await init_database_data(session)

    async with publication_sessions() as session:
        types = await op_list(session, JournalTypeModel, {})
        journals = await op_list(session, JournalModel, {"include": ["type"]})
        assert len(types) == len(data["journaltypes"]) > 1
        assert len(journals) == len(data["journals"]) > 0
        assert journals[0]["type"]["id"] == journals[0]["journal_type_id"]
        root_id = uuid.UUID(data["journaltypes"][0]["id"])
        root = await op_get(session, JournalTypeModel, {"id": root_id, "include": ["children"]})
        assert len(root["children"]) == 1

        # Každá publikace musí načíst svůj časopis i opačnou vazbu.
        publications = await op_list(session, PublicationModel, {"include": ["journal"]})
        assert len(publications) == len(data["publications"]) > 0
        for publication in publications:
            assert publication["journal"]["id"] == publication["journal_id"]
            journal = await op_get(session, JournalModel, {
                "id": publication["journal_id"], "include": ["publications"],
            })
            assert publication["id"] in {row["id"] for row in journal["publications"]}

        assert len(await op_list(session, AuthorModel, {})) == len(data["authors"])
        assert len(await op_list(session, PublicationTypeModel, {})) == len(data["publicationtypes"])
        authorships = await op_list(session, AuthorshipModel, {"include": ["author", "publication"]})
        assert len(authorships) == len(data["authorships"])
        for authorship in authorships:
            assert authorship["author"]["id"] == authorship["author_id"]
            assert authorship["publication"]["id"] == authorship["publication_id"]


async def test_catalog_import_without_demo_journals(publication_sessions, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("DEMODATA", raising=False)
    async with publication_sessions() as session:
        await init_database_data(session)
    async with publication_sessions() as session:
        assert len(await op_list(session, JournalTypeModel, {})) > 1
        assert await op_list(session, JournalModel, {}) == []
        assert await op_list(session, PublicationModel, {}) == []


async def test_publication_journal_relationship(publication_sessions):
    async with publication_sessions() as session:
        first = await op_create(session, JournalModel, {"name": "První časopis"})
        second = await op_create(session, JournalModel, {"name": "Druhý časopis"})
        publication = await op_create(session, PublicationModel, {
            "title": "První článek", "journal_id": first["id"],
        })
        other = await op_create(session, PublicationModel, {
            "title": "Druhý článek", "journal_id": first["id"],
        })

    async with publication_sessions() as session:
        loaded = await op_get(session, PublicationModel, {
            "id": publication["id"], "include": ["journal"],
        })
        assert loaded["journal"]["name"] == "První časopis"
        journal = await op_get(session, JournalModel, {
            "id": first["id"], "include": ["publications"],
        })
        assert {row["id"] for row in journal["publications"]} == {publication["id"], other["id"]}
        await op_update(session, PublicationModel, {
            "id": publication["id"], "journal_id": second["id"],
        })

    async with publication_sessions() as session:
        loaded = await op_get(session, PublicationModel, {
            "id": publication["id"], "include": ["journal"],
        })
        assert loaded["journal"]["id"] == second["id"]
        journal = await op_get(session, JournalModel, {
            "id": first["id"], "include": ["publications"],
        })
        assert [row["id"] for row in journal["publications"]] == [other["id"]]


@pytest.mark.parametrize("operation", ["create", "update"])
async def test_publication_rejects_unknown_journal(publication_sessions, operation):
    async with publication_sessions() as session:
        journal = await op_create(session, JournalModel, {"name": "Existující časopis"})
        publication = await op_create(session, PublicationModel, {
            "title": "Původní článek", "journal_id": journal["id"],
        })
        with pytest.raises(IntegrityError):
            if operation == "create":
                await op_create(session, PublicationModel, {
                    "title": "Neplatný článek", "journal_id": uuid.uuid4(),
                })
            else:
                await op_update(session, PublicationModel, {
                    "id": publication["id"], "title": "Neuložená změna",
                    "journal_id": uuid.uuid4(),
                })
        await session.rollback()

    async with publication_sessions() as session:
        rows = await op_list(session, PublicationModel, {})
        assert len(rows) == 1
        assert rows[0]["title"] == "Původní článek"
        assert rows[0]["journal_id"] == journal["id"]


@pytest.mark.parametrize("load_publications", [False, True])
async def test_used_journal_cannot_be_deleted(publication_sessions, load_publications):
    async with publication_sessions() as session:
        journal = await op_create(session, JournalModel, {"name": "Používaný časopis"})
        publication = await op_create(session, PublicationModel, {
            "title": "Navázaný článek", "journal_id": journal["id"],
        })

    async with publication_sessions() as session:
        if load_publications:
            loaded_journal = await session.get(JournalModel, journal["id"])
            await op_get(session, JournalModel, {"id": journal["id"], "include": ["publications"]})
            assert len(loaded_journal.publications) == 1
        with pytest.raises(IntegrityError):
            await op_delete(session, JournalModel, {"id": journal["id"]})
        await session.rollback()

    async with publication_sessions() as session:
        loaded = await op_get(session, PublicationModel, {"id": publication["id"]})
        assert loaded["journal_id"] == journal["id"]
        await op_delete(session, PublicationModel, {"id": publication["id"]})
        assert (await op_delete(session, JournalModel, {"id": journal["id"]}))["ok"] is True
