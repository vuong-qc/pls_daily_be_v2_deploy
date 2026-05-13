# Engineering Standards

## Principles
- Keep data validation in Pydantic models; keep business logic in services; keep data access in repositories.
- Favor explicit, consistent API responses: `{success, message?, data?}`.
- Treat security checks as first-class logic, not as afterthoughts.

## API Design
- Use RESTful naming: plural resources (`/users`, `/jobs`) and standard verbs.
- Validate inputs at the edge (models + query params); reject invalid IDs early.
- Return 4xx for client errors and 5xx for server errors; avoid 200 with error payloads.

## Security
- Never store or return plaintext passwords; hash on create and on any password update.
- Protect all non-public routes with JWT + role checks.
- Avoid hardcoded secrets or default passwords in code.
- Lock down CORS origins in production.

## Data Layer
- Always convert Mongo ObjectId to string before returning responses.
- Use consistent timestamp fields: `created_at`, `updated_at` in milliseconds.
- Add indexes for any query filters and sort fields used in list endpoints.

## Error Handling
- Avoid bare `except`; catch specific exceptions and return clear error messages.
- When a record is missing, return 404.
- Validate that IDs are valid ObjectIds before querying.

## Testing
- Add unit tests for services and repositories.
- Add API tests for auth, users, jobs.
- Add negative tests for invalid IDs, bad input, and unauthorized access.

## Dependencies
- Pin package versions in `requirements.txt`.
- Regularly run a dependency vulnerability scan (e.g., `pip-audit`).

## Production Sync Flow

Before running:
- Make sure source changes in `be_buddy_v3` branch `vuong` are ready.
- If production deploy files changed, review:
  - `deploy/`
  - `ops/production-deploy-repo-template/`
  - `docs/DEPLOY_PRODUCTION.md`
  - `scripts/sync_to_deploy_repo.*`

Commands:

```cmd
cd C:\AutoTest-Selenium-MedicineStudy\PLS_Student_Automation_Test\be_buddy_v2_deploy
git fetch origin
git checkout main
git reset --hard origin/main
```

```cmd
cd C:\AutoTest-Selenium-MedicineStudy\PLS_Student_Automation_Test\be_buddy_v3
git checkout vuong
git pull origin vuong
Windows: scripts\sync_to_deploy_repo.cmd ..\be_buddy_v2_deploy
Mac: bash ./scripts/sync_to_deploy_repo.sh ../be_buddy_v2_deploy
```

```cmd
cd C:\AutoTest-Selenium-MedicineStudy\PLS_Student_Automation_Test\be_buddy_v2_deploy
git status
git add .
git commit -m "Sync source for production release"
git push origin main
```

Expected result:
- Source changes from `be_buddy_v3` branch `vuong` are copied into `be_buddy_v2_deploy`.
- Push to `main` of `vuong-qc/be_buddy_v2_deploy`.
- GitHub Actions `Deploy Production` starts automatically.
