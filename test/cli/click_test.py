"""Click test cases."""

import json

from typing_extensions import Self

from esxport.click_opt.cli_options import CliOptions


class TestClick:
    """Test clock option."""

    @staticmethod
    def is_json(myjson: str) -> bool:
        """Check if a string is json."""
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True

    def test_str_method_print_json(self: Self, cli_options: CliOptions) -> None:
        """Test str method print json."""
        str_method = str(cli_options)
        assert TestClick.is_json(str_method) is True
