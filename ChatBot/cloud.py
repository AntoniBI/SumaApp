from qdrant_client import QdrantClient
from loading import load_dotenv
import os

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("endpoint"),
    api_key=os.getenv("apikey"),
)

print(qdrant_client.get_collections())