import typing as t

from googleapiclient import discovery

from tlab_google import abstract


def build_service(api: abstract.AbstractAPI, **kwargs: t.Any) -> t.Any:
    """
    Construct a Resource for interacting with an API.

    Parameters
    ----------
    api : tlab_google.abstract.AbstractAPI
        An API to interact.
    **kwargs : Any
        Additional keyword arguments for `googleapiclient.discovery.build`.

    Returns
    -------
    Any
       A Resource object with methods for interacting with the service.
    """
    return discovery.build(
        serviceName=api.service_name,
        version=api.version,
        credentials=api.credentials._credentials,
        **kwargs,
    )
