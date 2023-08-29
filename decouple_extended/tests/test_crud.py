from unittest.mock import mock_open
from unittest.mock import patch

import boto3
from moto import mock_secretsmanager  # noqa F401
from moto import mock_ssm  # noqa F401

from decouple_extended.crud import CRUDRepositoryAWSParameterStore
from decouple_extended.crud import CRUDRepositoryAWSSecrets
from decouple_extended.crud import CRUDRepositoryEnv
from decouple_extended.crud import CRUDRepositoryIni


# AWS-based repositories
@mock_ssm
def test_crud_repository_aws_systems_manager():
    """Tests that CRUDRepositoryAWSParameterStore is able to set, check and delete keys"""
    parameter_store_name = "test_parameter_store"
    ssm = boto3.client("ssm")
    ssm.put_parameter(Name=parameter_store_name, Value="{}", Type="String")

    repo = CRUDRepositoryAWSParameterStore(parameter_store_name)

    # Test setting a key-value pair
    repo.set("key", "value")
    assert "key" in repo
    assert repo["key"] == "value"

    # list
    assert repo.list() == ["key"]

    # Test deleting a key
    repo.delete("key")
    assert "key" not in repo


@mock_secretsmanager
def test_crud_repository_aws_secrets():
    """Tests that CRUDRepositoryAWSSecrets is able to set, check and delete keys"""
    secret_name = "test_secret"
    secretsmanager = boto3.client("secretsmanager")
    secretsmanager.create_secret(Name=secret_name, SecretString="{}")

    repo = CRUDRepositoryAWSSecrets(secret_name)

    # Test setting a key-value pair
    repo.set("secret_key", "secret_value")
    assert "secret_key" in repo
    assert repo["secret_key"] == "secret_value"

    # list
    assert repo.list() == ["secret_key"]

    # Test deleting a key
    repo.delete("secret_key")
    assert "secret_key" not in repo


# File-based repositories
def test_crud_repository_env():
    data = "KEY=OLD_VALUE"
    with patch("decouple.open", mock_open(read_data=data)), patch("decouple_extended.crud.open", mock_open(read_data=data)):
        repo = CRUDRepositoryEnv(".env")

        repo.set("KEY", "VALUE")
        assert "KEY" in repo
        assert repo["KEY"] == "VALUE"

        # list
        assert repo.list() == ["KEY"]

        repo.delete("KEY")
        assert "KEY" not in repo


def test_crud_repository_ini():
    data = "[settings]\nKEY=OLD_VALUE"
    with patch("decouple.open", mock_open(read_data=data)), patch("decouple_extended.crud.open", mock_open(read_data=data)):
        repo = CRUDRepositoryIni("config.ini")

        repo.set("KEY", "VALUE")
        assert "KEY" in repo
        assert repo["KEY"] == "VALUE"

        # list
        assert repo.list() == ["key"]  # config parser returns a lower-cased key

        repo.delete("KEY")
        assert "KEY" not in repo
