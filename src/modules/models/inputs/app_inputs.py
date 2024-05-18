"""Module for app inputs"""

from pydantic import BaseModel


class LoginInput(BaseModel):
    """Input model for user login"""

    email: str
    password: str


class RegisterInput(LoginInput):
    """Input model for user registration"""

    confirm_password: str
