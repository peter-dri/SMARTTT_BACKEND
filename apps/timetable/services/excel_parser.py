import pandas as pd
from typing import Dict, List, Any, Tuple

from apps.timetable.utils import (
    FileValidationException,
    ExcelParsingException,
    TimetableLogger,
    REQUIRED_TIMETABLE_COLUMNS,
)


class TimetableExcelParserService:
    def __init__(self):
        """Initialize parser with logging."""
        self.logger = TimetableLogger()
    
    def parse(self, file_path: str) -> pd.DataFrame:
        try:
            # Read Excel file without assuming types
            df = pd.read_excel(
                file_path,
                sheet_name=0,  # Read first sheet
                dtype=str,  # Read everything as string initially
                na_values=["", "NA", "N/A", "null", "NULL", "None"],
            )
            
            # Normalize column names: strip spaces and convert to lowercase
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            # Remove completely empty rows
            df = df.dropna(how="all")
            
            # Reset index after dropping rows
            df = df.reset_index(drop=True)
            
            if len(df) == 0:
                raise ExcelParsingException(
                    "Excel file contains no data rows after the header."
                )
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ExcelParsingException("Excel file is empty.")
        except pd.errors.ParserError as e:
            raise ExcelParsingException(f"Failed to parse Excel file: {str(e)}")
        except Exception as e:
            raise ExcelParsingException(f"Unexpected error reading Excel file: {str(e)}")
    
    def extract_rows(self, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """
        Extract and normalize rows from dataframe.
        
        Args:
            df: Parsed pandas DataFrame
            
        Returns:
            Tuple of (valid_rows, error_rows) where each is a list of dictionaries
            
        Raises:
            ExcelParsingException: If critical parsing error occurs
        """
        valid_rows = []
        error_rows = []
        
        for idx, row in df.iterrows():
            try:
                # Convert row to dict
                row_dict = row.to_dict()
                
                # Clean up the row data
                cleaned_row = self._clean_row_data(row_dict, idx + 2)  # +2 for header and 1-based
                
                valid_rows.append(cleaned_row)
                
            except ValueError as e:
                error_rows.append({
                    "row_number": idx + 2,
                    "error": str(e),
                    "data": row.to_dict(),
                })
        
        if len(valid_rows) == 0 and len(error_rows) > 0:
            raise ExcelParsingException(
                f"All {len(error_rows)} rows contained parsing errors."
            )
        
        return valid_rows, error_rows
    
    @staticmethod
    def _clean_row_data(row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
        cleaned = {}
        
        # Process each required column
        for field in REQUIRED_TIMETABLE_COLUMNS:
            value = row.get(field)
            
            # Handle NaN and null values
            if pd.isna(value) or value is None:
                cleaned[field] = None
                continue
            
            # Convert to string and strip whitespace
            if isinstance(value, str):
                value = value.strip()
            else:
                value = str(value).strip()
            
            cleaned[field] = value if value else None
        
        # Add optional fields if present
        for field in ["notes", "venue_name", "session_type"]:
            if field in row:
                value = row.get(field)
                if pd.isna(value) or value is None:
                    continue
                if isinstance(value, str):
                    value = value.strip()
                else:
                    value = str(value).strip()
                if value:
                    cleaned[field] = value
        
        # Parse time fields
        try:
            start_time = row.get("start_time")
            end_time = row.get("end_time")
            
            if pd.isna(start_time):
                raise ValueError("start_time is empty")
            if pd.isna(end_time):
                raise ValueError("end_time is empty")
            
            # If times are already time objects, keep them
            if not isinstance(start_time, str):
                if hasattr(start_time, "strftime"):
                    cleaned["start_time"] = start_time.time() if hasattr(start_time, "time") else start_time
                else:
                    cleaned["start_time"] = start_time
            else:
                # Parse string time
                cleaned["start_time"] = start_time
            
            if not isinstance(end_time, str):
                if hasattr(end_time, "strftime"):
                    cleaned["end_time"] = end_time.time() if hasattr(end_time, "time") else end_time
                else:
                    cleaned["end_time"] = end_time
            else:
                cleaned["end_time"] = end_time
                
        except Exception as e:
            raise ValueError(f"Error parsing times: {str(e)}")
        
        return cleaned

