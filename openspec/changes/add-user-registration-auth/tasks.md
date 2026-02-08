# Tasks: Add user model and registration & authorization

## 1. User model and persistence

- [ ] 1.1 Add SQLAlchemy User model (id, email, hashed_password) with unique constraint on email.
- [ ] 1.2 Create Alembic revision for users table and apply upgrade.
- [ ] 1.3 Add Pydantic schemas for user (e.g. UserCreate with email/password, UserResponse without password).

## 2. Security utilities

- [ ] 2.1 Implement password hashing (hash and verify) using pwdlib.
- [ ] 2.2 Implement JWT creation (encode with sub, exp) and validation (decode, verify signature and exp).
- [ ] 2.3 Add FastAPI dependency that extracts Bearer token, validates JWT, and returns current user (or user id).

## 3. Auth API

- [ ] 3.1 Implement POST /register/: accept email and password; hash password; persist user; return appropriate response (e.g. 201 with user id/email); return 4xx if email already exists.
- [ ] 3.2 Implement POST /token/: accept OAuth2 form (username=email, password); validate credentials; return JSON with access_token and token_type "bearer"; return 401 for invalid credentials.
- [ ] 3.3 Mount auth routes and document endpoints in OpenAPI (tags, summary).

## 4. Validation and tests

- [ ] 4.1 Add tests for registration (success, duplicate email).
- [ ] 4.2 Add tests for token endpoint (success, invalid credentials).
- [ ] 4.3 Add tests for protected route access with valid JWT and without/invalid token.
- [ ] 4.4 Run `uv run pytest` and ensure coverage remains acceptable; run `uv run ruff check .` and `uv run ruff format .`.
