# schema_generator.py
from enum import Enum
from typing import Type, get_args, get_origin
from pydantic import BaseModel, Field
import inspect


def python_type_to_json_schema(param_type):
    origin = get_origin(param_type)
    if origin is not None:
        args = get_args(param_type)
        if origin == list:
            return {"type": "array", "items": python_type_to_json_schema(args[0])}
        elif origin == dict:
            value_schema = python_type_to_json_schema(args[1])
            return {"type": "object", "additionalProperties": value_schema}
        # Handle other generic types as needed
        return {"type": "object"}  # Fallback for unmapped generic types

    if isinstance(param_type, type):
        if issubclass(param_type, BaseModel):
            return generate_model_schema(param_type)
        elif issubclass(param_type, Enum):
            return {"type": "string", "enum": [e.value for e in param_type]}
        elif param_type == str:
            return {"type": "string"}
        elif param_type == int:
            return {"type": "integer"}
        elif param_type == float:
            return {"type": "number"}
        elif param_type == bool:
            return {"type": "boolean"}
        elif param_type == list:
            return {"type": "array", "items": {"type": "string"}}
        elif param_type == dict:
            return {"type": "object", "additionalProperties": {"type": "string"}}
        # Add more type mappings here as needed

    return {"type": "object"}  # Fallback for unmapped types


def generate_model_schema(model: Type[BaseModel]):
    properties = {}
    required = []

    for field_name, field_info in model.model_fields.items():

        field_type = field_info.annotation
        properties[field_name] = python_type_to_json_schema(field_type)
        if field_info.is_required():
            required.append(field_name)

    return {"type": "object", "properties": properties, "required": required}


def generate_method_schema(method_identifier, registry_entry):
    method = registry_entry.method
    annotations = registry_entry.annotations

    method_schema = {
        "type": "function",
        "function": {
            "name": method_identifier,
            "description": method.__doc__.strip() if method.__doc__ else "",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }
    sig = inspect.signature(method)
    for name, param in sig.parameters.items():
        param_type = annotations.get(name, param.annotation)
        if param_type == param.empty:
            param_type = type(None)

        param_schema = python_type_to_json_schema(param_type)
        method_schema["function"]["parameters"]["properties"][name] = param_schema
        if param.default == param.empty:
            method_schema["function"]["parameters"]["required"].append(name)

    return method_schema


def generate_tool_schema(registry):
    tool_schema = []

    for method_identifier, registry_entry in registry.methods.items():
        method_schema = generate_method_schema(method_identifier, registry_entry)
        tool_schema.append(method_schema)

    return tool_schema
