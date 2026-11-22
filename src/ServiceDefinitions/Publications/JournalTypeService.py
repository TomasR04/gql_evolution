from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import JournalTypeModel
from src.ServiceDefinitions.BaseService import BaseService
from src.ServiceDefinitions.ServiceContext import ServiceContext


class JournalTypeService(BaseService[IDLoader[JournalTypeModel]]):
    # Služba pracuje s typy časopisů přes jejich loader.
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[JournalTypeModel]:
        return ctx.loaders.JournalTypeModel
