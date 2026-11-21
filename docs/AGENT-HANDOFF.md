# Handoff contract for the next AI coding agent

## Objective
Turn the read-only starter into a tested enterprise-safe, version-aware dependency discovery and remediation planning service. **Do not implement autonomous publication or deployment in the first iteration.**

## Inputs
1. A locally accessible, explicitly approved repository catalog with repo, path, ref/commit, producing image ref, variants and build args.
2. Dockerfiles/Containerfiles, Actions workflows, Makefiles and build scripts.
3. Later (only when authorized): read-only enterprise GitHub Actions and registry manifest APIs, SBOM and vulnerability reports.

## Outputs
Normalized `graph.json`, `unresolved.json`, `dependencies.csv`, `graph.mmd`, `report.md` and `rebuild-plan.json`; every edge must include evidence and confidence. Record published digest and runner/build metadata separately from static source declarations.

## Next coding tickets (in order)
- [ ] Write scanner tests for multi-stage aliases, `ARG` before `FROM`, nonliteral args and inherited stage references.
- [ ] Implement robust workflow parser for build/push jobs, reused workflows, matrices and generated tags.
- [ ] Resolve image producers by *exact* OCI reference, not string matching; model version and architecture.
- [ ] Add strongly typed JSON Schema validation and source commit attribution.
- [ ] Implement descendant impact, SCC cycle reporting and topological rebuild waves.
- [ ] Add integration fixture with two repos sharing a base and one unrelated image.
- [ ] Add read-only API adapters behind feature flags and unit-test them against mock responses.
- [ ] Add SBOM/vulnerability enrichment with applicability and package-origin verification.
- [ ] Add human-readable rebuild plan and review gate, without triggering workflows.

## Agent restrictions
Do not make claims of a production-ready graph from static Dockerfiles. Do not introduce automatic builds, remote modification, network access or secrets without explicit security review. No real enterprise input, logs or output may be committed to public GitHub. Validate each milestone with tests and cite modified files in your handoff report.
