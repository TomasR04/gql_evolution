from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import AuthorshipModel
from src.ServiceDefinitions.BaseService import BaseService, ServiceExceptionWithCode
from src.ServiceDefinitions.ServiceContext import ServiceContext

class AuthorshipService(BaseService[IDLoader[AuthorshipModel]]):
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[AuthorshipModel]:
        return ctx.loaders.AuthorshipModel

    @classmethod
    async def CreateAuthorship(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.create(entity=entity)

    @classmethod
    async def UpdateAuthorship(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.update(entity=entity)
    
    @classmethod
    async def DeleteAuthorship(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.delete(entity.id)

    @classmethod
    async def ViewAuthorship(cls, ctx: ServiceContext, authorship_id):
        loader = await cls.getLoader(ctx)
        authorship = await loader.load(authorship_id)
        if authorship is None:
            raise ServiceExceptionWithCode('Authorship not found', code='authorship_not_found')
        return authorship