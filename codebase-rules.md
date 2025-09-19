# Codebase Rules

This document defines the required standards for any change made to this repository.  
All contributors — human or automated — must follow these rules.

## R1 — Work on a Branch (Never on Default)
All commits must target a non-default branch (`feature/<slug>`, `fix/<slug>`, `chore/<slug>`).  
Branches `main`, `master`, or `trunk` must remain stable and green at all times.

## R2 — No Debug/Temporary Artifacts
No debug or temporary files should be left in the repo.  
Forbidden patterns include `*.log`, `*.tmp`, `*.swp`, `debug_*`, `.DS_Store`, `__pycache__/`, coverage outputs, build artifacts, and distribution folders.

## R3 — CI Must Be Green
All CI jobs must pass before reporting success.  
If CI fails for reasons outside of code (e.g. infrastructure, missing secrets), report with a link to the failing step and stop.

## R4 — Zero Warnings Policy
Code and tests must pass with **zero** warnings.  
If a warning is intentional, it must be explicitly suppressed with a pragma/comment and a short justification.

- **Python:** `pytest -W error`; use `# noqa` / `# type: ignore[code]` with rationale.
- **JS/TS:** Linter/compiler warnings are treated as errors; use `// eslint-disable-next-line <rule>` with a justification.
- **C/C++:** Build with `-Wall -Wextra -Werror` (or `/W4 /WX` on MSVC).  
  Suppress only with `// NOLINT(reason)` or equivalent, and document why.

## R5 — Consistent Formatting
All code must be formatted with the project’s canonical tools before commit:

- **Python:** `ruff format` + `ruff check --fix`
- **JS/TS:** `biome check --write`
- **C/C++:** `clang-format -i` using the repo `.clang-format`, plus `clang-tidy` and/or `cppcheck` for static analysis

## R6 — Documentation for All Public APIs
Every public method, class, and data structure must have API documentation, including:

- Purpose and behavior  
- Parameters and return types  
- Side effects and errors  
- **Commented examples** of correct usage where possible

- **Python:** Google or NumPy style docstrings  
- **JS/TS:** JSDoc/TSDoc  
- **C/C++:** Doxygen-style comments

## R7 — Tests Are Required and Deterministic
Every change must include or update tests.  
Tests must be deterministic and run in under 10 minutes in CI.  
Flaky tests must be fixed, not ignored, unless an explicit reason is documented.

## R8 — Commit and PR Hygiene
Commits must follow [Conventional Commits](https://www.conventionalcommits.org).  
PR descriptions must include:

- Problem
- Approach
- Risks
- Validation (with coverage results before/after)
- Rollout notes

## R9 — Release Notes Must Be Updated
`RELEASE-NOTES.md` must be updated for every release branch or tag with version, date, highlights, breaking changes, and migration guidance.

## R10 — Coverage Requirements
- Capture coverage **before** and **after** work.  
- New/changed code must have **100% coverage**.  
- Overall project coverage must remain **≥ 80%**.  
- Coverage drops must block merge unless justified and approved.

## R11 — No “Fake” Mocks
Mocks must validate actual behavior, not just make a test pass.  
Each mock/stub must check call counts, argument shapes/values, and side effects.  
Favor realistic fakes over hollow mocks.

## Enforcement
Changes that violate these rules must be fixed or explicitly justified with comments and reviewed by a maintainer.  
Automated checks will block merges for formatting, linting, warnings, coverage, and release note compliance.
