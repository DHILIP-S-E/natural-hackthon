"""Standard API response shapes.

All routers must return APIResponse. All request/response schemas
must extend OurBaseModel so from_attributes=True is always set.

Usage:
    from schemas.response import APIResponse, OurBaseModel

    class MySchema(OurBaseModel):
        id: str
        name: str

    @router.get("/items/{id}")
    async def get_item(id: str, db=Depends(get_db)) -> APIResponse[MySchema]:
        item = await crud.get_by_id(db, id)
        return APIResponse.ok(MySchema.model_validate(item))
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class OurBaseModel(BaseModel):
    """Base for all AURA request/response schemas. Enables ORM mode."""
    model_config = {"from_attributes": True}


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope for every API response."""
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None
    errors: list[str] = []

    @classmethod
    def ok(cls, data: Any = None, message: str = "OK") -> "APIResponse":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, errors: list[str] | None = None) -> "APIResponse":
        return cls(success=False, message=message, data=None, errors=errors or [])
