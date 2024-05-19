"""Module for app inputs"""

from pydantic import BaseModel, model_validator

#TODO: #3 Add validators for each class
class LoginInput(BaseModel):
    """Input model for user login"""

    email: str
    password: str


class RegisterInput(LoginInput):
    """Input model for user registration"""

    confirm_password: str

    @model_validator(mode="after")
    def check_pass_match(self) -> 'RegisterInput':
        """Model validator for if passwords match"""
        confirm_password = self.confirm_password
        password = self.password
        if confirm_password != password:
            raise ValueError("Passwords do not match!")
        return self
