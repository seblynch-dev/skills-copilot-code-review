---
applyTo: "src/**/*.py"
---

## Backend Guidelines

- All API endpoints must be defined in the `routers` folder.
- Load example database content from the `database.py` file.
- Log detailed error information on the server, but return appropriate HTTP status codes and user-safe error messages to the frontend (avoid leaking stack traces or internals).
- Ensure all APIs are explained in the documentation.
- Verify changes in the backend are reflected in the frontend (`src/static/**`). If potentially breaking changes are found, mention them to the developer.