import enum
from pydantic import BaseModel, Field
from pydantic.types import datetime, date
from typing import Optional
from pydantic.types import Json


class StudentGender(enum.Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    def __str__(self) -> str:
        return self.value

class StudentBase(BaseModel):
    student_full_name: str = Field(min_length=5, max_length=30)
    student_dob: date
    student_gender: StudentGender
    student_mother_name: str =  Field(min_length=5, max_length=30)
    student_father_name: str =  Field(min_length=5, max_length=30)
    student_phone: str = Field(max_length=10)
    student_aadhar: str = Field(min_length=12, max_length=12)
    student_center_id: int
    student_image: str
    student_last_attendance: Optional[date] = Field(default=None)

class StudentPublic(StudentBase):
    student_id: int
    student_face_id: object
    student_center_id: int
    student_created_date: datetime

class StudentsPublic(BaseModel):
    data: list[StudentPublic]

class Student(StudentBase):
    student_face_id: Json

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    student_full_name: str = Field(min_length=5, max_length=30)
    student_dob: date
    student_gender: StudentGender
    student_mother_name: str =  Field(min_length=5, max_length=30)
    student_father_name: str =  Field(min_length=5, max_length=30)
    student_phone: str = Field(max_length=10)
    student_aadhar: str = Field(min_length=12, max_length=12)