"""Write Data to file."""
import csv
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from tqdm import tqdm

F = TypeVar("F", bound=Callable[..., Any])


class Writer(object):
    """Write Data to file."""

    @staticmethod
    def write_to_csv(total_records: int, out_file: str, csv_header: list[str], delimiter: str) -> None:
        """Write content to CSV file."""
        temp_file = out_file + ".tmp"
        with Path(out_file).open(mode="w", encoding="utf-8") as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=csv_header, delimiter=delimiter)
            csv_writer.writeheader()
            bar = tqdm(
                desc=out_file,
                total=total_records,
                unit="docs",
                colour="green",
            )
            with Path(temp_file).open(encoding="utf-8") as file:
                for _timer, line in enumerate(file, start=1):
                    bar.update(1)
                    csv_writer.writerow(json.loads(line))

            bar.close()
        Path(temp_file).unlink(missing_ok=True)
