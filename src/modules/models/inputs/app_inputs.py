"""Module for app inputs"""

import re
from pydantic import BaseModel, model_validator


class LoginInput(BaseModel):
    """Input model for user login"""

    email: str
    password: str

    @model_validator(mode="after")
    def check_email_regex(self) -> "LoginInput":
        """Model validator for if email matches the regex"""
        if not re.match(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email
        ):
            raise ValueError("Email does not match the required format.")
        return self


class RegisterInput(LoginInput):
    """Input model for user registration"""

    confirm_password: str

    @model_validator(mode="after")
    def check_pass_match(self) -> "RegisterInput":
        """Model validator for if passwords match"""
        confirm_password = self.confirm_password
        password = self.password
        if confirm_password != password:
            raise ValueError("Passwords do not match!")
        if len(password) <= 1:
            raise ValueError("Password not long enough")
        return self


class MedicineInput(BaseModel):
    """Input model for medicine records"""

    user_sub: str
    medicine_name: str
    medicine_type: str
    quantity: int
    expiration_date: str

    @model_validator(mode="after")
    def check_exp_date_regex(self) -> "MedicineInput":
        """Model validator for expiration date format"""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.expiration_date):
            raise ValueError("Expiration date must be in 'YYYY-MM-DD' format.")
        return self
