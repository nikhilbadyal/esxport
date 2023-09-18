"""Write Data to file."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from tqdm import tqdm
from typing_extensions import NotRequired, TypedDict, Unpack


class WriterParams(TypedDict):
    """Writer parameters."""

    output_format: NotRequired[str]
    delimiter: NotRequired[str]


class Writer(object):
    """Write Data to file."""

    @staticmethod
    def write(
        total_records: int,
        out_file: str,
        headers: list[str],
        **kwargs: Unpack[WriterParams],
    ) -> None:
        """Write data to output file."""
        output_format = kwargs.get("output_format", "csv")
        if output_format == "csv":
            Writer._write_to_csv(total_records, out_file, headers, str(kwargs.get("delimiter", ",")))
        else:
            msg = f"Format {output_format} is not supported"
            raise NotImplementedError(msg)

    @staticmethod
    def _write_to_csv(total_records: int, out_file: str, headers: list[str], delimiter: str) -> None:
        """Write content to CSV file."""
        temp_file = f"{out_file}.tmp"
        with Path(out_file).open(mode="w", encoding="utf-8") as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=headers, delimiter=delimiter)
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
