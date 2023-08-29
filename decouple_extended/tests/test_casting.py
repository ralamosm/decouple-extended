import json
from typing import Optional
from typing import Union
from unittest.mock import mock_open
from unittest.mock import patch

import boto3
import pytest
from moto import mock_secretsmanager  # noqa F401
from moto import mock_ssm  # noqa F401
from pydantic import BaseModel
from pydantic import Json

from decouple_extended import crud
from decouple_extended.extensions import ConfigByModel


class TestModel(BaseModel):
    """Model to be used for testing casting by pydantic"""

    int1: int
    dict1: Union[dict, Json]
    bool1: Optional[bool] = None


@pytest.mark.parametrize(
    "repo_cls,config_data",
    [
        (crud.CRUDRepositoryIni, '[settings]\nint1=1337\ndict1={"foo":"bar"}\n'),
        (crud.CRUDRepositoryEnv, 'int1=1337\ndict1={"foo":"bar"}\n'),
    ],
)
def test_casting_filebased_repositories(repo_cls, config_data):
    """Tests that CRUDConfig together with file-based repositories can correctly cast values"""
    m = mock_open(read_data=config_data)

    with patch("builtins.open", m), patch("decouple.open", m):
        config = crud.CRUDConfig(repo_cls("/path/to/config_file"))

        int1 = config("int1", cast=int)
        dict1 = config("dict1", cast=json.loads)

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}


@pytest.mark.parametrize(
    "repo_cls,aws_service,aws_method,aws_kwargs",
    [
        (crud.CRUDRepositoryAWSSecrets, "secretsmanager", "create_secret", {"SecretString": '{"int1": 1337, "dict1":{"foo":"bar"}}'}),
        (crud.CRUDRepositoryAWSParameterStore, "ssm", "put_parameter", {"Value": '{"int1": 1337, "dict1":{"foo":"bar"}}', "Type": "SecureString"}),
    ],
)
def test_casting_aws_repositories(repo_cls, aws_service, aws_method, aws_kwargs):
    """Tests that CRUDConfig together with aws-based repositories can perform CRUD operations"""
    with globals()["mock_{}".format(aws_service)]():  # mock aws service using one of the mock_x moto methods
        config_name = "config_data"
        awscli = boto3.client(aws_service)
        kwargs = {"Name": config_name}
        kwargs.update(aws_kwargs)
        getattr(awscli, aws_method)(**kwargs)

        repository = repo_cls(config_name)
        config = crud.CRUDConfig(repository)

        int1 = config("int1")
        dict1 = config("dict1")

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}


@pytest.mark.parametrize(
    "repo_cls,config_data",
    [
        (crud.CRUDRepositoryIni, '[settings]\nint1=1337\ndict1={"foo":"bar"}\n'),
        (crud.CRUDRepositoryEnv, 'int1=1337\ndict1={"foo":"bar"}\n'),
    ],
)
def test_casting_filebased_by_pydantic(repo_cls, config_data):
    """Tests that CRUDConfig together with file-based repositories can correctly cast values"""
    m = mock_open(read_data=config_data)

    with patch("builtins.open", m), patch("decouple.open", m):
        config = ConfigByModel(repo_cls("/path/to/config_file"), TestModel)

        int1 = config("int1")
        dict1 = config("dict1")

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}


@pytest.mark.parametrize(
    "repo_cls,aws_service,aws_method,aws_kwargs",
    [
        (crud.CRUDRepositoryAWSSecrets, "secretsmanager", "create_secret", {"SecretString": '{"int1": 1337, "dict1":{"foo":"bar"}}'}),
        (crud.CRUDRepositoryAWSParameterStore, "ssm", "put_parameter", {"Value": '{"int1": 1337, "dict1":{"foo":"bar"}}', "Type": "SecureString"}),
    ],
)
def test_casting_aws_by_pydantic(repo_cls, aws_service, aws_method, aws_kwargs):
    """Tests that CRUDConfig together with aws-based repositories can perform CRUD operations"""
    with globals()["mock_{}".format(aws_service)]():  # mock aws service using one of the mock_x moto methods
        config_name = "config_data"
        awscli = boto3.client(aws_service)
        kwargs = {"Name": config_name}
        kwargs.update(aws_kwargs)
        getattr(awscli, aws_method)(**kwargs)

        repository = repo_cls(config_name)
        config = ConfigByModel(repository, TestModel)

        int1 = config("int1")
        dict1 = config("dict1")

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}


@pytest.mark.parametrize(
    "repo_cls,config_data",
    [
        (crud.CRUDRepositoryIni, '[settings]\nint1=1337\ndict1={"foo":"bar"}\n'),
        (crud.CRUDRepositoryEnv, 'int1=1337\ndict1={"foo":"bar"}\n'),
    ],
)
def test_crud_casting_filebased_by_pydantic(repo_cls, config_data):
    """Tests that CRUDConfigByModel together with file-based repositories can correctly cast values"""
    m = mock_open(read_data=config_data)

    with patch("builtins.open", m), patch("decouple.open", m):
        config = crud.CRUDConfigByModel(repo_cls("/path/to/config_file"), TestModel)

        int1 = config("int1")
        dict1 = config("dict1")

        assert config.list() == ["int1", "dict1"]

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}
        assert config("bool1") is None

        config.set("bool1", True)
        assert config("bool1") is True

        assert config.list() == ["int1", "dict1", "bool1"]

        config.delete("int1")
        assert config("int1") is None

        assert config.list() == ["dict1", "bool1"]


@pytest.mark.parametrize(
    "repo_cls,aws_service,aws_method,aws_kwargs",
    [
        (crud.CRUDRepositoryAWSSecrets, "secretsmanager", "create_secret", {"SecretString": '{"int1": 1337, "dict1":{"foo":"bar"}}'}),
        (crud.CRUDRepositoryAWSParameterStore, "ssm", "put_parameter", {"Value": '{"int1": 1337, "dict1":{"foo":"bar"}}', "Type": "SecureString"}),
    ],
)
def test_crud_casting_aws_by_pydantic(repo_cls, aws_service, aws_method, aws_kwargs):
    """Tests that CRUDConfig together with aws-based repositories can perform CRUD operations"""
    with globals()["mock_{}".format(aws_service)]():  # mock aws service using one of the mock_x moto methods
        config_name = "config_data"
        awscli = boto3.client(aws_service)
        kwargs = {"Name": config_name}
        kwargs.update(aws_kwargs)
        getattr(awscli, aws_method)(**kwargs)

        repository = repo_cls(config_name)
        config = crud.CRUDConfigByModel(repository, TestModel)

        int1 = config("int1")
        dict1 = config("dict1")

        assert config.list() == ["int1", "dict1"]

        assert int1 == 1337
        assert dict1 == {"foo": "bar"}
        assert config("bool1") is None

        config.set("bool1", True)
        assert config("bool1") is True

        assert config.list() == ["int1", "dict1", "bool1"]

        config.delete("int1")
        assert config("int1") is None

        assert config.list() == ["dict1", "bool1"]
