# Copilot repository instructions
- This is a public, synthetic, offline-first container dependency mapping framework.
- Do not fetch or expose confidential code, credentials, private repository identifiers, internal registry names, or production vulnerability details.
- Discovery and reporting are read-only. Never edit scanned repositories or trigger builds, PRs, releases, or deployments.
- Cite evidence with source path, line number, commit SHA when available; label uncertain results as `unresolved`.
- Parse build instructions deterministically; do not hallucinate dynamic `ARG`, templating, runtime package installs, or reusable workflow behavior.
- Add unit tests for parser changes, including multi-stage builds and cycles.
- Separate build dependencies from workflow orchestration dependencies and application consumption.
- Use synthetic fixtures for all commits to this public project.
