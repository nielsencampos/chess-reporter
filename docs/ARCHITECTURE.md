# ARCHITECTURE.md

This document describes the high-level architecture of the **chess-reporter** system.

The purpose of this document is to explain how the main components interact to parse chess games, evaluate positions, and generate structured reports.

---

# System Overview

The system processes chess games stored in PGN files, evaluates each position using a chess engine, and generates reports based on the resulting evaluations.

High-level flow:

PGN File  
↓  
PGN Parser  
↓  
Engine Analysis  
↓  
Evaluation Processing  
↓  
Storage  
↓  
Report Generation

Each stage is responsible for a specific transformation of the game.

---

# Main Components

## PGN Parser

The PGN parser reads chess games from PGN files and converts them into structured game objects.

Responsibilities:

- read PGN files
- extract game metadata
- reconstruct move sequences
- generate board states

The parser is implemented using the **python-chess** library.

Output:

A structured representation of a chess game including moves and positions.

---

## Engine Analysis

The engine analysis module evaluates each position of the game using a chess engine.

Responsibilities:

- initialize the engine (Stockfish)
- analyze board positions
- retrieve evaluation scores
- detect mate positions
- capture principal variation lines

Output:

Position evaluations for each move in the game.

---

## Evaluation Processing

The evaluation processing module converts raw engine evaluations into meaningful information.

Responsibilities:

- detect inaccuracies
- detect mistakes
- detect blunders
- calculate evaluation deltas
- track evaluation progression during the game

Output:

Processed evaluation metrics associated with each move.

---

## Storage

The storage layer persists analyzed games and evaluation results.

Responsibilities:

- store game metadata
- store move-by-move evaluations
- store processed evaluation metrics
- enable querying of analyzed games

DuckDB is used as the embedded storage engine.

---

## Report Generation

The reporting module generates structured summaries of analyzed games.

Reports may include:

- move accuracy metrics
- evaluation progression
- mistake and blunder detection
- player performance summaries

Reports may be exported in formats such as:

- JSON
- CSV
- structured tables

---

# System Layers

The architecture can be divided into the following layers.

## Input Layer

Responsible for ingesting chess games.

Components:

- PGN file reader
- PGN parser

---

## Analysis Layer

Responsible for evaluating chess positions.

Components:

- engine integration
- position analysis
- evaluation processing

---

## Storage Layer

Responsible for storing analyzed game data and evaluation results.

Components:

- DuckDB database
- structured evaluation records

---

## Reporting Layer

Responsible for producing reports and summaries.

Components:

- report generation
- export formats

---

# Execution Modes

The system may operate in multiple modes.

## CLI Mode

The project can be used as a command-line tool.

Example usage:

`chess-reporter analyze game.pgn`

This mode processes PGN files and generates reports locally.

---

## Library Mode

The project can also be used as a Python library.

Example usage:

`from chess_reporter import analyze_game`

This allows integration into other Python applications.

---

# Future Extensions

Possible future extensions include:

- API interface for remote analysis
- distributed engine analysis workers
- Kubernetes-based deployment
- infrastructure provisioning with Terraform
- batch processing of large PGN collections

These features may be introduced as the project evolves.

---

# Architectural Goals

The system is designed with the following goals:

- modular architecture
- clear separation of responsibilities
- easy extensibility
- reproducible analysis results
- simple local execution
