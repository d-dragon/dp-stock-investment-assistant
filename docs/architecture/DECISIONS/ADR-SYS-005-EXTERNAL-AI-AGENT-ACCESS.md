# ADR-SYS-005: External AI agent access

| Field | Value |
|---|---|
| Status | Proposed (stub) |
| Date | 2026-10-12 |
| Owner | Software Architect Assistant; decision by Phan Duy |
| Blocks | Future only |
| Depends on | ADR-SYS-001 identity; ADR-SYS-002 gate |

## Context

Outside agents (Claude, ChatGPT, Grok, or the user's own) can call a remote tool server. The overview lists them as a future neighbour, proposed by this architecture and not yet named in the Spec.

## Decision to make

Whether and how outside agents reach a user's work through a Backend-owned tool interface.

## Options to evaluate

- A. No outside access in Phase 1 (default).
- B. A Backend-owned MCP interface: read-only first, acting in the user's own sign-in, writes only as proposals the user confirms through the gate, output labelled AI-assisted.
- Note: xAI's remote tool calling has no approval prompt.

## Decision

Not yet decided.

## Follow-ups

- Threats from the security view: confused deputy, prompt injection, excessive agency.
