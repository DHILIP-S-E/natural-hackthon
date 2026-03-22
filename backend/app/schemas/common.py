"""Common schemas — standard response wrappers, pagination."""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Any = None
    message: str = ""
    errors: List[str] = []


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    success: bool = True
    data: List[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0
    message: str = ""


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20
