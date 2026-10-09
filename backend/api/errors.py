from fastapi import HTTPException, status


class ChainPulseAPIError(HTTPException):
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class ResourceNotFoundError(ChainPulseAPIError):
    def __init__(self, resource: str) -> None:
        super().__init__(
            detail=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BusinessRuleError(ChainPulseAPIError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
