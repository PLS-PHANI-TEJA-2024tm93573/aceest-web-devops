# 🚀 CI/CD Pipeline Overview

This document visualizes the complete CI/CD flow involving:

- GitHub Actions
- Jenkins Pipeline
- Docker build & push logic
- Branch vs Tag-based triggers

---

## 🔁 Pipeline Flow

```mermaid
flowchart TD

    %% ---------------------------
    %% TRIGGERS
    %% ---------------------------
    A[GitHub Push] --> B{Trigger Type}

    B -->|main / release/* / feature-*| C[GitHub Actions Pipeline]
    B -->|tag v*.*.*| T[Tag Trigger]

    B -->|Pull Request to main| C

    %% ---------------------------
    %% GITHUB ACTIONS PIPELINE
    %% ---------------------------
    subgraph GHA [GitHub Actions]
        C --> D[Build & Lint]
        D --> E[Docker Build]
        E --> F[Automated Testing]
        F --> G[Trigger Jenkins]
    end

    %% ---------------------------
    %% JENKINS PIPELINE
    %% ---------------------------
    subgraph JENKINS [Jenkins Pipeline]
        G --> H[Checkout Repo]
        H --> I[Setup Python Env]
        I --> J[Lint Check]
        J --> K[Build Validation]
        K --> L[Build Docker Image]
        L --> M[Build Test Image]
        M --> N[Run Tests]

        N --> O{Branch is main?}
        O -->|Yes| P[Push Docker Image: dev-latest]
        O -->|No| Q[Skip Push]
    end

    %% ---------------------------
    %% TAG FLOW (AFTER JENKINS SUCCESS)
    %% ---------------------------
    T --> R[Wait for Jenkins Success]
    R --> S[Build Docker Image with Tag]
    S --> U[Push Docker Image with Tag]

    %% ---------------------------
    %% CONDITIONS
    %% ---------------------------
    style P fill:#d4fcd4,stroke:#333
    style U fill:#d4fcd4,stroke:#333
    style Q fill:#fcd4d4,stroke:#333
```

---

## 📌 Key Behaviors

### 🔹 GitHub Actions Triggers
- Runs on:
  - `main`
  - `release/*`
  - `feature-*`
  - Pull Requests → `main`
  - Tags → `v*.*.*`

---

### 🔹 Jenkins Trigger
- Triggered **only after GitHub Actions succeeds**
- Uses branch name:
  ```
  ${{ github.head_ref || github.ref_name }}
  ```

---

### 🔹 Docker Push Logic

#### ✅ Jenkins Push (DEV)
- Condition: **branch = `main`**
- Tag:
  ```
  dev-latest
  ```

---

#### ✅ GitHub Actions Push (RELEASE)
- Condition: **Git tag (v*.*.*)**
- Tag:
  ```
  <git-tag>
  ```

---

### 🔥 Summary

| Pipeline         | Trigger Condition       | Docker Tag     | Purpose        |
|-----------------|------------------------|----------------|----------------|
| GitHub Actions  | Branch / PR / Tag      | (build only)   | CI validation  |
| Jenkins         | After GHA success      | dev-latest     | Dev deployment |
| GitHub Actions  | Tag (v*.*.*)           | version tag    | Release build  |

---

## 🧠 Architecture Insight

- **GitHub Actions = CI Orchestrator**
- **Jenkins = Deep validation + controlled deploy**
- **Tags = Release gate**
- **Main branch = Dev deployment**

---
