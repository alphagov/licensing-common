# Licensing Common

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

Licensing Common holds models, and logic shared across different components of the Licensing applications.

# Setup

This project uses UV to manage packages and dependencies. 

To install UV if not already present, run the following command:

### MacOS

```
brew install uv
```

Use `uv sync` to create a virtual environment with all necessary dependencies and packages already resolved.

Activate the virtual environment by running `source .venv/bin/activate` from the root of the project if `uv` hasn't already done this for you

This project also uses `pre-commit` run `pre-commit install` to create the correct pre-commit git hooks.


# Testing

Ensure local database instance is running with port 27017 exposed.

With an activated virtual environment run ```make test``` to run pytest test suite. 

# Licence

[MIT License](./LICENSE)
