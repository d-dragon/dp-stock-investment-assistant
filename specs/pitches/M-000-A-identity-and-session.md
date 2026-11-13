# Pitch: M-000 Identity and session

| Field | Value |
|---|---|
| Milestone | [M-000 Platform foundation (identity + FE shell)](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) |
| Priority | P0 (from M-000) |
| Requirements covered | FR: [SR-10.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-1), [SR-10.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-2), [SR-10.1.3](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-3), [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2) (`sessionRef` contract) · NFR: [SNR-3.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-3-2-1) |
| Status | Draft (shaped-draft) |
| Appetite | 2 weeks *(proposed, to confirm by Product Owner)* |
| Cost | Team time within the appetite; an Auth0 tenant is expected *(estimate, Product Owner to confirm)* |
| Slices | A1 sign-in-and-sign-out — SR-10.1.1, SR-10.1.2; A2 session-expiry-and-isolation — SR-10.1.3, SNR-3.2.1; A3 session-reference — SR-1.4.2 *(proposed, may change in delivery; not created yet)* |
| Last re-ranked | 2026-11-13 |
| References | [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md) (Accepted in part: Auth0 IdP and Backend-for-Frontend token storage; role mapping still Proposed) · Product [§3.5 Isolation](../../docs/system/PRODUCT_SPECIFICATION.md#35-integration--trust-boundaries), [§5.3 M-000](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) · Design: [DESIGN_LOCK §3 Identity surfaces](../../docs/domains/frontend/DESIGN_LOCK.md) (rendered in the Pitch B shell) · Sibling: [M-000 Frontend foundation](M-000-B-frontend-foundation.md); [M-001](M-001-adaptive-visual-canvas.md) (context beyond one session waits on this pitch) |

## Problem
Milestone [M-000](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) must give Canvas and later Core objects a real owner and a login path. Today several lines ([SR-9.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-9-1-1), [SNR-3.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-3-2-1), [OI-4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#oi-4)) stay unverifiable on a caller-set `X-User-ID` header. Without authentication, sign-out, and an owner-scoped session, per-user isolation cannot close, and [M-001](M-001-adaptive-visual-canvas.md) slice S2 cannot keep context across a reload, a device, or a new session.

## Appetite
2 weeks *(proposed, to confirm by Product Owner)*: A1 and A2 are the main bet (sign-in, sign-out, expiry, isolation); A3 is the shorter `sessionRef` contract. Product §5.3 already frames M-000 as "flexible / agentic OK"; the two-week figure is a shaping estimate, not a lock. Frontend stack work is [Pitch B](M-000-B-frontend-foundation.md) and sits in a separate appetite.

## Solution sketch (product behavior, no stack detail)
- **A1 — sign-in and sign-out.** The user authenticates through Auth0 before any owner-scoped workspace, session, conversation or Investment Core data is granted ([SR-10.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-1); [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md)). The Backend is the Backend-for-Frontend: Flask is the confidential OAuth client, runs the authorization code flow with PKCE, keeps the tokens in a server-side session and scopes every user-owned record to `sub`. The browser never holds a token; it holds only a `__Host-` session cookie (`Secure`, `HttpOnly`, `SameSite=Strict`), the SPA and API share one origin, and calls that change state carry CSRF protection (ADR-SYS-001, Product Owner 2026-11-13). Sign-in and sign-out are provided; sign-out ends the authenticated session so later requests are unauthenticated ([SR-10.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-2)). The caller-set `X-User-ID` header is retired as the identity mechanism. Surfaces: [DESIGN_LOCK §3](../../docs/domains/frontend/DESIGN_LOCK.md) (sign-in screen; sign-out returns to it; account menu in Z2), rendered in the Pitch B shell.

  Acceptance: an unauthenticated request cannot read or write owner-scoped data; after sign-out, the same client is unauthenticated; identity is the verified `sub`, not `X-User-ID`.

- **A2 — expired session and isolation.** When the authenticated session expires or is rejected, the system requires re-authentication and does not expose another user's data ([SR-10.1.3](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-3)). On an owner mismatch the Backend reveals nothing (ADR-SYS-001: 404). Workspace, session, conversation and Investment Core objects are owner-scoped ([SNR-3.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-3-2-1)). Unsent client input for the same user is preserved across the re-auth step: the Z4 draft lives in `sessionStorage` and survives a re-auth redirect and a reload in the same tab (Product Owner, 2026-11-13; DESIGN_LOCK §2–§3). The user returns to the same URL.

  Acceptance: tests show one user cannot read another user's thread or Core records (ADR-SYS-001 follow-up); an expired session yields a re-auth flow and never another user's data; the same user's unsent Z4 draft is still there after re-auth. This is what lets [OI-4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#oi-4) move.

- **A3 — session reference.** `sessionRef` is the Backend session id plus the conversation id, following the API hierarchy workspace > session > conversation in [`docs/openapi.yaml`](../../docs/openapi.yaml) ([SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2), Product Owner 2026-11-13). The Frontend holds those references only and never copies the Z4 thread or Backend session state into a second source of truth ([DESIGN_LOCK §2](../../docs/domains/frontend/DESIGN_LOCK.md); M-001 S2). The in-session workspace context *store* that holds the references is realized in [Pitch B](M-000-B-frontend-foundation.md); this slice owns the identity meaning: `sessionRef` comes from the authenticated session, is cleared on sign-out, and after this pitch M-001 S2 context can extend across reload, device or account for the owning user.

  Acceptance: `sessionRef` is the pair (Backend session id, conversation id) and is used as a reference, not a copied thread; after sign-in, shell surfaces share one `sessionRef`; after sign-out, it is cleared; cross-reload restore of owner-scoped context is only for the authenticated owner.

## Rabbit holes
- **Cookie and redirect details ([ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md), Backend-for-Frontend).** The Auth0 callback arrives as a cross-site redirect, so a `Strict` cookie is not sent on it: the short-lived login cookie holding `state` and PKCE values must be `Lax`, and the callback should finish with a same-site redirect before the `Strict` session cookie is relied on. Session store, cookie settings, CSRF mechanism, routes and dev proxy belong to TECHNICAL_DESIGN; this pitch does not redesign them.
- **Role-to-permission mapping (still Proposed on ADR-SYS-001).** This pitch authenticates and isolates by `sub`. It must not grow into a full RBAC product.
- Per-device or multi-session policy beyond Phase 1 needs.

## Risks
- The Backend-for-Frontend adds Backend work to A1 (confidential client, server-side session, CSRF), which makes the two-week appetite tighter.
- Isolation ([SNR-3.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-3-2-1), [OI-4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#oi-4)) stays unverifiable until `X-User-ID` is actually retired and owner = `sub` is tested.
- Auth0 tenant cost and operations sit outside team time and need a Product Owner confirm.

## No-gos
- Canvas zones, chart, or Decision-gate behavior ([M-001](M-001-adaptive-visual-canvas.md) / Milestone [M-006](../../docs/system/PRODUCT_SPECIFICATION.md#m-006)).
- Frontend stack modernization ([Pitch B](M-000-B-frontend-foundation.md)).
- Replacing Auth0 or reopening the IdP choice without a new ADR amend.
- A full role-and-permission product, or multi-tenant features beyond owner isolation.
- A second copy of the Z4 thread in Frontend state.

## Done means
- [SR-10.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-1), [SR-10.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-2), [SR-10.1.3](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-10-1-3) and [SNR-3.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-3-2-1) are `verified`. The `sessionRef` contract in [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2) is agreed and used as a reference (the shell store that holds it closes with Pitch B).
- M-001 S2 is no longer blocked on identity for context beyond one browser session.
- Given/When/Then acceptance, including the UX Designer's criteria for sign-in and expired-session surfaces ([DESIGN_LOCK §3](../../docs/domains/frontend/DESIGN_LOCK.md)), lives in each slice's `spec.md`.

## Open questions
- [NEEDS CLARIFICATION] Is the 2-week appetite right, or should this stay "flexible / agentic OK" as in Product §5.3?
- [NEEDS CLARIFICATION] Is the cost estimate right: team time plus an Auth0 tenant?
- *Decided 2026-11-13:* token storage is the Backend-for-Frontend with an HttpOnly session cookie (ADR-SYS-001 choice 2, Accepted by Product Owner). Tokens stay on the Backend; the browser holds none.
- [NEEDS CLARIFICATION] Is role-to-permission mapping (ADR-SYS-001 choice 3) in this pitch, or deferred? Recommendation: defer; this pitch authenticates and isolates by `sub` only.
- *Decided 2026-10-13:* Auth0 is the identity provider (ADR-SYS-001, Accepted in part). The Backend validates Auth0-issued JWT access tokens and scopes every user-owned record to `sub`.
- *Decided 2026-11-13:* `sessionRef` is the Backend session id plus the conversation id (API hierarchy workspace > session > conversation). The Frontend holds the references only.
- *Decided 2026-11-13:* the Z4 unsent draft lives in `sessionStorage` so it survives a re-auth redirect and a reload in the same tab (DESIGN_LOCK §2–§3; SR-10.1.3 "where feasible").
