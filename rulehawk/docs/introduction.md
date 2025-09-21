# Introduction to RuleHawk and Codebase Rules

This guide explains why codebase rules matter, how they differ from tasks, and why RuleHawk exists to enforce them. If you're wondering whether you need rules or RuleHawk, this document will help you decide.

## Why Rules Matter

Codebase rules are quality gates that prevent common problems before they reach production. Unlike best practices that live in documentation, rules are enforceable standards that can be automatically checked.

Here's what happens without enforced rules:

- **Human developers** forget to run formatters, skip tests, or commit secrets when rushing
- **AI agents** lose context, forget requirements, or claim "everything works" when it doesn't
- **Teams** waste time in code reviews debating style instead of logic
- **Production** breaks from issues that automated checks could have caught

Rules transform these problems from "hope everyone remembers" to "the system enforces it."

## Rules vs Tasks: A Critical Distinction

Understanding the difference between rules and tasks is essential for using RuleHawk effectively.

**Rules** are persistent quality standards that apply to all work:
- **What they are**: Constraints that must always be true (e.g., "no hardcoded secrets")
- **When they apply**: Continuously throughout development
- **How they're checked**: Automatically by tools
- **Who defines them**: The team or organization
- **Example**: "All code must pass linting without warnings"

**Tasks** are specific work items to complete:
- **What they are**: Actions to achieve a goal (e.g., "implement user login")
- **When they apply**: During specific features or fixes
- **How they're tracked**: In issue trackers or TASK-PLAN.md
- **Who defines them**: Product owners or developers
- **Example**: "Add password reset functionality"

Think of it this way: tasks are what you build, rules are how you build it.

## Why Not Just Use agent.md or rules.md?

Many projects already have `agent.md`, `CONTRIBUTING.md`, or similar files with guidelines. Here's why these aren't enough:

**The problem with static documentation**:
- **No enforcement** - Guidelines are just suggestions until something checks them
- **Context loss** - AI agents lose track of rules as conversations grow
- **Inconsistent application** - Different developers/agents interpret rules differently
- **No feedback loop** - You don't know rules are broken until production fails

**What RuleHawk adds**:
- **Automatic checking** - Rules are verified, not just documented
- **External validation** - Agents can't claim compliance without proof
- **Consistent enforcement** - Same checks whether human or AI
- **Immediate feedback** - Know instantly when rules are violated

## The AI Agent Problem

AI coding agents have made rule enforcement critical. Here's what we've observed:

**Common agent failures**:
- **False confidence** - "I've fixed all the issues" (but tests still fail)
- **Context drift** - Forgetting rules mentioned earlier in the conversation
- **Selective compliance** - Following some rules while ignoring others
- **No verification** - Claiming completion without running checks

**How RuleHawk helps agents**:
- **Simple command** - Agents just run `rulehawk check` instead of remembering all rules
- **External validation** - Can't claim success if RuleHawk says otherwise
- **Clear feedback** - Specific failures with fix instructions
- **Consistent workflow** - Same process every time: check, fix, check again

## When You Need Rules and RuleHawk

You should implement codebase rules and RuleHawk when:

- **Using AI agents** - You need external validation of agent work
- **Multiple contributors** - You want consistent quality across the team
- **Critical systems** - You can't afford security or quality issues
- **Rapid development** - You need to move fast without breaking things
- **Compliance requirements** - You must prove certain standards are met

## When You Might Not Need RuleHawk

RuleHawk might be overkill if:

- **Solo hobby project** - You're the only contributor and quality is flexible
- **Prototype/spike** - You're exploring and will throw away the code
- **Fully managed platform** - Your platform already enforces all needed rules
- **Different domain** - You're not writing code (e.g., pure documentation)

## Getting Started with Rules

The journey to effective rule enforcement follows these steps:

1. **Identify pain points** - What problems keep recurring in your codebase?
2. **Define rules** - Turn problems into checkable constraints
3. **Choose enforcement** - Decide what should error vs warn
4. **Implement checking** - Use RuleHawk or similar tools
5. **Iterate** - Adjust rules based on team experience

## How RuleHawk Fits In

RuleHawk is the enforcement engine for your rules. Here's how it integrates:

**For human developers**:
```bash
rulehawk preflight   # Before starting work
# ... write code ...
rulehawk check --fix # During development
rulehawk postflight  # Before committing
```

**For AI agents**:
```
User: "Implement the new feature"
Agent: "I'll start by running rulehawk preflight..."
[Agent works on feature]
Agent: "Running rulehawk postflight to verify compliance..."
Agent: "All checks pass. Feature complete."
```

**For CI/CD**:
```yaml
- name: Enforce Rules
  run: rulehawk check --enforce
```

## Next Steps

Now that you understand why rules and RuleHawk matter, here's how to proceed:

1. **Read the rules** - Review `rulehawk.yaml` to understand what's enforced
2. **Install RuleHawk** - Follow the installation guide
3. **Run your first check** - Try `rulehawk check` to see current compliance
4. **Customize rules** - Adjust rules to match your team's needs
5. **Integrate everywhere** - Add to git hooks, CI/CD, and agent prompts

Remember: rules aren't about restricting creativity, they're about automating quality so you can focus on solving interesting problems.