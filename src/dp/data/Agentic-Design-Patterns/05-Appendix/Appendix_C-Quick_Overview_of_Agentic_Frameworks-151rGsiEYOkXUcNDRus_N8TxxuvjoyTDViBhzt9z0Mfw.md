# 附錄 C - 代理式 框架快速概述

## LangChain

LangChain 是用於開發由大型語言模型支援的應用程式的框架。它的核心優勢在於它的 LangChain 表達式語言（LCEL），它允許您將元件「管道」到一個鏈中。這創建了一個清晰的線性序列，其中一個步驟的輸出成為下一步的輸入。它專為有向非循環圖 (DAG) 工作流程而構建，這意味著流程朝一個方向流動，沒有循環。

將其用於：

* 簡單 RAG：檢索文件、建立提示、從大型語言模型獲得答案。

* 摘要：取得使用者文本，將其提供給摘要提示，然後返回輸出。

* 擷取：從文字區塊中擷取結構化資料（如 JSON）。

Python

```python
# A simple LCEL chain conceptually # (This is not runnable code, just illustrates the flow) 
chain = prompt | model | output_parse
```

## LangGraph

LangGraph 是一個建構在 LangChain 之上的函式庫，用於處理更先進的代理系統。它允許您將工作流程定義為具有節點（函數或 LCEL 鏈）和邊（條件邏輯）的圖形。它的主要優點是能夠創建循環，允許應用程式以靈活的順序循環、重試或呼叫工具，直到任務完成。它明確管理應用程式狀態，該狀態在節點之間傳遞並在整個過程中更新。

將其用於：

* 多代理系統：主管代理將任務路由給專門的工作代理，可能會循環直到達到目標。

* 規劃和執行代理：代理建立計劃，執行步驟，然後循環返回以根據結果更新計劃。

* 人機循環：圖可以等待人類輸入，然後再決定下一步要轉到哪個節點。

|特色|LangChain |LangGraph|
| :---- | :---- | :---- |
|核心抽象|鏈條（使用 LCEL）|節點圖|
|工作流程類型 |線性（有向無環圖） |循環（帶循環的圖形）|
|國家管理|每次運行通常都是無狀態的 |明確且持久的狀態物件 |
|主要用途 |簡單、可預測的序列 |複雜、動態、有狀態的代理 |

### 您應該使用哪一個？

* 當您的應用程式具有清晰、可預測且線性的步驟流程時，請選擇 LangChain。如果您可以定義從 A 到 B 到 C 的流程而不需要環回，那麼帶有 LCEL 的 LangChain 是完美的工具。

* 當您需要應用程式在循環中進行推理、規劃或操作時，請選擇 LangGraph。如果您的代理需要使用工具、反思結果，並可能使用不同的方法重試，那麼您需要 LangGraph 的循環和狀態特性。

```python
# Graph state
class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str


# Nodes
def call_llm_1(state: State):
    """First LLM call to generate initial joke"""
    msg = llm.invoke(f"Write a joke about {state['topic']}")
    return {"joke": msg.content}


def call_llm_2(state: State):
    """Second LLM call to generate story"""
    msg = llm.invoke(f"Write a story about {state['topic']}")
    return {"story": msg.content}


def call_llm_3(state: State):
    """Third LLM call to generate poem"""
    msg = llm.invoke(f"Write a poem about {state['topic']}")
    return {"poem": msg.content}


def aggregator(state: State):
    """Combine the joke and story into a single output"""
    combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
    combined += f"STORY:\n{state['story']}\n\n"
    combined += f"JOKE:\n{state['joke']}\n\n"
    combined += f"POEM:\n{state['poem']}"
    return {"combined_output": combined}


# Build workflow
parallel_builder = StateGraph(State)

# Add nodes
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")
parallel_builder.add_edge("aggregator", END)

parallel_workflow = parallel_builder.compile()

# Show workflow
display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

# Invoke
state = parallel_workflow.invoke({"topic": "cats"})
print(state["combined_output"])
```

此程式碼定義並執行平行操作的 LangGraph 工作流程。其主要目的是同時產生關於給定主題的笑話、故事和詩歌，然後將它們組合成單一格式化文字輸出。

## 谷歌的 ADK

