import dataclasses
import typing

from src.Dataloaders import LoaderMap

if typing.TYPE_CHECKING:
    from src.ServiceDefinitions.Domain_Events.EventService import EventService as _EventService
    from src.ServiceDefinitions.Domain_Events.EventInvitationService import EventInvitationService as _EventInvitationService
    from src.ServiceDefinitions.Publications.PublicationService import PublicationService as _PublicationService
    from src.ServiceDefinitions.Publications.PublicationTypeService import PublicationTypeService as _PublicationTypeService
    from src.ServiceDefinitions.Publications.AuthorService import AuthorService as _AuthorService
    from src.ServiceDefinitions.Publications.AuthorshipService import AuthorshipService as _AuthorshipService



@dataclasses.dataclass(frozen=True)
class ServiceRegistry:
    @property
    def EventService(self) -> type['_EventService']:
        from src.ServiceDefinitions.Domain_Events.EventService import EventService
        return EventService

    @property
    def EventInvitationService(self) -> type['_EventInvitationService']:
        from src.ServiceDefinitions.Domain_Events.EventInvitationService import EventInvitationService
        return EventInvitationService
    
    @property
    def PublicationService(self) -> type['_PublicationService']:
        from src.ServiceDefinitions.Publications.PublicationService import PublicationService
        return PublicationService
    
    @property
    def PublicationTypeService(self) -> type['_PublicationTypeService']:
        from src.ServiceDefinitions.Publications.PublicationTypeService import PublicationTypeService
        return PublicationTypeService
    
    @property
    def AuthorService(self) -> type['_AuthorService']:
        from src.ServiceDefinitions.Publications.AuthorService import AuthorService
        return AuthorService
    
    @property
    def AuthorshipService(self) -> type['_AuthorshipService']:
        from src.ServiceDefinitions.Publications.AuthorshipService import AuthorshipService
        return AuthorshipService


SERVICES = ServiceRegistry()


@dataclasses.dataclass
class ServiceContext:
    loaders: LoaderMap
    user: typing.Any = None
    ug_client: typing.Callable[..., typing.Awaitable[typing.Any]] | None = None
    request: typing.Any = None
    session: typing.Any = None
    Services: ServiceRegistry = SERVICES

    # uoishelpers helpers commonly expect info.context to behave like a dict
    # with at least the key "loaders". Keeping these methods lets us pass a
    # typed ServiceContext directly as Strawberry context.
    def __getitem__(self, key: str) -> typing.Any:
        return getattr(self, key)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)
