"""AWS Cognito Client class"""

import uuid
from typing import List

from boto3.session import Session

from src.modules.config.aws_settings import DynamoDBSettings
from src.modules.models.inputs.app_inputs import MedicineInput, UpdateMedicineInput


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

    async def insert_medicine(self, medicine_input: MedicineInput):
        """Insert a new medicine record into the DynamoDB table"""
        # Generate a random UUID for medicine_id
        medicine_id = str(uuid.uuid4())
        try:
            # Prepare the item for insertion
            item = {
                "user_sub": {"S": medicine_input.user_sub},
                "medicine_id": {"S": medicine_id},
                "medicine_name": {"S": medicine_input.medicine_name},
                "medicine_type": {"S": medicine_input.medicine_type},
                "quantity": {"N": str(medicine_input.quantity)},
                "expiration_date": {"S": medicine_input.expiration_date},
            }

            # Insert the item into the DynamoDB table
            response = self.client.put_item(TableName=self.table_name, Item=item)

            return response
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    async def get_medicines_by_user_sub(self, user_sub: str):
        """Query all medicine records for a given user_sub"""
        try:
            # Query the DynamoDB table for items with the specified user_sub
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="user_sub = :user_sub",
                ExpressionAttributeValues={":user_sub": {"S": user_sub}},
            )
            items = response.get("Items", [])
            return items
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    async def delete_medicine(self, user_sub: str, medicine_id: str):
        """Delete a medicine record from the DynamoDB table"""
        try:
            key = {"user_sub": {"S": user_sub}, "medicine_id": {"S": medicine_id}}
            # Delete the item from the DynamoDB table
            response = self.client.delete_item(TableName=self.table_name, Key=key)
            return response
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    async def edit_medicine(
    self,
    update_medicine_input: UpdateMedicineInput,
    ):
        """Edit a medicine record in the DynamoDB table"""
        try:
            # Initialize update expression components
            update_expression_parts: List[str] = []
            expression_attribute_values = {}

            # Directly map fields to the update expression
            field_map = {
                "medicine_name": "S",
                "medicine_type": "S",
                "quantity": "N",
                "expiration_date": "S",
            }

            for field, dynamo_type in field_map.items():
                value = getattr(update_medicine_input, field)
                update_expression_parts.append(f"{field} = :{field}")
                expression_attribute_values[f":{field}"] = {dynamo_type: str(value)}

            # Join the update expression parts into a single string
            update_expression = "SET " + ", ".join(update_expression_parts)

            # Perform the update operation using DynamoDB API
            response = self.client.update_item(
                TableName=self.table_name,
                Key={
                    "user_sub": {"S": update_medicine_input.user_sub},
                    "medicine_id": {"S": update_medicine_input.medicine_id}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )

            return response

        except Exception as e:
            return {"error": str(e), "status_code": 500}
