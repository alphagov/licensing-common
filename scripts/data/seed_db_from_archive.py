import logging
import sys
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, run

from pymongo import MongoClient

from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_connection():
    client.admin.command("ping")


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


def check_existing_collections(db_to_check):
    collections = db_to_check.list_collection_names()
    if len(collections) != 0:
        continue_response = input("Database not empty, continue y/n? \n")
        if continue_response.lower() != "y":
            sys.exit("Seed aborted.")


sys.stdout.reconfigure(line_buffering=True)

if not settings.DEBUG:
    sys.exit("Aborting, not a debug environment.")

if "localhost" not in settings.DOCUMENT_DB_CONN:
    sys.exit("Aborting, not localhost.")

client = MongoClient(settings.DOCUMENT_DB_CONN)

try:
    test_connection()
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
