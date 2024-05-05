from typing import Dict, List
import unittest
from model_utils import ModelValidator
from pydantic import BaseModel


# Create a subclass of BaseModel for testing purposes
class MyModel(BaseModel):
    pass


def example_method(model: MyModel, name: str, age: int) -> MyModel:
    pass


def another_method(model: BaseModel, items: List[str]) -> Dict[str, BaseModel]:
    pass


def not_model_method(name: str, age: int) -> str:
    pass


class TestModelValidator(unittest.TestCase):
    def test_is_base_model(self):
        self.assertTrue(ModelValidator.is_base_model(BaseModel))
        self.assertFalse(ModelValidator.is_base_model(MyModel))
        self.assertFalse(ModelValidator.is_base_model(str))

    def test_is_base_model_subclass(self):
        self.assertTrue(ModelValidator.is_base_model_subclass(MyModel))
        self.assertFalse(ModelValidator.is_base_model_subclass(BaseModel))
        self.assertFalse(ModelValidator.is_base_model_subclass(str))

    def test_has_base_model_annotations(self):
        self.assertFalse(ModelValidator.has_base_model_annotations(example_method))
        self.assertTrue(ModelValidator.has_base_model_annotations(another_method))
        self.assertFalse(ModelValidator.has_base_model_annotations(not_model_method))

    def test_has_base_model_subclass_annotations(self):
        self.assertTrue(ModelValidator.has_base_model_subclass_annotations(example_method))
        self.assertFalse(ModelValidator.has_base_model_subclass_annotations(another_method))
        self.assertFalse(ModelValidator.has_base_model_subclass_annotations(not_model_method))


if __name__ == "__main__":
    unittest.main()
