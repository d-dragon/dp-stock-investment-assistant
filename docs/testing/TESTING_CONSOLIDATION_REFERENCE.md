# Testing Instructions: Section Mapping & Line Numbers

A quick reference for all testing sections across both instruction files.

---

## testing.instructions.md (908 total lines)

### Testing Philosophy (Lines 8–35)
```
8   | ## Testing Philosophy
10  | ### Core Principles
18  | ### Test Levels Overview
29  | ### Coverage Targets
```

### Test Organization (Lines 37–72)
```
37  | ## Test Organization
37  | ### Directory Structure
63  | ### Naming Conventions
71  | ### pytest Configuration  ← Backend Testing Starts Here
```

### Backend Testing (Lines 71–379) [309 lines]
```
71  | ### pytest Configuration
76  | ### Fixture Patterns
110 | ### Unit Test Patterns
    | - Testing pure functions
    | - Testing classes with dependencies
    | - Testing streaming functions
178 | ### Integration Test Patterns
    | - Testing Flask API routes
    | - Testing database repositories
240 | ### Mocking Strategies
    | - Protocol-based mocking for services
    | - Cache testing patterns
    | - Mocking external APIs
    | - Mocking MongoDB
    | - Mocking Redis
354 | ### Running Backend Tests
380 | ### Jest Configuration  ← Frontend Testing Starts Here
```

### Frontend Testing (Lines 380–560) [180 lines]
```
380 | ### Jest Configuration
385 | ### Component Testing Patterns
    | - Testing presentational components
    | - Testing components with state
    | - Testing custom hooks
504 | ### Service Layer Testing
539 | ### Running Frontend Tests
561 | ### E2E Testing Strategy  ← E2E Testing Starts Here
```

### E2E Testing (Lines 561–594)
```
561 | ### E2E Testing Strategy
567 | ### Example E2E Test Pattern (Playwright)
595 | ### Load Testing Strategy  ← Performance Testing Starts Here
```

### Performance Testing (Lines 595–650)
```
595 | ### Load Testing Strategy
604 | ### Example Load Test (Locust)
633 | ### Performance Benchmarking
651 | ### Security Testing Strategy  ← Security Testing Starts Here
```

### Security Testing (Lines 651–750)
```
651 | ### Security Testing Strategy
    | - Static analysis tools
    | - Dependency scanning
    | - Container scanning
    | - Secrets detection
658 | ### Static Security Analysis
665 | ### Security Test Patterns
    | - Testing authentication/authorization
    | - Testing input validation
    | - Testing rate limiting
723 | ### OWASP Top 10 Test Coverage
751 | ### Fixtures and Seed Data  ← Test Data Mgmt Starts Here
```

### Test Data Management (Lines 751–780)
```
751 | ### Fixtures and Seed Data
768 | ### Test Isolation Strategies
781 | ### GitHub Actions Test Workflow  ← CI/CD Integration Starts Here
```

### CI/CD Integration (Lines 781–850)
```
781 | ### GitHub Actions Test Workflow
851 | ### Test Quality Gates
851 | ### Common Debugging Techniques  ← Debugging Starts Here
```

### Debugging (Lines 851–908)
```
851 | ### Common Debugging Techniques
862 | ### Troubleshooting Patterns
877 | ### Testing Best Practices Summary
    | - Do's (8 items)
    | - Don'ts (8 items)
908 | [END OF FILE]
```

---

## backend-python.instructions.md (1,713 total lines, 284 lines of testing)

### Testing with pytest (Lines 868–1,151) [284 lines]

```
868 | ## Testing with pytest
    | ├─ Framework overview
    | ├─ Mocking strategy
    | ├─ Coverage targets
    | ├─ Test structure
    | ├─ Run commands
    | └─ PYTHONPATH note
    |
887 | ### Protocol-Based Mocking for Services [4 lines]
    | - Brief pattern description
    | - Reference: examples/testing/test_service_with_protocols.py
    |
892 | ### Service Test Helper Pattern [4 lines]
    | - Brief pattern description
    | - Reference: examples/testing/test_service_with_protocols.py
    |
897 | ### Health Check Testing [104 lines] ★ CANDIDATE FOR MOVE
    | 
    | Pattern 1: All dependencies healthy
    | Pattern 2: Required dependency failure
    | Pattern 3: Optional dependency failure (degraded mode)
    | Pattern 4: MagicMock fixture patterns
    | 
    | Common Fixtures:
    | - healthy_repository
    | - unhealthy_repository
    | 
    | Key Testing Patterns: ✅ Checklist (6 items)
    |
1002| ### WebSocket Testing Patterns [50 lines] ★ CANDIDATE FOR MOVE
    | 
    | Testing Approaches:
    | - Mock Socket.IO Client Setup
    | - Testing Event Handlers (Unit Tests)
    | - Testing Connection Events (Integration Tests)
    | - Testing Streaming Events
    | 
    | Key Testing Patterns: ✅ Checklist (6 items)
    |
1052| ## Model Factory and AI Clients [99 lines]
    | (Not testing per se, but client caching/fallback patterns)
    |
1152| ## Data Manager [4 lines]
    | (End of testing context)
```

