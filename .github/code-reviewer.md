# BE Daily Code Review Instructions

## Review Behavior

Review in a direct, evidence-based style. Start with a short summary, then list
findings ordered by severity. Focus on bugs, security issues, regressions,
data-integrity risks, deployment risks, and missing tests.

Only report an issue when it is supported by the changed lines and available
context. Do not invent missing context, enforce broad refactors, or comment on
formatting and missing docstrings unless they affect correctness. Respect the
repository's existing route, service, repository, and model boundaries.

For every finding:

- State the concrete failure mode and affected behavior.
- Reference the smallest relevant file and line range.
- Explain why existing validation or error handling does not prevent it.
- Suggest a focused fix that fits the current architecture.
- Do not expose credentials, tokens, personal data, or production values.

## Paths to Skip

Do not review generated or local-only artifacts:

- `**/.venv/**`
- `**/venv/**`
- `**/__pycache__/**`
- `**/*.pyc`
- `**/.mypy_cache/**`
- `**/.pytest_cache/**`
- `**/build/**`
- `**/dist/**`
- `**/.DS_Store`

Do not skip database migrations, deployment files, Docker files, Nginx files,
or GitHub Actions workflows. Those files are production-critical.

## 1. Python and Architecture

Applies to: `src/**/*.py`

This is a Python 3.11 FastAPI backend using Pydantic v2, Beanie, MongoDB,
httpx, Redis, and ARQ.

Focus on:

- Incorrect or missing type handling that can cause runtime errors.
- Unsafe access to `Optional` values and incorrect Pydantic defaults.
- Mutable default arguments and shared mutable state.
- Bare or overly broad exception handling that hides failures.
- Unawaited coroutines, blocking I/O inside `async def`, and unsafe background work.
- Business rules in services, persistence in repositories, and validation in
  Pydantic models, following the repository's established structure.
- Duplicate or near-duplicate business logic that can diverge over time.
- Backward compatibility of public API requests and responses.
- Existing response envelopes such as `{success, message, data}`.

Do not request framework-independent services as a blanket rule. Existing
services may use FastAPI exceptions and response types. Flag that coupling only
when it introduces incorrect behavior, inconsistent responses, or prevents a
focused test.

## 2. FastAPI Routes

Applies to: `src/routes/**/*_route.py`

Focus on:

- Authentication on every non-public route.
- Authorization, role checks, ownership checks, and protection against IDOR.
- Correct use of `Depends`, path/query/body types, and Pydantic validation.
- Thin handlers that delegate business operations to services.
- Correct HTTP status codes and the repository's response envelope.
- Pagination limits and validation for list endpoints.
- ObjectId validation before repository queries.
- Accidental exposure of password hashes, tokens, internal keys, or private fields.
- Breaking route, parameter, or response changes that affect existing clients.
- Expensive or sequential repository calls inside loops.

Only recommend concurrent I/O when operations are independent and concurrency
is bounded. Do not suggest `asyncio.gather` when ordering, transactions, rate
limits, or shared state make parallel execution unsafe.

## 3. Pydantic Request and Response Models

Applies to:

- `src/models/**/request/**/*.py`
- `src/models/**/response/**/*.py`
- `src/models/**/*_model.py`

Focus on:

- Correct Pydantic v2 APIs, including `model_validate`, `model_dump`,
  `field_validator`, and `model_config`.
- Defaults and `Optional` fields matching actual API and database behavior.
- Constraints for IDs, pagination, text lengths, lists, dates, and enums.
- Separate request and response concerns where sensitive/internal fields exist.
- ObjectId and datetime serialization.
- Newly required fields breaking older clients or stored documents.
- Response fields silently becoming `null` because repository projections,
  aggregation pipelines, or Mongo views omit them.

Avoid suggesting inheritance or mixins solely to remove a few repeated fields.
Prefer clarity unless duplication creates a real maintenance or correctness risk.

## 4. Beanie and MongoDB

Applies to:

- `src/models/**/*_document.py`
- `src/models/**/*_view.py`
- `src/repositories/**/*.py`
- `src/database.py`

Focus on:

- Correct Beanie `Document`, `Link`, DBRef, View, and soft-delete behavior.
- Valid ObjectId conversion and consistent string/ObjectId comparisons.
- Filters that unintentionally include soft-deleted documents.
- Missing indexes for frequent filters, joins, sorting, and uniqueness rules.
- Duplicate records caused by check-then-insert races or missing unique indexes.
- Atomic updates where concurrent requests can overwrite each other.
- MongoDB aggregation correctness, especially `$lookup`, `$match`, `$group`,
  `$project`, `$unwind`, date conversion, and pagination stages.
- `$project` or `$group.$push` dropping fields expected by response models.
- N+1 repository calls and unbounded queries.
- Changes to a Beanie View pipeline without a safe strategy to recreate or
  update the existing MongoDB view during deployment.
- Data migrations being idempotent, scoped, reversible where practical, and
  safe against production data.

