# crewAI - 打造多 Agent 協作的任務指揮系統

## 攔截源頭

- 發現管道：Threads
- 攔截原因：最近在研究多 Agent 協作框架（像是 AutoGen、LangGraph、OpenDevin），想找一個更直覺的系統，讓多個 AI 角色分工合作。看到 crewAI 的標語「Building multi-agent teams with memory, roles, and workflows」，立刻決定攔截。

## 技術初探

- 官方定義：crewAI helps you build agentic teams that collaborate using shared memory, tools, and workflows. It provides abstractions for roles, tasks, and communication.
- 核心賣點：
  - 多智慧體團隊（Crew）：每個 Agent 具備角色、能力、記憶。
  - 任務與工作流（Tasks & Flows）：支援多階段任務、指揮鏈設計。
  - 工具與整合（Tools）：內建 Google、Serper、Browser、Python、文件讀取等常用工具。
  - 語意協作（Semantic Collaboration）：Agent 之間以自然語言互動，非硬性規則。
  - 記憶系統（Memory）：支援對話歷史、上下文保存，甚至長期記憶。
- 適用場景：
  - 建立「AI 團隊」來解決複雜任務（例如：內容生產、研究報告、自動化決策）。
  - 需要多角色分工（PM、研究員、工程師、審稿人）的 AI 應用。
  - 想快速驗證多智慧體概念，而不想自己寫溝通邏輯。

## 實戰使用

### 快速安裝

```bash
pip install crewai
```

### Hello World：建立兩個協作 Agent

```python
from crewai import Agent, Task, Crew
from langchain.chat_models import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 定義兩個角色
researcher = Agent(
    role="Researcher",
    goal="研究最新的 AI 工具與框架",
    backstory="你是一位專業技術研究員，擅長從多來源整理資訊。",
    llm=llm,
)

writer = Agent(
    role="Writer",
    goal="撰寫技術部落格文章",
    backstory="你是一名文字編輯，善於用簡潔語言說明技術內容。",
    llm=llm,
)

# 定義任務
task = Task(
    description="請合作撰寫一篇介紹 CrewAI 的技術文章。",
    agents=[researcher, writer],
)

# 組成團隊
crew = Crew(agents=[researcher, writer], tasks=[task])
result = crew.run()

print(result)
```

這樣就能建立一個最小化的多 Agent 團隊，由研究員與寫手分工完成同一個任務。

#### 進階：加入工具與記憶

crewAI 支援讓 Agent 使用工具（Tools），例如網頁搜尋、文件讀取、Python 程式執行：

```python
from crewai_tools import SerperDevTool, BrowserTool, FileReadTool

search_tool = SerperDevTool()
browser = BrowserTool()
file_reader = FileReadTool()

researcher = Agent(
    role="Researcher",
    goal="找出最新 AI 框架趨勢",
    backstory="你是一位技術研究員。",
    tools=[search_tool, browser],
)

writer = Agent(
    role="Writer",
    goal="撰寫摘要與分析",
    backstory="你是一名部落客。",
    tools=[file_reader],
)
```

#### Workflow（多階段任務範例）

crewAI 支援設計任務流程：

```python
from crewai import Process

crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    process=Process.sequential,  # 也可設定為 concurrent 並行
)
crew.run()
```

可讓多 Agent 同時或依序執行，根據任務需求選擇流程策略。

## 記憶碼摘要

```text
技術：crewAI
分類：多智慧體協作框架
難度：⭐⭐⭐☆☆（1-5 顆星）
實用度：⭐⭐⭐⭐⭐（1-5 顆星）
一句話：讓多個 AI Agent 能像團隊一樣分工合作完成任務。
適用情境：需要多角色 AI 協作（研究、撰文、測試、分析等）或自動化工作流。
```

## 結語

crewAI 的設計讓我想到「AI 團隊的 Slack」：每個成員（Agent）都有自己的角色、目標與背景，然後透過自然語言協作完成任務。
它最大的價值是把多智慧體協作模組化，不再需要手動寫互動邏輯，直接描述角色與流程即可。
