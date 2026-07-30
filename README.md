# Licensing Common

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

Licensing Common holds models, and logic shared across different components of the Licensing applications.

# Setup

## Mise

This project uses [mise-en-place](https://mise.jdx.dev/) to provide specific versions of tools, listed in .tool-versions. You should set up mise to [activate automatically](https://mise.jdx.dev/getting-started.html#activate-mise)

## UV

This project uses UV to manage packages and dependencies. 

To install UV if not already present, run the following command:

### MacOS

```
brew install uv
```

Use `uv sync` to create a virtual environment with all necessary dependencies and packages already resolved.

Activate the virtual environment by running `source .venv/bin/activate` from the root of the project if `uv` hasn't already done this for you

## Direnv

Get direnv to load required environment variables automatically by setting up the [direnv hook](https://direnv.net/docs/hook.html) to run when your shell starts up.

You will also need to allow direnv to load environment variables from this directory with `direnv allow .`

## Pre-commit

This project also uses `pre-commit` run `pre-commit install` to create the correct pre-commit git hooks.

# Testing

Ensure local database instance is running with port 27017 exposed.

With an activated virtual environment run `make test` to run pytest test suite. This will create a local instance of DocumentDB, run the tests, and tear down the instance of DocumentDB

# Data Seeding
>  **Note:** This command requires local BSON files and is restricted to local development environments.

The `make seed-db` command will attempt to seed data within the local DocumentDB instance. It will connect using the `DOCUMENT_DB_CONN` within the main Django `settings.py` file. During the process it will check for existing collections and will ask you to specify the folder containing the BSON. It will convert all BSON files to collections where the collection does not already exist.

# Troubleshooting
## Authentication Error when Connecting to New Local DocumentDB Instance
If this is the first time you are connecting to the database, the most likely cause of authentication errors is the Docker DocumentDB image not having correct credentials created. If you have previously been able to connect this is unlikely the case.

1. Make sure your terminal is in the project root and the virtual environment is active with `source .venv/bin/activate` .
2. Check status with `direnv status`. If you see `No .envrc or .env loaded` then your direnv isn't working correctly. 
   - Ensure all the steps in the Direnv section of the readme have been followed. 
   - Ensure you are using a terminal that has a hook setup. Default IDE terminals may not be the terminal you expect. For example, it may open a Zsh terminal whereas your hook was on the bash terminal.

3. Once direnv is working correctly, `direnv status` should log that a .envrc is being loaded via the terminal messages.

4. Remove the existing DocumentDB image using docker desktop or a compose down command.

5. Create a new one instance using 'make prepare-tests'. This should create a new DocumentDB with the expected credentials from .envrc.

# Licence

[MIT License](./LICENSE)