谷歌的代理開發套件（ADK）提供了一個高級的結構化框架，用於建立和部署由多個互動的人工智慧代理組成的應用程式。它與 LangChain 和 LangGraph 形成鮮明對比，它提供了一個更加固執和麵向生產的系統來協調代理協作，而不是為代理的內部邏輯提供基本構建塊。

LangChain 在最基礎的層面上運行，提供元件和標準化介面來建立操作序列，例如呼叫模型並解析其輸出。 LangGraph 透過引入更靈活、更強大的控制流程來擴展這一點；它將代理的工作流程視為狀態圖。使用 LangGraph，開發人員明確定義節點（函數或工具）和邊（指示執行路徑）。這種圖結構允許複雜的循環推理，系統可以循環、重試任務，並根據節點之間傳遞的明確管理的狀態物件做出決策。它使開發人員能夠對單一代理的思考過程進行細微控制，或能夠根據第一原理建立多代理系統。

Google 的 ADK 抽象化了大部分這種低階圖構造。它不是要求開發人員定義每個節點和邊緣，而是為多代理互動提供預先建構的架構模式。例如，ADK 具有內建代理類型，如 SequentialAgent 或 ParallelAgent，它們可自動管理不同代理之間的控制流程。它是圍繞著代理“團隊”的概念構建的，通常有一個主要代理將任務委託給專門的子代理。狀態和會話管理由框架更隱式地處理，提供了比 LangGraph 的顯式狀態傳遞更具凝聚力但粒度更小的方法。因此，雖然 LangGraph 為您提供了設計單個機器人或團隊的複雜佈線的詳細工具，但 Google 的 ADK 為您提供了一條工廠裝配線，旨在建造和管理一組已經知道如何協同工作的機器人。

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_Search

dice_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="question_answer_agent",
    description="A helpful assistant agent that can answer questions.",
    instruction="""Respond to the query using google search""",
    tools=[google_search],
)
```

此程式碼建立一個搜尋增強代理。當該代理收到問題時，它不會僅依賴其預先存在的知識。相反，它將按照指示使用 Google 搜尋工具從網路上尋找相關的即時訊息，然後使用該資訊建立答案。

## 船員.人工智慧

CrewAI 提供了一個編排框架，用於透過專注於協作角色和結構化流程來建立多代理系統。它在比基礎工具包更高的抽象層級上運行，提供反映人類團隊的概念模型。開發人員不是將細粒度的邏輯流定義為圖表，而是定義參與者及其任務，並由 CrewAI 管理他們的互動。

該框架的核心元件是 代理、Tasks 和 Crew。代理不僅由其功能定義，還由角色定義，包括特定角色、目標和背景故事，指導其行為和溝通方式。任務是分配給特定代理的離散工作單元，具有清晰的描述和預期輸出。 Crew 是包含代理和任務清單的內聚單元，它執行預先定義的流程。此過程規定了工作流程，該工作流程通常是順序的（其中一個任務的輸出成為下一個任務的輸入）或分層的（其中類似經理的代理在其他代理之間委派任務並協調工作流程）。

與其他框架相比，CrewAI 佔據著獨特的地位。它擺脫了 LangGraph 的低階、顯式狀態管理和控制流，在 LangGraph 中，開發人員將每個節點和條件邊連接在一起。開發人員設計了團隊章程，而不是建構狀態機。雖然 Googlés ADK 為整個代理生命週期提供了一個全面的、面向生產的平台，但 CrewAI 特別專注於代理協作的邏輯以及模擬專家團隊

```python
@crew
def crew(self) -> Crew:
   """Creates the research crew"""
   return Crew(
     agents=self.agents,
     tasks=self.tasks,
     process=Process.sequential,
     verbose=True,
   )
