from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_api_key
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
def get_all_projects():
    return project_service.get_projects()


@router.get("/{project_id}")
def get_project(project_id: int):
    project = project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", status_code=201, dependencies=[Depends(require_api_key)])
def create_project(project: ProjectCreate):
    return project_service.create_project(project)


@router.patch("/{project_id}", dependencies=[Depends(require_api_key)])
def update_project(project_id: int, project: ProjectUpdate):
    updated = project_service.update_project(project_id, project)
    if updated is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", dependencies=[Depends(require_api_key)])
def delete_project(project_id: int):
    deleted = project_service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
