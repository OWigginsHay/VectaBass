# model_utils.py
from typing import get_type_hints
from pydantic import BaseModel
import inspect


class ModelValidator:
    @staticmethod
    def is_base_model(param_type):
        """Check if the parameter type is exactly BaseModel."""
        return param_type is BaseModel

    @staticmethod
    def is_base_model_subclass(param_type):
        """Check if the parameter type is a subclass of BaseModel, excluding BaseModel itself."""
        return inspect.isclass(param_type) and issubclass(param_type, BaseModel) and param_type is not BaseModel

    @staticmethod
    def is_generic_base_model_subclass(param_type):
        """Check for generic types that are subclasses of BaseModel."""
        if hasattr(param_type, "__origin__"):  # This checks if it's a generic type
            return inspect.isclass(param_type.__origin__) and issubclass(param_type.__origin__, BaseModel)
        return False

    @staticmethod
    def get_annotations(method):
        """Get annotations of a method."""
        if hasattr(method, "__annotations__"):
            return method.__annotations__
        else:
            return {}

    @staticmethod
    def has_base_model_annotations(method) -> bool:
        """Check if a method has annotations that are exactly BaseModel."""
        annotations = get_type_hints(method)
        return any(ModelValidator.is_base_model(type_) for type_ in annotations.values())

    @staticmethod
    def has_base_model_subclass_annotations(method):
        """Check if a method has annotations that are subclasses of BaseModel."""
        annotations = get_type_hints(method)
        return any(ModelValidator.is_base_model_subclass(type_) for type_ in annotations.values())
