
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

# name – interní název typu
# label – zobrazovaný název
# description – popis typu publikace

class PublicationTypeModel(BaseDBModel):
    __tablename__ = "publicationtypes"

    path_attribute_name = "path"
    parent_attribute_name = "parent"
    parent_id_attribute_name = "parent_id"
    children_attribute_name = "children"

    path: Mapped[str] = mapped_column(
        index=True,
        nullable=True,
        default=None,
        comment="Materialized path for the publication type tree",
    )
    parent_id: Mapped[IDType] = mapped_column(
        ForeignKey("publicationtypes.id"),
        index=True,
        nullable=True,
        default=None,
        comment="Parent publication type",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        kw_only=True,
    )
    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        kw_only=True,
    )
    description: Mapped[str] = mapped_column(String(500), nullable=True, default=None)

    parent = relationship(
        "PublicationTypeModel",
        remote_side="PublicationTypeModel.id",
        uselist=False,
        back_populates="children",
    )
    children = relationship(
        "PublicationTypeModel",
        back_populates="parent",
        uselist=True,
        cascade="save-update",
    )
    publications = relationship(
        "PublicationModel",
        back_populates="publication_type",
    )