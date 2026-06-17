# Repository Structure

Top-level layout (actual)

voice-to-text-app/
├── api/                  # FastAPI routes, schemas, dependencies
├── services/             # Business logic: validation, audio, transcription orchestration
├── models/               # Model wrappers and registry (HF integrations)
├── core/                 # Config, logging, exceptions, constants
├── frontend/             # Gradio and Streamlit demos
├── tests/                # Unit and integration tests
├── uploads/              # Uploaded audio and temporary artifacts
├── logs/                 # Application and error logs
├── docs/                 # Design docs and cheat-sheets
├── .github/              # CI workflows
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-test.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

Key files and responsibilities
- api/routes.py: HTTP endpoints. Calls services via dependency-injection. Unit-testable via dependency overrides.
- api/schemas.py: Pydantic DTOs for requests/responses (kept minimal and stable).
- services/*.py: Core business logic that orchestrates validation, conversion, inference, and formatting.
- models/whisper_model.py: HF pipeline wrapper (lazy-loading, device selection).
- models/model_registry.py: Registry for available models; supports lazy instantiation.
- core/config.py: Environment-driven settings loader (python-dotenv) and ensures directories exist.
- core/logger.py: Loguru configuration for application and error logs.
- frontend/*: Local demos for manual QA and recruiter demos.
- tests/*: Unit tests for validation, API, and model stubs.

Developer notes
- Use dependency injection to stub or mock heavy components in tests.
- Keep files small and focused for easier review and token efficiency.
- Move heavy model serving to a separate process or container when scaling.
