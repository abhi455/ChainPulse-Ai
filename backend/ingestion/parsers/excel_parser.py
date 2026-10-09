from pathlib import Path

import pandas as pd


class ExcelParser:
    SUPPORTED_EXTENSIONS = {".xlsx", ".xlsm"}

    @classmethod
    def parse(cls, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported Excel file extension: {path.suffix}"
            )

        if not path.exists():
            raise FileNotFoundError(path)

        dataframe = pd.read_excel(path)

        dataframe.columns = [
            str(column).strip().lower()
            for column in dataframe.columns
        ]

        return dataframe
