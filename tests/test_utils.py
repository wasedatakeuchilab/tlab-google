from unittest import mock

import pytest

from tlab_google import abstract, utils


@pytest.fixture()
def api() -> abstract.AbstractAPI:
    return mock.Mock(parent=abstract.AbstractAPI)


@mock.patch("googleapiclient.discovery.build")
def test_build_service(build_mock: mock.Mock, api: abstract.AbstractAPI) -> None:
    assert utils.build_service(api) == build_mock.return_value
    build_mock.assert_called_once_with(
        serviceName=api.service_name,
        credentials=api.credentials._credentials,
        version=api.version,
    )
