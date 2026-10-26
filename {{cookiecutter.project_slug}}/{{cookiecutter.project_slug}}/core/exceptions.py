from typing import Any


# Base of the errors services raise on purpose, for rules that depend on database
# state. Each app adds <App>Error(ApplicationError) and subclasses it per rule:
# <App><Thing>Error.
class ApplicationError(Exception):
    def __init__(self, message: str, *, extra: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.extra = extra or {}
