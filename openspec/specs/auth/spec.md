# auth Specification

## Purpose
TBD - created by archiving change add-user-registration-auth. Update Purpose after archive.
## Requirements
### Requirement: User registration endpoint

The system SHALL expose a POST registration endpoint that accepts email and password, creates a user with a hashed password, and returns a success response. The endpoint SHALL NOT require authentication.

#### Scenario: Registration success

- **WHEN** a client sends POST with a valid email and password that do not already exist
- **THEN** the system SHALL create a user with that email and a hashed password
- **AND** SHALL respond with a success status (e.g. 201) and representation of the created user (e.g. id and email, no password)

#### Scenario: Registration rejected for duplicate email

- **WHEN** a client sends POST with an email that is already registered
- **THEN** the system SHALL NOT create a new user
- **AND** SHALL respond with an error status (e.g. 400 or 409) indicating the email is already in use

### Requirement: Login and access token

The system SHALL expose a POST token endpoint (OAuth2 Password Flow) that accepts credentials and returns a JWT access token. The token SHALL be usable as a Bearer token for authorized requests.

#### Scenario: Token issued for valid credentials

- **WHEN** a client sends POST with valid email (as username) and password
- **THEN** the system SHALL validate the credentials (email lookup and password verify)
- **AND** SHALL respond with a JSON body containing access_token (JWT) and token_type "bearer"

#### Scenario: Token rejected for invalid credentials

- **WHEN** a client sends POST with invalid email or wrong password
- **THEN** the system SHALL NOT issue a token
- **AND** SHALL respond with 401 Unauthorized

#### Scenario: JWT contains required claims

- **WHEN** a token is issued
- **THEN** the JWT SHALL include a subject (sub) identifying the user and an expiration (exp)
- **AND** SHALL be signed with the configured secret and algorithm (e.g. HS256)

### Requirement: Authorization for protected routes

The system SHALL require a valid JWT for protected endpoints. Requests without a valid Bearer token SHALL be rejected with 401.

#### Scenario: Protected route accepts valid token

- **WHEN** a client sends a request to a protected endpoint with a valid Bearer JWT
- **THEN** the system SHALL accept the request and SHALL associate the request with the user identified by the token

#### Scenario: Protected route rejects missing or invalid token

- **WHEN** a client sends a request to a protected endpoint without a token or with an invalid/expired JWT
- **THEN** the system SHALL respond with 401 Unauthorized
- **AND** SHALL NOT perform the protected operation

