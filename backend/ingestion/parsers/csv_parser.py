from pathlib import Path

import pandas as pd


class CSVParser:
    SUPPORTED_EXTENSIONS = {".csv"}

    @classmethod
    def parse(cls, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported CSV file extension: {path.suffix}"
            )

        if not path.exists():
            raise FileNotFoundError(path)

        dataframe = pd.read_csv(path)

        dataframe.columns = [
            str(column).strip().lower()
            for column in dataframe.columns
        ]

        return dataframe
