import json
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

import counter


class TestVisitorCounter(unittest.TestCase):

    @patch("counter.boto3")
    def test_counter_returns_200(self, mock_boto3):
        mock_table = MagicMock()
        mock_boto3.resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {
            "Attributes": {"count": Decimal("42")}
        }
        result = counter.lambda_handler({}, {})
        self.assertEqual(result["statusCode"], 200)

    @patch("counter.boto3")
    def test_counter_returns_count(self, mock_boto3):
        mock_table = MagicMock()
        mock_boto3.resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {
            "Attributes": {"count": Decimal("7")}
        }
        result = counter.lambda_handler({}, {})
        body = json.loads(result["body"])
        self.assertEqual(body["count"], 7)

    @patch("counter.boto3")
    def test_cors_headers_present(self, mock_boto3):
        mock_table = MagicMock()
        mock_boto3.resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {
            "Attributes": {"count": Decimal("1")}
        }
        result = counter.lambda_handler({}, {})
        self.assertIn("Access-Control-Allow-Origin", result["headers"])

    @patch("counter.boto3")
    def test_dynamodb_update_called(self, mock_boto3):
        mock_table = MagicMock()
        mock_boto3.resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {
            "Attributes": {"count": Decimal("3")}
        }
        counter.lambda_handler({}, {})
        mock_table.update_item.assert_called_once()

    @patch("counter.boto3")
    def test_response_body_is_valid_json(self, mock_boto3):
        mock_table = MagicMock()
        mock_boto3.resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {
            "Attributes": {"count": Decimal("5")}
        }
        result = counter.lambda_handler({}, {})
        parsed = json.loads(result["body"])
        self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()