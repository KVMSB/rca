import json
import os
import sys
import uuid
from mongoengine import connect
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey

from azure.identity import DefaultAzureCredential

ENDPOINT = os.environ["COSMOS_ENDPOINT"]


DATABASE_NAME = "test"


# Connect to Azure Cosmos DB
def initialize_database():
    """
    Initialize database connection using mongoengine
    """
    connect(
        db=DATABASE_NAME,
        host=ENDPOINT,
    )


initialize_database()
