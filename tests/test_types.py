import pytest

from dynconfig.exceptions import ConfigTypeError
from dynconfig.types import cast_value


class TestCastString:
    def test_basic(self):
        assert cast_value("k", "hello", "string") == "hello"

    def test_empty(self):
        assert cast_value("k", "", "string") == ""

    def test_number_as_string(self):
        assert cast_value("k", "123", "string") == "123"


class TestCastInteger:
    def test_basic(self):
        assert cast_value("k", "42", "integer") == 42

    def test_negative(self):
        assert cast_value("k", "-7", "integer") == -7

    def test_empty_returns_zero(self):
        assert cast_value("k", "", "integer") == 0

    def test_invalid_raises(self):
        with pytest.raises(ConfigTypeError):
            cast_value("k", "not_a_number", "integer")


class TestCastFloat:
    def test_basic(self):
        assert cast_value("k", "3.14", "float") == 3.14

    def test_empty_returns_zero(self):
        assert cast_value("k", "", "float") == 0.0

    def test_integer_string(self):
        assert cast_value("k", "5", "float") == 5.0


class TestCastBoolean:
    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "yes", "on"])
    def test_truthy(self, value):
        assert cast_value("k", value, "boolean") is True

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "off", ""])
    def test_falsy(self, value):
        assert cast_value("k", value, "boolean") is False

    def test_invalid_raises(self):
        with pytest.raises(ConfigTypeError):
            cast_value("k", "maybe", "boolean")

    def test_python_bool_passthrough(self):
        assert cast_value("k", True, "boolean") is True
        assert cast_value("k", False, "boolean") is False


class TestCastJSON:
    def test_dict(self):
        result = cast_value("k", '{"a": 1}', "json")
        assert result == {"a": 1}

    def test_list(self):
        result = cast_value("k", '[1, 2, 3]', "json")
        assert result == [1, 2, 3]

    def test_empty_returns_dict(self):
        assert cast_value("k", "", "json") == {}

    def test_invalid_raises(self):
        with pytest.raises(ConfigTypeError):
            cast_value("k", "not json", "json")

    def test_python_dict_passthrough(self):
        data = {"key": "value"}
        assert cast_value("k", data, "json") == data


class TestCastList:
    def test_basic(self):
        assert cast_value("k", "a, b, c", "list") == ["a", "b", "c"]

    def test_strips_whitespace(self):
        assert cast_value("k", " x , y , z ", "list") == ["x", "y", "z"]

    def test_empty_returns_list(self):
        assert cast_value("k", "", "list") == []

    def test_single_item(self):
        assert cast_value("k", "only", "list") == ["only"]

    def test_python_list_passthrough(self):
        data = ["a", "b"]
        assert cast_value("k", data, "list") == data

    def test_filters_empty_items(self):
        assert cast_value("k", "a,,b, ,c", "list") == ["a", "b", "c"]
