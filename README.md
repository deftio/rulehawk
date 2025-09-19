# Codebase Standards — Why They Exist

This repository enforces a strict set of development rules (see [`codebase-rules.md`](./codebase-rules.md)) to ensure that every change is:

- **Safe** — won’t break production or degrade user experience  
- **Maintainable** — easy for future developers to understand and extend  
- **Consistent** — uses a single, unified style across all languages and modules  
- **High-quality** — tested, documented, and warning-free

These rules are not about slowing you down — they are about reducing rework, surprises, and firefighting later.  
They make sure that every contributor (human or automated) leaves the codebase better than they found it.

## Goals

### 1. Prevent Production Breakages
Working on a branch, requiring green CI, and blocking on warnings ensures the main branch always deploys safely.

### 2. Keep the Codebase Clean
Formatting, linting, and banning debug artifacts keep the repo consistent, readable, and free of clutter.

### 3. Future-Proof the Code
API docs with examples, meaningful commit messages, and updated release notes help new developers understand why code exists and how to use it — months or years from now.

### 4. Build Confidence Through Tests
Deterministic tests with strict coverage thresholds mean every merge is backed by real, automated verification — not guesswork.

### 5. Encourage Honest Testing
Rejecting “fake” mocks forces contributors to write tests that actually validate logic, not just turn CI green.

## Philosophy

A good codebase is like a well-kept lab notebook:  
anyone should be able to open it, see what was changed, why it was changed, how it was validated, and what the current state is — without guessing.

These rules turn that philosophy into a checklist the entire team (and coding agents) can follow.

## TL;DR
If you follow these rules, you get:

- Predictable builds and deployments  
- Cleaner diffs and fewer style debates  
- Faster onboarding for new contributors  
- Fewer regressions and late-night fire drills  
- A codebase that scales with the team

> **Tip:** If you ever find yourself thinking “this is overkill,” document why and open a PR to discuss relaxing the rule.  
> The rules are meant to protect the project, not block progress — but any exception must be deliberate, reviewed, and recorded.
