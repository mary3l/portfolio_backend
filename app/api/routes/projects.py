"""Projects endpoints. Reads are public; writes require the admin token."""

from typing import Annotated

from fastapi import APIRouter, Path, Response, status

from app.core.security import AdminUser
from app.db.supabase import SupabaseClient
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import projects as service

router = APIRouter(prefix="/projects", tags=["projects"])

ProjectId = Annotated[int, Path(ge=1, description="Project id")]


@router.get("/", response_model=list[ProjectRead], summary="List all projects")
def list_projects(client: SupabaseClient):
    return service.list_projects(client)


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get one project",
    responses={404: {"description": "Project not found"}},
)
def get_project(client: SupabaseClient, project_id: ProjectId):
    return service.get_project(client, project_id)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    responses={
        401: {"description": "Not signed in"},
        403: {"description": "Not an admin"},
    },
)
def create_project(client: SupabaseClient, payload: ProjectCreate, _: AdminUser):
    return service.create_project(client, payload)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update a project",
    responses={404: {"description": "Project not found"}},
)
def update_project(
    client: SupabaseClient,
    project_id: ProjectId,
    payload: ProjectUpdate,
    _: AdminUser,
):
    return service.update_project(client, project_id, payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    responses={404: {"description": "Project not found"}},
)
def delete_project(client: SupabaseClient, project_id: ProjectId, _: AdminUser):
    service.delete_project(client, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
