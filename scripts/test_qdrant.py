import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient


load_dotenv()






client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)



collections = client.get_collections()


print(
    f"Collections: "
    f"{len(collections.collections)}"
)


for collection in collections.collections:
    print(f" - {collection.name}")