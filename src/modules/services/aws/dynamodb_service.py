"""AWS Cognito Client class"""

from boto3.session import Session

from src.modules.config.aws_settings import DynamoDBSettings


class DynamoDBClient:
    """Class for AWS DynamoDB client"""

    def __init__(self):
        # Directly initialize with DynamoDBSettings
        self.env = DynamoDBSettings()

        # Create a session using the AWS credentials
        self.session = Session(
            aws_access_key_id=self.env.aws_access_key_id,
            aws_secret_access_key=self.env.aws_secret_access_key,
            region_name=self.env.aws_region,
        )
        # Create a client for interacting with AWS DynamoDB
        self.client = self.session.client("dynamodb")
        self.table_name = self.env.table_name
