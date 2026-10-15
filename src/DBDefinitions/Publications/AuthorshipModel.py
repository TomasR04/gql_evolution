import typing
import datetime
import dataclasses
import sqlalchemy
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, synonym

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property

from src.DBDefinitions.BaseModel import BaseDBModel, UUIDColumn, UUIDFKey, IDType

# publication_id – publikace
# author_id – autor
# position – pořadí autora v seznamu autorů
# share – autorský podíl
# corresponding_author – informace, zda jde o korespondenčního autora
# state_id – stav editace

class AuthorshipModel(BaseDBModel):
    __tablename__ = "authorships"

    publication_id: Mapped[IDType] = mapped_column(
        ForeignKey("publications.id"),
        index=True,
        nullable=True,
        default=None,
    )
    publication = relationship(
        "PublicationModel",
        back_populates="authorships",
    )
    author_id: Mapped[IDType] = mapped_column(
        ForeignKey("authors.id"),
        index=True,
        nullable=True,
        default=None,
    )
    author = relationship(
        "AuthorModel",
        back_populates="authorships",
    )
    position: Mapped[int] = mapped_column(nullable=True, default=None)
    share: Mapped[float] = mapped_column(nullable=True, default=None)
    corresponding_author: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
    )
    
    # BUDE TŘEBA ZKONTROLOVAT
    state_id: Mapped[IDType] = UUIDFKey(ForeignKey("authorshipstates.id"), index=True, nullable=True, default=None)