# Image-Update-Plans

An open-source, **read-only** project for discovering container image build dependencies and planning safe rebuild waves.

> **Public repository boundary:** All examples are synthetic. Never commit enterprise inventory, internal repositories or registries, vulnerability findings, application mappings, secrets, or production topology.

## Why this project exists
Large platform teams build base, language-runtime and middleware images that form transitive dependency chains. A vulnerability in a base image may require many downstream rebuilds. Image-Update-Plans captures version-specific ancestry, associated build workflows, evidence and unresolved references before any agent recommends remediation.

## Principles
- Evidence before inference: record source file and line for every parent relationship.
- Track versions, digests, platforms and variants; tags are mutable aliases.
- Report unresolved references rather than guessing.
- Keep image ancestry, GitHub Actions scheduling dependencies and application consumption as distinct edge types.
- Read-only discovery first; human-reviewed remediation and deployment gates later.
- Keep real enterprise inventories in an approved **internal** environment.

## Repository layout
- `.github/copilot-instructions.md` — Copilot-wide safety and implementation rules
- `.github/prompts/discover-image-dependencies.prompt.md` — reusable Copilot discovery prompt
- `docs/IMPLEMENTATION.md` — development milestones and enterprise rollout
- `docs/SCHEMA.md` — machine-readable graph contract
- `docs/AGENT-HANDOFF.md` — future automation agent instructions
- `src/image_update_plans/scan.py` — deterministic local-only proof of concept
- `examples/inventory.json`, `examples/repos/` — synthetic three-image fixture
- `tests/test_scan.py` — regression tests

## Run locally
Requires Python 3.11+:

```bash
python -m pip install -e .
python -m image_update_plans.scan --inventory examples/inventory.json --output-dir output
python -m unittest discover -s tests -v
```

Produces `output/graph.json`, `output/dependencies.csv`, `output/graph.mmd`, and `output/report.md`.

## Copilot workflow
Open this project and authorized source repositories in VS Code (or use an approved internal checkout). In Copilot Chat Agent mode, run `/discover-image-dependencies`. The agent can only inspect repositories that have been made accessible to its workspace. Begin with synthetic examples, then pilot on a small number of approved internal repositories. Keep discoveries, reports, and real metadata internal.

**Status:** Starter proof of concept, not production-ready. It cannot comprehensively resolve dynamic workflows, all Dockerfile syntax, registry digests, or build provenance. See the implementation plan before relying on its output.
