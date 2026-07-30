"""Domain errors and the HTTP responses they map to.

Services raise these instead of `HTTPException` so they stay independent of the
web layer; `register_exception_handlers` turns them into responses.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for errors this application raises deliberately."""

    detail = "Unexpected error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ProjectNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, project_id: int) -> None:
        self.detail = f"Project {project_id} not found"
        super().__init__(self.detail)


class DataAccessError(AppError):
    """Supabase rejected or could not serve the request."""

    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "The database is unavailable. Please try again."

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail
        super().__init__(self.detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        # 5xx means we broke, not the caller — log it with the traceback.
        if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.exception("%s: %s", type(exc).__name__, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
