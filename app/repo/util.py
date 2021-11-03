from typing import Tuple
from app.schemas.pagination import QueryPagination, ResponsePagination
from app.config.app_config import conf


def translate_query_pagination(
    query_pagination: QueryPagination, total: int
) -> Tuple[int, int, ResponsePagination]:
    """
    returns limit: int and offset: int and paging: ResponsePagination
    with pagesize undesided
    """
    limit: int
    offset: int
    if query_pagination.size == -1:
        # this means to to get all
        # the repo layer must ask DB again and again
        # instead of ask for a big chunk in one shot
        # repo layer has not implemented this yet
        limit = total
        offset = 0
        current_page = 1
        total_pages = 1
    else:
        limit = query_pagination.size or conf.DEFAULT_PAGE_SIZE
        offset = (query_pagination.page - 1) * limit if query_pagination.page else 0
        current_page = query_pagination.page or 1
        total_pages = (
            -(-total // query_pagination.size)
            if query_pagination.size
            else -(-total // conf.DEFAULT_PAGE_SIZE)
        )
    paging = ResponsePagination(
        total=total,
        total_pages=total_pages,
        current_page=current_page,
        page_size=0,
    )
    return limit, offset, paging
