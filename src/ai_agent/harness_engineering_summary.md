# Harness Engineering 重點整理（工程師版）

## 一句話總結

**Agent = Model + Harness**

未來 AI
系統的能力，不只取決於模型，而是你如何設計整個外部控制系統（Harness）。

------------------------------------------------------------------------

## 1. 什麼是 Harness？

**Harness = 控制 AI 做事的整個外部系統**

包含：

-   Prompt / System Prompt
-   Tools / MCP / CLI
-   Workflow / Orchestrator
-   Tests / CI/CD
-   Logs / Monitoring
-   Policies / Guardrails
-   Memory / Dataset
-   Evaluation / Retry logic

------------------------------------------------------------------------

## 2. 核心架構

    Agent = Model + Harness

而不是：

    Agent = Model

------------------------------------------------------------------------

## 3. Harness 的兩個核心元件

### 3.1 Guides（前饋 / Feedforward）

告訴 Agent：

> 你應該怎麼做

例如：

-   system prompt
-   coding standards
-   architecture docs
-   CLAUDE.md / AGENTS.md
-   spec / design doc
-   examples

------------------------------------------------------------------------

### 3.2 Sensors（回饋 / Feedback）

告訴 Agent：

> 你做得對不對

例如：

-   unit test
-   compile result
-   runtime log
-   lint result
-   benchmark
-   monitoring metrics
-   screenshot / UI test

------------------------------------------------------------------------

## 4. 控制循環（Harness Engineering 核心）

    Guide → Agent → Sensor → Adjust → repeat

等同：

    plan
    run
    measure
    fix
    loop

本質：

**Feedback Control System**

------------------------------------------------------------------------

## 5. Sensors 的兩種類型

### 5.5 Computational（確定性）

由程式算出來：

例如：

    exit code = 0
    tests passed
    coverage 92%
    build success

特性：

-   deterministic
-   reliable
-   repeatable

------------------------------------------------------------------------

### 5.2 Inferential（推論型）

由 LLM 判斷：

例如：

-   code review
-   log root cause analysis
-   UI screenshot analysis
-   architecture evaluation

特性：

-   probabilistic
-   approximate
-   flexible

------------------------------------------------------------------------

## 6. Harness 的三層架構（業界現況）

### Layer 1 --- Model

例如：

-   GPT
-   Claude
-   Gemini
-   Llama

角色：

    predict next token

------------------------------------------------------------------------

### Layer 2 --- Base Harness（平台內建）

例如：

-   tools
-   memory
-   system prompt
-   function calling
-   file system
-   code execution

代表：

-   Claude Code
-   Cursor
-   Copilot

------------------------------------------------------------------------

### Layer 3 --- User Harness（未來最重要）

你自己設計的：

    repo
    CI/CD
    tests
    retry logic
    workflow
    orchestrator
    monitoring
    policies
    dataset
    evaluation

------------------------------------------------------------------------

## 7. Coding Agent 真實運作流程

不是：

    AI 寫 code

而是：

    AI 寫 code
    → build
    → test
    → lint
    → run
    → measure
    → fix
    → retry
    → deploy

這整條 pipeline：

**就是 Harness**

------------------------------------------------------------------------

## 8. 為什麼 Harness 是未來核心能力？

因為：

模型會逐漸 commodity 化。

就像：

-   CPU
-   Linux
-   Docker
-   Kubernetes

最後價值在：

    how you run the system

而不是：

    what model you use

------------------------------------------------------------------------

## 9. 工程師最重要的心智模型

    LLM = brain
    Harness = nervous system
    Agent = organism

或：

    Model   = CPU
    Harness = OS + Scheduler + Monitoring + Toolchain
    Agent   = Computer

------------------------------------------------------------------------

## 10. 最短總結（可貼在 README）

    Agent = Model + Harness

    Harness = Guides + Sensors

    Guide   = instructions
    Sensor  = feedback

    Harness Engineering =
    designing the feedback loop

------------------------------------------------------------------------

（End）
