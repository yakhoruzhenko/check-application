
from uuid import UUID

from fastapi import Request
from pydantic import AnyHttpUrl
from pydantic_core import Url


def get_response_url(request: Request, id: UUID) -> AnyHttpUrl:
    path = request.app.url_path_for('get_check_text_repr_by_id', id=id)
    return AnyHttpUrl(str(request.base_url.replace(path=str(path))))
