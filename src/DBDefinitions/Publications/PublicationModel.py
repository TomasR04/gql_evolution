import typing
import datetime
import dataclasses
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, synonym

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property

from src.DBDefinitions.BaseModel import BaseDBModel, UUIDColumn, UUIDFKey, IDType

class PublicationModel(BaseDBModel):
    # title – název publikace
    # publication_type_id – typ publikace
    # year – rok vydání
    # language – jazyk publikace
    # abstract – abstrakt nebo stručný popis
    # doi – DOI publikace, pokud existuje
    # journal_id – časopis, ve kterém byla publikace vydána
    # volume – ročník časopisu
    # issue – číslo časopisu
    # pages – rozsah stran

    __tablename__ = "publications"

    title: Mapped[str] = mapped_column(default=None, nullable=True)
    publication_type_id: Mapped[IDType] = mapped_column(
        ForeignKey("publicationtypes.id"),
        index=True,
        nullable=True,
        default=None,
    )
    publication_type = relationship(
        "PublicationTypeModel",
        back_populates="publications",
    )
    authorships = relationship(
        "AuthorshipModel",
        back_populates="publication",
    )
    year: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, default=None)
    language: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    abstract: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    doi: Mapped[str] = mapped_column(String(200), nullable=True, default=None)
    journal_id: Mapped[IDType] = mapped_column(ForeignKey("journals.id"), index=True, nullable=True, default=None)
    volume: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    issue: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    pages: Mapped[str] = mapped_column(String(100), nullable=True, default=None)

