"""
This module provides fixtures for doctests.

Note that this file will NOT be included when installed.
"""
import base64
import typing as t
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def from_client_config_mock() -> t.Generator[mock.Mock, None, None]:
    """
    For tlab_google.credentials.new_credentials
    """
    with mock.patch(
        "google_auth_oauthlib.flow.InstalledAppFlow.from_client_config"
    ) as m:
        yield m


@pytest.fixture(autouse=True)
def from_authorized_user_file_mock() -> t.Generator[mock.Mock, None, None]:
    """
    For tlab_google.credentials.load_credentials
    """
    with mock.patch(
        "google.oauth2.credentials.Credentials.from_authorized_user_file"
    ) as m:
        m.return_value.valid = True
        m.return_value.to_json.return_value = "creds_j"
        yield m


@pytest.fixture(autouse=True)
def build_service_mock() -> t.Generator[mock.Mock, None, None]:
    """
    For all google api
    """
    with mock.patch("tlab_google.utils.build_service") as m:
        yield m


@pytest.fixture(autouse=True)
def users_messages_list(build_service_mock: mock.Mock) -> None:
    """
    For tlab_google.gmail.GmailAPI.list_message
    """
    build_service_mock.return_value.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        "messages": [
            {
                "id": f"fake id {i}",
                "threadId": f"fake threadId {i}",
            }
            for i in range(10)
        ],
        "nextPageToken": "fake page token",
        "resultSizeEstimate": 100,
    }


@pytest.fixture(autouse=True)
def users_message_get(build_service_mock: mock.Mock) -> None:
    """
    For tlab_google.gmail.GmailAPI.get_message
    """
    message_body = base64.urlsafe_b64encode(b"fake message").decode()
    build_service_mock.return_value.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        "id": "fake id",
        "threadId": "fake threadId",
        "labelIds": [],
        "snippet": "fake snippet",
        "historyId": "fake historyId",
        "internalDate": "",
        "payload": {
            "partId": "fake partId",
            "mimetype": "fake mimetype",
            "filename": "fake filename",
            "headers": [{"name": "Subject", "value": "fake subject"}],
            "body": {
                "attachmentId": "fake attachmentId",
                "size": len(message_body),
                "data": message_body,
            },
            "parts": [],
        },
        "sizeEstimate": 4096,
        "raw": "fake raw",
    }
