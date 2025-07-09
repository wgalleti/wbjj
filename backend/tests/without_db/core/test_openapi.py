from django.contrib.auth import get_user_model

from apps.core.openapi import (
    add_authentication_examples,
    postprocess_schema_enums,
    preprocess_filter_specs,
)
from tests.base import BaseModelTestCase

User = get_user_model()


class TestOpenAPI(BaseModelTestCase):
    model_class = User

    def test_preprocess_filter_specs(self):
        endpoints = []
        result = preprocess_filter_specs(endpoints)
        self.assertEqual(result, endpoints)

    def test_postprocess_schema_enums(self):
        result = {"components": {"schemas": {}}}
        processed = postprocess_schema_enums(result, None, None, None)
        self.assertIn("Error", processed["components"]["schemas"])

    def test_add_authentication_examples(self):
        examples = add_authentication_examples([])
        self.assertIn("login", examples)
        self.assertIn("refresh", examples)
