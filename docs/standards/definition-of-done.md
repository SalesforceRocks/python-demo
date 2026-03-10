# Definition of Done (DoD)

Done is binary. Work is either done or not done. There is no "mostly done" or "done except for."

## All Stories

- [ ] Story met Definition of Ready guidelines at time of planning
- [ ] All acceptance criteria met
- [ ] Every acceptance criterion has at least one automated test
- [ ] Changes approved by user
- [ ] Changes committed and pushed to feature branch
- [ ] PR created linking to issue
- [ ] All PR review comments processed

## Build Stories (Code)

### Testing

- [ ] All tests pass and are idempotent (can be run repeatedly with same results)
- [ ] Code coverage >= 85%
- [ ] Success + error paths tested
- [ ] Edge cases tested (empty data, zero values, missing groups)
- [ ] No regressions — existing tests still pass

### Code Documentation

- [ ] All public functions have docstrings
- [ ] Complex business logic has inline comments explaining the why (not the what)

### Static Code Analysis

- [ ] ruff check passes with no errors
- [ ] Type hints on all public function signatures

### Quality — Python

- [ ] Follows project patterns (pydantic models, click CLI)
- [ ] No hardcoded values — use parameters with sensible defaults
- [ ] Uses existing models from `models.py` where applicable
- [ ] Domain knowledge loaded from skills where applicable

### Security

- [ ] No sensitive data in logs or error messages
- [ ] Input validation on public interfaces (CLI, public functions)

### Documentation

- [ ] README updated if user-facing behavior changed
- [ ] No TBD/TODO markers (GitHub issues created instead)

### Review

- [ ] Reviewed by fresh adversarial review instance (automated loop)
- [ ] All blocking issues from review resolved
