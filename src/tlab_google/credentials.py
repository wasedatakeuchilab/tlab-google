from __future__ import annotations

import dataclasses
import os
import typing as t

from google.auth.transport import requests
from google.oauth2 import credentials
from google_auth_oauthlib import flow


def get_default_config() -> dict[str, t.Any]:
    return {
        "installed": {
            "client_id": "629905107772-2rq0b441g8k6v428ul0hvhlp0p8pq09a.apps.googleusercontent.com",
            "project_id": "tlab-346715",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": ["http://localhost"],
        }
    }


def new_credentials(
    scopes: list[str],
    client_id: str | None = None,
    client_secret: str | None = None,
    run_local_server: bool = True,
) -> Credentials:
    """
    Creates a new Credentials instance for Google API.

    Parameters
    ----------
    scopes : list[str]
        A list of scopes to request during the flow.
    client_id : str | None
        The client ID of the GCP project.
    client_secret : str | None
        The client secret of the GCP project.
    run_local_server : bool
        If true, a local server runs for the authorization flow.
        Otherwise, the user manually enters the authorization code instead.

    Returns
    -------
    tlab_google.credentials.Credentials
        A new OAuth 2.0 credentials.
    """
    client_config = get_default_config()
    if client_id:
        client_config["installed"]["client_id"] = client_id
    if client_secret:
        client_config["installed"]["client_secret"] = client_secret
    _flow = flow.InstalledAppFlow.from_client_config(client_config, scopes)
    creds = _flow.run_local_server() if run_local_server else _flow.run_console()
    return Credentials(creds)


def load_credentials(
    filepath: str | os.PathLike[str], scopes: list[str]
) -> Credentials:
    """
    Creates a Credentials instance for Google API from an authorized user json file.

    Parameters
    ----------
    filepath : str | os.PathLike[str]
        A path to the authorized user json file.
    scopes : list[str]
        A list of scopes to request during the flow.

    Returns
    -------
    tlab_google.credentials.Credentials
        The constructed OAuth 2.0 credentials.

    Raises
    ------
    ValueError
        If the constructed credentials is invalid.
    """
    creds = credentials.Credentials.from_authorized_user_file(filepath, scopes)
    if not creds.valid:
        if creds.refresh_token:
            creds.refresh(requests.Request())
        else:
            raise ValueError("The credentials is not valid and has no refresh token")
    return Credentials(creds)


@dataclasses.dataclass()
class Credentials:
    """
    Oauth 2.0 credentials for Google API.

    Examples
    --------
    Get a new Credentials through OAuth 2.0 flow.
    >>> scopes = []
    >>> creds = new_credentials(scopes)

    Load a Credentials from a file.
    >>> creds_filepath = "credentials.json"
    >>> creds = load_credentials(creds_filepath, scopes)

    Save the Credentials.
    >>> creds.save(creds_filepath)  # doctest: +SKIP

    Refresh the Crendentials.
    >>> creds.refresh()
    """

    _credentials: credentials.Credentials
    """Actual credentials."""

    def save(self, filepath: str | os.PathLike[str]) -> None:
        """
        Saves a Credentials instance as a json file.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            A path to save the credentials.
        """
        with open(filepath, "w") as f:
            f.write(self._credentials.to_json())

    def refresh(self) -> None:
        """
        Refreshes the access token.
        """
        self._credentials.refresh(requests.Request())
