import json

from decouple import Config
from decouple import DEFAULT_ENCODING
from decouple import RepositoryEnv
from decouple import RepositoryIni

from .extensions import ConfigByModel
from .repositories import RepositoryAWSParameterStore
from .repositories import RepositoryAWSSecrets


class CRUDConfig(Config):
    """
    CRUD Extension of python-decouple's Config class.

    Works the same as its parent method, but allows you to set, update, and delete keys.
    """

    def __iter__(self):
        return self.repository.__iter__()

    # CREATE method
    def set(self, key, value):
        if key not in self.repository:
            self.repository.set(key, value)
        else:
            raise ValueError("Error: Key already exists in the config")

    # LIST method
    def list(self):
        return self.repository.list()

    # UPDATE method
    def update(self, key, new_value):
        if key in self.repository:
            self.repository.set(key, new_value)
        else:
            raise KeyError("Error: There is no such key")

    # DELETE method
    def delete(self, key):
        if key in self.repository:
            del self.repository[key]
        else:
            raise KeyError("Error: There is no such key")


class CRUDConfigByModel(ConfigByModel, CRUDConfig):
    """Works the same as CRUDConfig but casts the values to the model."""


class CRUDBaseRepositoryMixin:
    def list(self):
        return list(self.data.keys())

    def __iter__(self):
        return iter(self.data)

    def __delitem__(self, __name: str) -> None:
        return self.delete(__name)


class CRUDRepositoryEnv(RepositoryEnv, CRUDBaseRepositoryMixin):
    """
    CRUD extension of python-decouple's RepositoryEnv class.

    Works the same as its parent method, but allows you to set, update, and delete keys.
    """

    def __init__(self, source, encoding=DEFAULT_ENCODING):
        self.source = source
        self.encoding = encoding
        super().__init__(source, encoding)

    def set(self, key, value):
        if not isinstance(value, str):
            try:
                value = json.dumps(value)
            except TypeError:
                raise TypeError("Error: Value must be a string or a JSON serializable object")

        self.data[key] = value
        with open(self.source, "a", encoding=self.encoding) as file_:
            file_.write(f"{key}={value}\n")

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            # This will rewrite the entire file without the deleted key
            with open(self.source, "w", encoding=self.encoding) as file_:
                for k, v in self.data.items():
                    file_.write(f"{k}={v}\n")


class CRUDRepositoryIni(RepositoryIni, CRUDBaseRepositoryMixin):
    """
    CRUD extension of python-decouple's RepositoryIni class.

    Works the same as its parent method, but allows you to set, update, and delete keys.
    """

    def __init__(self, source, encoding=DEFAULT_ENCODING):
        self.source = source
        self.encoding = encoding
        super().__init__(source, encoding)

    def list(self):
        if self.parser.has_section(self.SECTION):
            return self.parser.options(self.SECTION)
        else:
            return []

    def set(self, key, value):
        if not isinstance(value, str):
            try:
                value = json.dumps(value)
            except TypeError:
                raise TypeError("Error: Value must be a string or a JSON serializable object")

        self.parser.set(self.SECTION, key, value)
        with open(self.source, "w", encoding=self.encoding) as file_:
            self.parser.write(file_)

    def delete(self, key):
        if self.parser.has_option(self.SECTION, key):
            self.parser.remove_option(self.SECTION, key)
            with open(self.source, "w", encoding=self.encoding) as file_:
                self.parser.write(file_)


class CRUDBaseAWSRepositoryMixin:
    def set(self, key, value):
        # Check value
        if not isinstance(value, str):
            try:
                value = json.dumps(value)
            except TypeError:
                raise TypeError("Error: Value must be a string or a JSON serializable object")

        self.data[key] = value
        self._save_data()

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self._save_data()


class CRUDRepositoryAWSSecrets(RepositoryAWSSecrets, CRUDBaseAWSRepositoryMixin, CRUDBaseRepositoryMixin):
    """
    CRUD extension of our own RepositoryAWSSecrets class.

    Works the same as its parent method, but allows you to set, update, and delete keys.
    """

    def _save_data(self):
        self.client.put_secret_value(SecretId=self.secret_name, SecretString=json.dumps(self.data))


class CRUDRepositoryAWSParameterStore(RepositoryAWSParameterStore, CRUDBaseAWSRepositoryMixin, CRUDBaseRepositoryMixin):
    """
    CRUD extension of our own RepositoryAWSParameterStore class.

    Works the same as its parent method, but allows you to set, update, and delete keys.
    """

    def _save_data(self):
        self.client.put_parameter(Name=self.parameter_store_name, Value=json.dumps(self.data), Type="SecureString", Overwrite=True)
