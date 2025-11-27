# Contributing to SDLC_IDE

We welcome contributions to the SDLC_IDE project. To ensure a smooth and traceable workflow, we follow a Git-based process that maps directly to our project management style.

---

## 1. Kanban-to-Git Workflow Mapping

Our development process follows a Kanban-style flow, which is fully traceable in GitHub. Each stage of the process maps to a specific Git or GitHub entity.

| Kanban Column   | Git / GitHub Entity             | How to Use                                                                                                                                                 |
| --------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **To Do**       | Issue / Backlog                 | Create an **issue** for every task. Leave it **open** and assign a label like `To Do`. This is your “task pool.”                                           |
| **In Progress** | Feature branch / assigned issue | Developer creates a **branch** off `main` named after the issue, e.g. `feature/core-dag-scaffold`. Update the issue label to `In Progress`. |
| **Review**      | Pull Request                    | Once the branch is ready, open a **PR** targeting `main`. Label it `Review`. Assign reviewers. The PR represents the “in review” state.         |
| **Done**        | Merged PR / Closed Issue        | After PR merge: close the issue automatically and label it `Done`. The branch can be deleted.                                                    |

---

## 2. Recommended Git Workflow

Follow these steps to contribute code or documentation to the project.

### 1. Backlog / To Do
- **Create an Issue:** All work begins with a GitHub Issue. Describe the task, bug, or feature request in detail.
- **Assign Labels:** Use labels to categorize the issue. At a minimum, assign a status label (`To Do`) and a category label (`Core DAG`, `Mesh Layer`, `Governance/ADR`, etc.).

### 2. Start Work / In Progress
- **Create a Branch:** Checkout a new branch from `main` (or `develop`) for each issue. Use the naming convention below.
  ```bash
  git checkout -b <type>/<issue-id>-<short-description>
  ```
- **Reference the Issue:** As you work, reference the issue ID in your commit messages.
  ```bash
  git commit -m "CORE-1: Scaffold core DAG module"
  ```
- **Update Status:** Change the issue's label from `To Do` to `In Progress`.

### 3. Code Review / Review
- **Open a Pull Request:** When your work is complete, push your branch to the repository and open a Pull Request against the `main` branch.
- **Link the Issue:** In the PR description, use the `Closes #<issue-number>` keyword to link it to the original issue. This ensures the issue is automatically closed when the PR is merged.
- **Assign Reviewers and Labels:** Add the `Review` label to the PR and assign at least one reviewer.

### 4. Merge / Done
- **Merge:** Once the PR is approved, it will be merged into the `main` branch.
- **Automatic Cleanup:** The linked issue will be automatically closed and can be considered `Done`. The feature branch should be deleted after the merge to keep the repository clean.

---

## 3. Naming Conventions

To maintain consistency and traceability, please follow these naming conventions.

### Labels
- **Status:** `To Do`, `In Progress`, `Review`, `Done`
- **Category:** `Core DAG`, `Mesh Layer`, `Governance/ADR`, `Documentation`
- **Priority:** `High`, `Medium`, `Low`

### Branches
Use the format `<type>/<issue-id>-<short-description>`.

- **`type`:** `feature`, `fix`, `chore`, `docs`
- **`issue-id`:** The ID from the corresponding GitHub Issue (e.g., `CORE-1`, `MESH-2`).
- **`short-description`:** A few keywords describing the branch's purpose.

**Examples:**
```
feature/CORE-1-scaffold-dag
fix/MESH-2-api-bug
docs/DOC-1-readme-update
```

### Commit Messages
Start every commit message with the issue ID.

**Examples:**
```
CORE-1: Scaffold DAG module
MESH-2: Fix response validation in API
```
