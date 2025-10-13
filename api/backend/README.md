# FastAdventure Backend (Azure Functions)

This directory contains a copy of the FastAPI backend logic, adapted for use within Azure Functions. All modules (core, db, models, routers, schemas) are included to resolve import errors when running as an Azure Function.

- All backend code is now available under `api/backend/` for Azure Functions to import.
- Update `api/requirements.txt` to ensure all dependencies are installed in the Azure Functions environment.
- If you update backend logic, re-copy the relevant files here.
