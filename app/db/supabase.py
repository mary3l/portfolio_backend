"""Supabase client construction and injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from supabase import Client, create_client

from app.core.config import Settings, get_settings


@lru_cache
def _build_client(url: str, key: str) -> Client:
    """One client per (url, key) pair — it is thread-safe and holds a pool."""
    return create_client(url, key)


def get_supabase(settings: Annotated[Settings, Depends(get_settings)]) -> Client:
    return _build_client(settings.supabase_url, settings.supabase_key.get_secret_value())


SupabaseClient = Annotated[Client, Depends(get_supabase)]
"""Inject the shared Supabase client into a route or dependency."""
