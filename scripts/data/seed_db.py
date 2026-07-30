import sys
from pathlib import Path

import bson
from pymongo import MongoClient
from pymongo.database import Database

from config import settings

if not settings.DEBUG:
    sys.exit("Aborting, not a debug environment.")

if "localhost" not in settings.DOCUMENT_DB_CONN:
    sys.exit("Aborting, not localhost.")

client = MongoClient(settings.DOCUMENT_DB_CONN)


def test_connection():
    client.admin.command("ping")
    print("Database pinged successfully.")


def seed_collection(db_to_seed: Database, data_file: Path):
    if data_file.stem in db_to_seed.list_collection_names():
        print(f"Existing collection found for {data_file.stem}, skipping...")
        return
    with data_file.open("rb") as bson_file:
        # inefficient use of memory but assuming the data is no more than
        # a couple of hundred mb at worst, and it's a one time thing
        documents = list(bson.decode_file_iter(bson_file))

    if len(documents) > 0:
        db_to_seed[data_file.stem].insert_many(documents)
        print(f"Seeded {len(documents)} documents into '{data_file.stem}'...")


def check_existing_collections(db_to_check):
    collections = db_to_check.list_collection_names()
    if len(collections) != 0:
        continue_response = input("Database not empty, continue y/n? \n")
        if continue_response.lower() != "y":
            sys.exit("Seed aborted.")


try:
    test_connection()
    db = client["licensify"]
    check_existing_collections(db)
    path_to_files = input("What is the path to the data dump folder? \n").strip("'\" ")
    folder = Path(path_to_files)
    if not folder.is_dir():
        sys.exit("Seed aborted, that's not a folder.")
    files = list(folder.glob("*.bson"))
    if len(files) == 0:
        sys.exit("Seed aborted, no bson files found.")
    for file in files:
        seed_collection(db, file)

finally:
    client.close()
