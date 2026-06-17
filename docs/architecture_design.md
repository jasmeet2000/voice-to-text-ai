# Architecture Design

Goals
- Clean, testable, production-ready architecture for offline voice-to-text.

Layers (high-level)
- Presentation (Frontend: Gradio, Streamlit) — user interaction and UX.
- FastAPI Layer (API routes, request/response handling) — HTTP surface, validation, auth if needed.
- Service Layer (application logic) — orchestration: file validation, preprocessing, rate-limiting, caching.
- Model Inference Layer (model-loading, batching, device management) — abstracts HF model calls and token/decoding strategies.
- Whisper Model (weights) — the ML model and tokenizer/processor.
- Transcription Response (DTOs) — structured output, timestamps, confidence, segments.

Why each layer exists
- Presentation: Separates UX from backend; without it, UI logic would leak into services.
- FastAPI Layer: Handles HTTP concerns and schema validation; without it, services would need to parse requests and error handling would be inconsistent.
- Service Layer: Keeps business rules out of infrastructure; without it, model code would be tightly coupled to HTTP and hard to test.
- Model Inference Layer: Encapsulates device selection, batching, warm-up; without it, model usage would be duplicated and fragile.
- Whisper Model: Isolated ML artifact allowing swapping or upgrading; without it, migrating models is risky.
- Transcription Response: Ensures stable contracts for consumers (frontend, API clients).

Implementation notes
- Model layer uses a lazy-loading registry to avoid long startup times when no model is needed.
- Blocking audio conversion and file I/O are run in threadpool via `asyncio.to_thread` to keep FastAPI async.
- Uploads are sanitized and constrained to UPLOAD_DIR; transcription APIs accept filenames to avoid arbitrary file access.
- Loguru is configured with application and error sinks; use structured logs for observability.

Testability
- Each layer is small and mockable: unit tests for services, integration tests for API with dependency overrides.

Alternatives used in industry
- Monolith: fewer files but harder to scale/test.
- Microservices: split model-serving into its own service (useful for heavy models/GPU clusters). This project is designed to allow moving to a model-server with minimal changes (registry interface).
- Serverless: for on-demand inference (not applicable for strict offline requirement).

Trade-offs
- Keep orchestration lightweight in-process for local/offline use. For scale, move model-serving to a separate process or container with gRPC/REST and autoscaling.

Common interview talking points
- Explain dependency inversion: services depend on interfaces (model registry) not implementations.
- Explain why heavy work is offloaded to threadpools in an async framework.
- How to migrate model-serving to a dedicated service with little code change (swap registry implementation).
