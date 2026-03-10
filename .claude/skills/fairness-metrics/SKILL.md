---
description: MANDATORY when working on fairness metrics, bias analysis, or creating issues involving fairness concepts. Covers demographic parity, equalized odds, equal opportunity, predictive parity, and calibration — definitions, formulas, thresholds, and caveats.
---

# Fairness Metrics — Domain Knowledge

## Overview

Algorithmic fairness evaluates whether an ML model's predictions treat different demographic groups equitably. A "protected attribute" (race, gender, age, disability, etc.) defines the groups. Fairness metrics quantify disparities in model behavior across these groups.

## Key Metrics

### Demographic Parity (Statistical Parity)

**Definition**: P(Y_hat=1 | A=a) = P(Y_hat=1 | A=b) for all groups a, b.

The proportion of positive predictions should be equal across protected groups regardless of the true outcome.

**Ratio version**: min(P(Y_hat=1 | A=a) / P(Y_hat=1 | A=b)) >= threshold (typically 0.8, the "four-fifths rule").

**When to use**: When equal selection rates matter more than predictive accuracy (e.g., hiring, lending).

### Equalized Odds

**Definition**: P(Y_hat=1 | Y=y, A=a) = P(Y_hat=1 | Y=y, A=b) for y in {0, 1}.

Both the true positive rate (TPR) and false positive rate (FPR) should be equal across groups.

**When to use**: When both types of errors matter equally across groups (e.g., criminal recidivism prediction).

### Equal Opportunity

**Definition**: P(Y_hat=1 | Y=1, A=a) = P(Y_hat=1 | Y=1, A=b).

A relaxation of equalized odds — only requires equal true positive rates across groups.

**When to use**: When you primarily care that qualified individuals are treated equally (e.g., loan approval for creditworthy applicants).

### Predictive Parity

**Definition**: P(Y=1 | Y_hat=1, A=a) = P(Y=1 | Y_hat=1, A=b).

Precision (positive predictive value) should be equal across groups.

**When to use**: When the cost of a false positive is high and should be borne equally (e.g., medical screening).

### Calibration

**Definition**: P(Y=1 | S=s, A=a) = P(Y=1 | S=s, A=b).

For a given predicted probability score s, actual outcomes should be equal across groups.

**When to use**: When predicted probabilities are used for decision-making and must be trustworthy for all groups.

## Common Thresholds

- **Four-fifths (80%) rule**: A selection rate for any group below 80% of the highest group's rate indicates adverse impact. Widely used in US employment law (EEOC Uniform Guidelines).
- **Statistical significance tests**: Chi-squared test or Fisher's exact test to determine if observed disparities are statistically significant vs. random variation.

## Important Caveats

### Impossibility Theorem

It is mathematically impossible to simultaneously satisfy demographic parity, equalized odds, and calibration — except in trivial cases (perfect prediction or equal base rates). This means **every fairness intervention involves trade-offs**.

### Context Matters

The choice of metric depends on the domain, legal requirements, and values of stakeholders. There is no single "correct" fairness metric.

### Protected Attributes

Common protected attributes include: race, gender, age, disability, religion, national origin, sexual orientation. The relevant attributes depend on jurisdiction and application domain.

## Data Requirements

To compute fairness metrics, you need:

- **Predictions**: Binary (0/1) classification outputs, or probabilistic scores
- **Actual outcomes**: Ground truth labels (required for equalized odds, equal opportunity, predictive parity, calibration)
- **Protected attribute labels**: Group membership for each individual

**Expected DataFrame format**: One row per individual, with columns for predictions, actuals, and group membership.
