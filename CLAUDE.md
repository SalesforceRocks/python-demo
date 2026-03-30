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

## Orchestrator Workflow (Demo Mode)

These are instructions for the **orchestrator** (you). You manage the phases, pick the right agent for each step, and gate human approvals.

> **Demo mode**: Review loops removed for live demo speed. See `CLAUDE-production.md` for the full production workflow with adversarial review loops.

### Phase 0: Issue Creation
1. Spawn `@business-analyst` with `model: sonnet` to create a well-structured GitHub issue from the feature request. Must meet the Definition of Ready.
2. **Stop. Present issue to human for approval.** Do not proceed until approved.

### Phase 1: Feasibility
3. Spawn `@python-developer` with `model: sonnet` to read the issue, assess feasibility, and ask blocking questions via `AskUserQuestion`.

### Phase 2: Design
4. Spawn `@python-developer` with `model: sonnet` to create a design document (approach, data models, test strategy).
5. **Stop. Present design to human for approval.** Do not proceed until approved.

### Phase 3: Implementation
6. Spawn `@python-developer` with `model: sonnet` to implement using TDD — tests FIRST (one per acceptance criterion), then implementation. Must run `pytest` and `ruff check` before completing.
7. **Stop. Present implementation to human for approval.** Do not proceed until approved.

### Phase 4: PR
8. Create PR linking to the issue.

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
