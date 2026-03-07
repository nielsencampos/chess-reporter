# STACK.md

This document describes the technology stack used in the **chess-reporter** project and the role of each component in the system.

The goal of this document is to clarify how the system is built, which tools are used, and why they were selected.

---

# Core Language

## Python

Python is the primary programming language used in this project.

It is responsible for:

- PGN parsing
- interaction with the chess engine
- position evaluation processing
- report generation
- CLI and API logic

The recommended version is **Python 3.12+**.

---

# Chess Processing

## python-chess

`python-chess` is the core library used to interact with chess structures.

It provides:

- PGN parsing
- board representation
- legal move generation
- interaction with UCI engines (such as Stockfish)

This library acts as the foundation for game parsing and engine interaction.

---

# Chess Engine

## Stockfish

Stockfish is the chess engine used to evaluate positions.

The engine provides:

- centipawn evaluations
- mate detection
- principal variation analysis
- move ranking

Stockfish is accessed through the `python-chess` engine interface.

---

# Storage

## DuckDB

DuckDB is used as the primary storage engine for the project.

It allows efficient storage and querying of:

- analyzed games
- move evaluations
- player statistics
- generated reports

DuckDB was chosen because it:

- runs embedded (no server required)
- integrates well with Python
- provides fast querying capabilities
- supports Parquet and structured queries

---

# Dependency Management

## uv

`uv` is used to manage project dependencies and Python environments.

It replaces traditional tooling such as:

- pip
- virtualenv
- pip-tools

`uv` allows:

- dependency installation
- environment synchronization
- reproducible development environments

---

# Code Quality

## Ruff

Ruff is used for linting and formatting the codebase.

It performs static analysis to detect:

- style violations
- unused imports
- potential bugs
- inconsistent formatting

Ruff can also automatically format code according to the configured rules.

---

# Testing

## pytest

`pytest` is the framework used for automated testing.

Tests verify that:

- PGN parsing works correctly
- engine evaluation logic behaves as expected
- reports are generated correctly
- edge cases are handled properly

Tests are located in the `tests/` directory.

---

# Type Checking

## Pyright

Pyright is used for static type checking.

Type checking ensures that functions and modules use compatible types and helps detect bugs earlier during development.

---

# Git Hooks

## pre-commit

`pre-commit` is used to run automated checks before code is committed.

Typical checks include:

- Ruff linting
- code formatting
- additional validation rules

This ensures that only valid code enters the repository.

---

# Continuous Integration

## GitHub Actions

GitHub Actions provides the Continuous Integration (CI) pipeline for the project.

The CI pipeline automatically runs when code is pushed or pull requests are opened.

Typical CI tasks include:

- installing dependencies
- running lint checks
- executing tests
- performing type checking

---

# Containerization

## Docker

Docker is used to package the application and its dependencies into a container.

Containerization allows the project to run consistently across environments and simplifies deployment.

---

# Orchestration

## Kubernetes

Kubernetes may be used to orchestrate containers in a production environment.

Possible responsibilities include:

- service orchestration
- scaling workloads
- managing container deployments
- handling service discovery
- managing configuration and secrets

Kubernetes is optional for local development but can be used for production deployments.

---

# Development Environment

## Visual Studio Code

Visual Studio Code is the recommended development environment.

It provides integration with:

- Python tooling
- debugging
- Git
- linting and formatting tools
- testing frameworks

---

# AI Development Assistants

## Claude / ChatGPT

AI tools may be used to assist during development.

They can help with:

- generating code
- refactoring
- explaining logic
- generating tests
- improving architecture

Generated code should always be reviewed before being merged.

---

# Summary

The main technologies used in this project include:

- Python
- python-chess
- Stockfish
- DuckDB
- uv
- Ruff
- pytest
- Pyright
- pre-commit
- GitHub Actions
- Docker
- Kubernetes