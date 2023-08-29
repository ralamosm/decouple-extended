import json

import boto3
from decouple import UndefinedValueError


class RepositoryAWSSecrets:
    """
    Retrieves option keys from AWS Secrets Manager.
    """

    # Usage:
    # aws_secrets_repository = RepositoryAWSSecrets(secret_name="my_secret_name")

    def __init__(self, secret_name):
        self.secret_name = secret_name
        self.client = boto3.client("secretsmanager")
        self._load_secrets(secret_name)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise UndefinedValueError("{} not found in AWS Secrets. Declare it as envvar or define a default value.".format(key))

    def _load_secrets(self, secret_name):
        response = self.client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            self.data = json.loads(response["SecretString"])
        else:
            self.data = {}


class RepositoryAWSParameterStore:
    """
    Retrieves option keys from AWS Systems Manager Parameter Store.
    """

    def __init__(self, parameter_store_name):
        self.parameter_store_name = parameter_store_name
        self.client = boto3.client("ssm")
        self._load_parameters(parameter_store_name)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise UndefinedValueError(
                "{} not found in AWS Systems Manager Parameter Store. Declare it as an envvar or define a default value.".format(key)
            )

    def _load_parameters(self, parameter_store_name):
        response = self.client.get_parameter(Name=parameter_store_name, WithDecryption=True)
        if "Parameter" in response and "Value" in response["Parameter"]:
            self.data = json.loads(response["Parameter"]["Value"])
        else:
            self.data = {}
