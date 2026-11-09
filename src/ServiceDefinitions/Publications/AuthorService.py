from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import AuthorModel
from src.ServiceDefinitions.BaseService import BaseService, ServiceExceptionWithCode
from src.ServiceDefinitions.ServiceContext import ServiceContext

class AuthorService(BaseService[IDLoader[AuthorModel]]):
    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[AuthorModel]:
        return ctx.loaders.AuthorModel

    @classmethod
    async def CreateAuthor(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.create(entity=entity)

    @classmethod
    async def UpdateAuthor(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.update(entity=entity)
    
    @classmethod
    async def DeleteAuthor(cls, ctx: ServiceContext, entity):
        loader = await cls.getLoader(ctx)
        return await loader.delete(entity.id)

    @classmethod
    async def ViewAuthor(cls, ctx: ServiceContext, author_id):
        loader = await cls.getLoader(ctx)
        author = await loader.load(author_id)
        if author is None:
            raise ServiceExceptionWithCode('Author not found', code='author_not_found')
        return author