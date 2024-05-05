from enum import Enum
import unittest
from pydantic import BaseModel
from schema_generator import python_type_to_json_schema


class MatchType(str, Enum):
    EXACT = "exact"
    CONTAINS = "contains"


class QueryModel(BaseModel):
    field_name: str
    match_type: MatchType
    search_value: str


class TestModel(BaseModel):
    name: str
    age: int


class TestPythonTypeToJsonSchema(unittest.TestCase):
    def test_base_model(self):
        schema = python_type_to_json_schema(TestModel)
        expected_schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"]}
        self.assertEqual(schema, expected_schema)

    def test_base_model_with_enum(self):
        schema = python_type_to_json_schema(QueryModel)
        expected_schema = {
            "type": "object",
            "properties": {"field_name": {"type": "string"}, "match_type": {"type": "string", "enum": ["exact", "contains"]}, "search_value": {"type": "string"}},
            "required": ["field_name", "match_type", "search_value"],
        }
        self.assertEqual(schema, expected_schema)

    def test_string_type(self):
        schema = python_type_to_json_schema(str)
        expected_schema = {"type": "string"}
        self.assertEqual(schema, expected_schema)

    def test_integer_type(self):
        schema = python_type_to_json_schema(int)
        expected_schema = {"type": "integer"}
        self.assertEqual(schema, expected_schema)

    def test_float_type(self):
        schema = python_type_to_json_schema(float)
        expected_schema = {"type": "number"}
        self.assertEqual(schema, expected_schema)

    def test_boolean_type(self):
        schema = python_type_to_json_schema(bool)
        expected_schema = {"type": "boolean"}
        self.assertEqual(schema, expected_schema)

    def test_list_type(self):
        schema = python_type_to_json_schema(list)
        expected_schema = {"type": "array", "items": {"type": "string"}}
        self.assertEqual(schema, expected_schema)

    def test_dict_type(self):
        schema = python_type_to_json_schema(dict)
        expected_schema = {"type": "object", "additionalProperties": {"type": "string"}}
        self.assertEqual(schema, expected_schema)

    def test_list_of_integers(self):
        schema = python_type_to_json_schema(list[int])
        expected_schema = {"type": "array", "items": {"type": "integer"}}
        self.assertEqual(schema, expected_schema)

    def test_list_of_base_class_subclass(self):
        schema = python_type_to_json_schema(list[TestModel])
        expected_schema = {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"]}}
        self.assertEqual(schema, expected_schema)

    def test_dict_with_integer_values(self):
        schema = python_type_to_json_schema(dict[str, int])
        expected_schema = {"type": "object", "additionalProperties": {"type": "integer"}}
        self.assertEqual(schema, expected_schema)


if __name__ == "__main__":
    unittest.main()
