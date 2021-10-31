from typing import Any, Optional
from pydantic import BaseModel


class StandardResponse(BaseModel):
    success: bool
    response: Any
    message: Optional[str]
    error_code: Optional[int]
