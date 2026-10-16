import logging
import sys
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, run

from pymongo import MongoClient

from config import settings
from scripts.data.common import check_existing_collections, confirm_or_abort, run_initial_safeguards, test_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def verify_or_install_mongorestore():
    try:
        run(
            ["mongorestore", "--version"],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    except FileNotFoundError, CalledProcessError:
        verify_brew_or_exit()
        confirm_or_abort("Mongorestore not found, this will be installed by homebrew")
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


def restore_data(file_path: Path):
    uri = settings.DOCUMENT_DB_CONN
    if "?" in uri and "/?" not in uri:
        uri = uri.replace("?", "/?", 1)
    restore_command = [
        "mongorestore",
        f"--uri={uri}/",
        f"--archive={file_path}",
        "--nsFrom=licensify-refdata.*",
        "--nsTo=licensify.*",
        "--noIndexRestore",
        "--tlsInsecure",
    ]
    result = run(restore_command, text=True)
    if result.returncode != 0:
        logger.error("Restore failed with exit code %s", result.returncode)
        sys.exit("Seed aborted")


def get_file_path() -> Path:
    path_input = input("What is the path to the data dump file? \n").strip("'\" ")
    file_path = Path(path_input)
    if not file_path.is_file():
        sys.exit("Seed aborted, that's not a file.")
    return file_path


client = MongoClient(settings.DOCUMENT_DB_CONN)
try:
    run_initial_safeguards()
    test_connection(client)
    db = client["licensify"]
    check_existing_collections(db)
    verify_or_install_mongorestore()

    path_to_file = get_file_path()
    restore_data(path_to_file)
finally:
    client.close()
