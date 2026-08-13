# Licensing Common

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

Licensing Common holds models, and logic shared across different components of the Licensing applications.

# Setup

## Mise

This project uses [mise-en-place](https://mise.jdx.dev/) to provide specific versions of tools, listed in .tool-versions. You should set up mise to [activate automatically](https://mise.jdx.dev/getting-started.html#activate-mise) with your shell, then run `mise install` and `mise trust`.

## UV

This project uses UV to manage packages and dependencies. 

To install UV if not already present, run the following command:

### MacOS

Use `make sync` to create a virtual environment with all necessary dependencies and packages already resolved. This will also happen automatically when running other make commands.

Activate the virtual environment by running `source .venv/bin/activate` from the root of the project if `mise` hasn't already done this for you.

## Pre-commit

This project also uses `pre-commit` run `pre-commit install` to create the correct pre-commit git hooks.

# Testing

Ensure local database instance is running with port 27017 exposed.

With an activated virtual environment run `make test` to run pytest test suite. This will create a local instance of DocumentDB, run the tests, and tear down the instance of DocumentDB

## Testing Django Models Against Existing Data

A test utility called `verify_model_against_collection` is available for comparing "raw" documents from the database against hydrated Django models to ensure model mappings match reality. The models are tested as part of a parameterised test in `test_model_hydration_and_data_integrity.py`.

To run the tests remove the skip fixture and use the following command:
```
pytest common/tests/hydration/test_model_hydration_and_data_integrity.py --log-cli-level=INFO
```
### Options & Security Flags
* Add `--show-diffs` to log detailed diff output in the terminal for troubleshooting data mismatches. Diff output logging is intentionally gated behind `--show-diffs` so that sensitive data (PII) is never accidentally logged during automated CI/CD runs.
* Add `-vv` to disable Pytest output truncation and view full mismatch lists or deep tracebacks.

# Data Seeding
>  **Note:** This command requires local BSON files and is restricted to local development environments.

The `make seed-db` command will attempt to seed data within the local DocumentDB instance. It will connect using the `DOCUMENT_DB_CONN` within the main Django `settings.py` file. During the process it will check for existing collections and will ask you to specify the folder containing the BSON. It will convert all BSON files to collections where the collection does not already exist.

# Troubleshooting
## Authentication Error when Connecting to New Local DocumentDB Instance
If this is the first time you are connecting to the database, the most likely cause of authentication errors is the Docker DocumentDB image not having correct credentials created. If you have previously been able to connect this is unlikely the case.

1. Make sure your terminal is in the project root and the virtual environment is active with `source .venv/bin/activate`.

2. Ensure all the steps under mise setup have been followed and the hook is setup in your shell startup file (e.g. `.zshrc`).

3. Remove the existing DocumentDB image using docker desktop or a compose down command.

4. Create a new one instance using 'make prepare-tests'. This should create a new DocumentDB with the expected credentials from .envrc.

# Licence

[MIT License](./LICENSE)
