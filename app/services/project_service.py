from app.database import supabase
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_projects():
    response = (
        supabase
        .table("projects")
        .select("*")
        .order("id")
        .execute()
    )
    return response.data


def get_project(project_id: int):
    response = (
        supabase
        .table("projects")
        .select("*")
        .eq("id", project_id)
        .execute()
    )
    return response.data[0] if response.data else None


def create_project(project: ProjectCreate):
    response = (
        supabase
        .table("projects")
        .insert(project.model_dump())
        .execute()
    )
    return response.data[0]


def update_project(project_id: int, project: ProjectUpdate):
    changes = project.model_dump(exclude_unset=True)
    if not changes:
        return get_project(project_id)

    response = (
        supabase
        .table("projects")
        .update(changes)
        .eq("id", project_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_project(project_id: int):
    response = (
        supabase
        .table("projects")
        .delete()
        .eq("id", project_id)
        .execute()
    )
    return bool(response.data)
