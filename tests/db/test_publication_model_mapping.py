from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers

from src.DBDefinitions import (
    AuthorshipModel,
    AuthorModel,
    PublicationModel,
    PublicationTypeModel,
)


def test_publication_models_have_valid_mappings():
    configure_mappers()

    publication_type_id = inspect(PublicationModel).columns["publication_type_id"]
    assert {fk.target_fullname for fk in publication_type_id.foreign_keys} == {
        "publicationtypes.id"
    }
    publication_relationships = inspect(PublicationModel).relationships
    assert (
        publication_relationships["publication_type"].mapper.class_
        is PublicationTypeModel
    )
    assert publication_relationships["authorships"].mapper.class_ is AuthorshipModel
    assert inspect(AuthorModel).relationships["authorships"].mapper.class_ is AuthorshipModel

    authorship_columns = inspect(AuthorshipModel).columns
    assert {
        fk.target_fullname
        for fk in authorship_columns["publication_id"].foreign_keys
    } == {"publications.id"}
    assert {
        fk.target_fullname
        for fk in authorship_columns["author_id"].foreign_keys
    } == {
        "authors.id"
    }
    assert authorship_columns["corresponding_author"].type.python_type is bool


def test_publication_type_keeps_required_fields_keyword_only():
    publication_type = PublicationTypeModel(
        name="journal-article",
        label="Journal article",
    )

    assert publication_type.name == "journal-article"
    assert publication_type.label == "Journal article"
