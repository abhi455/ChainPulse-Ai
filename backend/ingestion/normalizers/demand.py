import pandas as pd


def normalize_demand(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()

    result["date"] = pd.to_datetime(
        result["date"],
        errors="raise",
    )

    result["product_id"] = (
        result["product_id"]
        .astype(str)
        .str.strip()
    )

    result["quantity"] = pd.to_numeric(
        result["quantity"],
        errors="raise",
    )

    result = result.sort_values(
        ["product_id", "date"]
    ).reset_index(drop=True)

    return result
