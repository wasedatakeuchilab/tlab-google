import abc
import dataclasses

from . import credentials


@dataclasses.dataclass()  # type: ignore[misc]
class AbstractAPI(abc.ABC):
    """
    Abstract class for Google API.
    """

    credentials: credentials.Credentials
    """Credentials for the Google API."""
    version: str = ""
    """The version of the Google API."""

    @property
    @abc.abstractmethod
    def service_name(self) -> str:
        """
        The name of the Google service.
        """

    @classmethod
    @abc.abstractmethod
    def get_default_scopes(cls) -> list[str]:
        """
        Get the default scopes for the Google API.

        Returns
        -------
        list[str]
            A list of scopes.
        """
