# iT 邦幫忙::一起幫忙解決難題，拯救 IT 人的一天

在現代前端開發中，前後端的界線越來越模糊。**前端靜態頁面**和**後端無伺服器運算**的結合，讓開發者能以最少的基礎建設快速上線專案。Cloudflare 提供的 **Pages** 與 **Functions**，正是這種模式的最佳搭配。本文將帶你快速了解兩者的特性，以及如何結合使用。

---

## Cloudflare Pages：前端靜態網站平台

Cloudflare Pages 是一個 **靜態網站託管服務**，支援從 GitHub/GitLab 自動部署。特色包括：

-   **免費 & 全球 CDN**：內容自動分發到 Cloudflare 的邊緣節點，確保快速載入。
-   **CI/CD 整合**：每次 push 代碼就會自動部署。
-   **Preview Deployments**：每個 PR 都會產生預覽連結，方便團隊測試。
-   **自訂網域**：可以綁定自己的網域並自動支援 HTTPS。
-   **環境變數支援**：可在不同部署環境（Production/Preview/Dev）設定 API keys、config。

📌 適合用來部署：

-   個人作品集
-   前端框架專案（React、Vue、Next.js、Astro）
-   文件網站或靜態部落格（Hugo、Jekyll

![https://ithelp.ithome.com.tw/upload/images/20250928/2016341610UCRfAVaC.png](https://ithelp.ithome.com.tw/upload/images/20250928/2016341610UCRfAVaC.png)  
[https://developers.cloudflare.com/pages/framework-guides/](https://developers.cloudflare.com/pages/framework-guides/)

---

## Cloudflare Functions：邊緣運算的後端

Functions 是 Cloudflare 提供的 **無伺服器函式運算**（類似 AWS Lambda、Vercel Functions），但運行在 Cloudflare 的邊緣節點。特色包括：

-   **全球邊緣節點**：程式碼在用戶最近的 Cloudflare 節點執行，延遲極低。
-   **無伺服器**：不需要維護伺服器，Cloudflare 會自動擴展。
-   **事件驅動**：支援 
    ```
    fetch
    ```
    、HTTP API 呼叫等事件觸發。
-   **原生整合 Cloudflare 生態系**：可與 KV、D1（資料庫）、R2（S3 物件儲存）結合。
-   **語言支援**：主要使用 JavaScript/TypeScript，並逐步支援更多生態。

適合用來處理：

-   API Proxy（避免 CORS 問題）
-   使用者驗證（Auth / JWT）
-   表單處理與寄信
-   輕量 API（查詢資料庫、KV、Redis）
---

## Pages + Functions：完美結合

Cloudflare Pages 與 Functions 的關係，可以理解成 **前端 + 後端** 的組合。

-   **Pages**：負責靜態資源（HTML/CSS/JS）的快速載入。
-   **Functions**：負責動態需求（API、商業邏輯、與資料庫互動）。

**範例情境**

1.  **靜態網站 + 後端 API**
    
      3.   前端：使用 React 部署到 Pages。
      4.   後端：在 Functions 中建立 
          ```
          /api/*
          ```
           路由，提供資料給前端呼叫。
    
2.  **表單處理**
    
      12.   頁面表單透過 
          ```
          fetch('/api/submit')
          ```
           呼叫 Functions。
      17.   Functions 驗證資料並存到 Cloudflare D1 或 KV。
    
3.  **動態內容**
    
      21.   使用 Pages 提供部落格靜態頁面。
      22.   Functions 根據請求動態產生內容（例如 Markdown 轉換、RSS Feed）。
---

## 實際範例：Pages + Functions

### 1\. 新建專案

```
npm create cloudflare@latest my-app
cd my-app

```

### 2\. 啟用 Functions

在專案中新增 
```
functions/hello-world.js
```
：

```
export async functiononRequest(context) {
  return new Response("Hello from Cloudflare Functions!");
}

```

### 3\. 部署

```
npx wrangler pages deploy ./dist

```

部署後，你可以透過  
```
https://<your-project>.pages.dev/hello-world
```
  
看到 Functions 的輸出。

---

## 結語

Cloudflare Pages 與 Functions 提供了 **全靜態網站 + 輕量後端 API** 的完美解決方案，開發者能夠用最少的基礎設施快速打造完整應用。無論是個人部落格、作品集，還是中小型 Web App，都可以透過 Pages + Functions 來實現高效、安全、可擴展的架構。

如果你已經有一個 GitHub Repo 的靜態頁面，部署到 **Pages** 只要幾分鐘，而加上 **Functions** 後，你的靜態網站就瞬間升級成 **全端應用** 。

