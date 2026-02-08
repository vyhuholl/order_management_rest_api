# Change: Add user model and registration & authorization system

## Why

The API currently has no user identity or access control. Order management requires associating orders with users and protecting endpoints. Adding a user model with registration and JWT-based authorization enables authenticated order creation and user-scoped order retrieval as described in project conventions.

## What Changes

- Introduce a **User** persistence model (id, email, hashed_password) with unique email constraint.
- Add **registration**: `POST /register/` to create a user (email and password); passwords SHALL be hashed with pwdlib before storage.
- Add **login**: `POST /token/` (OAuth2 Password Flow) returning a JWT access token for valid credentials.
- Add **authorization**: JWT validation dependency for protected routes (e.g. order creation and retrieval); reject requests without a valid token.
- Add Alembic migration for the users table.
- Wire registration and token routes into the FastAPI app and document in OpenAPI.

## Impact

- **Affected specs**: New capabilities `users`, `auth` (no existing specs).
- **Affected code**: New `app/models/user.py`, `app/schemas/user.py` and auth schemas, `app/routes/auth.py` (or equivalent), `app/core/security.py` (or similar) for JWT and password hashing, `app/main.py` (router inclusion, dependencies), new Alembic revision, `app/core/config.py` (already has JWT settings).
