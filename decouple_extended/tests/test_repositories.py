import boto3
import pytest
from decouple import UndefinedValueError
from moto import mock_secretsmanager
from moto import mock_ssm

from decouple_extended.repositories import RepositoryAWSParameterStore
from decouple_extended.repositories import RepositoryAWSSecrets


@mock_ssm
def test_repository_aws_systems_manager():
    """Tests that RepositoryAWSParameterStore works as expected as a python-decouple repository"""
    parameter_store_name = "test_parameter_store"
    ssm = boto3.client("ssm")
    ssm.put_parameter(Name=parameter_store_name, Value='{"key": "value"}', Type="SecureString")

    repo = RepositoryAWSParameterStore(parameter_store_name)
    assert "key" in repo
    assert repo["key"] == "value"

    with pytest.raises(UndefinedValueError):
        _ = repo["undefined_key"]


@mock_secretsmanager
def test_repository_aws_secrets():
    """Tests that RepositoryAWSSecrets works as expected as a python-decouple repository"""
    secret_name = "test_secret"
    secretsmanager = boto3.client("secretsmanager")
    secretsmanager.create_secret(Name=secret_name, SecretString='{"secret_key": "secret_value"}')

    repo = RepositoryAWSSecrets(secret_name)
    assert "secret_key" in repo
    assert repo["secret_key"] == "secret_value"

    with pytest.raises(UndefinedValueError):
        _ = repo["undefined_key"]
