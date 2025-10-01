from typing import Literal
from pydantic import (
    BaseModel,
    StrictStr,
    Field,
)


class UserContext(BaseModel):
    germany_region: StrictStr = Field(
        description="The specific region or federal state in Germany where the person currently lives.",
        min_length=1,
    )

    student_or_teacher: Literal["student", "teacher"] | None = Field(
        description="Indicates whether the person is a student or a teacher.",
        default=None,
    )


class Domain(BaseModel):
    name: StrictStr
    description: StrictStr
