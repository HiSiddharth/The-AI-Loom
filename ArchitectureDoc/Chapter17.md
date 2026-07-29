# AI Loom Architecture Specification

# Chapter 17 — Testing, Validation & Quality Assurance

**Version:** 1.0 Draft

---

# 17.1 Purpose

The Validation System ensures that AI Loom never considers work complete simply because an LLM says it is.

Every significant change must be validated using deterministic mechanisms whenever possible.

The system answers:

> **"How do we know this task is actually finished?"**

---

# 17.2 Philosophy

LLMs generate.

Validation verifies.

Trust should always be earned through evidence.

Validation should be:

* Deterministic
* Repeatable
* Explainable
* Fast
* Extensible

---

# 17.3 Validation Architecture

```text
                Worker

                   │

                   ▼

          Validation Pipeline

                   │

      ┌────────────┼────────────┐

      ▼            ▼            ▼

 Static      Runtime Tests   Reviewers

 Analysis

      ▼

 Validation Report

      ▼

 Planner
```

---

# 17.4 Validation Pipeline

Every completed task enters validation.

```text
Worker Finished

↓

Identify Validators

↓

Execute Validators

↓

Aggregate Results

↓

Compute Confidence

↓

Planner Review
```

Completion is not determined by the Worker.

---

# 17.5 Validator Types

AI Loom supports multiple validator categories.

```text
Compilation

Unit Tests

Integration Tests

Linting

Formatting

Static Analysis

Architecture Rules

Security

Performance

Custom Plugins
```

Validators execute independently.

---

# 17.6 Validation Levels

Every task declares its required validation level.

```text
MINIMAL

STANDARD

STRICT

PARANOID
```

Example:

Small documentation change:

```text
MINIMAL
```

Authentication refactor:

```text
STRICT
```

---

# 17.7 Validator Interface

Every validator implements:

```python
class Validator:

    discover()

    validate()

    supports()

    priority()
```

Validators are plugins.

---

# 17.8 Automatic Validator Discovery

Repository inspection determines available validators.

Examples:

Python

```text
pytest

ruff

black

mypy
```

Node

```text
eslint

prettier

vitest

jest

tsc
```

Rust

```text
cargo test

cargo fmt

clippy
```

Java

```text
mvn test

gradle test
```

---

# 17.9 Validation Order

Recommended execution order:

```text
Formatting

↓

Linting

↓

Compilation

↓

Static Analysis

↓

Unit Tests

↓

Integration Tests

↓

Reviewer Models
```

Cheap validators execute first.

---

# 17.10 Formatting

Formatting validators verify:

* Style
* Indentation
* Imports
* Line endings

Example:

```text
black

prettier

rustfmt

gofmt
```

Formatting failures should usually be auto-fixable.

---

# 17.11 Linting

Examples:

```text
ruff

eslint

flake8

clippy
```

Warnings and errors remain distinct.

---

# 17.12 Compilation

Compiled languages:

```text
javac

cargo build

go build

dotnet build
```

Compilation failures stop validation.

---

# 17.13 Static Analysis

Examples:

```text
mypy

pyright

spotbugs

pylint

clang-tidy
```

Static analysis improves confidence without executing code.

---

# 17.14 Unit Testing

Preferred strategy:

Only run tests affected by changed files.

Example:

```text
Changed File

↓

Test Mapper

↓

Affected Tests

↓

Execute
```

Avoid running the full suite unnecessarily.

---

# 17.15 Integration Testing

Integration tests execute only when:

* Public APIs changed
* Database schema changed
* Configuration changed
* Requested explicitly

---

# 17.16 Incremental Validation

Example:

```text
Edit auth.py

↓

Compile auth.py

↓

Run auth tests

↓

Skip frontend tests
```

Validation scope should match change scope.

---

# 17.17 Validation Report

Every validator returns:

```text
ValidatorResult

Name

Status

Duration

Diagnostics

Confidence

Files Tested
```

---

# 17.18 Status Values

```text
PASSED

FAILED

WARNING

SKIPPED

NOT_APPLICABLE
```

---

# 17.19 Confidence Calculation

Confidence combines:

* Validator success
* Worker confidence
* Planner review
* Historical reliability

Example:

