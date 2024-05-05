# registry.py

"""
the desired behavior for the Registry is to distinguish between methods that:

Use a specific subclass of BaseModel directly, which should be registered normally under methods 
if it doesn’t require any special handling or dynamic model substitution.

Use a parameter of type BaseModel, which should be registered under model_methods because 
it indicates a need for potential model substitution or more dynamic handling.
"""
import inspect

from pydantic import BaseModel, Field
from .model_utils import ModelValidator


class RegistryEntry(BaseModel):
    method: callable
    annotations: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class ManagerRegistry:
    managers = {}

    @classmethod
    def add_manager(cls, manager):
        cls.managers[manager.name] = manager


class Registry:
    def __init__(self, parent):
        self.parent = parent
        self.methods = {}
        self.models = {}
        self.model_methods = {}
        self._register_parent_methods()

    def _update_manager(self):
        self.parent.assistant_manager.chat.add_tool(self.generate_json_schema(), [])

    def _register_parent_methods(self):
        methods = inspect.getmembers(self.parent, predicate=inspect.ismethod)
        for name, method in methods:
            if not name.startswith("_"):
                self.register_method(self.parent.name, name, method)
        self._update_manager()

    def register_method(self, parent_name, method_name, method):
        annotations = ModelValidator.get_annotations(method)
        has_base_model = ModelValidator.has_base_model_annotations(method)
        has_base_model_subclass = ModelValidator.has_base_model_subclass_annotations(method)

        entry = RegistryEntry(method=method, annotations=annotations)

        if has_base_model:
            self.model_methods[f"{parent_name}_{method_name}"] = entry
        elif has_base_model_subclass:
            self.methods[f"{parent_name}_{method_name}"] = entry
            # Register each unique subclass found in annotations as a model
            for type_ in annotations.values():
                if ModelValidator.is_base_model_subclass(type_):
                    if type_.__name__ not in self.models:
                        self.register_model(type_.__name__, type_)
        else:
            self.methods[f"{parent_name}_{method_name}"] = entry

    def register_model(self, model_name, model):
        if model_name not in self.models:
            self.models[model_name] = model
            print(f"Model {model_name} registered.")

    def link_model_to_methods(self, model_name, methods):
        model = self.models.get(model_name)
        if model:
            for method in methods:
                method_name = f"{method.__qualname__}_{model_name}_"
                annotations = ModelValidator.get_annotations(method)
                updated_annotations = {key: model if ModelValidator.is_base_model(value) else value for key, value in annotations.items()}
                entry = RegistryEntry(method=method, annotations=updated_annotations)
                self.methods[method_name] = entry
                self._update_manager()
        else:
            raise ValueError(f"Model {model_name} not found in the registry.")

    def unregister_model(self, model_name):
        if model_name in self.models:
            del self.models[model_name]
            tools_to_remove = self.unregister_model_specific_methods(model_name)
            self.parent.assistant_manager.chat.add_tool(self.generate_json_schema(), tools_to_remove)

    def unregister_model_specific_methods(self, model_name):
        tools_to_remove = []
        for key, entry in self.methods.items():
            print(key)
            if key.endswith(f"_{model_name}_"):
                tool_name = key.replace(f"{self.parent.name}_", "")
                tools_to_remove.append(tool_name)
        if not tools_to_remove:
            print("No specific methods found to unregister.")
        return tools_to_remove

    def generate_json_schema(self):
        from .schema_generator import generate_tool_schema

        return generate_tool_schema(self)
