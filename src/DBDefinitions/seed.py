from __future__ import annotations

import os
import uuid

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import NoInspectionAvailable

from uoishelpers.dataloaders import readJsonFile
from uoishelpers.feeders import ImportModels

from src.DBDefinitions import BaseDBModel
from src.DBDefinitions.Domain_Events.EventTypeModel import EventTypeModel


DEFAULT_EVENT_TYPES = (
    {
        'id': uuid.UUID('11111111-1111-1111-1111-111111111111'),
        'name': 'Událost',
        'name_en': 'Event',
    },
    {
        'id': uuid.UUID('22222222-2222-2222-2222-222222222222'),
        'name': 'Schůzka',
        'name_en': 'Meeting',
    },
)

DEFAULT_PUBLICATIONS = [
  {
    "title": "Využití umělé inteligence ve vzdělávání",
    "publication_type_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "year": "2023-01-01T00:00:00",
    "language": "cs",
    "abstract": "Studie se zabývá možnostmi využití umělé inteligence v moderním vzdělávání.",
    "doi": "10.1234/edu.2023.001",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789001",
    "volume": "12",
    "issue": "3",
    "pages": "45-58",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789001",
    "created": "2024-08-19T20:34:24.539770",
    "lastchange": "2024-08-22T10:15:30",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Moderní přístupy k analýze dat",
    "publication_type_id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    "year": "2022-01-01T00:00:00",
    "language": "en",
    "abstract": "The study explores modern approaches to data analysis and interpretation.",
    "doi": "10.5678/data.2022.002",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789003",
    "volume": "8",
    "issue": "2",
    "pages": "101-119",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789004",
    "created": "2024-09-10T08:22:14",
    "lastchange": "2024-10-01T14:30:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Digitální transformace ve veřejné správě",
    "publication_type_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "year": "2024-01-01T00:00:00",
    "language": "cs",
    "abstract": "Publikace analyzuje možnosti digitalizace a automatizace procesů veřejné správy.",
    "doi": "10.9876/gov.2024.003",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789006",
    "volume": "5",
    "issue": "1",
    "pages": "12-27",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789007",
    "created": "2025-01-15T11:45:00",
    "lastchange": "2025-02-03T09:12:45",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Data Quality in Information Systems",
    "publication_type_id": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
    "year": "2021-01-01T00:00:00",
    "language": "en",
    "abstract": "This paper examines data quality management and validation in information systems.",
    "doi": "10.2468/it.2021.004",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789009",
    "volume": "15",
    "issue": "4",
    "pages": "220-238",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789010",
    "created": "2025-03-08T16:20:00",
    "lastchange": "2025-03-12T13:40:20",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Vývoj informačních systémů v akademickém prostředí",
    "publication_type_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "year": "2025-01-01T00:00:00",
    "language": "cs",
    "abstract": "Článek se zaměřuje na návrh a vývoj informačních systémů v akademickém prostředí.",
    "doi": "10.1357/is.2025.005",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789012",
    "volume": "9",
    "issue": "2",
    "pages": "67-81",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789013",
    "created": "2025-06-20T12:05:30",
    "lastchange": "2025-07-01T08:30:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Analýza kybernetické bezpečnosti v organizacích",
    "publication_type_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "year": "2022-01-01T00:00:00",
    "language": "cs",
    "abstract": "Výzkum hodnotí aktuální hrozby kybernetické bezpečnosti a možnosti jejich prevence.",
    "doi": "10.3456/cyber.2022.006",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789015",
    "volume": "7",
    "issue": "2",
    "pages": "33-49",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789016",
    "created": "2024-11-05T09:15:00",
    "lastchange": "2024-11-18T12:40:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Machine Learning for Predictive Analytics",
    "publication_type_id": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
    "year": "2024-01-01T00:00:00",
    "language": "en",
    "abstract": "The article investigates machine learning methods for predictive analytics in business.",
    "doi": "10.7890/ml.2024.007",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789017",
    "volume": "11",
    "issue": "1",
    "pages": "88-104",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789018",
    "created": "2025-02-14T13:25:00",
    "lastchange": "2025-03-02T16:10:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Udržitelnost a inovace v průmyslu",
    "publication_type_id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    "year": "2023-01-01T00:00:00",
    "language": "cs",
    "abstract": "Publikace představuje inovativní přístupy k udržitelnému rozvoji průmyslových podniků.",
    "doi": "10.4567/industry.2023.008",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789019",
    "volume": "4",
    "issue": "3",
    "pages": "150-172",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789020",
    "created": "2025-04-09T10:00:00",
    "lastchange": "2025-04-20T11:35:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Digitalizace zdravotnických služeb",
    "publication_type_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "year": "2025-01-01T00:00:00",
    "language": "cs",
    "abstract": "Článek analyzuje přínosy digitálních technologií pro dostupnost a kvalitu zdravotnických služeb.",
    "doi": "10.6789/health.2025.009",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789021",
    "volume": "6",
    "issue": "1",
    "pages": "21-39",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789022",
    "created": "2025-08-12T14:45:00",
    "lastchange": "2025-08-29T09:20:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  },
  {
    "title": "Open Data and Smart Cities",
    "publication_type_id": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
    "year": "2023-01-01T00:00:00",
    "language": "en",
    "abstract": "This paper explores the role of open data in the development of smart cities and public services.",
    "doi": "10.2468/smart.2023.010",
    "journal_id": "a1b2c3d4-e5f6-4789-8123-123456789023",
    "volume": "10",
    "issue": "4",
    "pages": "200-218",
    "id": "f1a2b3c4-d5e6-4789-8123-123456789024",
    "created": "2025-09-17T08:10:00",
    "lastchange": "2025-10-02T15:55:00",
    "createdby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "changedby_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
    "rbacobject_id": "51d101a0-81f1-44ca-8366-6cf51432e8d6"
  }
]

def is_sqlalchemy_model(cls: type) -> bool:
    """Return True only for SQLAlchemy mapped model classes."""
    try:
        mapper = sa_inspect(cls, raiseerr=False)
        return mapper is not None
    except NoInspectionAvailable:
        return False
    
get_demodata = lambda :readJsonFile(jsonFileName="./systemdata.json")

async def init_database_data(session: AsyncSession, get_demodata=get_demodata) -> None:
    """Idempotent seed hook for application startup.

    Keep this function small and explicit. It is called once from
    DatabaseRuntime.start(), after metadata.create_all().
    """

    json_data = get_demodata()

    Models = [
        mapper.class_
        for mapper in BaseDBModel.registry.mappers
        if is_sqlalchemy_model(mapper.class_)
    ]

    ModelNames = [Model.__name__ for Model in Models]

    TypeNames = [
        Model.__name__
        for Model in Models
        if Model.__name__.endswith("TypeModel")
    ]

    isDemo = os.environ.get("DEMODATA", None) in ["True", "true", True]

    ModelNamesToImport = ModelNames if isDemo else TypeNames

    print(
        f"Importing models: (isDemo = {isDemo})\n{ModelNamesToImport}",
        flush=True,
    )

    ModelsToImport = [
        Model
        for Model in Models
        if Model.__name__ in ModelNamesToImport
        and is_sqlalchemy_model(Model)
        and hasattr(Model, "__tablename__")
    ]
    table_names = [Model.__tablename__ for Model in ModelsToImport]
    modelIndex = dict((DBModel.__tablename__, DBModel) for DBModel in ModelsToImport)
    print(f"Models to import: {ModelsToImport}\nTable names: {table_names}\nModel index: {modelIndex}", flush=True)

    @asynccontextmanager
    async def session_maker():
        try:
            yield session
        finally:
            pass

    await ImportModels(session_maker, ModelsToImport, json_data)

    print("Data initialized", flush=True)
