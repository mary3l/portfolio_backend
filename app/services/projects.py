"""Project persistence. Talks to Supabase and raises domain errors."""

from typing import Any

import httpx
from postgrest.exceptions import APIError
from supabase import Client

from app.core.exceptions import DataAccessError, ProjectNotFoundError
from app.schemas.project import ProjectCreate, ProjectUpdate

TABLE = "projects"

Row = dict[str, Any]

# APIError covers rejections from Supabase; httpx.HTTPError covers never getting
# there at all (DNS, timeout, TLS). Both mean "the database is unavailable".
DB_ERRORS = (APIError, httpx.HTTPError)


def _reason(err: Exception) -> str:
    return getattr(err, "message", None) or str(err) or type(err).__name__


def _table(client: Client):
    return client.table(TABLE)


def list_projects(client: Client) -> list[Row]:
    try:
        response = _table(client).select("*").order("id").execute()
    except DB_ERRORS as err:
        raise DataAccessError(f"Could not load projects: {_reason(err)}") from err
    return response.data or []


def get_project(client: Client, project_id: int) -> Row:
    """Fetch one project, or raise `ProjectNotFoundError`."""
    try:
        response = _table(client).select("*").eq("id", project_id).limit(1).execute()
    except DB_ERRORS as err:
        raise DataAccessError(f"Could not load project: {_reason(err)}") from err

    if not response.data:
        raise ProjectNotFoundError(project_id)
    return response.data[0]


def create_project(client: Client, payload: ProjectCreate) -> Row:
    try:
        response = _table(client).insert(payload.model_dump()).execute()
    except DB_ERRORS as err:
        raise DataAccessError(f"Could not create project: {_reason(err)}") from err

    if not response.data:
        # A write that reports success but returns nothing usually means the
        # service_role key is missing and RLS silently filtered the result.
        raise DataAccessError(
            "The project was not created. Check that SUPABASE_KEY is the "
            "service_role key."
        )
    return response.data[0]


def update_project(client: Client, project_id: int, payload: ProjectUpdate) -> Row:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        # Nothing to write; confirm the project exists and echo it back.
        return get_project(client, project_id)

    try:
        response = _table(client).update(changes).eq("id", project_id).execute()
    except DB_ERRORS as err:
        raise DataAccessError(f"Could not update project: {_reason(err)}") from err

    if not response.data:
        raise ProjectNotFoundError(project_id)
    return response.data[0]


def delete_project(client: Client, project_id: int) -> None:
    try:
        response = _table(client).delete().eq("id", project_id).execute()
    except DB_ERRORS as err:
        raise DataAccessError(f"Could not delete project: {_reason(err)}") from err

    if not response.data:
        raise ProjectNotFoundError(project_id)
