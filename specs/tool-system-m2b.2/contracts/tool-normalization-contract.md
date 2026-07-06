# Contract: Tool Execution Normalization

## Purpose

Define the internal shape required for governed tool execution outcomes before prompt assembly.

## ToolExecutionEnvelope

Every governed tool call in scope must produce or be wrapped by an envelope containing:

- Route
- Selected tool
- Selected adapter where applicable
- Descriptor version or hash
- Admission outcome
- Normalized output reference
- Cache status
- Freshness status
- Warnings
- Degraded-state reason
- Trace metadata

## NormalizedOutput Kinds

Exactly one output kind is assigned:

- `EvidenceFact`
- `EvidenceSnippet`
- `EvidenceDocument`
- `SystemRecord`
- `MutationReceipt`
- `VisualizationProvenance`
- `GeneratedArtifact`
- `DegradedState`

## ToolContextPack

The request-scoped context pack contains:

- Normalized outputs
- Citations
- Source metadata
- Freshness metadata
- Warnings
- Degraded states
- Artifact references

## Prompt Boundary Rules

Allowed into prompt context:

- Normalized facts
- Normalized snippets
- Normalized documents
- System records
- Mutation receipts
- Visualization provenance
- Generated artifact metadata
- Degraded states
- Safe citations and warnings

Blocked from prompt context:

- Raw HTML
- Raw PDF bytes
- Scripts
- Hidden page text
- Untrusted page instructions
- Raw provider payloads
- Raw parser artifacts
- Credentials or parser limits

## Verification Expectations

- Every fixture has an envelope and exactly one normalized output kind.
- Raw-payload fixtures are excluded from `ToolContextPack`.
- Degraded fixtures are machine-detectable and safe to show.
- Trace metadata is internal and sanitized.
