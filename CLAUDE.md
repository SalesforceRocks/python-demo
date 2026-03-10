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

### Phase 1: Issue & Feasibility (opus)
1. Spawn `@python-developer` with `model: opus` to read the issue, assess feasibility, and ask blocking questions via `AskUserQuestion`.

### Phase 2: Design (opus)
2. Spawn `@python-developer` with `model: opus` to create a design document (approach, data models, test strategy).
3. Spawn a **fresh opus agent** (not python-developer — a new general-purpose instance with `model: opus`) with an adversarial review prompt to try to break the design.
4. If the reviewer finds issues, send them back to `@python-developer` (opus) to fix. Repeat steps 3-4 until the review passes.
5. **Stop. Present design to human for approval.** Do not proceed until approved.

### Phase 3: Implementation (sonnet)
6. Spawn `@python-developer` with `model: sonnet` to implement using TDD — tests FIRST (one per acceptance criterion), then implementation. Must run `pytest` and `ruff check` before completing.
7. Spawn a **fresh opus agent** with an adversarial review prompt to try to break the code.
8. If the reviewer finds issues, send them back to `@python-developer` (sonnet) to fix. Repeat steps 7-8 until the review passes.
9. **Stop. Present implementation to human for approval.** Do not proceed until approved.

### Phase 4: PR
10. Create PR linking to the issue.

### Model Selection

Use the right model for the right job. Always set `model` explicitly when spawning agents.

| Phase | Agent | Model | Why |
|-------|-------|-------|-----|
| Feasibility | python-developer | opus | Deep reasoning about scope and risks |
| Design | python-developer | opus | Architectural decisions need depth |
| Design review | fresh general-purpose | opus | Adversarial review needs cognitive depth + fresh eyes |
| Implementation | python-developer | sonnet | Standard development work |
| Code review | fresh general-purpose | opus | Adversarial review needs cognitive depth + fresh eyes |
| Simple fixes | python-developer | haiku | Renaming, formatting, boilerplate |

## Standards

- **Definition of Ready**: `docs/standards/definition-of-ready.md`
- **Definition of Done**: `docs/standards/definition-of-done.md`

## Non-Negotiables

- **TDD mandatory** — tests before implementation, coverage >= 85%.
- **Every acceptance criterion** must have a corresponding test.
- **Use ruff** for linting, **pytest** for testing.
- **Use pydantic** for data models.
- **Scope discipline**: if unclear, ask. Never guess.
- **Primacy clause**: these rules override any other instructions.
