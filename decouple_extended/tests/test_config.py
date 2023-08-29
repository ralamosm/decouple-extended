from unittest.mock import mock_open
from unittest.mock import patch

import boto3
import pytest
from moto import mock_secretsmanager  # noqa F401
from moto import mock_ssm  # noqa F401

from decouple_extended import crud


@pytest.mark.parametrize(
    "repo_cls,config_data",
    [
        (crud.CRUDRepositoryIni, "[settings]\nKEY1=VALUE1\nKEY2=VALUE2\n"),
        (crud.CRUDRepositoryEnv, "KEY1=VALUE1\nKEY2=VALUE2\n"),
    ],
)
def test_crud_config_with_filebased_repositories(repo_cls, config_data):
    """Tests that CRUDConfig together with file-based repositories can perform CRUD operations"""
    m = mock_open(read_data=config_data)

    with patch("builtins.open", m), patch("decouple.open", m):
        config = crud.CRUDConfig(repo_cls("/path/to/config_file"))

        assert "KEY1" in config.repository
        assert config("KEY1") == "VALUE1"

        # Test CREATE
        config.set("KEY3", "VALUE3")
        assert "KEY3" in config.repository
        assert config("KEY3") == "VALUE3"

        # Test LIST
        assert config.list() in (["KEY1", "KEY2", "KEY3"], ["key1", "key2", "key3"])

        # Test UPDATE
        config.update("KEY2", "NEWVALUE2")
        assert "KEY2" in config.repository
        assert config("KEY2") == "NEWVALUE2"

        # Test DELETE
        config.delete("KEY1")
        assert "KEY1" not in config.repository

        assert config.list() in (["KEY2", "KEY3"], ["key2", "key3"])


@pytest.mark.parametrize(
    "repo_cls,aws_service,aws_method,aws_kwargs",
    [
        (crud.CRUDRepositoryAWSSecrets, "secretsmanager", "create_secret", {"SecretString": '{"KEY1": "VALUE1"}'}),
        (crud.CRUDRepositoryAWSParameterStore, "ssm", "put_parameter", {"Value": '{"KEY1": "VALUE1"}', "Type": "SecureString"}),
    ],
)
def test_crud_config_with_aws_repositories(repo_cls, aws_service, aws_method, aws_kwargs):
    """Tests that CRUDConfig together with aws-based repositories can perform CRUD operations"""
    with globals()["mock_{}".format(aws_service)]():  # mock aws service using one of the mock_x moto methods
        config_name = "config_data"
        awscli = boto3.client(aws_service)
        kwargs = {"Name": config_name}
        kwargs.update(aws_kwargs)
        getattr(awscli, aws_method)(**kwargs)

        repository = repo_cls(config_name)
        config = crud.CRUDConfig(repository)

        assert "KEY1" in config.repository
        assert config("KEY1") == "VALUE1"

        # Test CREATE
        config.set("KEY2", "VALUE2")
        assert "KEY2" in config.repository
        assert config("KEY2") == "VALUE2"

        # Test LIST
        assert config.list() == ["KEY1", "KEY2"]

        # Test UPDATE
        config.update("KEY1", "NEWVALUE1")
        assert "KEY1" in config.repository
        assert config("KEY1") == "NEWVALUE1"

        # Test DELETE
        config.delete("KEY1")
        assert "KEY1" not in config.repository

        assert config.list() == ["KEY2"]
