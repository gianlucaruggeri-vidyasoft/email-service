import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://root:pass@localhost:27017/")

# Inizializziamo il client
client = AsyncIOMotorClient(MONGO_URL)
# Definiamo il database (chiamiamolo 'biblioteca_db')
db = client.biblioteca_db

def get_database():
    return db