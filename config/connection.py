from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

client = MongoClient(os.getenv('MONGO_URI').format(os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PASSWORD')), server_api=ServerApi('1'))