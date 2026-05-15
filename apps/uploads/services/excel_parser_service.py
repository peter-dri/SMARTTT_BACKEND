from __future__ import annotations

import pandas as pd
from django.core.files.uploadedfile import UploadedFile

from apps.uploads.utils import ParsedWorkbookRow, normalize_column_name, normalize_row_payload


class ExcelParserService:
    @staticmethod
    def read_workbook(uploaded_file: UploadedFile, sheet_name: int | str = 0) -> pd.DataFrame:
        dataframe = pd.read_excel(uploaded_file, sheet_name=sheet_name, dtype=object, engine="openpyxl")
        dataframe = dataframe.dropna(how="all").reset_index(drop=True)
        dataframe.columns = [normalize_column_name(column) for column in dataframe.columns]
        return dataframe

    @staticmethod
    def parse_rows(dataframe: pd.DataFrame) -> list[ParsedWorkbookRow]:
        rows: list[ParsedWorkbookRow] = []
        for index, row in dataframe.iterrows():
            raw_data = {key: (None if pd.isna(value) else value) for key, value in row.to_dict().items()}
            rows.append(
                ParsedWorkbookRow(
                    row_number=index + 2,
                    raw_data=raw_data,
                    normalized_data=normalize_row_payload(raw_data),
                )
            )
        return rows