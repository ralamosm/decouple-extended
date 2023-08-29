import os
from typing import Dict
from typing import Type

from decouple import Undefined
from decouple import undefined
from decouple import UndefinedValueError
from pydantic import BaseModel
from pydantic import create_model


class ConfigBaseModel(BaseModel):
    """Base class used by ConfigByModel to create one model per field"""

    @classmethod
    def with_fields(cls, **field_definitions):
        return create_model("ConfigSingleFieldModel", __base__=cls, **field_definitions)


class ConfigByModel(object):
    """
    Extension of python-decouple's Config class, to do casting using pydantic models
    """

    def __init__(self, repository, model: BaseModel = None):
        self.repository = repository
        self.model = model
        self.models_by_field = self.create_field_models(model)

    def create_field_models(self, model: Type[BaseModel]) -> Dict[str, Type[BaseModel]]:
        field_models = {}

        for field_name, field in model.__fields__.items():
            # Dynamically create a Pydantic model for the individual field
            attributes = {field_name: (field.annotation, field.default)}
            field_model = ConfigBaseModel.with_fields(**attributes)
            field_models[field_name] = field_model

        return field_models

    def _cast_with_pydantic(self, option, value):
        if self.model is None:
            return value

        parsed_data = self.models_by_field[option].parse_obj({option: value})
        return getattr(parsed_data, option)
        # except ValueError:
        #    # If the attribute doesn't exist or there's an error parsing, return the default value
        #    return self.model.__fields__[option].default

    def get(self, option, default=undefined, cast=undefined):
        """
        Return the value for option or default if defined.
        """

        # We can't avoid __contains__ because value may be empty.
        if option in os.environ:
            value = os.environ[option]
        elif option in self.repository:
            value = self.repository[option]
        elif option in self.models_by_field:
            if default and not isinstance(default, Undefined):
                value = default
            else:
                value = self.model.__fields__[
                    option
                ].default  # must be none because it wasn't caught by the repository, but still is defined in the model
        else:
            if isinstance(default, Undefined):
                raise UndefinedValueError("{} not found. Declare it as envvar or define a default value.".format(option))
            value = default

        # Use Pydantic model for casting if available
        if isinstance(cast, Undefined):
            value = self._cast_with_pydantic(option, value)
        else:
            # Fallback to the provided cast method if Pydantic didn't work or wasn't used
            if cast is bool:
                cast = self._cast_boolean
            value = cast(value)

        return value

    def __call__(self, *args, **kwargs):
        """
        Convenient shortcut to get.
        """
        return self.get(*args, **kwargs)
