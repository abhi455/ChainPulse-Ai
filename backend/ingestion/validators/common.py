from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


def require_columns(
    columns: list[str],
    required: list[str],
) -> ValidationResult:
    errors = [
        f"Missing required column: {column}"
        for column in required
        if column not in columns
    ]

    return ValidationResult(
        valid=not errors,
        errors=errors,
    )
