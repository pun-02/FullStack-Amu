
import os
from decimal import Decimal
from pathlib import Path

import ijson
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

# Find the project folder and load environment settings
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://127.0.0.1:27017/"
)
DATA_FILE = PROJECT_ROOT / "data" / "nvdcve-2.0-2025.json"

BATCH_SIZE = 500

def convert_decimals(value):
    """Convert Decimal values into MongoDB-compatible numbers."""
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {
            key: convert_decimals(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [convert_decimals(item) for item in value]

    return value


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        collection = client["cybershield"]["vulnerabilities"]

        # A CVE ID must be unique
        collection.create_index("cve.id", unique=True)

        batch = []
        processed = 0

        with DATA_FILE.open("rb") as file:
            for record in ijson.items(file, "vulnerabilities.item"):
                record = convert_decimals(record)
                cve_id = record.get("cve", {}).get("id")

                if not cve_id:
                    continue

                batch.append(
                    UpdateOne(
                        {"cve.id": cve_id},
                        {"$set": record},
                        upsert=True
                    )
                )

                if len(batch) >= BATCH_SIZE:
                    collection.bulk_write(batch, ordered=False)
                    processed += len(batch)
                    print(f"Processed {processed:,} records")
                    batch.clear()

        if batch:
            collection.bulk_write(batch, ordered=False)
            processed += len(batch)

        print(f"Import finished. Processed: {processed:,}")
        print(f"Documents in database: {collection.count_documents({}):,}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
