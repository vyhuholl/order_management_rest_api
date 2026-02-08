# users Specification

## Purpose
TBD - created by archiving change add-user-registration-auth. Update Purpose after archive.
## Requirements
### Requirement: User persistence model

The system SHALL persist users in a relational store with a stable primary key, a unique email, and a stored password hash. The model SHALL support lookup by id and by email.

#### Scenario: User record has required fields

- **GIVEN** a user has been created with email and password
- **THEN** the stored record SHALL have an integer id, a unique email, and a hashed_password field
- **AND** the plain-text password SHALL NOT be stored

#### Scenario: Email uniqueness enforced

- **WHEN** a second user is created with an email that already exists
- **THEN** the system SHALL reject the creation (e.g. unique constraint or application-level check)
- **AND** the existing user record SHALL remain unchanged

### Requirement: Password hashing

The system SHALL hash user passwords before persisting them and SHALL use pwdlib for hashing and verification.

#### Scenario: Password hashed on storage

- **WHEN** a user is registered with a plain-text password
- **THEN** only a hash produced by pwdlib SHALL be stored
- **AND** the hash SHALL be verifiable via pwdlib against the original password

#### Scenario: Verification rejects wrong password

- **WHEN** a stored hash is verified against a different plain-text password
- **THEN** verification SHALL fail