| Signal          | Weight |
| --------------- | -----: |
| Compilation     |     40 |
| Tests           |     30 |
| Static Analysis |     20 |
| Worker          |      5 |
| Reviewer        |      5 |

Deterministic evidence outweighs LLM opinion.

---

# 17.20 Failure Handling

If validation fails:

```text
Validation Failed

↓

Return Diagnostics

↓

Worker Retry

↓

Revalidate
```

Planner intervenes only after retry limits.

---

# 17.21 Reviewer Models

After deterministic validation:

```text
Code

↓

Reviewer Model

↓

Issues

↓

Planner
```

Reviewer checks:

* Maintainability
* Readability
* Architecture
* Best practices

Reviewer never replaces tests.

---

# 17.22 Architecture Validation

Future validators may verify:

```text
Layer Boundaries

Dependency Rules

Naming Rules

Folder Structure

API Conventions
```

Useful for enterprise repositories.

---

# 17.23 Security Validation

Examples:

```text
Secret Detection

Unsafe APIs

Dependency Audit

SQL Injection

XSS

Path Traversal
```

Security validators may be language-specific.

---

# 17.24 Performance Validation

Optional validators:

```text
Benchmarks

Memory Usage

Algorithm Complexity

Regression Detection
```

Useful for optimisation tasks.

---

# 17.25 Regression Detection

Compare before and after.

Example:

```text
Old Tests

↓

New Tests

↓

Performance Delta

↓

Regression?
```

Large regressions reduce confidence.

---

# 17.26 Validation Policies

Example:

Development

```yaml
validation:

  compile: true

  tests: affected

  reviewer: true
```

CI

```yaml
validation:

  compile: true

  tests: all

  reviewer: true

  security: true
```

---

# 17.27 Parallel Validation

Independent validators execute concurrently.

```text
Compile

Lint

Tests

Security

↓

Merge Results
```

Reduces total validation time.

---

# 17.28 Validation Caching

Successful validator outputs may be reused.

Example:

```text
No Code Change

↓

Reuse Previous Lint Result
```

Avoid repeated work.

---

# 17.29 Extensibility

New validators require:

1. Validator implementation.
2. Registration.
3. Capability declaration.
4. Tests.

Planner requires no modification.

---

# 17.30 Metrics

Track:

```text
Validation Time

Failure Rate

Retry Count

Test Coverage

Average Confidence

Pass Rate
```

Useful for optimisation.

---

# 17.31 Design Constraints

1. Validation is mandatory before task completion.
2. Deterministic validators take precedence over LLM reviewers.
3. Validators are independent plugins.
4. Validation is incremental where possible.
5. Validation results are machine-readable.
6. Confidence is evidence-based.
7. Failed validation blocks task completion.
8. Validation pipelines are configurable.
9. Validators are observable.
10. Every validation result is reproducible.

---

# Architect's Notes (Normative)

## 1. Never Let an LLM Mark Its Own Homework

A Worker must never declare:

> "The code works."

Instead, require evidence.

Good:

```text
✓ Compilation passed

✓ 14 affected tests passed

✓ Ruff found no errors

✓ Reviewer found no architectural issues
```

This is a foundational design principle.

---

## 2. Introduce Validation Profiles

Instead of selecting individual validators each time, define reusable profiles.

Example:

```yaml
profiles:

  quick:

    compile: true

    lint: true

  standard:

    compile: true

    lint: true

    tests: affected

  release:

    compile: true

    tests: all

    security: true

    reviewer: true
```

---

## 3. Make Validation Incremental

Your indexing engine already knows:

* Which symbols changed
* Which files changed
* Which tests map to those files

Exploit this.

Running the entire test suite after changing a comment is wasteful.

---

## 4. Build a Validation Graph

Instead of a linear pipeline:

```text
Compile

↓

Tests

↓

Reviewer
```

Represent validators as a dependency graph.

Example:

```text
Compile

↓

Unit Tests

↓

Integration Tests

↓

Reviewer
```

If compilation fails, downstream validators are skipped automatically.

---

## 5. AI Loom's Competitive Advantage

Most coding agents stop after producing code.

AI Loom should stop only after producing **verified** code.

This distinction is one of the strongest differentiators of the entire architecture.

A successful task is not:

> "The model generated code."

It is:

> "The system produced code that passed every required validator."

---
