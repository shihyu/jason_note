# crewAI (PyPI) 繁體中文翻譯

- 來源: https://pypi.org/pypi/crewai/json
- 版本: `1.9.3`

<p align="center">
  <a href="https://github.com/crewAIInc/crewAI">
    <img src="docs/images/crewai_logo.png" width="600px" alt="Open source Multi-AI Agent orchestration framework">
  </a>
</p>
<p align="center" style="display: flex; justify-content: center; gap: 20px; align-items: center;">
  <a href="https://trendshift.io/repositories/11239" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/11239" alt="crewAIInc%2FcrewAI | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/>
  </a>
</p>

<p align="center">
<a href="https://crewai.com">首頁</a>
·
<a href="https://docs.crewai.com">文件</a>
·
<a href="https://app.crewai.com">開始雲端試用</a>
·
<a href="https://blog.crewai.com">部落格</a>
·
<a href="https://community.crewai.com">論壇</a>
</p>

<p align="center">
  <a href="https://github.com/crewAIInc/crewAI">
    <img src="https://img.shields.io/github/stars/crewAIInc/crewAI" alt="GitHub Repo stars">
  </a>
  <a href="https://github.com/crewAIInc/crewAI/network/members">
    <img src="https://img.shields.io/github/forks/crewAIInc/crewAI" alt="GitHub forks">
  </a>
  <a href="https://github.com/crewAIInc/crewAI/issues">
    <img src="https://img.shields.io/github/issues/crewAIInc/crewAI" alt="GitHub issues">
  </a>
  <a href="https://github.com/crewAIInc/crewAI/pulls">
    <img src="https://img.shields.io/github/issues-pr/crewAIInc/crewAI" alt="GitHub pull requests">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/crewai/">
    <img src="https://img.shields.io/pypi/v/crewai" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/crewai/">
    <img src="https://img.shields.io/pypi/dm/crewai" alt="PyPI downloads">
  </a>
  <a href="https://twitter.com/crewAIInc">
    <img src="https://img.shields.io/twitter/follow/crewAIInc?style=social" alt="Twitter Follow">
  </a>
</p>

### 快速且靈活的多代理自動化框架

> CrewAI 是一個精益、快如閃電的 Python 框架，完全從頭開始構建，完全**獨立於 LangChain 或其他代理框架**。
> 它為開發人員提供了高級簡單性和精確的低階控制，非常適合創建適合任何場景的自主人工智慧代理。

- **CrewAI Crews**：優化自主性和協作智能。
- **CrewAI Flows**：啟用精細的事件驅動控制，單一 LLM 呼叫可實現精確的任務編排並原生支援 Crews

