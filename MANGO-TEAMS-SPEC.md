# MANGO Teams & Handoffs Specification (MTHS) v0.1

Created by **Amílcar Zozaya**, creator of Método MANGO.

**ASSIGN → DELEGATE → CONTRACT → ACCEPT → EXECUTE → TRACE → RETURN/COMPLETE**

A Handoff Contract binds sender, recipient, Team, Skill, exact task, deliverable, acceptance criteria, context references, allowed memory scopes and linked Runs. Delegation never expands authority. Shared-memory scopes must be explicitly allowed. Self-delegation and active circular delegation are forbidden. Acceptance creates a linked child Run.

**Delegated Authority = Sender Authority ∩ Recipient Authority ∩ Handoff Scope ∩ Employee Policy ∩ Gates**
