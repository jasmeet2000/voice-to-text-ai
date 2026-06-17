# AGENTS.md

Purpose: Rules for AI agents and contributors (human and automated)

Architecture rules
- Follow Clean Architecture
- Keep business logic out of API route functions
- Use dependency injection for services

Coding standards
- Python 3.11+, type hints, meaningful names
- Max ~200 LOC per file where practical
- Docstrings for public functions and modules

Naming conventions
- snake_case for functions and files
- CamelCase for classes
- services.* for business logic, models.* for ML code, api.* for HTTP layer

Dependency rules
- Minimize third-party libraries; prefer stdlib + well-known libs
- Pin versions in requirements.txt; use requirements-test.txt for CI/test deps

Testing requirements
- Unit tests for services and models
- Integration tests for API endpoints (pytest + TestClient)
- Mock external I/O (disk, model weights) in unit tests

CI & Pre-commit
- Pre-commit configured with black, isort, ruff; run locally before commits
- CI runs linting, pre-commit, and pytest with coverage

Documentation
- Update docs/memory.md and docs/context.md after significant changes
- Add README sections for new features and architecture updates

Agent usage
- Agents may modify only files listed in a requested change
- Agents must not commit secrets or environment-specific data
- Agents should not push changes directly to main without review

Security
- Do not add model weights or secrets to the repo
- Use .env for local config and never commit .env to version control
