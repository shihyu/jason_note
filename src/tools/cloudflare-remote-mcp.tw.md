# 在 Cloudflare 上構建並部署遠端模型上下文協議 (MCP) 伺服器

2025-03-25

9 分鐘閱讀

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/6ifiJyB00Saj3K0TtU5QWn/7c552a4795603414457c7c33c4f432a2/image2.png)

感覺幾乎所有構建 AI 應用程式和[代理 (agents)](https://www.cloudflare.com/learning/ai/what-is-agentic-ai/) 的人都在談論[模型上下文協議 (Model Context Protocol)](https://www.cloudflare.com/learning/ai/what-is-model-context-protocol-mcp/) (MCP)，以及構建在自己電腦上本地安裝和運行的 MCP 伺服器。

現在，您可以向 Cloudflare [構建並部署遠端 MCP 伺服器](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)。我們在 Cloudflare 中添加了四項功能，為您處理構建遠端 MCP 伺服器的困難部分：

1.  [workers-oauth-provider](https://developers.cloudflare.com/agents/model-context-protocol/authorization) — 一個讓授權變得簡單的 [OAuth](https://www.cloudflare.com/learning/access-management/what-is-oauth/) 提供者
    
2.  [McpAgent](https://developers.cloudflare.com/agents/model-context-protocol/tools/) — 內建於 [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/) 中、負責處理遠端傳輸的類別
    
3.  [mcp-remote](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/) — 一個適配器，讓原本僅支援本地連接的 MCP 客戶端能與遠端 MCP 伺服器配合使用
    
4.  [AI playground 作為遠端 MCP 客戶端](https://playground.ai.cloudflare.com/) — 一個聊天介面，允許您連接到遠端 MCP 伺服器，並包含身份驗證檢查

點擊下方的按鈕，或參考[開發者文檔](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)，只需不到兩分鐘即可讓[此範例 MCP 伺服器](https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-server)在生產環境中運行：

[![部署到 Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-server)

與您之前可能使用的本地 MCP 伺服器不同，遠端 MCP 伺服器可以在網際網路上存取。使用者只需登入並使用熟悉的授權流程向 MCP 客戶端授予權限。我們認為這將是一件大事——在過去幾個月中，將程式碼代理連接到 MCP 伺服器讓開發者大開眼界，而遠端 MCP 伺服器具有同樣的潛力，可以為更廣泛的受眾（包括更多日常消費者用例）開闢與 LLM 和代理互動的新方式。

## 從本地到遠端 —— 將 MCP 帶給大眾

MCP 正迅速成為通用協議，使 LLM 能超越[推理 (inference)](https://www.cloudflare.com/learning/ai/inference-vs-training/) 和 [RAG](https://developers.cloudflare.com/reference-architecture/diagrams/ai/ai-rag/)，採取需要存取 AI 應用程式本身以外資源的行動（例如發送電子郵件、部署程式碼變更、發布部落格文章等，隨您想像）。它使 AI 代理（MCP 客戶端）能存取來自外部服務（MCP 伺服器）的工具和資源。

到目前為止，MCP 僅限於在您自己的機器上本地運行——如果您想使用 MCP 存取網路上的工具，則必須在本地設定伺服器。您無法從基於網路的介面或行動應用程式使用 MCP，也沒有辦法讓使用者進行身份驗證並授予 MCP 客戶端權限。實際上，MCP 伺服器尚未真正上線。

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/1EyiTXzB4FvBs2zEfzuNTp/5ce4b55457348e9ab83e6d9cf35d8c3c/image7.png)

支援[遠端 MCP 連接](https://spec.modelcontextprotocol.io/specification/draft/basic/transports/#streamable-http)改變了這一點。它創造了接觸更廣泛網際網路使用者的機會，這些使用者不會為了配合桌面應用程式而特別在本地安裝和運行 MCP 伺服器。遠端 MCP 支援就像是從桌面軟體到網頁軟體的過渡。人們期望能跨裝置繼續任務，並在登入後讓一切正常運作。本地 MCP 對開發者來說很棒，但遠端 MCP 連接是觸及網際網路上所有人的最後一塊拼圖。

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/7bI7rJtLh89jmZaibSgiLl/e426f93616a8210d80b979c47d89dc75/image4.png)

## 讓身份驗證與授權在 MCP 上順利運作

除了改變傳輸層（從 [stdio](https://modelcontextprotocol.io/docs/concepts/transports#standard-input%2Foutput-stdio) 到 [streamable HTTP](https://github.com/modelcontextprotocol/specification/pull/206)）之外，當您構建使用來自終端使用者帳戶資訊的遠端 MCP 伺服器時，您需要[身份驗證與授權](https://www.cloudflare.com/learning/access-management/authn-vs-authz/)。您需要一種方式讓使用者登入並證明自己的身份（身份驗證），以及一種方式讓使用者控制 AI 代理在測試服務時能存取什麼（授權）。

MCP 通過 [OAuth](https://oauth.net/2/) 實現這一點，OAuth 是一項標準協議，允許使用者授予應用程式存取其資訊或服務的權限，而無需分享密碼。在這裡，MCP 伺服器本身充當 OAuth 提供者。然而，自己實作 MCP 的 OAuth 非常困難，因此當您在 Cloudflare 上構建 MCP 伺服器時，我們為您提供了這項功能。

### workers-oauth-provider — 適用於 Cloudflare Workers 的 OAuth 2.1 提供者庫

當您向 Cloudflare [部署 MCP 伺服器](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)時，您的 Worker 會使用 [workers-oauth-provider](https://github.com/cloudflare/workers-oauth-provider) 充當 OAuth 提供者。這是一個新的 TypeScript 庫，它包裝了您的 Worker 程式碼，為 API 端點添加授權，包括（但不限於）MCP 伺服器 API 端點。

您的 MCP 伺服器將接收已經過身份驗證的使用者詳細資訊作為參數。您不需要自己執行任何檢查，也不需要直接管理令牌。您仍然可以完全控制如何驗證使用者：從他們登入時看到的 UI，到他們使用哪個提供者登入。您可以選擇帶入自己的第三方身份驗證和授權提供者（如 Google 或 GitHub），或整合您自己的。

完整的 [MCP OAuth 流程](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization/)如下所示：

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/VTPBfZ4hRPdq2TWE5VOjS/00abc97e4beedf59a4101957612fd503/image5.png)

在這裡，您的 MCP 伺服器既充當上游服務的 OAuth 客戶端，*又*充當 MCP 客戶端的 OAuth 伺服器（也稱為 OAuth「提供者」）。您可以使用任何您想要的上游身份驗證流程，但 workers-oauth-provider 保證您的 MCP 伺服器[符合規格](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization)，並能與各種客戶端應用程式和網站配合使用。這包括對動態客戶端註冊 ([RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)) 和授權伺服器元數據 ([RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)) 的支援。

### 一個簡單、可插拔的 OAuth 介面

當您使用 Cloudflare Workers 構建 MCP 伺服器時，您需要提供 OAuth 提供者實例，指向您的授權、令牌和客戶端註冊端點，以及適用於 MCP 伺服器和身份驗證的[處理程序 (handlers)](https://developers.cloudflare.com/workers/runtime-apis/handlers/fetch/)：

```JavaScript
import OAuthProvider from "@cloudflare/workers-oauth-provider";
import MyMCPServer from "./my-mcp-server";
import MyAuthHandler from "./auth-handler";

export default new OAuthProvider({
  apiRoute: "/sse", // MCP 客戶端連接到您伺服器的路徑
  apiHandler: MyMCPServer.mount('/sse'), // 您的 MCP 伺服器實作
  defaultHandler: MyAuthHandler, // 您的身份驗證實作
  authorizeEndpoint: "/authorize",
  tokenEndpoint: "/token",
  clientRegistrationEndpoint: "/register",
});
```

這種抽象讓您可以輕鬆插入自己的身份驗證。看看[這個範例](https://github.com/cloudflare/ai/blob/main/demos/remote-mcp-github-oauth/src/github-handler.ts)，它使用 GitHub 作為 MCP 伺服器的身份提供者，通過實作 /callback 和 /authorize 路由，只需不到 100 行程式碼。

### 為什麼 MCP 伺服器要發行自己的令牌？

您可能在上面的授權圖示以及 MCP 規格的[授權章節](https://spec.modelcontextprotocol.io/specification/draft/basic/authorization)中注意到，MCP 伺服器會向 MCP 客戶端發行自己的令牌。

您的 Worker 不會將從上游提供者收到的令牌直接傳遞給 MCP 客戶端，而是將加密的存取令牌儲存在 [Workers KV](https://developers.cloudflare.com/kv/) 中。然後，它向客戶端發行自己的令牌。如上面的 [GitHub 範例](https://github.com/cloudflare/ai/blob/main/demos/remote-mcp-github-oauth/src/github-handler.ts)所示，workers-oauth-provider 會代表您處理這項工作——您的程式碼永遠不會直接處理寫入此令牌的操作，從而防止錯誤。您可以在上述 [GitHub 範例](https://github.com/cloudflare/ai/blob/main/demos/remote-mcp-github-oauth/src/github-handler.ts)的以下程式碼片段中看到這一點：

```JavaScript
  // 當您呼叫 completeAuthorization 時，您傳遞給它的 accessToken
  // 會被加密並儲存，永遠不會暴露給 MCP 客戶端
  // 一個新的、獨立的令牌會被生成，並在 /token 端點提供給客戶端
  const { redirectTo } = await c.env.OAUTH_PROVIDER.completeAuthorization({
    request: oauthReqInfo,
    userId: login,
    metadata: { label: name },
    scope: oauthReqInfo.scope,
    props: {
      accessToken,  // 加密儲存，永遠不會發送給 MCP 客戶端
    },
  })

  return Response.redirect(redirectTo)
```

從表面上看，這種間接方式聽起來可能更複雜。為什麼要這樣運作？

通過發行自己的令牌，MCP 伺服器可以比上游提供者限制更多存取權限並執行更細粒度的控制。如果您發行給 MCP 客戶端的令牌遭到破解，攻擊者只能獲得您通過 MCP 工具明確授予的有限權限，而無法完全存取原始令牌的權限。

假設您的 MCP 伺服器請求使用者授權從其 Gmail 帳戶讀取電子郵件的權限，使用的是 [gmail.readonly 範圍](https://developers.google.com/identity/protocols/oauth2/scopes#gmail)。MCP 伺服器公開的工具則更為狹隘，僅允許讀取來自有限寄件者的旅遊預訂通知，以處理像是「我明天旅館房間的退房時間是幾點？」之類的問題。您可以在 MCP 伺服器中強制執行此約束，如果發行給 MCP 客戶端的令牌遭到破解，由於該令牌是針對您的 MCP 伺服器——而不是針對上游提供者 (Google) 的原始令牌——攻擊者將無法使用它來讀取任意電子郵件。他們只能呼叫您的 MCP 伺服器提供的工具。OWASP 將[「過度代理 (Excessive Agency)」](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)列為構建 AI 應用程式的首要風險因素之一，通過向客戶端發行自己的令牌並強制執行約束，您的 MCP 伺服器可以將工具存取權限限制在客戶端僅需要的範圍內。

或者延續早前的 GitHub 範例，您可以強制要求只有特定使用者才能存取特定工具。在下面的範例中，只有白名單中的使用者才能看到或呼叫 `generateImage` 工具，該工具使用 [Workers AI](https://developers.cloudflare.com/workers-ai/) 根據提示詞生成圖像：

```JavaScript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const USER_ALLOWLIST = ["geelen"];

export class MyMCP extends McpAgent<Props, Env> {
  server = new McpServer({
    name: "Github OAuth Proxy Demo",
    version: "1.0.0",
  });

  async init() {
    // 根據使用者身份動態添加工具
    if (USER_ALLOWLIST.has(this.props.login)) {
      this.server.tool(
        'generateImage',
        'Generate an image using the flux-1-schnell model.',
        {
          prompt: z.string().describe('A text description of the image you want to generate.')
        },
        async ({ prompt }) => {
          const response = await this.env.AI.run('@cf/black-forest-labs/flux-1-schnell', { 
            prompt, 
            steps: 8 
          })
          return {
            content: [{ type: 'image', data: response.image!, mimeType: 'image/jpeg' }],
          }
        }
      )
    }
  }
}

```

## 介紹 McpAgent：現即可用的遠端傳輸支援，並將支援 MCP 規格修訂

將 MCP 擴展到本地機器之外的下一步是開啟遠端傳輸層進行通訊。您在本地機器上運行的 MCP 伺服器僅通過 [stdio](https://modelcontextprotocol.io/docs/concepts/transports#standard-input%2Foutput-stdio) 進行通訊，但要讓 MCP 伺服器能透過網際網路呼叫，它必須實作[遠端傳輸](https://spec.modelcontextprotocol.io/specification/draft/basic/transports/#http-with-sse)。

我們今天作為 [Agents SDK](https://github.com/cloudflare/agents) 一部分介紹的 [McpAgent](https://github.com/cloudflare/agents/blob/2f82f51784f4e27292249747b5fbeeef94305552/packages/agents/src/mcp.ts) 類別會為您處理這項工作，它在後台使用 [Durable Objects](https://developers.cloudflare.com/durable-objects/) 來保持持久連接開啟，以便 MCP 客戶端可以向您的 MCP 伺服器發送[伺服器發送事件 (SSE)](https://modelcontextprotocol.io/docs/concepts/transports#server-sent-events-sse)。您不需要編寫程式碼來自行處理傳輸或序列化。一個只需 15 行程式碼的最簡 MCP 伺服器如下所示：

```JavaScript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export class MyMCP extends McpAgent {
  server = new McpServer({
    name: "Demo",
    version: "1.0.0",
  });
  async init() {
    this.server.tool("add", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
      content: [{ type: "text", text: String(a + b) }],
    }));
  }
}
```

經過多次[討論](https://github.com/modelcontextprotocol/specification/discussions/102)，MCP 規格中的遠端傳輸正在發生變化，[Streamable HTTP 將取代 HTTP+SSE](https://github.com/modelcontextprotocol/specification/pull/206)。這允許與 MCP 伺服器進行無狀態、純 HTTP 的連接，並提供升級到 SSE 的選項，同時取消了 MCP 客戶端必須向與初始連接不同的端點發送消息的需求。McpAgent 類別將隨之改變並直接與 Streamable HTTP 配合使用，因此您無需為了支援傳輸方式的修訂而重新開始。

這也適用於傳輸方式的未來迭代。今天，絕大多數 MCP 伺服器僅公開工具，這些工具是簡單的[遠端程序呼叫 (RPC)](https://en.wikipedia.org/wiki/Remote_procedure_call) 方法，可由無狀態傳輸提供。但更複雜的人機協作 (human-in-the-loop) 和代理間互動將需要[提示詞 (prompts)](https://modelcontextprotocol.io/docs/concepts/prompts) 和[取樣 (sampling)](https://modelcontextprotocol.io/docs/concepts/sampling)。我們預期這些類型的頻繁對話、雙向互動將需要即時性，如果沒有雙向傳輸層，這將難以良好實作。屆時，Cloudflare、[Agents SDK](https://developers.cloudflare.com/agents/) 和 Durable Objects 都原生支援 [WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/)，這能實現全雙工、雙向的即時通訊。

## 有狀態的代理式 MCP 伺服器

當您在 Cloudflare 上構建 MCP 伺服器時，每個 MCP 客戶端會話都由透過 [Agents SDK](https://developers.cloudflare.com/agents/) 提供的 Durable Object 支援。這意味著每個會話都可以管理並持久化自己的狀態，並[由其專屬的 SQL 資料庫支援](https://developers.cloudflare.com/agents/api-reference/store-and-sync-state/)。

這開啟了構建有狀態 MCP 伺服器的大門。Cloudflare 上的 MCP 伺服器不僅僅是充當客戶端應用程式與外部 API 之間的無狀態層，它們本身就可以是有狀態的應用程式——遊戲、購物車與結帳流程、[持久化知識圖譜](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)，或者任何您能想像到的東西。當您在 Cloudflare 上構建時，MCP 伺服器可以遠超僅作為 REST API 前端的角色。

要理解其運作基本原理，讓我們看一個遞增計數器的最簡範例：

```JavaScript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

type State = { counter: number }

export class MyMCP extends McpAgent<Env, State, {}> {
  server = new McpServer({
    name: "Demo",
    version: "1.0.0",
  });

  initialState: State = {
    counter: 1,
  }

  async init() {
    this.server.resource(`counter`, `mcp://resource/counter`, (uri) => {
      return {
        contents: [{ uri: uri.href, text: String(this.state.counter) }],
      }
    })

    this.server.tool('add', 'Add to the counter, stored in the MCP', { a: z.number() }, async ({ a }) => {
      this.setState({ ...this.state, counter: this.state.counter + a })

      return {
        content: [{ type: 'text', text: String(`Added ${a}, total is now ${this.state.counter}`) }],
      }
    })
  }

  onStateUpdate(state: State) {
    console.log({ stateUpdate: state })
  }

}
```

對於給定的會話，上述 MCP 伺服器將在不同工具呼叫之間記住計數器的狀態。

在 MCP 伺服器內，您可以使用 Cloudflare 的整個開發者平台，讓您的 MCP 伺服器[啟動自己的網頁瀏覽器](https://developers.cloudflare.com/agents/api-reference/browse-the-web/)、[觸發 Workflow](https://developers.cloudflare.com/agents/api-reference/run-workflows/)、[呼叫 AI 模型](https://developers.cloudflare.com/agents/api-reference/using-ai-models/)等等。我們很高興看到 MCP 生態系演進到更進階的用例。

## 從目前僅支援本地 MCP 的客戶端連接到遠端 MCP 伺服器

Cloudflare 很早就開始支援遠端 MCP——在最著名的 MCP 客戶端應用程式支援遠端、經過驗證的 MCP 之前，以及在其他平台支援遠端 MCP 之前。我們這樣做是為了讓您在 MCP 的發展方向上搶佔先機。

但如果您今天構建遠端 MCP 伺服器，這會面臨一個挑戰——如果沒有支援遠端 MCP 的 MCP 客戶端，人們該如何開始使用您的 MCP 伺服器？

我們有兩個新工具，可以讓您測試遠端 MCP 伺服器並模擬使用者未來的互動方式：

我們更新了 [Workers AI Playground](https://playground.ai.cloudflare.com/)，使其成為一個完全遠端的 MCP 客戶端，允許您連接到任何具有內建身份驗證支援的遠端 MCP 伺服器。這個線上聊天介面讓您可以立即測試遠端 MCP 伺服器，而無需在裝置上安裝任何東西。只需輸入遠端 MCP 伺服器的 URL（例如 https://remote-server.example.com/sse）並點擊「Connect」。

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/4N64nJHJiQygmMdSK7clIs/c0bf8c64f1607674f81be10c3871a64b/image1.png)

點擊「Connect」後，您將進入身份驗證流程（如果您有設定的話），之後您就能直接從聊天介面與 MCP 伺服器工具互動。

如果您更偏好使用像 Claude Desktop 或 Cursor 這樣已經支援 MCP、但尚未處理帶身份驗證之遠端連接的客戶端，您可以使用 [mcp-remote](https://www.npmjs.com/package/mcp-remote)。mcp-remote 是一個適配器，讓原本僅支援本地連接的 MCP 客戶端能與遠端 MCP 伺服器配合使用。這讓您和您的使用者能在客戶端原生支援遠端 MCP 之前，從您目前已在使用的工具中預覽與遠端 MCP 伺服器的互動情況。

我們已經[發布了一份指南](https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/)，介紹如何在熱門的 MCP 客戶端（包括 Claude Desktop、Cursor 和 Windsurf）中使用 mcp-remote。在 Claude Desktop 中，您可以在設定檔中添加以下內容：

```JavaScript
{
  "mcpServers": {
    "remote-example": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://remote-server.example.com/sse"
      ]
    }
  }
}
```

遠端模型上下文協議 (MCP) 即將到來！當客戶端應用程式支援遠端 MCP 伺服器時，能使用它們的受眾將從僅限我們這些開發者，擴大到其餘大眾——他們甚至可能永遠不需要知道 MCP 是什麼或代表什麼。

構建遠端 MCP 伺服器是將您的服務帶入數百萬人使用的 AI 助手和工具的方法。我們很高興看到網際網路上許多大公司目前正忙著構建 MCP 伺服器，我們也對那些以代理優先、MCP 原生方式出現的新企業感到好奇。

在 Cloudflare 上，[您今天就可以開始構建](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)。我們已經準備好為您服務，並準備好協助您共同構建。請發送電子郵件至 [1800-mcp@cloudflare.com](mailto:1800-mcp@cloudflare.com)，我們將協助您開始。MCP 還有很多新功能即將推出，我們期待看到您的創作。

Cloudflare 的連線性雲 (connectivity cloud) 保護[整個企業網路](https://www.cloudflare.com/network-services/)，協助客戶[高效構建網際網路規模的應用程式](https://workers.cloudflare.com/)，加速任何[網站或網際網路應用程式](https://www.cloudflare.com/performance/accelerate-internet-applications/)，[抵禦 DDoS 攻擊](https://www.cloudflare.com/ddos/)，阻止[駭客入侵](https://www.cloudflare.com/application-security/)，並能協助您[邁向 Zero Trust 之旅](https://www.cloudflare.com/products/zero-trust/)。

從任何裝置造訪 [1.1.1.1](https://one.one.one.one/) 即可開始使用我們的免費應用程式，讓您的網際網路更快速且更安全。

要瞭解更多關於我們協助構建更好網際網路的使命，[請點此開始](https://www.cloudflare.com/learning/what-is-cloudflare/)。如果您正在尋找新的職涯方向，請查看[我們的職缺](http://www.cloudflare.com/careers)。

[AI](https://blog.cloudflare.com/tag/ai/)[Developers](https://blog.cloudflare.com/tag/developers/)[MCP](https://blog.cloudflare.com/tag/mcp/)[Agents](https://blog.cloudflare.com/tag/agents/)
