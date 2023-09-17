"""File Writer Test case."""
import csv
import json
from pathlib import Path
from typing import Any, Self

from faker import Faker

from src.writer import Writer

fake = Faker("en_IN")


class TestWriter:
    """File Writer Test case."""

    out_file = "test.csv"
    no_of_records = 10
    csv_header = ["age", "name"]
    fake_data: list[dict[str, Any]] = []

    @staticmethod
    def _gen_fake_json(file_name: str = "") -> None:
        """Generate fake data."""
        if not file_name:
            file_name = TestWriter.out_file
        with Path(file_name + ".tmp").open(mode="w", encoding="utf-8") as tmp_file:
            for _ in range(TestWriter.no_of_records):
                cur_dict = {}
                for key in TestWriter.csv_header:
                    cur_dict[key] = fake.name()
                TestWriter.fake_data.append(cur_dict)
                tmp_file.write(json.dumps(cur_dict))
                tmp_file.write("\n")

    def setup_method(self: Self) -> None:
        """Create resources."""
        Path(self.out_file + ".tmp").unlink(missing_ok=True)
        self._gen_fake_json()

    def teardown_method(self: Self) -> None:
        """Cleaer up resources."""
        Path(self.out_file + ".tmp").unlink(missing_ok=True)
        self.fake_data = []

    def test_write_to_csv(self: Self) -> None:
        """Test write_to_csv function."""
        kwargs = {"delimiter": ","}
        Writer.write(self.no_of_records, self.out_file, self.csv_header, **kwargs)
        assert Path(self.out_file).exists(), "File does not exist"
        with Path(self.out_file).open() as file:
            reader = csv.reader(file)
            headers = next(reader)
            assert headers == self.csv_header, "Headers do not match"
            csv_data = [dict(zip(headers, i, strict=True)) for i in reader]

        assert len(csv_data) == self.no_of_records, "Record count does not match"
        assert csv_data == self.fake_data, "Generated data does not match with written data"
