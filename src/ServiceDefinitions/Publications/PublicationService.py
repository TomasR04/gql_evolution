
from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import PublicationModel
from src.ServiceDefinitions.BaseService import BaseService, ServiceExceptionWithCode
from src.ServiceDefinitions.ServiceContext import ServiceContext

class PublicationService(BaseService[IDLoader[PublicationModel]]):
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[PublicationModel]:
        return ctx.loaders.PublicationModel

    @classmethod
    async def CreatePublication(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.create(entity=entity)

    @classmethod
    async def UpdatePublication(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.update(entity=entity)
    
    @classmethod
    async def DeletePublication(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.delete(entity.id)

    @classmethod
    async def ViewPublication(cls, ctx: ServiceContext, publication_id):
        loader = await cls.getLoader(ctx)
        publication = await loader.load(publication_id)
        if publication is None:
            raise ServiceExceptionWithCode('Publication not found', code='publication_not_found')
        return publication
    