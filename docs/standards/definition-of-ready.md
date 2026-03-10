# Definition of Ready (DoR)

These are guidelines for effective backlog refinement, not a gate that blocks work. Use judgement. A story that mostly meets these criteria but has one open question can still be picked up — just address the question early.

## Checklist

### User Story Format
- [ ] Follows format: "As a [role], I want [feature] so that [benefit]"
- [ ] Role is a real person (e.g., data scientist, compliance officer), not "system", "developer", or generic "user"
- [ ] Benefit is clear business value
- [ ] Story delivers working, deployed functionality — no design-only or documentation-only stories

### Acceptance Criteria
- [ ] Each AC uses Given-When-Then format
- [ ] Each AC is testable (can write an automated test for it)
- [ ] Each AC is unambiguous (one interpretation only)
- [ ] Each AC is independent (can be verified separately)
- [ ] No implementation details in ACs (what, not how)
- [ ] Success and error scenarios covered

### INVEST Compliance
- [ ] **Independent** — can be developed and delivered without requiring other stories to be in progress simultaneously
- [ ] **Negotiable** — describes the what and why, not the how; implementation approach is open
- [ ] **Valuable** — delivers value to the end user, not just technical enablement
- [ ] **Estimable** — well-understood enough that the team can estimate effort
- [ ] **Small** — small enough to complete within reasonable time; no hidden complexity
- [ ] **Testable** — every AC has a clear pass/fail condition

### Dependencies
- [ ] Dependencies section exists
- [ ] Blocking issues identified (or "None" stated)
- [ ] Blocked-by issues are complete (status: done)

### Test Plan
- [ ] Brief test plan section exists describing how ACs will be verified
- [ ] Identifies which ACs can be tested automatically and which require manual verification

## Red Flags (Not Ready)

- Vague language: "user-friendly", "fast", "intuitive"
- Missing error handling: "system displays data" (what if no data?)
- Implementation in AC: "use pandas to..." (how, not what)
- Unbounded scope: "and other related metrics"
- Unknown dependencies: "may need to integrate with..."
- No test plan: story has no indication of how to verify it

## Example: Ready vs Not Ready

### Not Ready
```
As a user, I want to check fairness so I can use the system.

AC1: User can check fairness
AC2: System shows results
```

### Ready
```
As a data scientist evaluating model fairness,
I want to calculate demographic parity for my model's predictions
so that I can assess whether positive prediction rates are equitable across protected groups.

AC1: Given a dataset with binary predictions and two demographic groups,
     When I calculate the demographic parity metric,
     Then I receive the positive prediction rate for each group and the parity ratio
AC2: Given a dataset where one group has no positive predictions,
     When I calculate demographic parity,
     Then the metric handles this gracefully with rate = 0.0 and ratio = 0.0
```
