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

# user_id – identifikátor interního uživatele, pokud je autor veden v gql_ug
# first_name – jméno externího autora
# last_name – příjmení externího autora
# middle_name – další část jména, pokud je potřeba
# display_name – jméno používané při zobrazení autora
# orcid – ORCID autora, pokud je znám
# affiliation – pracoviště externího autora, pokud je známo

class AuthorModel(BaseDBModel):
    __tablename__ = "authors"

    user_id: Mapped[IDType] = UUIDFKey(ForeignKey("users.id"), index=True, nullable=True, default=None)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    display_name: Mapped[str] = mapped_column(String(200), nullable=True, default=None)
    orcid: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    affiliation: Mapped[str] = mapped_column(String(200), nullable=True, default=None)

    authorships = relationship(
        "AuthorshipModel",
        back_populates="author",
    )