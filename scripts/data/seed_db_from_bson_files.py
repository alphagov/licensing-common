import logging
import sys
from pathlib import Path

import bson
from pymongo import MongoClient
from pymongo.database import Database

from config import settings
from scripts.data.common import check_existing_collections, run_initial_safeguards, test_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_collection(db_to_seed: Database, data_file: Path):
    if data_file.stem in db_to_seed.list_collection_names():
        logger.info("Existing collection found for %s, skipping...", data_file.stem)
        return
    with data_file.open("rb") as bson_file:
        # inefficient use of memory but assuming the data is no more than
        # a couple of hundred mb at worst, and it's a one time thing
        documents = list(bson.decode_file_iter(bson_file))

    if len(documents) > 0:
        db_to_seed[data_file.stem].insert_many(documents)
        logger.info("Seeded %s documents into %s ...", len(documents), data_file.stem)


run_initial_safeguards()
client = MongoClient(settings.DOCUMENT_DB_CONN)

try:
    test_connection(client)
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
