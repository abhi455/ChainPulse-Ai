from __future__ import annotations

from typing import Any, Callable


class ColumnMapper:

    @staticmethod
    def map_records(
        records: list[dict[str, Any]],
        mapping: dict[str, str],
    ) -> list[dict[str, Any]]:

        result = []

        for record in records:
            result.append(
                {
                    target: record.get(source)
                    for source, target in mapping.items()
                }
            )

        return result

    @staticmethod
    def transform(
        records: list[dict[str, Any]],
        transforms: dict[str, Callable[[Any], Any]],
    ) -> list[dict[str, Any]]:

        result = []

        for record in records:
            transformed = dict(record)

            for field, function in transforms.items():
                if field in transformed:
                    transformed[field] = function(
                        transformed[field]
                    )

            result.append(transformed)

        return result
