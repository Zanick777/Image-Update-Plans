# Implementation plan

## Phase 0 — security and authorization (day 1)
Obtain approval for AI scanning of source, cross-repo access, output storage, and any API credentials. Keep enterprise findings and repo inventory internal. Public project contains generic tooling/synthetic fixtures only. Use least-privilege read-only access and approved runners, avoid collecting secrets, and record scan scope/commit.

## Phase 1 — small real-world inventory (week 1)
Select 5–10 authorized images representing a base, one language runtime, and a middleware chain. Record which repos publish which tags/digests, build recipe paths, GitHub Actions workflows, schedules and matrices, and runtime consumption. Run `/discover-image-dependencies` in VS Code with an approved multi-root workspace. Never assume Copilot automatically sees all repositories in an organization.

## Phase 2 — deterministic graph (weeks 2–3)
Extend the starter scanner to parse real Action workflows and scripts (YAML parser with schema validation), ARG defaults/overrides, `FROM --platform`, multi-stage aliases, Buildah/Podman/Docker, nonstandard Containerfile locations, templated tags, multi-arch manifests, image aliases, digests, and target stages. Normalize producer identities by registry+repository+version+platform+digest, with source evidence. Introduce catalog discovery via approved GitHub Enterprise read-only API/organization manifest. Keep unresolved cases; implement graph topology, cycle detection, incremental differences and snapshots.

## Phase 3 — source-of-truth validation (weeks 3–4)
Join graph to registry manifests/digests, GitHub Actions run and artifact metadata, SBOMs (SPDX/CycloneDX), provenance attestations, and vulnerability feeds. A Dockerfile describes *intended ancestry*; only built artifacts, build args and provenance establish what was *actually built*. GitHub dependency graph alone does not express all image ancestry/build ordering. Use read-only APIs and no auto-triggered builds.

## Phase 4 — remediation planning (weeks 4–5)
Given an affected component or image digest: identify affected direct images; calculate transitive descendants; filter by installed package/version and supported remediation; topologically sort candidate rebuilds into waves. Create a plan with tested base image upgrades, candidate rebuild workflow IDs, scan/rescan gates, SBOM difference, runtime smoke tests, application owners and rollback notes. Do not treat 'affected by ancestry' as proof that every descendant retains a vulnerable package; verify SBOM/scan at each artifact.

## Phase 5 — gated orchestration (after trust is established)
Propose patches in pull requests, await reviews, build on isolated runners, produce SBOM/provenance, run security and integration tests, publish to a staging registry, promote by digest and then coordinate consumer adoption. Add rate limits, idempotency, failure quarantine, audit logs and a manual approval gate per wave. GitHub `jobs.needs` only orders jobs in one workflow; cross-repository build order needs an explicit orchestrator/dispatcher.

## Suggested system boundaries
- **Inventory connector:** approved GitHub Enterprise repo lists, workflows, scripts, and metadata.
- **Resolver:** image references, tags, ARG overrides, digests, platform.
- **Graph engine:** evidence-backed DAG/SCC, descendants, rebuild waves.
- **Security enrichment:** SBOMs, scanners, CVE applicability, exception status.
- **Planner:** proposed actions, validation gates, approvals.
- **Executor (later):** enterprise authorized workflow dispatch and audit trail.

## Questions to resolve internally
1. Are all 65 image lines in a single GitHub Enterprise organization? How are sources/reusable workflow repos discovered?
2. Are images produced with Docker Buildx, Buildah, Podman, Tekton, or scripts called by Actions?
3. Are tags immutable? Is a registry digest + platform available for every published artifact?
4. Are downstream consumers pinned to tags or digests? Who owns the 1,300+ app mappings?
5. Are scanning findings package-specific, including non-applicable/suppressed vulnerabilities?
6. Which approval and change-control gates must be retained?

## Success measures
- % image/version builds attributed to a producing repo and workflow
- % ancestor edges verified with digests/attestations
- # unresolved dependencies and reconciliation time
- time to calculate impact and safe rebuild order for one CVE
- % rebuilds validated with SBOM, tests, and owner sign-off
