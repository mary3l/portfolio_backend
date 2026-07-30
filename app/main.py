"""Application entrypoint. Run with: uvicorn app.main:app --reload"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """Build the app. A factory keeps construction testable — a test can build a
    fresh instance with overridden dependencies instead of importing a global."""
    settings = get_settings()

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    # A read-only key still serves the public site, so this is a warning rather
    # than a startup failure — but every write would fail with a row-level
    # security error, which is confusing to diagnose from the frontend.
    if not settings.can_write_to_supabase:
        logging.getLogger(__name__).warning(
            "SUPABASE_KEY looks like a %r key, which cannot write past row level "
            "security. Creating or editing projects will fail. Use the "
            "service_role (or sb_secret_) key from Supabase -> Settings -> API.",
            settings.supabase_key_role,
        )

    app = FastAPI(
        title=settings.project_name,
        version="1.0.0",
        summary="Projects powering the Mabano portfolio site.",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        # Only what the frontend actually uses, instead of a blanket "*".
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
