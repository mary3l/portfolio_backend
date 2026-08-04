"""Request and response models for the contact form."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BudgetRange(StrEnum):
    """Fixed choices so enquiries are comparable and the field cannot be abused
    as another free-text box."""

    UNDER_500 = "under_500"
    FROM_500 = "500_1500"
    FROM_1500 = "1500_5000"
    OVER_5000 = "over_5000"
    UNSURE = "unsure"

    @property
    def label(self) -> str:
        return {
            BudgetRange.UNDER_500: "Under $500",
            BudgetRange.FROM_500: "$500 – $1,500",
            BudgetRange.FROM_1500: "$1,500 – $5,000",
            BudgetRange.OVER_5000: "$5,000+",
            BudgetRange.UNSURE: "Not sure yet",
        }[self]


class ContactRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Annotated[str, Field(min_length=1, max_length=120)]
    email: EmailStr
    problem: Annotated[str, Field(min_length=10, max_length=3000)]
    solution: Annotated[str, Field(min_length=10, max_length=3000)]
    budget: BudgetRange

    # Honeypot: a hidden field real users never see. Bots fill in everything, so
    # anything here means "discard", handled in the route.
    company: Annotated[str, Field(max_length=200)] = ""


class ContactResponse(BaseModel):
    message: str
