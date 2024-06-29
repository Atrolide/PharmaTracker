"""AWS Cognito Client class"""

from boto3.session import Session

from src.modules.config.aws_settings import CognitoSettings
from src.modules.utils.aws_helpers import calculate_secret_hash


class CognitoClient:
    """Class for AWS Cognito User Pool client"""

    def __init__(self):
        # Directly initialize with CognitoSettings
        self.env = CognitoSettings()

        # Create a session using the AWS credentials
        self.session = Session(
            aws_access_key_id=self.env.aws_access_key_id,
            aws_secret_access_key=self.env.aws_secret_access_key,
            region_name=self.env.aws_region,
        )
        # Create a client for interacting with AWS Cognito
        self.client = self.session.client("cognito-idp")

    async def create_user_account(self, email: str, password: str):
        """
        Asynchronously creates a new user account in AWS Cognito.
        """
        try:
            response = self.client.sign_up(
                ClientId=self.env.app_client_id,
                SecretHash=calculate_secret_hash(
                    self.env.app_client_id, self.env.app_client_secret, email
                ),
                Username=email,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
            # TODO: Log response success
            return response
        except self.client.exceptions.InvalidPasswordException as e:
            return {"error": str(e).split(": ", 2)[-1], "status_code": 422}
        except self.client.exceptions.UsernameExistsException as e:
            return {"error": str(e).split(": ", 2)[-1], "status_code": 409}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
        # TODO: Log errors

    async def auth_user(self, email: str, password: str):
        """
        Authenticates user credentials
        """
        try:
            response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': calculate_secret_hash(self.env.app_client_id, self.env.app_client_secret, email)
                },
                ClientId=self.env.app_client_id
            )
            return response
        except (self.client.exceptions.NotAuthorizedException, self.client.exceptions.UserNotFoundException):
            # TODO: Log -> {"error": str(e).split(": ", 2)[-1], "status_code": 401}
            return {"error": "Incorrect Username or password!", "status_code": 401}
        except Exception as e:
            print(e)
            return e
