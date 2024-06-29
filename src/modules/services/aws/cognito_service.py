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
            username = email
            response = self.client.sign_up(
                ClientId=self.env.app_client_id,
                SecretHash=calculate_secret_hash(
                    self.env.app_client_id, self.env.app_client_secret, username
                ),
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
            print(response)
            return response
        except self.client.exceptions.InvalidPasswordException as e:
            print(e)
            return {"error": str(e).split(': ', 2)[-1], "status_code": 422}
        except self.client.exceptions.UsernameExistsException as e:
            print(e)
            return {"error": str(e).split(': ', 2)[-1], "status_code": 409}
        except Exception as e:
            print(f"Error creating user account: {e}")
            return {"error": str(e), "status_code": 500}
