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

# publication_id – publikace
# author_id – autor
# position – pořadí autora v seznamu autorů
# share – autorský podíl
# corresponding_author – informace, zda jde o korespondenčního autora
# state_id – stav editace

class AuthorshipModel(BaseDBModel):
    __tablename__ = "authorships"

    publication_id: Mapped[IDType] = relationship("PublicationModel", back_populates="authorships")
    author_id: Mapped[IDType] = relationship("AuthorModel", back_populates="authorships")
    position: Mapped[int] = mapped_column(nullable=True, default=None)
    share: Mapped[float] = mapped_column(nullable=True, default=None)
    corresponding_author: Mapped[bool] = relationship("AuthorModel", back_populates="authorships")
    state_id: Mapped[IDType] = mapped_column(ForeignKey("authorshipstates.id"), index=True, nullable=True, default=None)