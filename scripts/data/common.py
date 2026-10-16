import logging
import sys

from pymongo import MongoClient

from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_existing_collections(db_to_check):
    collections = db_to_check.list_collection_names()
    if len(collections) != 0:
        confirm_or_abort("Database has existing collections.")


def test_connection(client: MongoClient):
    client.admin.command("ping")
    logger.info("Db pinged successfully.")


def run_initial_safeguards():
    if not settings.DEBUG:
        sys.exit("Aborting, not a debug environment.")

    if "localhost" not in settings.DOCUMENT_DB_CONN:
        sys.exit("Aborting, not localhost.")


def confirm_or_abort(confirm_prompt: str, exit_message="Seed aborted."):
    input_message = confirm_prompt + " Enter y to continue or n to exit. \n"
    continue_response = input(input_message)
    if not continue_response.lower() == "y":
        sys.exit(exit_message)