---

## Content Overlap Matrix

### Fully Covered in Both Files

| Content | testing.instructions.md | backend-python.instructions.md | Status |
|---------|--------------------------|-------------------------------|--------|
| pytest fixtures | Lines 76–109 | Embedded in task examples | ✅ Duplicate |
| Flask test client | Lines 178–211 | "Add API Endpoint" task | ✅ Duplicate |
| Protocol-based mocking | Lines 240–264 | Lines 887–890 (ref) | ✅ Duplicate |

### Covered ONLY in testing.instructions.md

| Content | Lines | Notes |
|---------|-------|-------|
| Jest + React Testing Library | 380–560 | Frontend testing |
| E2E testing (Playwright) | 561–594 | End-to-end workflows |
| Load testing (Locust) | 595–650 | Performance testing |
| Security testing (Bandit, Snyk) | 651–750 | Static analysis + OWASP |
| Test data management | 751–780 | Factories + isolation |
| CI/CD GitHub Actions | 781–850 | Pipeline integration |
| Debugging techniques | 851–908 | Best practices + troubleshooting |

### Covered ONLY in backend-python.instructions.md

| Content | Lines | Status |
|---------|-------|--------|
| Health check testing | 897–1000 | ⭐ Comprehensive + unique |
| WebSocket testing | 1002–1051 | ⭐ Comprehensive + unique |
| Service test helper | 892–895 | Brief (should expand) |

---

## Consolidation Action Items

### MOVE to testing.instructions.md

- [ ] **Health Check Testing** (backend-python lines 897–1000)
  - Insert after line 239 (Integration Test Patterns)
  - Include all 4 patterns + fixtures
  - Keep reference in backend-python

- [ ] **WebSocket Testing Patterns** (backend-python lines 1002–1051)
  - Insert after Health Check Testing
  - Include all testing approaches
  - Keep reference in backend-python

- [ ] **Service Test Helper Pattern** (backend-python lines 892–895)
  - Enhance in testing.instructions.md Fixtures section
  - Provide full code example, not just reference

### UPDATE References

- [ ] backend-python lines 887–890: Point to testing.instructions.md instead of example file
- [ ] backend-python lines 897–1000: Replace with brief summary + link
- [ ] backend-python lines 1002–1051: Replace with brief summary + link
- [ ] Add cross-reference section at top of backend-python testing section

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Total testing content** | ~570 lines across both files |
| **Duplicate content** | ~150 lines (can consolidate) |
| **Unique to testing.instructions.md** | ~360 lines |
| **Unique to backend-python.instructions.md** | ~154 lines (health check + WebSocket) |
| **Potential size after consolidation** | ~420 lines in testing.instructions.md |
| **Reduction in backend-python** | ~150 lines (net improvement) |

---

## File Organization After Consolidation

### testing.instructions.md (projected ~1,100 lines)
```
1. Testing Philosophy (28 lines)
2. Test Organization (36 lines)
3. Backend Testing (≈450 lines)
   - pytest configuration
   - Fixtures & Patterns
   - Unit tests
   - Integration tests
   - Mocking strategies
   - Health check testing [NEW - moved from backend]
   - WebSocket testing [NEW - moved from backend]
   - Running tests
4. Frontend Testing (160 lines)
5. E2E Testing (34 lines)
6. Performance Testing (56 lines)
7. Security Testing (100 lines)
8. Test Data Management (30 lines)
9. CI/CD Integration (70 lines)
10. Debugging (58 lines)
```

### backend-python.instructions.md (projected ~1,563 lines)
```
(Main content unchanged, testing section simplified)

## Testing with pytest [lines reduced from 284 to ~100]
- Brief overview
- Link to testing.instructions.md
- Model factory testing patterns (unique to backend)
- References to examples/
```

---

## Next Steps

1. **Review this mapping** - Confirm line numbers and content status
2. **Implement Phase 1** - Add Health Check + WebSocket + enhanced Service Helper to testing.instructions.md
3. **Implement Phase 2** - Update references in backend-python.instructions.md
4. **Verify links** - Ensure all cross-references work (relative paths)
5. **Test rendering** - Check markdown renders correctly in VS Code + GitHub

---

**Created**: December 11, 2025  
**Status**: Research Complete - Ready for Implementation  
**Effort Estimate**: 1-2 hours (3 phases)
