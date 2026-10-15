import logging
import sys
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, run

from pymongo import MongoClient

from config import settings
from scripts.data.common import check_existing_collections, run_initial_safeguards, test_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_mongo_restore():
    try:
        run(
            ["mongorestore", "--version"],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    except FileNotFoundError, CalledProcessError:
        verify_brew_or_exit()
        continue_response = input("Mongorestore not found, install using brew? y/n \n")
        if continue_response.lower() != "y":
            sys.exit("Seed aborted.")
        run(
            ["brew", "install", "mongodb/brew/mongodb-database-tools"],
            check=True,
        )


def verify_brew_or_exit():
    try:
        run(
            ["brew", "--version"],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    except FileNotFoundError, CalledProcessError:
        sys.exit("homebrew not installed, manually install homebrew before trying again")


client = MongoClient(settings.DOCUMENT_DB_CONN)
try:
    run_initial_safeguards()
    test_connection(client)
    check_mongo_restore()
    db = client["licensify"]
    check_existing_collections(db)
    path_to_file = input("What is the path to the data dump file? \n").strip("'\" ")
    file = Path(path_to_file)
    if not file.is_file():
        sys.exit("Seed aborted, that's not a file.")
    uri = settings.DOCUMENT_DB_CONN
    if "?" in uri and "/?" not in uri:
        uri = uri.replace("?", "/?", 1)
    restore_command = [
        "mongorestore",
        f"--uri={uri}/",
        f"--archive={path_to_file}",
        "--nsFrom=licensify-refdata.*",
        "--nsTo=licensify.*",
        "--noIndexRestore",
        "--tlsInsecure",
    ]
    result = run(restore_command, text=True)
    if result.returncode != 0:
        logger.error("Restore failed with exit code %s", result.returncode)
        sys.exit("Seed aborted")
finally:
    client.close()
