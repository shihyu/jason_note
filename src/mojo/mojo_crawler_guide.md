# Mojo 爬蟲完整指南

## 📚 目錄
- [Mojo 安裝](#mojo-安裝)
- [環境準備](#環境準備)
- [基礎爬蟲範例](#基礎爬蟲範例)
- [進階爬蟲範例](#進階爬蟲範例)
- [實用工具函數](#實用工具函數)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)

## 🚀 Mojo 安裝

### 系統需求
- **作業系統**: Ubuntu 20.04+ 或 macOS 12+
- **硬體**: x86-64 或 ARM64 架構
- **記憶體**: 至少 4GB RAM

### 安裝步驟

#### 方法 1: 官方安裝器（推薦）
```bash
# 1. 訪問 Modular 官網
curl -s https://get.modular.com | sh -

# 2. 安裝 Mojo
modular install mojo

# 3. 設定環境變數
echo 'export MODULAR_HOME="$HOME/.modular"' >> ~/.bashrc
echo 'export PATH="$MODULAR_HOME/pkg/packages.modular.com_mojo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 4. 驗證安裝
mojo --version
```

#### 方法 2: MAX Platform
```bash
# 1. 註冊並下載 MAX Platform
# 2. 安裝 MAX
sudo dpkg -i max-*.deb

# 3. 啟動 MAX
max auth login

# 4. 安裝 Mojo
max install mojo

# 5. 驗證
mojo --version
```

### 開發環境設定

#### VS Code 擴展
```bash
# 安裝 Mojo 語言支援
code --install-extension modular-mojotools.mojo
```

#### Jupyter Notebook 支援
```bash
# 安裝 Jupyter
pip install jupyter

# 註冊 Mojo 核心
max install jupyter

# 啟動 Jupyter
jupyter notebook
```

## 🛠️ 環境準備

### Python 依賴安裝
```bash
# 安裝爬蟲必要套件
pip install requests beautifulsoup4 lxml html5lib aiohttp

# 可選套件
pip install selenium pandas numpy
```

### 項目結構
```
mojo-crawler/
├── crawler.mojo          # 主爬蟲檔案
├── utils.mojo           # 工具函數
├── config.mojo          # 配置檔案
├── requirements.txt     # Python 依賴
└── README.md           # 說明文件
```

## 🕷️ 基礎爬蟲範例

### 1. 簡單的網頁爬蟲

```mojo
# crawler.mojo
from python import Python

def main():
    """基礎爬蟲範例"""
    
    # 導入 Python 模組
    let requests = Python.import_module("requests")
    let bs4 = Python.import_module("bs4")
    
    # 設定請求標頭
    let headers = Python.dict()
    headers["User-Agent"] = "Mozilla/5.0 (compatible; MojoCrawler/1.0)"
    
    try:
        # 發送 HTTP 請求
        let url = "https://example.com"
        let response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 請求成功")
            
            # 解析 HTML
            let soup = bs4.BeautifulSoup(response.content, "html.parser")
            
            # 提取標題
            let title = soup.find("title")
            if title:
                print("標題:", title.get_text())
            
            # 提取所有連結
            let links = soup.find_all("a", href=True)
            print(f"找到 {len(links)} 個連結")
            
            for i in range(min(5, len(links))):  # 只顯示前5個
                let link = links[i]
                print(f"  {i+1}. {link.get_text()}: {link['href']}")
                
        else:
            print("❌ 請求失敗, 狀態碼:", response.status_code)
            
    except Exception as e:
        print("錯誤:", e)
```

### 2. JSON API 爬蟲

```mojo
def crawl_json_api():
    """爬取 JSON API 數據"""
    
    let requests = Python.import_module("requests")
    let json = Python.import_module("json")
    
    let headers = Python.dict()
    headers["Accept"] = "application/json"
    headers["User-Agent"] = "MojoCrawler/1.0"
    
    try:
        # 爬取 API 數據
        let api_url = "https://jsonplaceholder.typicode.com/posts"
        let response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            let data = response.json()
            print(f"📊 獲取到 {len(data)} 筆數據")
            
            # 處理前3筆數據
            for i in range(min(3, len(data))):
                let post = data[i]
                print(f"\n📝 貼文 {i+1}:")
                print(f"  標題: {post['title']}")
                print(f"  用戶ID: {post['userId']}")
                print(f"  內容: {post['body'][:50]}...")
                
        else:
            print("❌ API 請求失敗")
            
    except Exception as e:
        print("錯誤:", e)
```

## 🚀 進階爬蟲範例

### 1. 面向對象的爬蟲類

```mojo
from python import Python
from memory import Reference

struct WebCrawler:
    """高性能網頁爬蟲"""
    var session: PythonObject
    var headers: PythonObject
    var delay: Float64
    var max_retries: Int
    
    fn __init__(inout self):
        """初始化爬蟲"""
        let requests = Python.import_module("requests")
        self.session = requests.Session()
        
        # 設定標頭
        self.headers = Python.dict()
        self.headers["User-Agent"] = "Mozilla/5.0 (compatible; MojoCrawler/2.0)"
        self.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        self.headers["Accept-Language"] = "zh-TW,zh;q=0.9,en;q=0.8"
        self.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.headers["Connection"] = "keep-alive"
        
        self.delay = 1.0
        self.max_retries = 3
    
    fn fetch_url(self, url: String) raises -> PythonObject:
        """獲取 URL 內容（帶重試機制）"""
        let time = Python.import_module("time")
        
        for retry in range(self.max_retries):
            try:
                let response = self.session.get(
                    url, 
                    headers=self.headers, 
                    timeout=10,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    print(f"⚠️ 請求過於頻繁，等待 {(retry + 1) * 2} 秒...")
                    time.sleep((retry + 1) * 2)
                else:
                    print(f"❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"🔄 重試 {retry + 1}/{self.max_retries}: {e}")
                if retry < self.max_retries - 1:
                    time.sleep(self.delay * (retry + 1))
        
        raise Error("所有重試都失敗了")
    
    fn parse_html(self, html_content: PythonObject) -> PythonObject:
        """解析 HTML 內容"""
        let bs4 = Python.import_module("bs4")
        return bs4.BeautifulSoup(html_content, "html.parser")
    
    fn extract_data(self, soup: PythonObject) -> PythonObject:
        """提取結構化數據"""
        let data = Python.dict()
        
        # 提取標題
        let title = soup.find("title")
        data["title"] = title.get_text().strip() if title else "無標題"
        
        # 提取 meta 描述
        let meta_desc = soup.find("meta", attrs={"name": "description"})
        data["description"] = meta_desc.get("content", "") if meta_desc else ""
        
        # 提取所有標題
        let headings = Python.list()
        for level in range(1, 7):  # h1-h6
            let tags = soup.find_all(f"h{level}")
            for i in range(len(tags)):
                let heading = tags[i]
                headings.append({
                    "level": level,
                    "text": heading.get_text().strip()
                })
        data["headings"] = headings
        
        # 提取連結
        let links = Python.list()
        let link_tags = soup.find_all("a", href=True)
        for i in range(len(link_tags)):
            let link = link_tags[i]
            links.append({
                "text": link.get_text().strip(),
                "url": link["href"]
            })
        data["links"] = links
        
        # 提取圖片
        let images = Python.list()
        let img_tags = soup.find_all("img", src=True)
        for i in range(len(img_tags)):
            let img = img_tags[i]
            images.append({
                "src": img["src"],
                "alt": img.get("alt", "")
            })
        data["images"] = images
        
        return data
```

### 2. 批量爬蟲範例

```mojo
def batch_crawl_demo():
    """批量爬蟲示例"""
    
    let time = Python.import_module("time")
    let json = Python.import_module("json")
    
    var crawler = WebCrawler()
    
    # 要爬取的 URL 列表
    let urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    
    let results = Python.list()
    
    print("🚀 開始批量爬取...")
    
    for i in range(len(urls)):
        let url = urls[i]
        print(f"\n📄 正在處理第 {i+1}/{len(urls)} 個: {url}")
        
        try:
            # 獲取頁面
            let response = crawler.fetch_url(url)
            
            # 解析內容
            if "application/json" in str(response.headers.get("content-type", "")):
                # JSON 數據
                let data = response.json()
                results.append({
                    "url": url,
                    "type": "json",
                    "data": data
                })
            else:
                # HTML 數據
                let soup = crawler.parse_html(response.content)
                let extracted_data = crawler.extract_data(soup)
                results.append({
                    "url": url,
                    "type": "html",
                    "data": extracted_data
                })
            
            print("✅ 處理完成")
            
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            results.append({
                "url": url,
                "type": "error",
                "error": str(e)
            })
        
        # 請求間隔
        if i < len(urls) - 1:
            time.sleep(crawler.delay)
    
    # 保存結果
    try:
        with open("crawl_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n💾 結果已保存到 crawl_results.json")
    except Exception as e:
        print(f"💥 保存失敗: {e}")
    
    print(f"\n🎉 批量爬取完成! 共處理 {len(urls)} 個 URL")
```

## 🛠️ 實用工具函數

### 1. URL 工具

```mojo
def normalize_url(base_url: String, relative_url: String) -> String:
    """規範化 URL"""
    let urllib = Python.import_module("urllib.parse")
    return str(urllib.urljoin(base_url, relative_url))

def is_valid_url(url: String) -> Bool:
    """檢查 URL 是否有效"""
    let urllib = Python.import_module("urllib.parse")
    let parsed = urllib.urlparse(url)
    return bool(parsed.netloc and parsed.scheme)
```

### 2. 數據處理工具

```mojo
def clean_text(text: PythonObject) -> String:
    """清理文本數據"""
    let re = Python.import_module("re")
    
    # 移除多餘空白
    cleaned = re.sub(r'\s+', ' ', str(text))
    
    # 移除特殊字符
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', cleaned)
    
    return str(cleaned).strip()

def extract_emails(text: String) -> PythonObject:
    """提取電子郵件地址"""
    let re = Python.import_module("re")
    let pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def extract_phone_numbers(text: String) -> PythonObject:
    """提取電話號碼（臺灣格式）"""
    let re = Python.import_module("re")
    let patterns = [
        r'09\d{8}',           # 手機號碼
        r'0\d{1,2}-\d{7,8}',  # 市話
        r'\(\d{2,3}\)\d{7,8}' # 括號格式
    ]
    
    let results = Python.list()
    for pattern in patterns:
        let matches = re.findall(pattern, text)
        results.extend(matches)
    
    return results
```

### 3. 數據存儲工具

```mojo
def save_to_csv(data: PythonObject, filename: String):
    """保存數據到 CSV"""
    let pandas = Python.import_module("pandas")
    
    try:
        let df = pandas.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 數據已保存到 {filename}")
    except Exception as e:
        print(f"💥 CSV 保存失敗: {e}")

def save_to_json(data: PythonObject, filename: String):
    """保存數據到 JSON"""
    let json = Python.import_module("json")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 數據已保存到 {filename}")
    except Exception as e:
        print(f"💥 JSON 保存失敗: {e}")
```

## 📋 最佳實踐

### 1. 尊重 robots.txt

```mojo
def check_robots_txt(base_url: String) -> Bool:
    """檢查 robots.txt"""
    let urllib = Python.import_module("urllib.robotparser")
    
    let robots_url = base_url.rstrip('/') + '/robots.txt'
    let rp = urllib.RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
        return rp.can_fetch('*', base_url)
    except:
        return True  # 如果無法讀取，假設允許
```

### 2. 請求限制

```mojo
struct RateLimiter:
    """請求速率限制器"""
    var last_request_time: Float64
    var min_interval: Float64
    
    fn __init__(inout self, requests_per_second: Float64):
        self.last_request_time = 0.0
        self.min_interval = 1.0 / requests_per_second
    
    fn wait_if_needed(inout self):
        """如有需要則等待"""
        let time = Python.import_module("time")
        let current_time = float(time.time())
        
        let time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            let wait_time = self.min_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = float(time.time())
```

### 3. 錯誤處理

```mojo
def robust_crawl(url: String) -> PythonObject:
    """具有強健錯誤處理的爬蟲函數"""
    let requests = Python.import_module("requests")
    let time = Python.import_module("time")
    
    let max_retries = 3
    let backoff_factor = 2
    
    for attempt in range(max_retries):
        try:
            let response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "MojoCrawler/1.0"}
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                let wait_time = backoff_factor ** attempt
                print(f"⏳ 請求限制，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"🔄 嘗試 {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
    
    raise Error("所有嘗試都失敗了")
```

## 💡 常見問題

### Q: Mojo 相比 Python 有什麼優勢？

**A:** Mojo 在爬蟲方面的優勢：
- **性能**: 比 Python 快 10-100 倍
- **記憶體效率**: 更好的記憶體管理
- **並行處理**: 原生支援並行計算
- **兼容性**: 可以直接使用 Python 套件

### Q: 如何處理反爬蟲機制？

**A:** 常見策略：
```mojo
# 1. 隨機 User-Agent
let user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

# 2. 使用代理
let proxies = {
    "http": "http://proxy:port",
    "https": "https://proxy:port"
}

# 3. 模擬真實行為
time.sleep(random.uniform(1, 3))
```

### Q: 如何處理 JavaScript 渲染的頁面？

**A:** 使用 Selenium：
```mojo
def crawl_js_page(url: String) -> PythonObject:
    let selenium = Python.import_module("selenium")
    let webdriver = selenium.webdriver
    
    let driver = webdriver.Chrome()
    driver.get(url)
    
    # 等待頁面載入
    let time = Python.import_module("time")
    time.sleep(3)
    
    let content = driver.page_source
    driver.quit()
    
    return content
```

### Q: 如何進行分散式爬蟲？

**A:** 可以結合 Celery 或 RQ：
```mojo
# 任務分發
def distribute_urls(urls: PythonObject, num_workers: Int) -> PythonObject:
    let chunks = Python.list()
    let chunk_size = len(urls) // num_workers
    
    for i in range(num_workers):
        let start = i * chunk_size
        let end = start + chunk_size if i < num_workers - 1 else len(urls)
        chunks.append(urls[start:end])
    
    return chunks
```

## 🎯 完整範例運行

```bash
# 1. 創建項目目錄
mkdir mojo-crawler && cd mojo-crawler

# 2. 創建並運行爬蟲
echo '# 上面的完整代碼' > crawler.mojo
mojo crawler.mojo

# 3. 查看結果
cat crawl_results.json
```

## 📚 進階學習資源

- [Mojo 官方文檔](https://docs.modular.com/mojo/)
- [Modular 開發者社群](https://discord.gg/modular)
- [Mojo GitHub 範例](https://github.com/modularml/mojo)

---

**注意**: 請務必遵守目標網站的使用條款和 robots.txt 規則，進行合理合法的數據收集。