```

這段程式碼為人工智慧代理團隊建立了一個連續的工作流程，他們按照特定的順序處理一系列任務，並啟用詳細的日誌記錄來監控他們的進度。

## 其他代理開發框架

**Microsoft AutoGen**：AutoGen 是一個以編排多個代理為中心的框架，這些代理透過對話解決任務。其架構使具有不同功能的代理能夠進行交互，從而實現複雜的問題分解和協作解決。 AutoGen 的主要優勢是其靈活的、對話驅動的方法，支援動態和複雜的多代理互動。然而，這種對話範例可能會導致執行路徑的可預測性較差，並且可能需要複雜的提示工程來確保任務有效聚合。

**LlamaIndex**：LlamaIndex 本質上是一個資料框架，旨在將大型語言模型與外部和私有資料來源連接起來。它擅長創建複雜的資料攝取和檢索管道，這對於建立能夠執行 RAG 的知識豐富的代理至關重要。雖然其資料索引和查詢功能對於建立上下文感知代理非常強大，但與代理優先框架相比，其用於複雜代理控制流和多代理編排的本機工具還不夠發達。當核心技術挑戰是資料檢索和合成時，LlamaIndex 是最佳選擇。

**Haystac**k：Haystack 是一個開源框架，旨在建立由語言模型支援的可擴展且可立即投入生產的搜尋系統。其架構由模組化、可互通的節點組成，這些節點形成文件檢索、問答和摘要的管道。 Haystack 的主要優勢在於其專注於大規模資訊檢索任務的效能和可擴展性，使其適合企業級應用程式。一個潛在的權衡是，它的設計針對搜尋管道進行了最佳化，可以更加嚴格地實現高度動態和創造性的代理行為。

**MetaGPT**：MetaGPT 透過根據一組預先定義的標準作業程序 (SOP) 分配角色和任務來實現多代理系統。該框架建構代理協作來模仿軟體開發公司，代理扮演產品經理或工程師等角色來完成複雜的任務。這種 SOP 驅動的方法會產生高度結構化和一致的輸出，這對於程式碼生成等專業領域來說是一個顯著的優勢。該框架的主要限制是其高度專業化，使其不太適合其核心設計之外的通用代理任務。

**SuperAGI**：SuperAGI 是一個開源框架，旨在為自主代理提供完整的生命週期管理系統。它包括代理配置、監控和圖形介面功能，旨在提高代理執行的可靠性。主要好處是它專注於生產就緒性，具有內建機制來處理循環等常見故障模式，並提供代理性能的可觀察性。一個潛在的缺點是，與更輕量級的基於庫的框架相比，其綜合平台方法可能會帶來更多的複雜性和開銷。

**語意核心**：語意核心由微軟開發，是一個透過「外掛程式」和「規劃器」系統將大型語言模型與常規程式碼整合的 SDK。它允許大型語言模型調用本機函數並編排工作流程，有效地將模型視為大型軟體應用程式中的推理引擎。它的主要優勢是與現有企業程式碼庫的無縫集成，特別是在 .NET 和 Python 環境中。與更簡單的代理框架相比，其插件和規劃器架構的概念開銷可以呈現更陡峭的學習曲線。

**Strands 代理：** AWS 輕量級且靈活的 SDK，使用模型驅動的方法來建置和運行 人工智慧 代理。它的設計簡單且可擴展，支援從基本對話助理到複雜的多代理自治系統的一切。該框架與模型無關，為各種 大型語言模型 提供者提供廣泛支持，並包括與 MCP 的本機集成，以便輕鬆存取外部工具。其核心優勢在於簡單性和靈活性，具有易於上手的可自訂代理循環。一個潛在的權衡是，其輕量級設計意味著開發人員可能需要建造更多的周圍操作基礎設施，例如高級監控或生命週期管理系統，更全面的框架可能會提供開箱即用的功能。

## 結論

代理框架提供了各種各樣的工具，從用於定義代理邏輯的低階庫到用於編排多代理協作的高級平台。在基礎層面上，LangChain 支援簡單的線性工作流程，而 LangGraph 則引入了有狀態的循環圖以實現更複雜的推理。 CrewAI 和 Google 的 ADK 等更高層級的框架將重點轉移到編排具有預定義角色的代理團隊，而 LlamaIndex 等其他框架則專注於資料密集型應用程式。這種多樣性為開發人員提供了基於圖形的系統的精細控制和更固執己見的平台的簡化開發之間的核心權衡。因此，選擇正確的框架取決於應用程式是否需要簡單的序列、動態推理循環或受管理的專家團隊。最終，這個不斷發展的生態系統使開發人員能夠透過選擇專案所需的精確抽象層級來建構日益複雜的人工智慧系統。

參考

1.LangChain，[https://www.langchain.com/](https://www.langchain.com/)

2. LangGraph，[https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)

3. Google 的 ADK，[https://google.github.io/adk-docs/](https://google.github.io/adk-docs/)

4.Crew.人工智慧，[https://docs.crewai.com/en/introduction](https://docs.crewai.com/en/introduction)