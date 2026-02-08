# Design: User model and registration & authorization

## Context

The order management API must support user identity so that orders can be associated with users and access to order endpoints can be restricted. Project conventions (project.md) specify OAuth2 Password Flow, JWT, pwdlib for password hashing, and existing config for JWT (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES). There are no existing user models or auth routes in the codebase.

## Goals / Non-Goals

- **Goals**: Persist users with hashed passwords; expose registration and login endpoints; issue and validate JWTs for protected routes.
- **Non-Goals**: Refresh tokens, role-based access control (RBAC), password reset, email verification, or social login.

## Decisions

- **User primary key**: Integer (as per project.md). Enables simple foreign key from orders and compact JWTs if we ever put user_id in claims.
- **Password hashing**: Use pwdlib (already in dependencies) with a policy suitable for production (e.g. argon2). Passwords MUST NOT be stored in plain text.
- **Token format**: JWT (HS256), containing sub (user identifier) and exp. Access token only; no refresh token in this change.
- **Protected routes**: Use a FastAPI dependency that extracts and validates the Bearer token and loads the user (or at least user id) for use in route handlers.
- **Registration uniqueness**: Reject registration when email already exists; return a clear 4xx response (e.g. 400 or 409).
- **Alternatives considered**: (1) UUID for user id — project.md specifies integer; (2) bcrypt — project already standardizes on pwdlib; (3) API keys — JWT preferred for OAuth2 and existing project conventions.

## Risks / Trade-offs

- **JWT secret in env**: If JWT_SECRET_KEY is weak or leaked, tokens can be forged. Mitigation: document strong secret in production and use env-only configuration.
- **No refresh token**: Users must re-login after expiry. Acceptable for initial scope; can be added later.

## Migration Plan

- Add Alembic revision creating `users` table (id SERIAL PRIMARY KEY, email VARCHAR UNIQUE NOT NULL, hashed_password VARCHAR NOT NULL).
- No data migration from other systems. Rollback: downgrade revision to drop `users` table (only safe if no orders reference users yet; otherwise add user_id to orders in a later change).

## Open Questions

- None for initial scope.
