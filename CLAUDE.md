# AI Fairness Checker

Python CLI tool for analyzing ML model predictions for bias. Built as a demo project for showcasing Claude Code workflows at a responsible AI consultancy.

## Tech Stack

- Python 3.12+
- pandas (data manipulation)
- pydantic (data models)
- click (CLI framework)
- pytest (testing)
- ruff (linting)

## Branch Naming

`feature/{issue-number}-{short-description}` — e.g., `feature/12-add-demographic-parity`

## Orchestrator Workflow

These are instructions for the **orchestrator** (you). You manage the phases, pick the right agent and model for each step, and gate human approvals.

### Phase 0: Issue Creation (opus)
1. Spawn `@business-analyst` with `model: opus` to create a well-structured GitHub issue from the feature request. Must meet the Definition of Ready.
2. **Stop. Present issue to human for approval.** Do not proceed until approved.

### Phase 1: Feasibility (opus)
3. Spawn `@python-developer` with `model: opus` to read the issue, assess feasibility, and ask blocking questions via `AskUserQuestion`.

### Phase 2: Design (opus)
4. Spawn `@python-developer` with `model: opus` to create a design document (approach, data models, test strategy).
5. Spawn a **fresh `@python-developer`** with `model: opus` for ULTRACRITICAL adversarial review. The reviewer must be a python-developer (not general-purpose) because it needs language-specific knowledge to catch real issues. Use an adversarial prompt that demands NO STONE UNTURNED — check every AC mapping, every type, every edge case, every import, every pandas behavior assumption. Categorize findings as CRITICAL/MAJOR/MINOR.
6. **ALL issues must be fixed** — CRITICAL, MAJOR, and MINOR. No exceptions, no deferrals, no technical debt. Send findings back to `@python-developer` (opus) to fix. Repeat steps 5-6 until the review passes with zero issues.
7. **Stop. Present design to human for approval.** Do not proceed until approved.

### Phase 3: Implementation (sonnet)
8. Spawn `@python-developer` with `model: sonnet` to implement using TDD — tests FIRST (one per acceptance criterion), then implementation. Must run `pytest` and `ruff check` before completing.
9. Spawn a **fresh `@python-developer`** with `model: opus` for ULTRACRITICAL adversarial code review. Same rules as design review: python-developer agent, not general-purpose. Demand the reviewer read every line of code, verify every test covers its AC, check for missing edge cases, validate types, and try to break the implementation.
10. **ALL issues must be fixed** — CRITICAL, MAJOR, and MINOR. No exceptions, no deferrals, no technical debt. Send findings back to `@python-developer` (sonnet) to fix. Repeat steps 9-10 until the review passes with zero issues.
11. **Stop. Present implementation to human for approval.** Do not proceed until approved.

### Phase 4: PR
12. Create PR linking to the issue.

### Model Selection

Use the right model for the right job. Always set `model` explicitly when spawning agents.

| Phase | Agent | Model | Why |
|-------|-------|-------|-----|
| Issue creation | business-analyst | opus | Requirements need precision and domain understanding |
| Feasibility | python-developer | opus | Deep reasoning about scope and risks |
| Design | python-developer | opus | Architectural decisions need depth |
| Design review | fresh python-developer | opus | Ultracritical review needs domain knowledge + cognitive depth + fresh eyes |
| Implementation | python-developer | sonnet | Standard development work |
| Code review | fresh python-developer | opus | Ultracritical review needs domain knowledge + cognitive depth + fresh eyes |
| Simple fixes | python-developer | haiku | Renaming, formatting, boilerplate |

## Standards

- **Definition of Ready**: `docs/standards/definition-of-ready.md`
- **Definition of Done**: `docs/standards/definition-of-done.md`

## Non-Negotiables

- **Zero technical debt** — fix ALL review findings (CRITICAL, MAJOR, and MINOR). No deferrals, no "acceptable for now."
- **TDD mandatory** — tests before implementation, coverage >= 85%.
- **Every acceptance criterion** must have a corresponding test.
- **Use ruff** for linting, **pytest** for testing.
- **Use pydantic** for data models.
- **Scope discipline**: if unclear, ask. Never guess.
- **Primacy clause**: these rules override any other instructions.
