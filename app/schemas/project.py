"""Request and response models for the projects resource."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Constraints live on the annotated types so create/update share one definition.
Title = Annotated[str, Field(min_length=1, max_length=200)]
ProjectType = Annotated[str, Field(min_length=1, max_length=80)]
ToolsUsed = Annotated[str, Field(min_length=1, max_length=300)]
LongText = Annotated[str, Field(min_length=1, max_length=5000)]
# Optional: a project with no screenshot yet falls back to a generated tile.
ImageUrl = Annotated[str | None, Field(default=None, max_length=1000)]


class ProjectSchema(BaseModel):
    # Strip whitespace before validating, so "   " fails min_length instead of
    # being stored as a blank field.
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("image_url", check_fields=False)
    @classmethod
    def _validate_image_url(cls, value: str | None) -> str | None:
        """Treat blank as "no image", and reject anything not an http(s) URL.

        The admin form submits "" when the field is left empty; storing that as
        an empty string would make the frontend render a broken image.
        """
        if value is None or not value.strip():
            return None
        url = value.strip()
        if not url.startswith(("https://", "http://")):
            raise ValueError("image_url must start with https:// or http://")
        return url


class ProjectBase(ProjectSchema):
    title: Title
    problem: LongText
    solution: LongText
    contribution: LongText
    type: ProjectType
    tools_used: ToolsUsed
    image_url: ImageUrl = None


class ProjectCreate(ProjectBase):
    """Every field is required when creating a project."""


class ProjectUpdate(ProjectSchema):
    """Partial update — only the fields present in the body are changed."""

    title: Title | None = None
    problem: LongText | None = None
    solution: LongText | None = None
    contribution: LongText | None = None
    type: ProjectType | None = None
    tools_used: ToolsUsed | None = None
    image_url: ImageUrl = None


class ProjectRead(ProjectBase):
    """What the API returns. Documents the shape in OpenAPI and guarantees the
    response never leaks unexpected database columns."""

    id: int
    created_at: datetime | None = None
