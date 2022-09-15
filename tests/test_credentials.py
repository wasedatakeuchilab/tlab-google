import os
from collections import abc
from unittest import mock

import pytest
from google.oauth2 import credentials as google_oauth2_credentials

from tests import FixtureRequest
from tlab_google import credentials

CREDENTIALS_MOCK = mock.Mock(spec_set=credentials.Credentials)


@pytest.fixture(params=["empty", "single"])
def scopes(request: FixtureRequest[str]) -> list[str]:
    match request.param:
        case "empty":
            return []
        case "single":
            return ["https://www.googleapis.com/auth/gmail.send"]
    raise NotImplementedError


@pytest.fixture()
def from_client_config_mock() -> abc.Generator[mock.Mock, None, None]:
    with mock.patch(
        "google_auth_oauthlib.flow.InstalledAppFlow.from_client_config"
    ) as m:
        yield m


def test_new_credentials(from_client_config_mock: mock.Mock, scopes: list[str]) -> None:
    creds = credentials.new_credentials(scopes)
    assert (
        creds._credentials
        == from_client_config_mock.return_value.run_local_server.return_value
    )
    config = credentials.get_default_config()
    from_client_config_mock.assert_called_once_with(config, scopes)


@pytest.mark.parametrize("client_id", ["client_id_1", "client_id_2"])
def test_new_credentials_client_id(
    from_client_config_mock: mock.Mock, scopes: list[str], client_id: str
) -> None:
    creds = credentials.new_credentials(scopes, client_id=client_id)
    assert (
        creds._credentials
        == from_client_config_mock.return_value.run_local_server.return_value
    )
    config = credentials.get_default_config()
    config["installed"]["client_id"] = client_id
    from_client_config_mock.assert_called_once_with(config, scopes)


@pytest.mark.parametrize("client_secret", ["client_secret_1", "client_secret_2"])
def test_new_credentials_client_secret(
    from_client_config_mock: mock.Mock, scopes: list[str], client_secret: str
) -> None:
    creds = credentials.new_credentials(scopes, client_secret=client_secret)
    assert (
        creds._credentials
        == from_client_config_mock.return_value.run_local_server.return_value
    )
    config = credentials.get_default_config()
    config["installed"]["client_secret"] = client_secret
    from_client_config_mock.assert_called_once_with(config, scopes)


@pytest.mark.parametrize("run_local_server", [True, False])
def test_new_credentials_run_local_server(
    from_client_config_mock: mock.Mock, scopes: list[str], run_local_server: bool
) -> None:
    creds = credentials.new_credentials(scopes, run_local_server=run_local_server)
    if run_local_server:
        assert (
            creds._credentials
            == from_client_config_mock.return_value.run_local_server.return_value
        )
        from_client_config_mock.return_value.run_local_server.assert_called_once()
        from_client_config_mock.return_value.run_console.assert_not_called()
    else:
        assert (
            creds._credentials
            == from_client_config_mock.return_value.run_console.return_value
        )
        from_client_config_mock.return_value.run_local_server.assert_not_called()
        from_client_config_mock.return_value.run_console.assert_called_once()
    config = credentials.get_default_config()
    from_client_config_mock.assert_called_once_with(config, scopes)


@pytest.fixture()
def from_authorized_user_file_mock() -> abc.Generator[mock.Mock, None, None]:
    with mock.patch(
        "google.oauth2.credentials.Credentials.from_authorized_user_file"
    ) as m:
        yield m


@pytest.fixture()
def creds_mock(
    from_authorized_user_file_mock: mock.Mock,
    valid: bool,
    refresh_token: str | None,
) -> mock.Mock:
    creds_mock = from_authorized_user_file_mock.return_value
    assert isinstance(creds_mock, mock.Mock)
    creds_mock.valid = valid
    creds_mock.refresh_token = refresh_token
    return creds_mock


@pytest.mark.parametrize("filename", ["new_credentials_from_file_testcase.json"])
@pytest.mark.parametrize(["valid", "refresh_token"], [(True, None)])
def test_load_credentials(
    creds_mock: mock.Mock,
    from_authorized_user_file_mock: mock.Mock,
    filepath: str | os.PathLike[str],
    scopes: list[str],
) -> None:
    creds = credentials.load_credentials(filepath, scopes)
    assert creds._credentials == creds_mock
    from_authorized_user_file_mock.assert_called_once_with(filepath, scopes)
    creds_mock.refresh.assert_not_called()


@mock.patch("google.auth.transport.requests.Request")
@pytest.mark.parametrize("filename", ["new_credentials_from_file_testcase.json"])
@pytest.mark.parametrize(["valid", "refresh_token"], [(False, "refresh_token")])
def test_load_credentials_invalid_refreshable(
    request_mock: mock.Mock,
    creds_mock: mock.Mock,
    from_authorized_user_file_mock: mock.Mock,
    filepath: str | os.PathLike[str],
    scopes: list[str],
) -> None:
    creds = credentials.load_credentials(filepath, scopes)
    assert creds._credentials == creds_mock
    from_authorized_user_file_mock.assert_called_once_with(filepath, scopes)
    creds_mock.refresh.assert_called_once_with(request_mock.return_value)


@pytest.mark.parametrize("filename", ["new_credentials_from_file_testcase.json"])
@pytest.mark.parametrize(["valid", "refresh_token"], [(False, None)])
def test_load_credentials_invalid_unrefreshable(
    creds_mock: mock.Mock,
    from_authorized_user_file_mock: mock.Mock,
    filepath: str | os.PathLike[str],
    scopes: list[str],
) -> None:
    with pytest.raises(ValueError):
        credentials.load_credentials(filepath, scopes)
    from_authorized_user_file_mock.assert_called_once_with(filepath, scopes)
    creds_mock.refresh.assert_not_called()


def describe_credentials() -> None:
    @pytest.fixture()
    def creds() -> credentials.Credentials:
        return credentials.Credentials(
            mock.Mock(spec_set=google_oauth2_credentials.Credentials)
        )

    @pytest.fixture(params=["json1", "json2"])
    def json_text(request: FixtureRequest[str]) -> str:
        json_text = '{"token": "' + request.param + '"}'
        return json_text

    @pytest.mark.parametrize("filename", ["credentials.json"])
    def test_save(
        creds: credentials.Credentials, filepath: str | os.PathLike[str], json_text: str
    ) -> None:
        creds._credentials.to_json.return_value = json_text
        assert not os.path.exists(filepath)
        creds.save(filepath)
        with open(filepath) as f:
            assert f.read() == json_text

    @mock.patch("google.auth.transport.requests.Request")
    def test_refresh(request_mock: mock.Mock, creds: credentials.Credentials) -> None:
        creds.refresh()
        creds._credentials.refresh.assert_called_once_with(request_mock.return_value)
