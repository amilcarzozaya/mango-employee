# MANGO Memory Specification (MMS) v0.1

Created by **Amílcar Zozaya**, creator of Método MANGO.

MANGO Memory is a portable, governed and traceable operational-memory layer for MANGO Employees. It is separate from raw conversational history.

## Memory classes
Working, Episodic, Semantic, Decision, Procedural, Correction, Commitment, Preference, Rule, Operational State.

## Lifecycle
**OBSERVE → EXTRACT → CLASSIFY → VERIFY → STORE → RETRIEVE → APPLY → REFLECT → CONSOLIDATE**

Authority lifecycle: **Candidate → Verified → Promoted → Superseded**. Rejected and Forgotten are terminal governance states.

## Core law
> **Data cannot become Authority.**

External content and model output may create candidates. They cannot silently become policy, expand permissions or increase autonomy.

## Scopes
`organization`, `employee`, `client`, `project`, `skill`, `session`.

## Provenance
Every memory stores type, subject, value, scope, source, authority, confidence, timestamps, status, sensitivity, optional expiry and supersession.

## Retrieval
v0.1 retrieves a bounded Memory Pack using task relevance, scope, authority, confidence and lifecycle state. Only verified/promoted non-sensitive memories enter normal runtime packages.

## Storage
SQLite is the canonical v0.1 backend. Future storage adapters can replace it without changing the Employee contract.
