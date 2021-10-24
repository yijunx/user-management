from typing import Dict, List
from app.schemas.response import StandardResponse
from pydantic import BaseModel
from flask import make_response, jsonify


def create_response(
    response: BaseModel = None,
    success: bool = True,
    message: str = None,
    status_code: int = 200,
    headers: Dict = None,
    cookies: Dict = None,
    cookies_to_delete: List[str] = None,
):
    resp = make_response(
        jsonify(
            StandardResponse(success=success, response=response, message=message).dict()
        ),
        status_code,
    )
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    if cookies:
        for k, v in cookies.items():
            resp.set_cookie(key=k, value=v, httponly=True, secure=True)
    if cookies_to_delete:
        for key in cookies_to_delete:
            resp.delete_cookie(key=key)
    return resp