超過 100,000 名開發人員通過[學習網](https://learn.crewai.com) 社區課程獲得認證，CrewAI 正在迅速成為
企業級人工智慧自動化標準。

# CrewAI AMP 套件

CrewAI AMP Suite 是一款綜合套件，專為需要安全、可擴展且易於管理的代理驅動自動化的組織量身定制。

您可以嘗試該套件的一部分 [免費機組人員控制飛機](https://app.crewai.com)

## 機組控制飛機主要特點：

- **追蹤和可觀察性**：即時監控和追蹤您的 AI 代理和工作流程，包括指標、日誌和追蹤。
- **統一控制平面**：用於管理、監控和擴展 AI 代理和工作流程的集中式平台。
- **無縫整合**：輕鬆連接現有企業系統、資料來源和雲端基礎架構。
- **進階安全性**：內建強大的安全性和合規性措施，確保安全部署和管理。
- **可行的見解**：即時分析和報告以優化效能和決策。
- **24/7 支援**：專門的企業支持，確保不間斷運作和快速解決問題。
- **本地和雲端部署選項**：根據您的安全性和合規性要求，在本地或雲端部署 CrewAI AMP。

CrewAI AMP 專為尋求強大、可靠的解決方案以將複雜的業務流程轉變為高效、可靠的企業而設計。
智慧自動化。

## 目錄

- [為什麼選擇 CrewAI？](#why-crewai)
- [入門](#getting-started)
- [主要特點](#key-features)
- [了解流程和人員](#understanding-flows-and-crews)
- [CrewAI 與 LangGraph](#how-crewai-compares)
- [範例](#examples)
  - [快速教學](#quick-tutorial)
  - [撰寫職位說明](#write-job-descriptions)
  - [旅行計劃](#trip-planner)
  - [庫存分析](#stock-analysis)
  - [一起使用人員和流程](#using-crews-and-flows-together)
- [將您的團隊與模型聯繫起來](#connecting-your-crew-to-a-model)
- [CrewAI 的比較](#how-crewai-compares)
- [常見問題 (FAQ)](#frequently-asked-questions-faq)
- [貢獻](#contribution)
- [遙測](#telemetry)
- [執照](#license)

## 為什麼選擇 CrewAI？

<div align="center" style="margin-bottom: 30px;">
  <img src="docs/images/asset.png" alt="CrewAI Logo" width="100%">
</div>

CrewAI 釋放了多代理自動化的真正潛力，透過 AI 代理人員或事件流提供速度、靈活性和控制的一流組合：

- **獨立框架**：從頭開始構建，獨立於LangChain或任何其他代理框架。
- **高效能**：針對速度和最少的資源使用進行了最佳化，從而實現更快的執行。
- **靈活的低階客製化**：在高低階上完全自由地自訂 - 從整體工作流程和系統架構到細粒度的代理行為、內部提示和執行邏輯。
- **適合每個用例**：事實證明，對於簡單的任務和高度複雜的現實企業級場景都有效。
- **強大的社區**：由超過 **100,000 名經過認證的**開發人員組成的快速增長的社區提供支持，提供全面的支持和資源。

CrewAI 讓開發人員和企業能夠自信地建立智慧自動化，縮小簡單性、靈活性和效能之間的差距。

## 入門

請按照本教學設定並執行您的第一個 CrewAI 代理程式。

[![CrewAI 入門教程](https://img.youtube.com/vi/-kSOTtYzgEw/hqdefault.jpg)](https://www.youtube.com/watch?v=-kSOTtYzgEw "CrewAI 入門教學")

### 學習資源

透過我們的綜合課程學習 CrewAI：

- [具有 CrewAI 的多人工智慧代理系統](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) - 掌握多代理系統的基礎知識
- [實用的多人工智慧代理和進階用例](https://www.deeplearning.ai/short-courses/practical-multi-ai-agents-and-advanced-use-cases-with-crewai/) - 深入研究高級實現

### 了解流程和人員

CrewAI 提供了兩種強大的互補方法，可以無縫協作來建立複雜的 AI 應用程式：

1. **工作人員**：具有真正自主權和代理權的人工智慧代理團隊，透過基於角色的協作共同完成複雜的任務。船員啟用：

   - 代理之間自然、自主的決策
   - 動態任務委派和協作
   - 具有明確目標和專業知識的專業角色
   - 靈活的解決問題的方法

2. **流程**：生產就緒、事件驅動的工作流程，可精確控制複雜的自動化。流程提供：

   - 對現實場景的執行路徑進行細粒度控制
   - 任務之間安全、一致的狀態管理
   - AI 代理與生產 Python 程式碼的乾淨集成
   - 複雜業務邏輯的條件分支

當 Crews 和 Flows 結合時，CrewAI 的真正力量就會顯現出來。這種協同作用使您能夠：

- 建立複雜的生產級應用程式
- 平衡自主性與精確控制
- 處理複雜的現實場景
- 保持乾淨、可維護的程式碼結構

### 開始安裝

要開始使用 CrewAI，請按照以下簡單步驟：

### 1. 安裝

確保您的系統上安裝了 Python >=3.10 <3.14。 CrewAI 使用 [紫外線](https://docs.astral.sh/uv/) 進行依賴管理和套件處理，提供無縫的設定和執行體驗。

首先，安裝CrewAI：

```shell
pip install crewai
```

如果您想要安裝「crewai」軟體包及其可選功能（包括用於代理的其他工具），您可以使用以下命令來完成此操作：

```shell
pip install 'crewai[tools]'
```

上面的命令安裝基本包，並添加需要更多依賴項才能運行的額外元件。

### 依賴性故障排除

如果您在安裝或使用過程中遇到問題，以下是一些常見的解決方案：

#### 常見問題

1. **ModuleNotFoundError：沒有名為「tiktoken」的模組**

   - 明確安裝 tiktoken：`pip install 'crewai[embeddings]'`
   - 如果使用 embedchain 或其他工具：`pip install 'crewai[tools]'`

2. **tiktoken 建造輪子失敗**

   - 確保 Rust 編譯器已安裝（請參閱上面的安裝步驟）
   - 對於 Windows：驗證 Visual C++ 建置工具是否已安裝
   - 試試升級 pip：`pip install --upgrade pip`
   - 如果問題仍然存在，請使用預先建造的輪子：`pip install tiktoken --prefer-binary`

### 2. 使用 YAML 設定設定您的團隊

若要建立新的 CrewAI 項目，請執行以下 CLI（命令列介面）命令：

```shell
crewai create crew <project_name>
```

此命令建立一個具有以下結構的新專案資料夾：

```
my_project/
├── .gitignore
├── pyproject.toml
├── README.md
├── .env
└── src/
    └── my_project/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── custom_tool.py
        │   └── __init__.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

現在您可以透過編輯 `src/my_project` 資料夾中的檔案來開始開發您的團隊。 `main.py` 文件是項目的入口點，`crew.py` 文件是您定義人員的位置，`agents.yaml` 文件是您定義代理的位置，`tasks.yaml` 文件是您定義任務的位置。

#### 要自訂您的項目，您可以：

- 修改`src/my_project/config/agents.yaml`來定義您的代理程式。
- 修改`src/my_project/config/tasks.yaml`來定義您的任務。
- 修改`src/my_project/crew.py`以新增您自己的邏輯、工具和特定參數。
- 修改 `src/my_project/main.py` 為您的代理程式和任務新增自訂輸入。
- 將環境變數加入`.env` 檔案。

#### 具有順序流程的簡單工作組範例：

實例化你的船員：

```shell
crewai create crew latest-ai-development
```

根據需要修改文件以適合您的用例：

**代理.yaml**

```yaml
# src/my_project/config/agents.yaml
researcher:
  role: >
    {topic} Senior Data Researcher
  goal: >
    Uncover cutting-edge developments in {topic}
  backstory: >
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}. Known for your ability to find the most relevant
    information and present it in a clear and concise manner.

reporting_analyst:
  role: >
    {topic} Reporting Analyst
  goal: >
    Create detailed reports based on {topic} data analysis and research findings
  backstory: >
    You're a meticulous analyst with a keen eye for detail. You're known for
    your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.
```

**任務.yaml**

````yaml
# src/my_project/config/tasks.yaml
research_task:
  description: >
    Conduct a thorough research about {topic}
    Make sure you find any interesting and relevant information given
    the current year is 2025.
  expected_output: >
    A list with 10 bullet points of the most relevant information about {topic}
  agent: researcher

reporting_task:
  description: >
    Review the context you got and expand each topic into a full section for a report.
    Make sure the report is detailed and contains any and all relevant information.
  expected_output: >
    A fully fledge reports with the mains topics, each with a full section of information.
    Formatted as markdown without '```'
  agent: reporting_analyst
  output_file: report.md
````

**船員.py**

```python
# src/my_project/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class LatestAiDevelopmentCrew():
	"""LatestAiDevelopment crew"""
	agents: List[BaseAgent]
	tasks: List[Task]

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[SerperDevTool()]
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the LatestAiDevelopment crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
```

**主.py**

```python
#!/usr/bin/env python
# src/my_project/main.py
import sys
from latest_ai_development.crew import LatestAiDevelopmentCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI Agents'
    }
    LatestAiDevelopmentCrew().crew().kickoff(inputs=inputs)
```

### 3.管理你的團隊

在運行您的工作人員之前，請確保您在 `.env` 檔案中將以下鍵設為環境變數：

- [OpenAI API 金鑰](https://platform.openai.com/account/api-keys)（或其他 LLM API 金鑰）：`OPENAI_API_KEY=sk-...`
- [Serper.dev](https://serper.dev/) API 金鑰：`SERPER_API_KEY=YOUR_KEY_HERE`

鎖定依賴項並使用 CLI 命令安裝它們，但首先導航到您的專案目錄：

```shell
cd my_project
crewai install (Optional)
```

若要執行您的工作人員，請在專案的根目錄中執行以下命令：

```bash
crewai run
```

或者

```bash
python src/my_project/main.py
```

如果因為使用poetry導致錯誤，請執行以下命令更新您的crewai套件：

```bash
crewai update
```

您應該在控制台中看到輸出，並且應該在專案的根目錄中建立 `report.md` 檔案以及完整的最終報告。

除了順序流程之外，您還可以使用分層流程，該流程會自動將經理指派給定義的人員，以透過委派和結果驗證來正確協調任務的規劃和執行。 [在此處查看有關流程的更多信息](https://docs.crewai.com/core-concepts/Processes/)。

## 主要特點

CrewAI 是一個精益、獨立、高效能的多 AI 代理框架，提供簡單性、靈活性和精確控制，不受其他代理框架中的複雜性和限制。

- **獨立且精實**：完全獨立於LangChain等其他框架，提供更快的執行速度和更輕的資源需求。
- **靈活精準**：透過直覺的[船員](https://docs.crewai.com/concepts/crews)或精確的[流量](https://docs.crewai.com/concepts/flows)輕鬆編排自主代理，實現您需求的完美平衡。
- **無縫整合**：輕鬆地將 Crews（自主性）和 Flows（精確性）結合起來，創建複雜的、真實的自動化。
- **深度客製化**：客製化各個面向－從高階工作流程到低階內部提示和座席行為。
- **可靠的效能**：在簡單的任務和複雜的企業級自動化中獲得一致的結果。
- **繁榮的社區**：以強大的文檔和超過 100,000 名經過認證的開發人員為後盾，提供卓越的支持和指導。

選擇 CrewAI 輕鬆建立功能強大、適應性強且可立即投入生產的 AI 自動化。

## 範例

您可以在[CrewAI-範例儲存庫](https://github.com/crewAIInc/crewAI-examples?tab=readme-ov-file)中測試人工智慧人員的不同現實生活範例：

- [登陸頁面產生器](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/landing_page_generator)
- [執行過程中有人工輸入](https://docs.crewai.com/how-to/Human-Input-on-Execution)
- [旅行計劃](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/trip_planner)
- [庫存分析](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/stock_analysis)

### 快速教學

[![CrewAI 教程](https://img.youtube.com/vi/tnejrr-0a94/maxresdefault.jpg)](https://www.youtube.com/watch?v=tnejrr-0a94 "CrewAI 教學")

### 撰寫職位說明

[查看此範例的程式碼](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/job-posting) 或觀看下面的影片：

[![職缺發布](https://img.youtube.com/vi/u98wEMz-9to/maxresdefault.jpg)](https://www.youtube.com/watch?v=u98wEMz-9to "職缺")

### 旅行計劃

[查看此範例的程式碼](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/trip_planner) 或觀看下面的影片：

[![旅行計劃](https://img.youtube.com/vi/xis7rWp-hjs/maxresdefault.jpg)](https://www.youtube.com/watch?v=xis7rWp-hjs "旅行計畫")

### 庫存分析

[查看此範例的程式碼](https://github.com/crewAIInc/crewAI-examples/tree/main/crews/stock_analysis) 或觀看下面的影片：

[![個股分析](https://img.youtube.com/vi/e0Uj4yWdaAg/maxresdefault.jpg)](https://www.youtube.com/watch?v=e0Uj4yWdaAg "股票分析")

### 一起使用人員和流程

當將 Crews 與 Flows 結合起來創建複雜的自動化管道時，CrewAI 的力量真正發揮了作用。
CrewAI 流支援 `or_` 和 `and_` 等邏輯運算子來組合多個條件。這可以與 `@start`、`@listen` 或 `@router` 裝飾器一起使用來創建複雜的觸發條件。

- `or_`：滿足任何指定條件時觸發。
- `and_`滿足所有指定條件時觸發。

以下是在一個 Flow 中協調多個 Crew 的方法：

```python
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai import Crew, Agent, Task, Process
from pydantic import BaseModel

# Define structured state for precise control
class MarketState(BaseModel):
    sentiment: str = "neutral"
    confidence: float = 0.0
    recommendations: list = []

class AdvancedAnalysisFlow(Flow[MarketState]):
    @start()
    def fetch_market_data(self):
        # Demonstrate low-level control with structured state
        self.state.sentiment = "analyzing"
        return {"sector": "tech", "timeframe": "1W"}  # These parameters match the task description template

    @listen(fetch_market_data)
    def analyze_with_crew(self, market_data):
        # Show crew agency through specialized roles
        analyst = Agent(
            role="Senior Market Analyst",
            goal="Conduct deep market analysis with expert insight",
            backstory="You're a veteran analyst known for identifying subtle market patterns"
        )
        researcher = Agent(
            role="Data Researcher",
            goal="Gather and validate supporting market data",
            backstory="You excel at finding and correlating multiple data sources"
        )

        analysis_task = Task(
            description="Analyze {sector} sector data for the past {timeframe}",
            expected_output="Detailed market analysis with confidence score",
            agent=analyst
        )
        research_task = Task(
            description="Find supporting data to validate the analysis",
            expected_output="Corroborating evidence and potential contradictions",
            agent=researcher
        )

        # Demonstrate crew autonomy
        analysis_crew = Crew(
            agents=[analyst, researcher],
            tasks=[analysis_task, research_task],
            process=Process.sequential,
            verbose=True
        )
        return analysis_crew.kickoff(inputs=market_data)  # Pass market_data as named inputs

    @router(analyze_with_crew)
    def determine_next_steps(self):
        # Show flow control with conditional routing
        if self.state.confidence > 0.8:
            return "high_confidence"
        elif self.state.confidence > 0.5:
            return "medium_confidence"
        return "low_confidence"

    @listen("high_confidence")
    def execute_strategy(self):
        # Demonstrate complex decision making
        strategy_crew = Crew(
            agents=[
                Agent(role="Strategy Expert",
                      goal="Develop optimal market strategy")
            ],
            tasks=[
                Task(description="Create detailed strategy based on analysis",
                     expected_output="Step-by-step action plan")
            ]
        )
        return strategy_crew.kickoff()

    @listen(or_("medium_confidence", "low_confidence"))
    def request_additional_analysis(self):
        self.state.recommendations.append("Gather more data")
        return "Additional analysis required"
```

此範例示範如何：

1. 使用Python程式碼進行基本資料操作
2. 建立並執行 Crews 作為工作流程中的步驟
3. 使用 Flow 裝飾器來管理操作順序
4. 根據 Crew 結果實施條件分支

## 將您的團隊與模型聯繫起來

CrewAI 支援透過各種連接選項使用各種 LLM。預設情況下，您的代理程式在查詢模型時將使用 OpenAI API。但是，還有其他幾種方法可以讓您的代理連接到模型。例如，您可以透過 Ollama 工具將代理程式配置為使用本機模型。

有關配置代理與模型的連接的詳細信息，請參閱[將 CrewAI 連接到法學碩士](https://docs.crewai.com/how-to/LLM-Connections/) 頁面。

## CrewAI 的比較

**CrewAI 的優勢**：CrewAI 透過其獨特的 Crews 和 Flows 架構將自主代理智慧與精確的工作流程控制相結合。該框架在高級編排和低階客製化方面均表現出色，可實現具有精細控制的複雜生產級系統。

- **LangGraph**：雖然 LangGraph 為建置代理程式工作流程提供了基礎，但其方法需要大量的樣板程式碼和複雜的狀態管理模式。該框架與 LangChain 的緊密耦合會限制實現自訂代理行為或與外部系統整合時的靈活性。

_P.S. CrewAI 展示了比 LangGraph 顯著的效能優勢，在某些情況下執行速度提高了 5.76 倍，例如此 QA 任務範例 ([查看比較](https://github.com/crewAIInc/crewAI-examples/tree/main/Notebooks/CrewAI%20Flows%20%26%20Langgraph/QA%20Agent))，同時在某些編碼任務中以更快的完成時間獲得更高的評估分數，如本例 ([詳細分析](https://github.com/crewAIInc/crewAI-examples/blob/main/Notebooks/CrewAI%20Flows%20%26%20Langgraph/Coding%20Assistant/coding_assistant_eval.ipynb))。 _

- **Autogen**：雖然 Autogen 擅長創建能夠協同工作的會話代理，但它缺乏固有的流程概念。在 Autogen 中，編排代理的互動需要額外的編程，隨著任務規模的成長，這可能會變得複雜和繁瑣。
- **ChatDev**：ChatDev 將流程的概念引入人工智慧代理領域，但其實現相當僵化。 ChatDev 中的自訂是有限的，並且不適合生產環境，這可能會阻礙實際應用程式中的可擴展性和靈活性。

## 貢獻

CrewAI 是開源的，我們歡迎貢獻。如果您想做出貢獻，請：

- 分叉儲存庫。
- 為您的功能建立一個新分支。
- 添加您的功能或改進。
- 發送拉取請求。
- 我們感謝您的意見！

### 安裝依賴項

```bash
uv lock
uv sync
```

### 虛擬環境

```bash
uv venv
```

### 預提交掛鉤

```bash
pre-commit install
```

### 運行測試

```bash
uv run pytest .
```

### 運行靜態類型檢查

```bash
uvx mypy src
```

### 包裝

```bash
uv build
```

### 本地安裝

```bash
pip install dist/*.tar.gz
```

## 遙測

CrewAI 使用匿名遙測來收集使用數據，主要目的是透過將精力集中在最常用的功能、整合和工具上來幫助我們改進程式庫。

至關重要的是要了解，**不會收集關於提示、任務描述、代理的背景故事或目標、工具的使用、API 呼叫、回應、代理處理的任何資料或秘密和環境變數的資料**，上述條件除外。啟用`share_crew`功能後，將收集詳細數據，包括任務描述、代理的背景或目標以及其他特定屬性，以在尊重用戶隱私的同時提供更深入的見解。使用者可以透過將環境變數 OTEL_SDK_DISABLED 設為 true 來停用遙測。

收集的數據包括：

- CrewAI 版本
  - 這樣我們就可以了解有多少用戶正在使用最新版本
- Python 版本
  - 這樣我們就可以決定要更好地支援哪些版本
- 通用作業系統（例如 CPU 數量、macOS/Windows/Linux）
  - 所以我們知道我們應該關注什麼作業系統以及我們是否可以建立特定的作業系統相關功能
- 團隊中的代理數量和任務
  - 因此，我們確保使用類似的用例進行內部測試，並教育人們最佳實踐
- 正在使用的船員流程
  - 了解我們應該把精力集中在哪裡
- 如果代理正在使用記憶體或允許委派
  - 了解我們是否改進了功能或甚至放棄了它們
- 如果任務是並行執行還是順序執行
  - 了解我們是否應該更專注於並行執行
- 正在使用的語言模型
  - 改進了對最常用語言的支持
- 特工在船員中的角色
  - 了解高級用例，以便我們可以建立更好的工具、整合和範例
- 可用的工具名稱
  - 了解公開可用的工具中哪些工具使用得最多，以便我們可以改進它們

使用者可以選擇加入進一步遙測，透過將其 Crew 上的 `share_crew` 屬性設為 `True` 來共享完整的遙測資料。啟用`share_crew`會收集詳細的人員和任務執行數據，包括任務的`goal`、`backstory`、`context`和`output`。這樣可以更深入了解使用模式，同時尊重使用者的分享選擇。

## 執照

CrewAI 在 [我的許可證](https://github.com/crewAIInc/crewAI/blob/main/LICENSE) 下發布。

## 常見問題 (FAQ)

### 一般的

- [CrewAI 到底是什麼？](#q-what-exactly-is-crewai)
- [如何安裝 CrewAI？](#q-how-do-i-install-crewai)
- [CrewAI 依賴 LangChain 嗎？](#q-does-crewai-depend-on-langchain)
- [CrewAI 是開源的嗎？](#q-is-crewai-open-source)
- [CrewAI 是否收集用戶資料？](#q-does-crewai-collect-data-from-users)

### 特性和功能

- [CrewAI 可以處理複雜的用例嗎？](#q-can-crewai-handle-complex-use-cases)
- [我可以將 CrewAI 與本地 AI 模型結合使用嗎？](#q-can-i-use-crewai-with-local-ai-models)
- [Crews 與 Flows 有何不同？](#q-what-makes-crews-different-from-flows)
- [CrewAI 與 LangChain 相比有何優點？](#q-how-is-crewai-better-than-langchain)
- [CrewAI 是否支援微調或訓練自訂模型？](#q-does-crewai-support-fine-tuning-or-training-custom-models)

### 資源和社區

- [在哪裡可以找到現實世界中的 CrewAI 範例？](#q-where-can-i-find-real-world-crewai-examples)
- [我如何為 CrewAI 做出貢獻？](#q-how-can-i-contribute-to-crewai)

### 企業特色

- [CrewAI AMP 提供哪些附加功能？](#q-what-additional-features-does-crewai-enterprise-offer)
- [CrewAI AMP 可用於雲端和本地部署嗎？](#q-is-crewai-enterprise-available-for-cloud-and-on-premise-deployments)
- [我可以免費試用 CrewAI AMP 嗎？](#q-can-i-try-crewai-enterprise-for-free)

### Q：CrewAI 到底是什麼？

答：CrewAI 是一個獨立、精簡且快速的 Python 框架，專為編排自主 AI 代理而建構。與 LangChain 等框架不同，CrewAI 不依賴外在依賴，使其更精簡、更快、更簡單。

### Q：如何安裝 CrewAI？

答：使用 pip 安裝 CrewAI：

```shell
pip install crewai
```

其他工具，請使用：

```shell
pip install 'crewai[tools]'
```

### Q：CrewAI 依賴 LangChain 嗎？

答：不會。 CrewAI 完全是從頭開始建立的，不依賴 LangChain 或其他代理框架。這確保了精益、快速且靈活的體驗。

### Q：CrewAI 可以處理複雜的用例嗎？

答：是的。 CrewAI 擅長簡單且高度複雜的現實場景，提供高低階的深度自訂選項，從內部提示到複雜的工作流程編排。

### Q：我可以將 CrewAI 與本地 AI 模型一起使用嗎？

答：當然！ CrewAI 支援各種語言模型，包括本地語言模型。 Ollama 和 LM Studio 等工具可實現無縫整合。查看[LLM 連線文檔](https://docs.crewai.com/how-to/LLM-Connections/) 以了解更多詳細資訊。

### Q：Crews 與 Flows 有何不同？

答：Crews 提供自主代理協作，非常適合需要靈活決策和動態互動的任務。流提供精確的事件驅動控制，非常適合管理詳細的執行路徑和安全的狀態管理。您可以將兩者無縫結合以獲得最大效率。

### Q：CrewAI 比 LangChain 好在哪裡？

答：CrewAI 提供更簡單、更直觀的 API、更快的執行速度、更可靠和一致的結果、強大的文件和活躍的社區，解決與 LangChain 相關的常見批評和限制。

### Q：CrewAI 是開源的嗎？

答：是的，CrewAI 是開源的，並積極鼓勵社群貢獻和合作。

### Q：CrewAI 是否收集用戶資料？

答：CrewAI 收集匿名遙測資料嚴格是為了改進目的。除非使用者明確啟用，否則永遠不會收集提示、任務或 API 回應等敏感資料。

### Q：在哪裡可以找到真實的 CrewAI 範例？

答：查看 [CrewAI-範例儲存庫](https://github.com/crewAIInc/crewAI-examples) 中的實際範例，涵蓋旅行計劃、股票分析和職位發布等用例。

### Q：我如何為 CrewAI 做出貢獻？

答：熱烈歡迎大家踴躍投稿！分叉儲存庫、建立分支、實施變更並提交拉取請求。有關詳細指南，請參閱自述文件的貢獻部分。

### Q：CrewAI AMP 提供哪些附加功能？

答：CrewAI AMP 提供先進的功能，例如統一控制平面、即時可觀測性、安全整合、進階安全性、可操作的見解和專門的 24/7 企業支援。

### Q：CrewAI AMP 可用於雲端和本地部署嗎？

答：是的，CrewAI AMP 支援基於雲端和本地部署選項，使企業能夠滿足其特定的安全性和合規性要求。

### Q：我可以免費試用 CrewAI AMP 嗎？

答：是的，您可以透過免費造訪 [機組人員控制機](https://app.crewai.com) 來探索 CrewAI AMP Suite 的部分內容。

### Q：CrewAI 是否支援微調或訓練自訂模型？

答：是的，CrewAI 可以與客製化訓練或微調的模型集成，使您能夠利用特定領域的知識和準確性來增強代理。

### Q：CrewAI 代理可以與外部工具和 API 互動嗎？

答：當然！ CrewAI 代理可以輕鬆與外部工具、API 和資料庫集成，使他們能夠利用現實世界的資料和資源。

### Q：CrewAI 適合生產環境嗎？

答：是的，CrewAI 明確按照生產級標準進行設計，確保企業部署的可靠性、穩定性和可擴展性。

### Q：CrewAI 的可擴充性如何？

答：CrewAI 具有高度可擴展性，支援簡單的自動化和同時涉及大量代理和複雜任務的大規模企業工作流程。

### Q：CrewAI 是否提供調試和監控工具？

答：是的，CrewAI AMP 包括進階調試、追蹤和即時可觀察性功能，可簡化自動化的管理和故障排除。

### Q：CrewAI 支援哪些程式語言？

答：CrewAI 主要基於 Python，但透過其靈活的 API 整合功能，可以輕鬆與任何程式語言編寫的服務和 API 整合。

### Q：CrewAI 是否為初學者提供教育資源？

答：是的，CrewAI 透過 learn.crewai.com 提供大量適合初學者的教程、課程和文檔，為各個技能水平的開發人員提供支援。

### Q：CrewAI 能否實現人機互動工作流程自動化？

答：是的，CrewAI 完全支援人機互動工作流程，讓人類專家和 AI 代理之間無縫協作，以增強決策能力。
