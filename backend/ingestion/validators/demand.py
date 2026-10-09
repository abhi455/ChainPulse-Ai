import pandas as pd

from backend.ingestion.validators.common import (
    ValidationResult,
    require_columns,
)


REQUIRED_COLUMNS = [
    "date",
    "product_id",
    "quantity",
]


def validate_demand_dataframe(
    dataframe: pd.DataFrame,
) -> ValidationResult:
    result = require_columns(
        list(dataframe.columns),
        REQUIRED_COLUMNS,
    )

    if not result.valid:
        return result

    errors = list(result.errors)
    warnings = list(result.warnings)

    dates = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    if dates.isna().any():
        errors.append("Column 'date' contains invalid dates")

    quantities = pd.to_numeric(
        dataframe["quantity"],
        errors="coerce",
    )

    if quantities.isna().any():
        errors.append("Column 'quantity' contains non-numeric values")

    if (quantities.dropna() < 0).any():
        errors.append("Column 'quantity' cannot contain negative values")

    if dataframe["product_id"].isna().any():
        errors.append("Column 'product_id' contains missing values")

    if dataframe.empty:
        errors.append("Dataset is empty")

    if len(dataframe) < 2:
        warnings.append("Dataset contains fewer than 2 records")

    return ValidationResult(
        valid=not errors,
        errors=errors,
        warnings=warnings,
    )
