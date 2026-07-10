# Apply for a licence

Apply for a licence allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Apply for a licence exists for authorities which can't or don't want to offer their own licensing application.

# Setup

This project uses UV to manage packages and dependencies. 

To install UV if not already present, run the following command:

### MacOS

```
brew install uv
```

Use ```uv sync``` to create a virtual environment with all necessary dependencies and packages already resolved.

Activate the virtual environment by running ```source .venv/bin/activate``` from the root of the project.


# Testing

Ensure local database instance is running with port 27017 exposed.

With an activated virtual environment run ```make test``` to run pytest test suite. 

# Licence

[MIT License](./LICENSE)
