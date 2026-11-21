# Graph data contract v0.1

Use `image_build` nodes rather than only image names. A logical product can have multiple supported versions, platforms and digests. Example ID: `registry.example.invalid/runtime/java:21@linux-amd64#sha256:...`. Avoid embedding private identifiers in public examples.

## Node
```json
{
  "id": "java-21-amd64",
  "type": "image_build",
  "image_ref": "registry.example.invalid/java:21",
  "resolved_digest": null,
  "platform": "linux/amd64",
  "producer_repo": "synthetic/java-runtime",
  "source_ref": "example-sha-or-tag",
  "dockerfile": "Containerfile",
  "target": null,
  "workflow": ".github/workflows/build.yml",
  "status": "source_only"
}
```

## Edge
```json
{
  "from": "ubi-9-amd64",
  "to": "java-21-amd64",
  "kind": "build_from",
  "reference": "registry.example.invalid/ubi:9",
  "confidence": "inferred",
  "evidence": [{"file": "examples/repos/java-runtime/Containerfile", "line": 1}],
  "verification": "resolve the build-time tag to the manifest digest"
}
```

## Scope semantics
- `build_from`: upstream parent/base used to create downstream image. Direction = **parent → child**.
- `workflow_needs`: GitHub Actions job dependencies. Different graph, not necessarily image ancestry.
- `consumed_by`: runtime/application consumption. Distinct third graph; do not infer from base-image inheritance.
- `confidence`: `verified`, `inferred`, `unresolved` (never claim registry verification from static source parsing).
- `unresolved`: explicitly retain expressions, missing refs, nonliteral build arguments, unknown workflows, and missing repos.
- `rebuild_wave`: based on topological order after changes; changing an ancestor may make descendants candidates, not guarantee remediation is required.
- `graph_snapshot`: scan time, repo commit SHAs, catalog version, registry resolution time, and scanner version for reproducibility.

Current starter outputs a simplified subset of this contract and is **not** an enterprise-complete schema implementation.
