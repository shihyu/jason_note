# OpenAlpha_Evolve: Contribute to Improve this Project

![openalpha_evolve_workflow](https://github.com/user-attachments/assets/9d4709ad-0072-44ae-bbb5-7eea1c5fa08c)

OpenAlpha_Evolve is an open-source Python framework inspired by the groundbreaking research on autonomous coding agents like DeepMind's AlphaEvolve. It's a **regeneration** of the core idea: an intelligent system that iteratively writes, tests, and improves code using Large Language Models (LLMs) via LiteLLM, guided by the principles of evolution.

Our mission is to provide an accessible, understandable, and extensible platform for researchers, developers, and enthusiasts to explore the fascinating intersection of AI, code generation, and automated problem-solving.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

## Table of Contents
- [✨ The Vision: AI-Driven Algorithmic Innovation](#-the-vision-ai-driven-algorithmic-innovation)
- [🧠 How It Works: The Evolutionary Cycle](#-how-it-works-the-evolutionary-cycle)
- [🧩 ASCII 架構圖](#-ascii-架構圖)
- [🚀 Key Features](#-key-features)
- [📂 Project Structure](#-project-structure)
- [🏁 Getting Started](#-getting-started)
- [💡 Defining Your Own Algorithmic Quests!](#-defining-your-own-algorithmic-quests)
- [🔮 The Horizon: Future Evolution](#-the-horizon-future-evolution)
- [🤝 Join the Evolution: Contributing](#-join-the-evolution-contributing)
- [📜 License](#-license)
- [🙏 Homage](#-homage)

---
![image](https://github.com/user-attachments/assets/ff498bb7-5608-46ca-9357-fd9b55b76800)
![image](https://github.com/user-attachments/assets/c1b4184a-f5d5-43fd-8f50-3e729c104e11)



## ✨ The Vision: AI-Driven Algorithmic Innovation

Imagine an agent that can:

*   Understand a complex problem description.
*   Generate initial algorithmic solutions.
*   Rigorously test its own code.
*   Learn from failures and successes.
*   Evolve increasingly sophisticated and efficient algorithms over time.

OpenAlpha_Evolve is a step towards this vision. It's not just about generating code; it's about creating a system that *discovers* and *refines* solutions autonomously.

---
<img width="1253" alt="Screenshot 2025-05-19 at 12 17 58 AM" src="https://github.com/user-attachments/assets/43d7c5a8-f361-438c-ac38-39717f28ee1f" />

## 🧠 How It Works: The Evolutionary Cycle

OpenAlpha_Evolve employs a modular, agent-based architecture to orchestrate an evolutionary process:

1.  **Task Definition**: You, the user, define the algorithmic "quest" – the problem to be solved, including examples of inputs and expected outputs.
2.  **Prompt Engineering (`PromptDesignerAgent`)**: This agent crafts intelligent prompts for the LLM. It designs:
    *   *Initial Prompts*: To generate the first set of candidate solutions.
    *   *Mutation Prompts*: To introduce variations and improvements to existing solutions, often requesting changes in a "diff" format.
    *   *Bug-Fix Prompts*: To guide the LLM in correcting errors from previous attempts, also typically expecting a "diff".
3.  **Code Generation (`CodeGeneratorAgent`)**: Powered by an LLM (currently configured for Gemini), this agent takes the prompts and generates Python code. If a "diff" is requested and received, it attempts to apply the changes to the parent code.
4.  **Evaluation (`EvaluatorAgent`)**: The generated code is put to the test!
    *   *Syntax Check*: Is the code valid Python?
    *   *Execution*: The code is run in a temporary, isolated environment against the input/output examples defined in the task.
    *   *Fitness Scoring*: Programs are scored based on correctness (how many test cases pass), efficiency (runtime), and other potential metrics.
5.  **Database (`DatabaseAgent`)**: All programs (code, fitness scores, generation, lineage) are stored, creating a record of the evolutionary history (currently in-memory).
6.  **Selection (`SelectionControllerAgent`)**: The "survival of the fittest" principle in action. This agent selects:
    *   *Parents*: Promising programs from the current generation to produce offspring.
    *   *Survivors*: The best programs from both the current population and new offspring to advance to the next generation.
7.  **Iteration**: This cycle repeats for a defined number of generations, with each new generation aiming to produce better solutions than the last.
8.  **Orchestration (`TaskManagerAgent`)**: The maestro of the operation, coordinating all other agents and managing the overall evolutionary loop.

---

## 🔬 核心技術完整說明

本專案的「核心演算法技術」不只是 LLM 產碼，而是把 **演化式搜尋**、**多島族群管理**、**差分式突變**、**沙盒評估** 這幾個關鍵機制串成閉環。以下用與實作一致的角度完整說明：

### A) 流程圖解（對照演化迴圈）
```text
Init Population
   |
   v
Evaluate (Docker + tests) ----> if syntax/runtime error -> failed_evaluation
   |
   v
Select Parents (elitism + roulette, per-island)
   |
   v
Generate Offspring
   |   \
   |    +-- Bug Fix (if errors & low correctness)
   |    +-- Mutation (otherwise)
   v
Evaluate Offspring
   |
   v
Select Survivors (per-island, with migration)
   |
   v
Next Generation -> repeat
```

### B) 偽碼（Pseudo-code）
```text
population = init_population()
population = evaluate(population)

for gen in 1..G:
    parents = select_parents(population)
    offspring = []
    for parent in parents:
        if needs_bug_fix(parent):
            child = bug_fix(parent)
        else:
            child = mutate(parent)
        if child is valid:
            offspring.append(child)

    offspring = evaluate(offspring)
    population = select_survivors(population, offspring)
```

### C) 關鍵公式（Fitness / Selection）
```text
correctness = passed_tests / total_tests

roulette_weight = correctness + ε
    where ε = 0.0001 (避免所有權重為 0)

best_program = argmax(
    correctness,
    -runtime_ms,
    -generation,
    -created_at
)
```

### D) 流程對照（檔案與方法）
```text
主迴圈:
  TaskManagerAgent.manage_evolutionary_cycle()

評估:
  EvaluatorAgent.evaluate_program()
  EvaluatorAgent._execute_code_safely()

突變 / 修錯:
  PromptDesignerAgent.design_mutation_prompt()
  PromptDesignerAgent.design_bug_fix_prompt()
  CodeGeneratorAgent.generate_code()
  CodeGeneratorAgent._apply_diff()

選擇與遷移:
  SelectionControllerAgent.select_parents()
  SelectionControllerAgent.select_survivors()
  SelectionControllerAgent._perform_migration()
```

### 1) 演化主迴圈（TaskManagerAgent）
核心流程是「初始化 → 評估 → 選擇 → 產生子代 → 再評估 → 取存活者」，並重複多代：
- 初始化族群時使用較便宜的次模型（`LLM_SECONDARY_MODEL`）大量探索。
- 每一代會依據適應度選父母，再用 LLM 產生「突變」或「修錯」的子代。
- 每代都會評估並保存結果，最後挑出全域最佳解。

### 2) 適應度評估（EvaluatorAgent）
評估分兩層：
- **語法檢查**：先用 `compile` 避免無效程式進入執行。
- **Docker 沙盒執行**：將候選程式包進臨時腳本，在 Docker 中跑測試案例。
  - 支援 `output`（直接比對）與 `validation_func`（自訂驗證）。
  - 計算 correctness（通過率）與平均 runtime。
  - 若採「分層測試」，失敗即停止級聯（避免浪費）。

### 3) 差分式突變 / 修錯（PromptDesignerAgent + CodeGeneratorAgent）
LLM 不直接重寫整個程式，而是輸出 **搜尋/替換 diff**，再由程式套用：
- **Mutation**：針對正確率或效能做優化。
- **Bug Fix**：當錯誤多且正確率低時，改用修錯提示。
- CodeGenerator 會嘗試「精確匹配 → 正規化空白匹配 → 行段落匹配」多層容錯套用 diff。
這能避免整段重寫、降低不穩定性，並強化局部修正能力。

### 4) 選擇與島嶼模型（SelectionControllerAgent）
採 **Island Model**：
- 族群被分成多個島，降低早熟收斂。
- 每島內先保留菁英（elitism），再用 **roulette wheel** 按適應度機率抽父母。
- 每隔若干代會進行 **遷移**：從強島抽最佳個體到弱島，讓優良基因擴散。
這是演化效率與多樣性之間的折衷機制。

### 5) 資料持久化與追蹤（InMemoryDatabaseAgent）
所有候選程式都會被保存（含世代、適應度、錯誤），
方便追蹤演化路徑，也能重啟後繼續演化。

### 6) 模型策略（config/settings.py）
模型使用上有明確策略：
- **初始化與低品質突變**：優先使用次模型省成本。
- **高品質突變與修錯**：改用主模型提升精度。
這讓演化在「成本」與「品質」間取得平衡。

---
以上即為演算法核心技術的完整說明，對應到實作中的：
`TaskManagerAgent`（主迴圈） / `EvaluatorAgent`（評估） /
`PromptDesignerAgent` + `CodeGeneratorAgent`（diff 產生與套用） /
`SelectionControllerAgent`（島嶼模型） / `DatabaseAgent`（持久化）。

## 🧩 核心程式碼解說（逐段對照）

以下以「核心邏輯 → 對應程式碼 → 行為說明」方式整理，方便對照閱讀：

### 1) 演化主迴圈（TaskManagerAgent）
- 入口：`task_manager/agent.py` 的 `manage_evolutionary_cycle()`
- 流程：
  1. `initialize_population()`：用次模型生成初始族群，並存入 DB。
  2. `evaluate_population()`：批次評估族群、更新 fitness。
  3. 迴圈：選父母 → 產生子代 → 評估子代 → 選存活者。
  4. 產生最佳解：`database.get_best_programs(...)`

### 2) 突變 / 修錯（PromptDesignerAgent + CodeGeneratorAgent）
- 入口：`task_manager/agent.py` 的 `generate_offspring(...)`
- 關鍵點：
  - 若錯誤多且正確率低 → 走 `design_bug_fix_prompt(...)`
  - 否則 → 走 `design_mutation_prompt(...)`
  - `code_generator/agent.py` 的 `execute(..., output_format="diff")` 會把 diff 套用到父代。

### 3) Diff 套用邏輯（CodeGeneratorAgent）
- 入口：`code_generator/agent.py` 的 `_apply_diff(...)`
- 容錯策略：
  1. 精確匹配 SEARCH block
  2. 空白正規化匹配
  3. 行段落匹配（首尾行對齊）

### 4) 評估流程（EvaluatorAgent）
- 入口：`evaluator_agent/agent.py` 的 `evaluate_program(...)`
- 重要步驟：
  1. 語法檢查（compile）
  2. Docker 沙盒執行 `_execute_code_safely(...)`
  3. `validation_func` 或 `output` 比對
  4. 回寫 fitness 與狀態（evaluated / failed_evaluation）

### 5) 島嶼模型與選擇策略（SelectionControllerAgent）
- 入口：`selection_controller/agent.py`
- 重要方法：
  - `initialize_islands(...)`：分配初始族群到島嶼
  - `select_parents(...)`：菁英保留 + 輪盤法抽樣
  - `select_survivors(...)`：島內競爭 + 遷移機制
  - `_perform_migration(...)`：強島最佳個體遷移到弱島

### 6) 儲存與持久化（InMemoryDatabaseAgent）
- 入口：`database_agent/agent.py`
- 特色：
  - 記憶體保存
  - JSON 檔落盤（每次 save）

如果要更細節（逐函式/逐段落）請指出要展開的區塊，我可以再補成逐行解說表格。

## 🧩 ASCII 架構圖

```text
+------------------------------------------------------------+
|                           app.py                           |
|       Gradio UI / input params / progress / trigger run     |
+------------------------+-----------------------------------+
                         |
                         v
+------------------------------------------------------------+
|                     TaskManagerAgent                       |
|     init population -> evaluate -> select -> offspring     |
+---------+--------------+---------------+--------------+----+
          |              |               |              |
          v              v               v              v
+---------------+  +---------------+  +---------------+  +---------------+
| PromptDesigner|  | CodeGenerator |  | EvaluatorAgent|  | SelectionCtrl |
|   prompts     |  | LLM + diff    |  | Docker eval   |  | parents/surv. |
+---------------+  +---------------+  +-------+-------+  +-------+-------+
                                             |                  |
                                             v                  v
                                      +---------------+  +---------------+
                                      | Docker Sandbox|  | Island Model  |
                                      +---------------+  +---------------+
                                             |
                                             v
                                      +----------------------+
                                      | InMemoryDatabaseAgent|
                                      | JSON persistence     |
                                      +----------------------+

Note: all agents read config from config/settings.py.
```

補充（繁體中文）：  
以上 ASCII 圖示描述 UI 觸發演化流程，由 TaskManager 統籌，透過 PromptDesigner/CodeGenerator 產生程式，Evaluator 以 Docker 評估，SelectionController 進行島嶼模型選擇與遷移，並由 InMemoryDatabaseAgent 持久化結果。

## 🚀 Key Features

*   **LLM-Powered Code Generation**: Leverages state-of-the-art Large Language Models via LiteLLM, supporting multiple providers (OpenAI, Anthropic, Google, etc.).
*   **Evolutionary Algorithm Core**: Implements iterative improvement through selection, LLM-driven mutation/bug-fixing using diffs, and survival.
*   **Modular Agent Architecture**: Easily extend or replace individual components (e.g., use a different LLM, database, or evaluation strategy).
*   **Automated Program Evaluation**: Syntax checking and functional testing against user-provided examples. Code execution is sandboxed using **Docker containers** for improved security and dependency management, with configurable timeout mechanisms.
*   **Configuration Management**: Easily tweak parameters like population size, number of generations, LLM models, API settings, and Docker configurations via `config/settings.py` and `.env`.
*   **Detailed Logging**: Comprehensive logs provide insights into each step of the evolutionary process.
*   **Diff-based Mutations**: The system is designed to use diffs for mutations and bug fixes, allowing for more targeted code modifications by the LLM.
*   **Open Source & Extensible**: Built with Python, designed for experimentation and community contributions.

---

## 📂 Project Structure

```text
./
├── code_generator/      # Agent responsible for generating code using LLMs.
├── database_agent/      # Agent for managing the storage and retrieval of programs and their metadata.
├── evaluator_agent/     # Agent that evaluates the generated code for syntax, execution, and fitness.
├── prompt_designer/     # Agent that crafts prompts for the LLM for initial generation, mutation, and bug fixing.
├── selection_controller/  # Agent that implements the selection strategy for parent and survivor programs.
├── task_manager/        # Agent that orchestrates the overall evolutionary loop and coordinates other agents.
├── config/                  # Holds configuration files, primarily `settings.py` for system parameters and API keys.
├── core/                    # Defines core data structures and interfaces, like `Program` and `TaskDefinition`.
├── tests/                   # Includes unit and integration tests to ensure code quality and correctness.
├── main.py                  # The main entry point to run the OpenAlpha_Evolve system and start an evolutionary run.
├── requirements.txt         # Lists all Python package dependencies required to run the project.
├── .env.example             # An example file showing the environment variables needed, such as API keys. Copy this to `.env` and fill in your values.
├── .gitignore               # Specifies intentionally untracked files that Git should ignore (e.g., `.env`, `__pycache__/`).
├── LICENSE.md               # Contains the full text of the MIT License under which the project is distributed.
└── README.md                # This file! Provides an overview of the project, setup instructions, and documentation.
```

---

## 🏁 Getting Started

1.  **Prerequisites**:
    *   Python 3.10+
    *   `pip` for package management
    *   `git` for cloning
    *   **Docker**: For sandboxed code evaluation. Ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is installed and running. Visit [docker.com](https://www.docker.com/get-started) for installation instructions.

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/shyamsaktawat/OpenAlpha_Evolve.git
    cd OpenAlpha_Evolve
    ```

3.  **Set Up a Virtual Environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up Environment Variables (Crucial for API Keys)**:
    *   **This step is essential for the application to function correctly with your API keys.** The `.env` file stores your sensitive credentials and configuration, overriding the default placeholders in `config/settings.py`.
    *   Create your personal environment file by copying the example:
        ```bash
        cp .env_example .env
        ```

    #### LLM Configuration
    Google Cloud authentication (e.g., via Application Default Credentials (ADC) or service account keys pointed to by `GOOGLE_APPLICATION_CREDENTIALS`) is a supported method for using Google's LLMs.

    To set up your environment variables for Google Cloud, you can use one of the following methods. These should be added to your `.env` file:

    ```bash
    # For Google Cloud (Vertex AI / AI Studio)
    # Option 1: Using Application Default Credentials (ADC)
    # Ensure you have authenticated via gcloud CLI:
    # gcloud auth application-default login
    # Or set the GOOGLE_APPLICATION_CREDENTIALS environment variable:
    # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

    # Option 2: Directly using an API Key for specific Google services (e.g., Gemini API)
    # GEMINI_API_KEY="your_gemini_api_key"
    ```

    This project uses LiteLLM to interface with various LLM providers. For providers other than Google Cloud (e.g., OpenAI, Anthropic, Cohere), please refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/providers) for the specific environment variables required. Common examples include:
    ```bash
    # OPENAI_API_KEY="your_openai_api_key"
    # ANTHROPIC_API_KEY="your_anthropic_api_key"
    # COHERE_API_KEY="your_cohere_api_key"
    ```
    Add the necessary API key variables for your chosen LLM provider(s) to your `.env` file.

6.  **Run OpenAlpha_Evolve!**
    Run the example task (Dijkstra's algorithm) with:
    ```bash
    python -m main examples/shortest_path.yaml
    ```
    Watch the logs in your terminal to see the evolutionary process unfold! Log files are also saved to `alpha_evolve.log` (by default).

7.  **Launch the Gradio Web Interface**
    Interact with the system via the web UI. To start the Gradio app:
    ```bash
    python app.py
    ```
    Gradio will display a local URL (e.g., http://127.0.0.1:7860) and a public share link if enabled. Open this in your browser to define custom tasks and run the evolution process interactively.

---

## 💡 Defining Your Own Algorithmic Quests!

Want to challenge OpenAlpha_Evolve with a new problem? It's easy! You can define your tasks in two ways:

### 1. Using YAML Files (Recommended)

Create a YAML file in the `examples` directory with the following structure:

```yaml
task_id: "your_task_id"
task_description: |
  Your detailed problem description here.
  Be specific about function names, expected behavior, and constraints.
function_name: "your_function_name"
allowed_imports: ["module1", "module2"]

tests:
  - description: "Test group description" # Describes a group of related tests
    name: "Test group name" # A name for this test group
    test_cases: # This should be a list of individual test cases
      - input: [arg1, arg2]  # First test case
        output: expected_output # Expected result for this input
        # Each test case uses either 'output' for direct comparison
        # or 'validation_func' for more complex validation.
      - input: [arg_for_validation_func_1, arg_for_validation_func_2] # Second test case
        validation_func: |
          def validate(output_from_function):
              # Custom validation logic for this specific test case's output
              # For example, check if output is within a certain range,
              # or if it has specific properties.
              return isinstance(output_from_function, bool) and output_from_function is True
```

See the example in `examples/shortest_path.yaml`

### 2. Using Python Code (Legacy)

You can still define tasks programmatically using the `TaskDefinition` class:

```python
from core.task_definition import TaskDefinition

task = TaskDefinition(
    id="your_task_id",
    description="Your detailed problem description",
    function_name_to_evolve="your_function_name",
    input_output_examples=[
        {"input": [arg1, arg2], "output": expected_output},
        # More examples...
    ],
    allowed_imports=["module1", "module2"]
)
```

### Best Practices for Task Definition

Crafting effective task definitions is key to guiding OpenAlpha_Evolve successfully. Consider these tips:

*   **Be Clear and Unambiguous**: Write task descriptions as if you're explaining the problem to another developer. Avoid jargon where possible, or explain it clearly.
*   **Provide Diverse and Comprehensive Examples**: Your test cases are the primary way the agent verifies its generated code.
    *   Include typical use cases
    *   Cover edge cases (empty inputs, boundary values, etc.)
    *   Include examples that test different logical paths
    *   Use validation functions for complex checks
*   **Start Simple, Then Increase Complexity**: Break down complex problems into simpler versions first.
*   **Specify Constraints and Edge Cases**: Mention specific constraints and edge cases in the description.
*   **Define Expected Function Signature**: Clearly state the expected function name and parameters.
*   **Iterate and Refine**: Review and refine your task definition based on the agent's performance.

---

## 🔮 The Horizon: Future Evolution



---

## 🤝 Join the Evolution: Contributing

This is an open invitation to collaborate! Whether you're an AI researcher, a Python developer, or simply an enthusiast, your contributions are welcome.

*   **Report Bugs**: Find an issue? Please create an issue on GitHub!
*   **Suggest Features**: Have an idea to make OpenAlpha_Evolve better? Open an issue to discuss it!
*   **Submit Pull Requests**:
    *   Fork the repository.
    *   Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`).
    *   Write clean, well-documented code.
    *   Add tests for your changes if applicable.
    *   Ensure your changes don't break existing functionality.
    *   Submit a pull request with a clear description of your changes!

Let's evolve this agent together!

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE.md` file for details.

---

## 🙏 Homage

OpenAlpha_Evolve is proudly inspired by the pioneering work of the Google DeepMind team on AlphaEvolve and other related research in LLM-driven code generation and automated discovery. This project aims to make the core concepts more accessible for broader experimentation and learning. We stand on the shoulders of giants.

---

*Disclaimer: This is an experimental project. Generated code may not always be optimal, correct, or secure. Always review and test code thoroughly, especially before using it in production environments.* 