Never suggest deleting production collections or volumes as a routine fix.

## 5. Sessions, Check-in, and Check-out

Applies to session routes, services, repositories, models, and workers.

Focus on:

- All date calculations using the intended `Asia/Ho_Chi_Minh` timezone.
- UTC/local-time boundary errors and inclusive/exclusive date ranges.
- Duplicate check-in/check-out or session creation under retries and concurrency.
- Correct ownership: a user must not update another user's session.
- Status fields remaining internally consistent, including `checkin`,
  `checkout`, late flags, arrival/departure status, and evaluation.
- Checkout updates being atomic when tasks and session state change together.
- Reminder schedules excluding the intended weekdays and reading environment
  values in the format expected by Pydantic settings.
- Reminder jobs being idempotent so retries do not send duplicate notifications.

## 6. ARQ Worker, Redis, and External APIs

Applies to:

- `src/worker.py`
- reminder/background-task code
- Google Chat and internal API integrations

Focus on:

- Worker and API containers receiving consistent environment variables.
- Cron jobs running once at the intended local time.
- Retry behavior, timeouts, idempotency, and useful failure logging.
- Redis connection failures and safe worker restart behavior.
- `httpx` calls having explicit timeouts and handling non-success responses.
- External calls not occurring while a database object is left partially updated.
- Internal API keys and webhook/token values never appearing in URLs, logs,
  exceptions, commits, or response payloads.
- Internal URLs resolving correctly from the worker's Docker network.

## 7. File Upload and Conversion

Applies to file routes, services, models, Docker dependencies, and GridFS usage.

Focus on:

- Upload size, filename, extension, MIME type, and ObjectId validation.
- Path traversal, unsafe temporary files, and command injection.
- Memory usage from reading whole uploads into memory.
- File handles, cursors, streams, and temporary files always being closed.
- FFmpeg, LibreOffice, Pillow, MoviePy, and PDF conversion failures being
  bounded by timeouts and surfaced clearly.
- Background conversion jobs not losing errors or leaving orphaned files.
- Range requests returning correct boundaries and headers.

## 8. Security and Configuration

Focus on:

- Hard-coded passwords, JWT secrets, Mongo credentials, deploy keys, internal
  API keys, webhook URLs, and private host information.
- Secure password hashing and token validation/expiration.
- Production CORS restrictions and documentation exposure.
- User-controlled values reaching shell commands, file paths, Mongo operators,
  redirects, or outbound URLs.
- Environment variables parsed consistently without duplicate keys.
- No secret values printed during validation or debugging.

Flag committed `.env` or credential files. Do not skip them from security review.

## 9. Docker, Nginx, and Deployment

Applies to:

- `.github/workflows/**/*.yml`
- `Dockerfile`
- `docker-compose*.yml`
- `deploy/**`
- `scripts/**`
- `ops/production-deploy-repo-template/**`

Focus on:

- Testing and production configuration remaining isolated.
- Blue/green deployment targeting the inactive slot and switching only after
  the new application is healthy.
- Failed health checks leaving the active slot untouched.
- Nginx proxy ports, domains, forwarded headers, body-size limits, and disabled
  production documentation being correct.
- MongoDB binding only to the intended interface and preserving volumes.
- Redis and worker services not disappearing during app-only deployment.
- Environment files being normalized without appending duplicate keys.
- Shell scripts using strict error handling, safe quoting, and non-destructive
  cleanup.
- GitHub Actions permissions being minimal and secrets remaining masked.
- Third-party actions being pinned to a trusted version or commit where feasible.
- Source-sync scripts copying all required deployment files without copying
  `.env`, credentials, local artifacts, or stale generated files.

## 10. Tests

The repository currently has limited automated Python test infrastructure. Do
not assume fixtures or pytest configuration already exist.

Request focused tests when changes affect:

- Authentication, authorization, or role/ownership checks.
- Session creation, check-in/check-out, reminders, or timezone boundaries.
- Mongo aggregations, views, indexes, and duplicate prevention.
- Pydantic validation and response serialization.
- Worker retries, idempotency, and external API failure handling.
- File upload validation, range responses, or conversion failures.
- Deployment scripts with branching or rollback behavior.

Tests must not call real external services or shared testing/production databases.
Prefer deterministic unit tests and isolated integration tests. Do not require a
large testing-framework migration for an unrelated small change.

## Severity Guidance

- **High:** security vulnerability, data loss/corruption, authorization bypass,
  leaked secret, production outage, duplicate financial/business records, or a
  deployment that can replace the healthy slot with a broken one.
- **Medium:** user-visible incorrect behavior, broken API contract, missed or
  duplicate reminder, timezone error, significant performance regression, or
  missing failure handling on an important path.
- **Low:** maintainability issue with a concrete future defect risk.
- **Suggestion:** optional improvement that should not block the PR.

Do not classify style preferences, naming, comments, or speculative concerns as
High or Medium severity.
