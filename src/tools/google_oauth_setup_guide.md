# Google OAuth 2.0 憑證設定指南

## 前置準備
- 確保已有 Google Cloud Platform (GCP) 帳戶
- 已建立或選擇一個 GCP 專案

## 步驟一：前往憑證頁面
1. 登入 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇您的專案
3. 前往「API 和服務」→「憑證」頁面

## 步驟二：設定 OAuth 同意畫面（首次設定時）
如果是第一次建立 OAuth 憑證，需要先設定同意畫面：

1. 點擊「OAuth 同意畫面」分頁
2. 選擇使用者類型：
   - **外部**：供一般使用者使用（推薦）
   - 內部：僅限組織內部使用者
3. 填寫必要資訊：
   - **應用程式名稱**：輸入您的應用程式名稱
   - **使用者支援電子郵件**：選擇或輸入您的 email
   - **開發人員聯絡資訊**：輸入您的 email 地址
4. 點擊「儲存並繼續」
5. 依需求設定範圍（Scopes），一般情況可先跳過
6. 完成設定

## 步驟三：建立 OAuth 2.0 憑證
1. 回到「憑證」分頁
2. 點擊「+ 建立憑證」
3. 選擇「OAuth 用戶端 ID」
4. 設定憑證詳細資訊：
   - **應用程式類型**：選擇「網路應用程式」
   - **名稱**：輸入有意義的名稱（例如：遊戲平臺、網站後端等）
   
5. 設定重新導向 URI：
   - 在「已授權的重新導向 URI」區域點擊「+ 新增 URI」
   - 輸入：`http://127.0.0.1:8001/accounts/google/login/callback/`
   - 如有其他環境（如正式站），也可一併加入

6. 點擊「建立」

## 步驟四：取得憑證資訊
建立完成後，系統會顯示：
- **用戶端 ID**（Client ID）
- **用戶端密鑰**（Client Secret）

請妥善保存這些資訊，並在您的應用程式中使用。

## 常見的重新導向 URI 範例
- 本地開發：`http://127.0.0.1:8001/accounts/google/login/callback/`
- 本地開發（localhost）：`http://localhost:8001/accounts/google/login/callback/`
- 正式環境：`https://yourdomain.com/accounts/google/login/callback/`

## 注意事項
- 重新導向 URI 必須完全符合您在程式中設定的回調地址
- 開發階段可以使用 HTTP，但正式環境建議使用 HTTPS
- 如需修改設定，隨時可以回到憑證頁面進行編輯
- 用戶端密鑰應妥善保管，不要公開在前端程式碼中

## 測試驗證
設定完成後，可以透過您的應用程式測試 Google OAuth 登入功能是否正常運作。
