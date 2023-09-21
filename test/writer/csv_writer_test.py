"""File Writer Test case."""
from __future__ import annotations

import csv
import inspect
import json
from pathlib import Path
from test.esxport._export_test import TestExport
from typing import TYPE_CHECKING, Any

from faker import Faker

from src.writer import Writer

if TYPE_CHECKING:
    from typing_extensions import Self

fake = Faker("en_IN")


class TestWriter:
    """File Writer Test case."""

    no_of_records = 10
    csv_header = ["age", "name"]
    fake_data: list[dict[str, Any]] = []

    @staticmethod
    def _gen_fake_json(file_name: str) -> None:
        """Generate fake data."""
        with Path(f"{file_name}.tmp").open(mode="w", encoding="utf-8") as tmp_file:
            for _ in range(TestWriter.no_of_records):
                cur_dict = {key: fake.name() for key in TestWriter.csv_header}
                TestWriter.fake_data.append(cur_dict)
                tmp_file.write(json.dumps(cur_dict))
                tmp_file.write("\n")

    @staticmethod
    def setup_data(file_name: str) -> None:
        """Create resources."""
        Path(f"{file_name}.tmp").unlink(missing_ok=True)
        TestWriter._gen_fake_json(file_name)

    def test_write_to_csv(self: Self) -> None:
        """Test write_to_csv function."""
        out_file = f"{inspect.stack()[0].function}.csv"
        TestWriter.setup_data(out_file)
        kwargs = {"delimiter": ","}
        Writer.write(self.no_of_records, out_file, self.csv_header, **kwargs)
        assert Path(out_file).exists(), "File does not exist"
        with Path(out_file).open() as file:
            reader = csv.reader(file)
            headers = next(reader)
            assert headers == self.csv_header, "Headers do not match"
            csv_data = [dict(zip(headers, i)) for i in reader]

        assert len(csv_data) == self.no_of_records, "Record count does not match"
        assert csv_data == self.fake_data, "Generated data does not match with written data"

        TestExport.rm_csv_export_file(out_file)
