# Demo Script: Claude Code Software Factory

**Target duration: 10-12 min**
**Feature: Equal Opportunity metric**

---

## Before Running Anything (1 min setup on projector)

1. **Show CLAUDE.md** — "This is the orchestrator's constitution. It defines the entire workflow, quality gates, and non-negotiables. Notice: demo mode — review loops removed for speed." (30 sec)
2. **Show python-developer.md** — "One agent definition. Lightweight — role + rules, not domain knowledge." (15 sec)
3. **Show fairness-metrics SKILL.md** — "Domain knowledge, auto-loaded when relevant. Reusable across projects." (15 sec)

---

## Beat 1: Issue Creation (~2 min)

```
@business-analyst Create a user story for adding an equal opportunity metric to the fairness checker. Equal opportunity measures whether true positive rates are equal across protected groups — it's a relaxation of equalized odds. The metric should support multiple groups, custom thresholds, handle edge cases like groups with no positive actuals, and integrate with the CLI.
```

**Narrate while it runs:**
- "Watch the skill auto-load — fairness-metrics injects domain knowledge"
- "GWT format, acceptance criteria, Definition of Ready compliance"
- Approve the issue when presented

---

## Beat 2: Feasibility + Design (~4 min)

```
@python-developer Pick up issue #N. Follow the full workflow from CLAUDE.md.
```

**Narrate while it runs:**
- "It reads the issue, assesses feasibility, asks blocking questions"
- "Design doc: approach, data models, test strategy"
- Answer any AskUserQuestion prompts quickly
- Approve the design when presented

---

## Beat 3: TDD Implementation — the crown jewel (~4 min)

**Narrate while it runs:**
- "Watch — tests FIRST. Every acceptance criterion maps to a test."
- Point out: tests fail (red), implementation written, tests pass (green)
- Point out: hook fires on bash commands (branch validation)
- "pytest and ruff check run automatically before completing"
- Approve the implementation when presented

---

## Beat 4: PR (~30 sec)

- "PR created, linking back to the issue. The human reviews polished output, not raw code."

---

## What to Say About What's NOT Shown

> "In production mode, this workflow includes two adversarial review loops — a fresh opus instance that tries to break the design, and another that tries to break the code. Those add about 20 minutes but catch real issues. I skipped them for the demo, but they're what I showed you in slides 7 and 12. The point is: CLAUDE.md is tunable."

---

## Fallback Plan

If the demo stalls or runs long:
- Have completed `feature/3-add-demographic-parity` branch ready
- `git diff main...feature/3-add-demographic-parity` — show generated code
- `pytest tests/ -v` on that branch — show test output
- "Here's what the finished product looks like"

---

## Timing Targets

| Beat | Target | Cumulative |
|------|--------|------------|
| Setup | 1 min | 1 min |
| Issue creation | 2 min | 3 min |
| Feasibility + Design | 4 min | 7 min |
| TDD Implementation | 4 min | 11 min |
| PR + wrap | 1 min | 12 min |
