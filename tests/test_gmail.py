import base64
import typing as t
from collections import abc
from email.mime import text
from unittest import mock

import pytest

from tests import FixtureRequest
from tlab_google import credentials, gmail


@pytest.fixture(autouse=True)
def build_service_mock() -> abc.Generator[mock.Mock, None, None]:
    with mock.patch("tlab_google.utils.build_service") as m:
        yield m


@pytest.fixture(params=["default", "version", "user_id"])
def api(request: FixtureRequest[str]) -> gmail.GmailAPI:
    creds = mock.Mock(spec_set=credentials.Credentials)
    match request.param:
        case "default":
            return gmail.GmailAPI(creds)
        case "version":
            return gmail.GmailAPI(creds, version="v2")
        case "user_id":
            return gmail.GmailAPI(creds, user_id="foo")
        case _:
            raise NotImplementedError


def describe_gmail_api() -> None:
    def test_service_name(api: gmail.GmailAPI) -> None:
        assert api.service_name == "gmail"

    def test__service(build_service_mock: mock.Mock, api: gmail.GmailAPI) -> None:
        assert api._service == build_service_mock.return_value
        build_service_mock.assert_called_once_with(api)

    def test_get_default_scopes(api: gmail.GmailAPI) -> None:
        assert api.get_default_scopes() == [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
        ]

    @pytest.mark.parametrize(
        "messages",
        [
            [
                {
                    "id": int(i).to_bytes(4, "little").hex(),
                    "threadId": int(j).to_bytes(4, "little").hex(),
                }
                for i in range(2)
            ]
            for j in range(2)
        ],
        ids=lambda msgs: "msgs_" + msgs[0]["threadId"],  # type: ignore
    )
    @pytest.mark.parametrize("next_page_token", [f"page_token_{i}" for i in range(2)])
    @pytest.mark.parametrize("result_size_estimate", [100, 200])
    def test_list_message_returns(
        api: gmail.GmailAPI,
        messages: list[gmail.Message],
        next_page_token: str,
        result_size_estimate: int,
    ) -> None:
        api._service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            "messages": messages,
            "nextPageToken": next_page_token,
            "resultSizeEstimate": result_size_estimate,
        }
        result = api.list_message("")
        assert result[0] == messages
        assert result[1] == next_page_token
        assert result[2] == result_size_estimate

    @pytest.mark.parametrize("query", [f"query_{i}" for i in range(2)])
    @pytest.mark.parametrize("max_results", [100, 200])
    @pytest.mark.parametrize("page_token", [None, "page_token"])
    @pytest.mark.parametrize("label_ids", [None, ["label"]])
    @pytest.mark.parametrize("include_spam_trash", [True, False])
    def test_list_message_api_call(
        api: gmail.GmailAPI,
        query: str,
        max_results: int,
        page_token: str | None,
        label_ids: list[str] | None,
        include_spam_trash: bool,
    ) -> None:
        api.list_message(
            query,
            max_results,
            page_token,
            label_ids,
            include_spam_trash,
        )
        users_messages_list = api._service.users.return_value.messages.return_value.list
        users_messages_list.assert_called_once_with(
            userId=api.user_id,
            q=query,
            maxResults=max_results,
            pageToken=page_token or "",
            labelIds=label_ids or [],
            includeSpamTrash=include_spam_trash,
        )
        users_messages_list.return_value.execute.assert_called_once_with()

    @pytest.mark.parametrize(
        "message",
        [
            {
                "id": int(i).to_bytes(4, "little").hex(),
                "threadId": int(i).to_bytes(4, "little").hex(),
            }
            for i in range(2)
        ],
        ids=lambda msg: "msg_" + msg["id"],  # type: ignore
    )
    def test_get_message_returns(api: gmail.GmailAPI, message: gmail.Message) -> None:
        api._service.users.return_value.messages.return_value.get.return_value.execute.return_value = (
            message
        )
        assert api.get_message(message["id"]) == message

    @pytest.mark.parametrize("id", ["foo", "bar"])
    @pytest.mark.parametrize("format", ["minimal", "full", "raw", "metadata"])
    def test_get_message_api_call(
        api: gmail.GmailAPI,
        id: str,
        format: t.Literal["minimal", "full", "raw", "metadata"],
    ) -> None:
        api.get_message(id, format=format)
        users_messages_get = api._service.users.return_value.messages.return_value.get
        users_messages_get.assert_called_once_with(
            userId=api.user_id, id=id, format=format
        )
        users_messages_get.return_value.execute_assert_called_once_with()

    @pytest.mark.parametrize(
        "message", [f"This is a mail test({i})." for i in range(3)]
    )
    def test_send_message(api: gmail.GmailAPI, message: str) -> None:
        msg = text.MIMEText(message)
        api.send_message(msg)
        users_messages_send = api._service.users.return_value.messages.return_value.send
        users_messages_send.assert_called_once_with(
            userId=api.user_id,
            body={"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()},
        )
        users_messages_send.return_value.execute.assert_called_once_with()

    @pytest.fixture()
    def sendas_list(api: gmail.GmailAPI) -> list[dict[str, t.Any]]:
        default_sendas = {
            "sendAsEmail": "default@example.com",
            "displayName": "dafault user",
            "signature": "default user",
            "isDefault": True,
        }
        sendas_list = [default_sendas] + [
            {
                "sendAsEmail": f"foo{i}@example.com",
                "displayName": "foo",
                "signature": f"foo{i} bar",
                "isDefault": False,
            }
            for i in range(3)
        ]
        users_settings_sendas_list = (
            api._service.users.return_value.settings.return_value.sendAs.return_value.list
        )
        users_settings_sendas_list.return_value.execute.return_value = {
            "sendAs": sendas_list
        }
        return sendas_list

    def test_get_signature_returns(
        api: gmail.GmailAPI, sendas_list: list[dict[str, t.Any]]
    ) -> None:
        default_sendas = [sendas for sendas in sendas_list if sendas["isDefault"]].pop()
        assert api.get_signature() == default_sendas.get("signature")

    @pytest.mark.parametrize("idx", list(range(3)))
    def test_get_signature_returns_address(
        api: gmail.GmailAPI, idx: int, sendas_list: list[dict[str, t.Any]]
    ) -> None:
        sendas = sendas_list[idx]
        assert api.get_signature(sendas["sendAsEmail"]) == sendas.get("signature")

    def test_get_signature_address_not_found(
        api: gmail.GmailAPI, sendas_list: list[dict[str, t.Any]]
    ) -> None:
        address_list = [sendas["sendAsEmail"] for sendas in sendas_list]
        address = "unexist_in_address_list@example.com"
        assert address not in address_list
        with pytest.raises(ValueError):
            api.get_signature(address)

    @pytest.mark.usefixtures(sendas_list.__name__)
    @pytest.mark.parametrize("address", [None, "default@example.com"])
    def test_get_signature_api_call(api: gmail.GmailAPI, address: str | None) -> None:
        api.get_signature(address)
        users_settings_sendas_list = (
            api._service.users.return_value.settings.return_value.sendAs.return_value.list
        )
        users_settings_sendas_list.assert_called_once_with(userId=api.user_id)
        users_settings_sendas_list.return_value.execute.assert_called_once_with()
