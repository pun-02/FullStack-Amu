import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# JWT secret key
secret_key = os.getenv("JWT_SECRET_KEY")

if not secret_key:
    raise RuntimeError("JWT_SECRET_KEY is missing from the .env file")

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")

# CyberShield database
db = client.cybershield

# Collections
vulnerabilities = db.vulnerabilities
users = db.users