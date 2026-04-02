from uuid import UUID
import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    cpf: str = Field(min_length=11, max_length=14)
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        # Remove non-digits
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        # Check if all digits are the same
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")

        # Validate first digit
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValueError("CPF inválido")

        return cpf


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    cpf: str
    full_name: str
    is_active: bool
    is_verified: bool
    tenant_id: UUID
    has_completed_onboarding: bool = False

    model_config = {"from_attributes": True}
