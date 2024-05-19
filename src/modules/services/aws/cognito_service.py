"""AWS Cognito Client class"""

from boto3.session import Session

from src.modules.config.aws_settings import CognitoSettings


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
            await self.client.admin_create_user(
                UserPoolId=self.env.user_pool_id,
                Username=username,
                TemporaryPassword=password,
                MessageAction="SUPPRESS",  # Suppresses the default welcome message
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"},
                ],
            )
            return True
        except Exception as e:
            print(f"Error creating user account: {e}")
            return False
