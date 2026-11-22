from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import JournalModel
from src.ServiceDefinitions.BaseService import BaseService
from src.ServiceDefinitions.ServiceContext import ServiceContext


class JournalService(BaseService[IDLoader[JournalModel]]):
    # Základní operace přebíráme z BaseService.
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[JournalModel]:
        return ctx.loaders.JournalModel
