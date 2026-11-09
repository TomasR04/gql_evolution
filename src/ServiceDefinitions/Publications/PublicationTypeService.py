from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import PublicationTypeModel
from src.ServiceDefinitions.BaseService import BaseService, ServiceExceptionWithCode
from src.ServiceDefinitions.ServiceContext import ServiceContext

class PublicationTypeService(BaseService[IDLoader[PublicationTypeModel]]):
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[PublicationTypeModel]:
        return ctx.loaders.PublicationTypeModel

    @classmethod
    async def CreatePublicationType(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.create(entity=entity)

    @classmethod
    async def UpdatePublicationType(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.update(entity=entity)
    
    @classmethod
    async def DeletePublicationType(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.delete(entity.id)

    @classmethod
    async def ViewPublicationType(cls, ctx: ServiceContext, publication_type_id):
        loader = await cls.getLoader(ctx)
        publication_type = await loader.load(publication_type_id)
        if publication_type is None:
            raise ServiceExceptionWithCode('Publication type not found', code='publication_type_not_found')
        return publication_type