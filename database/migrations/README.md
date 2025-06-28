# Watchtower Database Migrations

This directory contains all Alembic (or other schema migration tool) scripts for evolving the Watchtower database schema.

- **Never edit or delete migration files retroactively.**
- Always create a new migration script for each schema change, upgrade, or rollback.
- Ensure every migration is auditable and references the corresponding UpgradeProposal or LineageNode in the main ledger.

## Usage

- Initialize Alembic (if not already done):

      alembic init database/migrations

- Create a new migration:

      alembic revision --autogenerate -m "Short description of change"

- Apply migrations:

      alembic upgrade head

- Rollback to a previous migration:

      alembic downgrade <revision>

## Best Practices

- Always run migrations in a test/dev environment before production.
- Every upgrade, fork, or protocol spinoff should reference its migration revision.
- Document special migration considerations here.

