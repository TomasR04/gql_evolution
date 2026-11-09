from uoishelpers.dataloaders.LoaderMapBase import LoaderMapBase
from uoishelpers.dataloaders.IDLoader import IDLoader

import src.DBDefinitions
from src.DBDefinitions import BaseDBModel, EventModel, EventInvitationModel, PublicationModel, PublicationTypeModel, AuthorModel, AuthorshipModel 


class LoaderMap(LoaderMapBase[BaseDBModel]):
    BaseModel = BaseDBModel

    EventModel: IDLoader[src.DBDefinitions.EventModel] = None
    EventInvitationModel: IDLoader[src.DBDefinitions.EventInvitationModel] = None
    PublicationModel: IDLoader[src.DBDefinitions.PublicationModel] = None
    PublicationTypeModel: IDLoader[src.DBDefinitions.PublicationTypeModel] = None
    AuthorModel: IDLoader[src.DBDefinitions.AuthorModel] = None
    AuthorshipModel: IDLoader[src.DBDefinitions.AuthorshipModel] = None

    def __init__(self, session):
        super().__init__(session)
        self.EventModel = self.get(EventModel)
        self.EventInvitationModel = self.get(EventInvitationModel)
        self.PublicationModel = self.get(PublicationModel)
        self.PublicationTypeModel = self.get(PublicationTypeModel)
        self.AuthorModel = self.get(AuthorModel)
        self.AuthorshipModel = self.get(AuthorshipModel)

    def get_by_name(self, name: str):
        return getattr(self, name)


def createLoadersContext(session):
    """Compatibility helper for places expecting a dict context."""
    return {'loaders': LoaderMap(session)}
