<!--
Sync Impact Report
- Version change: N/A -> 1.0.0
- Modified principles: Initial constitution adoption
- Added sections: Core Principles, Additional Constraints, Development Workflow, Governance
- Removed sections: None
- Follow-up TODOs: None
-->

# NSE IPO Monitoring & Deadline Alert System Constitution

## Core Principles

### I. Deterministic IPO Monitoring
The project MUST treat IPO schedule tracking as a deterministic, rule-driven system. Every company record, date calculation, and deadline alert MUST be based on explicit business rules, validated inputs, and consistent current-date evaluation. Ambiguous or missing values MUST not be silently converted into a valid status.

### II. Clean, Modular Architecture
The system MUST follow clean code principles and modular architecture. Python application logic MUST be separated from API routes, database operations, and persistence logic so that business rules remain intelligible, testable, and easy to maintain. Meaningful variable names, structured functions, and explicit error handling are mandatory.

### III. Technology Conformance
The project MUST implement application logic in Python, use FastAPI for backend services, and use SQLite for persistent data storage unless a documented constraint requires otherwise. API endpoints and data-access code MUST not mix business rules with persistence concerns, and database interactions MUST use parameterized queries to reduce injection risk and improve integrity.

### IV. Functional Correctness and Data Integrity
The system MUST support adding, viewing, updating, and deleting IPO records while enforcing required fields and valid date semantics. Each IPO MUST include a company name and valid opening and closing dates; closing dates MUST NOT be earlier than opening dates; allotment, refund, and listing dates are optional; duplicate records MUST be handled safely; status MUST be calculated from predefined date rules; and days remaining MUST be derived consistently using the current date.

### V. Evidence-Driven Quality Gates
The project MUST validate behavior with Pytest, lint with Ruff, and analyze security with Bandit. Tests MUST be derived from approved specifications and acceptance criteria, remain independent from generated application code, and never be deleted or weakened to obtain a passing result. Actual failures and their evidence MUST be preserved and fed back to the coding agent for repair before acceptance.

## Additional Constraints

The project MUST validate all user inputs, reject invalid date formats, prevent invalid date sequences, preserve existing records during updates, and handle missing or corrupted data safely. Historical IPO records MUST remain available unless explicitly deleted, and duplicate or inconsistent records MUST be handled in a way that preserves data integrity and user trust.

The system MUST enforce secure coding practices and must not expose passwords, API keys, or other credentials. User inputs MUST be validated and sanitized before processing, and no sensitive configuration files MUST be committed to the repository. All work MUST document known limitations and residual risks so that human reviewers can evaluate trade-offs before approving or rejecting the implementation.

## Development Workflow

The project MUST maintain a traceable workflow covering specification, implementation, validation, and review. Requirements, plans, task records, and harness logs MUST remain available throughout the project, and implementation decisions MUST be linked to approved requirements. A dedicated harness-log.md file MUST be maintained so that validation evidence, repair attempts, and final outcomes remain auditable.

All mandatory validation gates MUST run before acceptance. The workflow MUST record actual test failures and their evidence, preserve the initial and repaired implementations, rerun the same harness after repair, and never manipulate test results to obtain PASS. The automated validation layer is a support mechanism, not a substitute for engineering judgment.

## Governance

This constitution is the governing engineering standard for Part 1A of the NSE IPO Monitoring & Deadline Alert System. It supersedes informal practices that conflict with it, and all implementation decisions, reviews, and acceptance checks MUST align with its rules.

Amendments to this constitution require a documented rationale, a clear statement of the new governance requirement, and a human review before adoption. Any change that alters a principle, weakens a safety rule, or changes project-level expectations MUST include the impact on implementation, validation, and compliance review. The project MUST keep governance decisions explicit and traceable so that the standard remains enforceable.

Human accountability is mandatory: automated validation does not guarantee production readiness. A human reviewer MUST inspect the application, validation results, and known limitations before recording a final ACCEPT or REJECT decision. This principle ensures that correctness, risk, and operational judgment remain with the responsible people rather than solely with automated checks.

**Version**: 1.0.0 | **Ratified**: 2026-11-10 | **Last Amended**: 2026-11-10
