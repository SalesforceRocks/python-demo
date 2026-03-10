# Demo Prompts

## Dry Run (Demographic Parity)

### Step 1: BA Agent creates the issue

```
@business-analyst Create a user story for adding a demographic parity metric to the fairness checker. Demographic parity measures whether the proportion of positive predictions is equal across protected groups, regardless of actual outcomes. It's also known as the "four-fifths rule" in US employment law. The metric should support multiple groups, custom thresholds, handle edge cases, and integrate with the CLI.
```

### Step 2: Developer picks up the issue

```
@python-developer Pick up issue #N. Follow the full workflow from CLAUDE.md.
```

---

## Live Demo (Equal Opportunity)

### Step 1: BA Agent creates the issue

```
@business-analyst Create a user story for adding an equal opportunity metric to the fairness checker. Equal opportunity measures whether true positive rates are equal across protected groups — it's a relaxation of equalized odds. The metric should support multiple groups, custom thresholds, handle edge cases like groups with no positive actuals, and integrate with the CLI.
```

### Step 2: Developer picks up the issue

```
@python-developer Pick up issue #N. Follow the full workflow from CLAUDE.md.
```
