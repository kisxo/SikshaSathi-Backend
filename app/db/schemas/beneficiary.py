from pydantic import BaseModel, Field


class BeneficiaryCreate(BaseModel):
    beneficiary_full_name: str
    beneficiary_address: str
    beneficiary_husband_name: str
    beneficiary_phone: str = Field(min_length=10, max_length=10)